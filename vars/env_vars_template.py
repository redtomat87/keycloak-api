keycloak_url = '**keycloak url**'

realm_name = '**keycloak realm name**'
client_scopes_url = f'{keycloak_url}/admin/realms/{realm_name}/client-scopes'
max_users = '**users batch**'
users_url_query_params = {'max': max_users}
users_url = f'{keycloak_url}/admin/realms/{realm_name}/users'
token_url = f'{keycloak_url}/realms/{realm_name}/protocol/openid-connect/token'
groups_url = f'{keycloak_url}/admin/realms/{realm_name}/groups'

username = '**keycloak service account name**'
users_to_keep = ['list', 'of', 'useres to keep when you delete users']


