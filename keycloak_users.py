import json, os, common
from vars.env_vars import users_url_query_params, users_url, users_to_keep, client_scopes_url, page_size, users_file_path, keycloak_url, realm_name, saml_assertion_cert_file, client_uuid, cert_type
from requests import exceptions as rexcept
from access_token import KeycloakTokenValidator


log = common.logging.getLogger(__name__)
common.configure_logging()

def get_users(headers, users_url_query_params=users_url_query_params, **kwargs):
    log.debug("Users_url_query_params: %s", users_url_query_params)
    if os.path.isfile(users_file_path):
        with open(users_file_path, 'w') as json_file:
            json_file.write('[\n') 

    is_first_chunk = True

    while True:
        try:
            log.debug("query starts")
            users_response = common.s.get(
                users_url,
                headers=headers,
                params=users_url_query_params,
                timeout=(2, 300))
            log.debug("query responce: %s ", users_response.status_code)
            users_response.raise_for_status()
            users_chunk = users_response.json()
            if not users_chunk:
                break
            if not isinstance(users_chunk, list):
                log.error("Invalid response format")
                break
            with open(users_file_path, 'a') as f:
                for user in users_chunk:
                    if is_first_chunk:
                        is_first_chunk = False
                    else:
                        f.write(',\n')
                    json.dump(user, f)
            log.info("Total: %s", users_url_query_params['first'])
            log.info("Page size: %s", page_size)
            log.info("The amount returned by the server: %s", len(users_chunk))
            users_url_query_params['first'] += len(users_chunk)
            if len(users_chunk) < page_size:
                break
        except rexcept.ChunkedEncodingError as e:
            log.error("last chunk %s", users_chunk)
            log.error("Response ended prematurely, All users were requested  %s", e)
            break
        except rexcept.Timeout as e:
            log.error("Timeout error: %s", e)
            continue
        except rexcept.JSONDecodeError as e:
            log.error("Json decoding error: %s", e)
        except rexcept.HTTPError as e:
            log.error("Response content: %s", e.response.text)
            log.error("HTTP exception: %s", e)
        except rexcept.ConnectionError as e:
            log.error("HTTP exception connection error: %s", e)
        except KeyboardInterrupt:
            with open(users_file_path, 'a') as f:
                f.write('\n]')
            raise
        # except Exception as e:
        #     log.error("Fatal error: %s", e)
        #     break
    
    with open(users_file_path, 'a') as f:
        f.write('\n]')
    return users_chunk
        
def delete_users(list_of_users, **kwargs):
    confirmation = input("Вы уверены, что хотите удалить пользователей? Введите 'YES IM SURE' для подтверждения: ")
    if confirmation == 'YES IM SURE':
        for user in list_of_users:
            if user['username'] not in users_to_keep:
                # delete_user_url = f'{users_url}/{user['id']}'
                # delete_user_response = common.s.delete(delete_user_url, headers=headers)
                # if delete_user_response.status_code == 204:
                #     print(f'User with ID {user['id']} has been deleted')
                # else:
                #     print(f'Failed to delete user with ID {user['id']}')
                    print(f"ID: {user['id']}, Username: {user['username']}")
    else:
        log.info("Удаление пользователей отменено.")

def get_client_scopes(client_scopes_url=client_scopes_url):
    try:
        client_scopes_response = common.s.get(client_scopes_url, headers=headers)
        client_scopes_response.raise_for_status()
        client_scopes = client_scopes_response.json()
        for client_scope in client_scopes:
            log.debug("Список client scopes: %s", client_scope['id'])
            log.debug("Список client scopes: %s", client_scope['name'])
    except rexcept.HTTPError as e:
        log.error("HTTP exceptiom: %s ", e)
        log.error("Статус код: %s", client_scopes_response.status_code)
        log.error("Ответ сервера: %s", client_scopes_response.text)
        raise
    return client_scopes_response

def get_disabled_users():
    users_url_query_params['enabled'] = 'False'
    list_of_disabled_users = get_users(headers, users_url_query_params=users_url_query_params)
    return list_of_disabled_users

if __name__ == "__main__":    
    validator = KeycloakTokenValidator()
    access_token = validator.read_token()
    headers = common.set_headers(access_token)
    # log.debug("Headers: %s", headers)
  #  get_client_scopes()
    # list_of_users = get_users(headers=headers)
    validator.validate_token(access_token)
  #  list_of_disabled_users = get_disabled_users()
  #  delete_users(list_of_users=list_of_users, headers=headers)
