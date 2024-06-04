import os
import common, requests, json
from vars.creds import password, client_id
from vars.env_vars import token_url, username, token_file_path, keycloak_url, realm_name
log = common.logging.getLogger(__name__)
common.configure_logging()

class KeycloakTokenValidator:
    def __init__(self, token_file_path=token_file_path):
        self.token_file = token_file_path
        self.access_token = None
        self.validation_url = f'{keycloak_url}/realms/{realm_name}/protocol/openid-connect/userinfo'

    def read_token(self):
        if os.path.isfile(self.token_file):
            with open(self.token_file, 'r') as file:
                access_token = json.load(file)
                log.debug("Getted token data: %s ", access_token)
                isValid = self.validate_token(access_token)
                if isValid:
                    return access_token
                else:
                    return self.request_new_token()
        else:
            return self.request_new_token()

    def validate_token(self, access_token):
        validation_url = self.validation_url
        log.debug("VALIDATING TOKEN:  %s", access_token)
        headers = {"Authorization": f"Bearer {access_token}"}

        response = requests.get(url=validation_url, headers=headers)
        log.debug("STATUS:  %s", response.status_code)

        if response.status_code == 200:
            log.debug("Token is valid!")
            return True
        else:
            log.debug("Token is invalid. Requesting new access_token...")
            return False

    def request_new_token(self):
        headers = {
            "Accept-Encoding": "gzip, deflate, br",
            "response_type": "code",
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
            access_token = token_response.json()['access_token']
            log.debug("new access token: %s", access_token)
            with open(self.token_file, 'w') as file:
                json.dump(access_token, file)
            return access_token
        except requests.exceptions.HTTPError as e:
            log.error("HTTP exception: %s", e)
            log.error("Status code: %s", token_response.status_code)
            log.error("Responce: %s", token_response.text)
        except json.JSONDecodeError as e:
            log.error("JSONDecodeError: %s", e)
        return None


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