from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

#keycloak urls
keycloak_url = '**keycloak url**'
realm_name = '***keycloak user name***'
users_url = f'{keycloak_url}/admin/realms/{realm_name}/users'
token_url = f'{keycloak_url}/realms/{realm_name}/protocol/openid-connect/token'
groups_url = f'{keycloak_url}/admin/realms/{realm_name}/groups'
client_scopes_url = f'{keycloak_url}/admin/realms/{realm_name}/client-scopes'

#pagination config
page_size = 200 #user per pagination page
page = 0 # first page to start

#get users params
users_url_query_params = {
                          'max': page_size,
                          'first': page,
                          'briefRepresentation': 'True'
                          }

#files 
users_file_path = (BASE_DIR / 'list_of_users.json') 
token_file_path = (BASE_DIR / 'token_file')

# Your username
username = '**keycloak service account name**'

# the list of users that should be keep during the user deletion function
users_to_keep = ['list', 'of', 'useres to keep when you delete users']


