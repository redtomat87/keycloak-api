from keycloak_users import get_access_token, set_headers, get_users, delete_users, get_access_token, set_headers, get_users
from kc_groups import get_groups


access_token = get_access_token()
    

if __name__ == "__main__":    
#    access_token = get_access_token()
    headers = set_headers(access_token)
 #   list_of_users = get_users(headers=headers)
 #   delete_users(list_of_users=list_of_users, headers=headers)
    groups = get_groups(access_token, headers)
  