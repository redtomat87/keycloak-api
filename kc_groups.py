import requests
from vars.env_vars import groups_url
import json
#groups_url_query_params = {'max': max_users}


def get_groups(access_token, headers):
    try:
        groups_responce = requests.get(groups_url, headers=headers)
        groups_responce.raise_for_status() 
        list_of_groups = groups_responce.json()
        print(type(list_of_groups))
        for group in list_of_groups:
            print(group['name'])
        with open('list_of_groups.json', 'w') as json_file:
             json_file.truncate(0) 
             json.dump(list_of_groups, json_file)
    except requests.exceptions.HTTPError as e:
        print(f"HTTP исключение: {e}\n Сатус код: {list_of_groups.status_code}\n Ответ сервера {list_of_groups.text} ")
        raise 
    return list_of_groups
