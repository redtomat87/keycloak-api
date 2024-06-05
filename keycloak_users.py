import json, os, common
from vars.creds import password, client_id
from vars.env_vars import users_url_query_params, users_url, token_url, username, users_to_keep, client_scopes_url, page_size, users_file_path, keycloak_url, realm_name
from requests import exceptions as rexcept


log = common.logging.getLogger(__name__)
common.configure_logging()

def set_headers(access_token=None):
    headers = {
        'Content-Type': 'application/json',
        "Authorization": f"Bearer {access_token}" if access_token else ""
        }
    return headers

def get_access_token():
 #   global access_token
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
        token_response = common.s.post(token_url, headers=headers, data=token_data)
        token_response.raise_for_status() 
        access_token = token_response.json()['access_token']
        log.debug("access_token: %s", access_token)
    except rexcept.HTTPError as e:
        log.error("HTTP exception: %s", e)
        log.error("Статус код: %s", token_response.status_code)
        log.error("Ответ сервера: %s", token_response.text)
        raise 
    return access_token

def get_users(headers, **kwargs):
    users_url_query_params['briefRepresentation'] = 'True'
    log.debug("Users_url_query_params: %s", users_url_query_params)
    pagination = 0
    if os.path.isfile(users_file_path):
        with open('list_of_users.json', 'w') as json_file:
            json_file.truncate(0) 
    while True:
        try:
            users_url_query_params['first'] = pagination
            log.debug("query starts")
            users_response = common.s.get(users_url, headers=headers, params=users_url_query_params, timeout=(2, 20))
            log.debug("query responce: %s ", users_response.status_code)
            users_response.raise_for_status()
            list_of_users = users_response.json()
         #   print(f"Список пользователей: {list_of_users}")
            with open('list_of_users.json', 'a') as json_file:
               json.dump(list_of_users, json_file)
            log.info("Page: %s", pagination)
            log.info("Page size: %s", page_size)
            log.info("The amount returned by the server: %s", len(list_of_users))
            pagination += page_size
        #    all_users = all_users.extend(list_of_users)
       #     log.info("Найдено пользователей: %" {len(all_users)})
            if len(list_of_users) < page_size:
                break
        except rexcept.Timeout as e:
                log.error("Timeout error: ", e)
                continue
        except rexcept.JSONDecodeError as e:
            log.error("Json decoding error: %s", e)
        except rexcept.HTTPError as e:
            log.error("HTTP exception: %s", e)
        except rexcept.ConnectionError as e:
            log.error("HTTP exception connection error: %s", e)
    return list_of_users
    
def validate_token(access_token, headers):
    validation_url = f'{keycloak_url}/realms/{realm_name}/protocol/openid-connect/userinfo'
    log.debug("VALIDATING TOKEN:  %s", access_token)
 #   headers = {"Authorization": f"Bearer {access_token}"}
    response = common.s.get(url=validation_url, headers=headers)
    log.debug("STATUS:  %s", response.status_code)
    if response.status_code == 200:
        log.debug("Token is valid!")
        return True
    else:
        log.debug("Token is invalid. Requesting new access_token...")
        return False
        
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
        print("Удаление пользователей отменено.")

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
    access_token = get_access_token()
    headers = set_headers(access_token)
  #  get_client_scopes()
    list_of_users = get_users(headers=headers)
    validate_token(access_token, headers)
  #  list_of_disabled_users = get_disabled_users()
  #  delete_users(list_of_users=list_of_users, headers=headers)
