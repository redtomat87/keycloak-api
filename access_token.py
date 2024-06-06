import os, datetime, common, requests, json
from jwt import PyJWKClient, exceptions, decode
import common, requests, json
from vars.creds import password, client_id
from vars.env_vars import token_url, username, token_file_path, keycloak_url, realm_name
log = common.logging.getLogger(__name__)
common.configure_logging()

class KeycloakTokenValidator:
    def __init__(self, token_file_path=token_file_path):
        self.token_file = token_file_path
        self.access_token = None
        self.validation_url = f"{keycloak_url}/realms/{realm_name}/protocol/openid-connect/certs"

    def read_token(self):
        if os.path.isfile(self.token_file):
            with open(self.token_file, 'r') as file:
                access_token = json.load(file)
                log.debug("Fetched token data: %s", access_token)
                if self.validate_token(access_token):
                    log.info("Token from file validated and returned")
                    return access_token
                else:
                    log.info("Token invalid and requested new one")
                    return self.request_new_token()
        else:
            log.info("Token file didn't finded. Requesting new token")
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
            'client_id': client_id,
            'username': username,
            'password': password
        }
        try:
            token_response = requests.post(token_url, headers=headers, data=token_data)
            token_response.raise_for_status()
            access_token = token_response.json().get('access_token')
            if not access_token:
                log.error("No access token found in response")
                return None
            log.debug("New access token: %s", access_token)
            with open(self.token_file, 'w') as file:
                json.dump(access_token, file)
            return access_token
        except requests.exceptions.HTTPError as e:
            log.error("HTTP exception: %s", e)
            log.error("Status code: %s", token_response.status_code)
            log.error("Response: %s", token_response.text)
        except json.JSONDecodeError as e:
            log.error("JSON decode error: %s", e)
        return access_token



    def write_token(self, access_token):
        new_token_data = {"access_token": access_token}
        try:
            with open(self.token_file, 'w') as file:
                json.dump(new_token_data, file)
        except Exception as e:
            log.error("Some error: %s", e)


if __name__ == '__main__':
    validator = KeycloakTokenValidator()
    access_token = validator.read_token()
    # log.debug("Main token: %s: ", access_token)
    # if access_token is None:
    #     access_token = validator.request_new_token()
    # if validator.validate_token(access_token):
    #     print("Token is valid!")
    # else:
    #     print("Token is invalid!")