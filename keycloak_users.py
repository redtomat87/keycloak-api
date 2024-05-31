# delete users testing 
import common, requests, json
from vars.creds import password, client_id
from vars.env_vars import users_url_query_params, users_url, token_url, username, users_to_keep, client_scopes_url

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
        token_response = requests.post(token_url, headers=headers, data=token_data)
        token_response.raise_for_status() 
        access_token = token_response.json()['access_token']
        log.debug("access_token: %s", access_token)
    except requests.exceptions.HTTPError as e:
        log.error("HTTP исключение: %s", e)
        log.error("Статус код: %s", token_response.status_code)
        log.error("Ответ сервера: %s", token_response.text)
        raise 
    return access_token

def get_users(headers, **kwargs):
    try:
        users_response = requests.get(users_url, headers=headers, params=users_url_query_params)
        users_response.raise_for_status()
        list_of_users = users_response.json()
     #   print(f"Список пользователей: {list_of_users}")
        with open('list_of_users.json', 'w') as json_file:
           json_file.truncate(0) 
           json.dump(list_of_users, json_file)
    except requests.exceptions.HTTPError as e:
        print(f"HTTP исключение: {e}\n Ответ сервера: {users_response.text} \n Сатус код: {users_response.status_code}")
        raise
    return list_of_users

def delete_users(list_of_users, **kwargs):
    confirmation = input("Вы уверены, что хотите удалить пользователей? Введите 'YES IM SURE' для подтверждения: ")
    if confirmation == 'YES IM SURE':
        for user in list_of_users:
            if user['username'] not in users_to_keep:
                # delete_user_url = f'{users_url}/{user['id']}'
                # delete_user_response = requests.delete(delete_user_url, headers=headers)
                # if delete_user_response.status_code == 204:
                #     print(f'User with ID {user['id']} has been deleted')
                # else:
                #     print(f'Failed to delete user with ID {user['id']}')
                    print(f"ID: {user['id']}, Username: {user['username']}")
    else:
        print("Удаление пользователей отменено.")

def get_client_scopes(client_scopes_url=client_scopes_url):
    try:
        client_scopes_response = requests.get(client_scopes_url, headers=headers)
        client_scopes_response.raise_for_status()
        client_scopes = client_scopes_response.json()
        log.debug("Список client scopes: %s", client_scopes)
    except requests.exceptions.HTTPError as e:
        log.error("HTTP исключение: %s ", e)
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
    get_client_scopes()
  #  list_of_users = get_users(headers=headers)
  #  list_of_disabled_users = get_disabled_users()
  #  delete_users(list_of_users=list_of_users, headers=headers)
