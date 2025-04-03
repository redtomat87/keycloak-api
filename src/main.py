from keycloak_users import get_users, delete_users, get_users
from kc_groups import get_groups
from access_token import KeycloakTokenValidator
import common
    


if __name__ == "__main__":    
    validator = KeycloakTokenValidator()
    access_token = validator.read_token()
    headers = common.set_headers(access_token)
 #   list_of_users = get_users(headers=headers)
 #   delete_users(list_of_users=list_of_users, headers=headers)
    groups = get_groups(headers)
  