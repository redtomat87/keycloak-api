import datetime, common, json
from jwt import PyJWKClient, exceptions, decode
from models.settings_model import config
from requests import exceptions as rexcept
from functools import lru_cache

log = common.logging.getLogger(__name__)
common.configure_logging()

class KeycloakTokenValidator:
    def __init__(self):
        self.validation_url = f"{config.keycloak_url}/realms/{config.realm_name}/protocol/openid-connect/certs"

    @lru_cache(maxsize=1)
    def get_cached_token(self):
        return self.request_new_token()

    def read_token(self):
        access_token = self.get_cached_token()
        if access_token and self.validate_token(access_token):
            log.info("Cached token validated and returned")
            return access_token
        else:
            log.info("Cached token invalid or not found. Requesting new token")
            return self.request_new_token()

    def validate_token(self, access_token):
        try:
            jwk_client = PyJWKClient(self.validation_url)
            signing_key = jwk_client.get_signing_key_from_jwt(access_token)
            decoded_token = decode(access_token, signing_key.key, algorithms=["RS256"], options={"verify_signature": False})
            log.debug("Decoded token: %s", decoded_token)

            expires_at = decoded_token.get('exp')
            if expires_at:
                expires_at = datetime.datetime.fromtimestamp(expires_at)
                if expires_at < datetime.datetime.now():
                    log.error("Token has expired")
                    return False

            return True
        except exceptions.ExpiredSignatureError as e:
            log.error("Token has expired: %s", e)
            return False
        except exceptions.InvalidTokenError as e:
            log.error("Invalid token error: %s", e)
            return False
        except Exception as e:
            log.error("Error during token validation: %s", e)
            return False

    def request_new_token(self):
        headers = {
            "Accept-Encoding": "gzip, deflate, br",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        token_data = {
            'grant_type': 'password',
            'client_id': config.client_id,
            'username': config.username,
            'password': config.password
        }
        try:
            token_response = common.s.post(config.token_url, headers=headers, data=token_data)
            token_response.raise_for_status()
            access_token_data = token_response.json()
            access_token = access_token_data.get('access_token')
            if not access_token:
                log.error("No access token found in response")
                return None
            log.debug("New access token: %s", access_token)
            return access_token
        except rexcept.HTTPError as e:
            log.error("HTTP exception: %s", e)
            log.error("Status code: %s", token_response.status_code)
            log.error("Response: %s", token_response.text)
        except json.JSONDecodeError as e:
            log.error("JSON decode error: %s", e)
        return None


try:
    validator = KeycloakTokenValidator()
except Exception as e:
    print(f"Configuration error: {str(e)}")
    exit(1)

if __name__ == '__main__':
    validator = KeycloakTokenValidator()
    access_token = validator.read_token()

    if not access_token:
        access_token = validator.request_new_token()

    if access_token and validator.validate_token(access_token):
        print("Token is valid!")
    else:
        print("Token is invalid!")