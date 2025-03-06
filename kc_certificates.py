import common
from vars.env_vars import keycloak_url, realm_name, saml_assertion_cert_file, client_uuid, cert_type
from requests import exceptions as rexcept
from access_token import KeycloakTokenValidator

log = common.logging.getLogger(__name__)
common.configure_logging()

def read_pem_certificate() -> str:
    try:
        with open(saml_assertion_cert_file, "r", encoding="utf-8") as cert_file:
            return cert_file.read().strip()
    except FileNotFoundError:
        raise ValueError("Certificate file not found")

def post_certificate(client_uuid, attr, headers) -> None:
    files = {
        'keystoreFormat': (None, 'Certificate PEM'),
        'file': (
                 open(saml_assertion_cert_file, 'rb')
                 )
    }
    upload_headers = {'Authorization': headers['Authorization']}
    client_cert_update_url = f'{keycloak_url}/admin/realms/{realm_name}/clients/{client_uuid}/certificates/{attr}/upload-certificate'
    try:
        response = common.s.post(
            client_cert_update_url,
            headers=upload_headers,
            files=files,
            timeout=(2, 20)
        )
        log.debug("query responce: %s ", response.status_code)
        response.raise_for_status()
    except rexcept.HTTPError as e:
        log.error("Response content: %s", e.response.text)
        log.error("HTTP exception: %s", e)
    except rexcept.ConnectionError as e:
        log.error("HTTP exception connection error: %s", e)
    except rexcept.RequestException as e:
        log.error("Request failed: %s", str(e))
        raise
    except KeyboardInterrupt as e:
        log.error("Iterrupted by user: %s", e)
        raise


if __name__ == "__main__":    
    validator = KeycloakTokenValidator()
    access_token = validator.read_token()
    headers = common.set_headers(access_token)
    post_certificate(
            client_uuid=client_uuid,
            attr=cert_type,
            headers=headers,
        )
    # log.debug("Headers: %s", headers)
  #  get_client_scopes()
    # list_of_users = get_users(headers=headers)
    validator.validate_token(access_token)
  #  list_of_disabled_users = get_disabled_users()
  #  delete_users(list_of_users=list_of_users, headers=headers)
