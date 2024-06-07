import requests, json, common
from vars.env_vars import groups_url, page, page_size, groups_url_query_params
from access_token import KeycloakTokenValidator
from keycloak_users import set_headers
from requests import exceptions as rexcept

log = common.logging.getLogger(__name__)
common.configure_logging()

def get_groups(headers):
    while True:
        try:
            groups_responce = common.s.get(groups_url, headers=headers, params=groups_url_query_params)
            groups_responce.raise_for_status() 
            list_of_groups = groups_responce.json()
            log.debug("Type of list of groups %s", type(list_of_groups))
            for group in list_of_groups:
                log.debug("Group name: %s, Group ID: %s", group['name'], group['id'])
            with open('list_of_groups.json', 'w') as json_file:
                json_file.truncate(0) 
                json.dump(list_of_groups, json_file)
            groups_url_query_params['first'] += page_size
            log.info("Total: %s", groups_url_query_params['first'])
            log.info("Page size: %s", page_size)
            log.info("The last amount returned by the server: %s", len(list_of_groups))           
            if len(list_of_groups) < page_size:
                break  
        except rexcept.Timeout as e:
                log.error("Timeout error: ", e)
                continue
        except rexcept.JSONDecodeError as e:
            log.error("Json decoding error: %s", e)
        except rexcept.HTTPError as e:
            log.error("HTTP exception", e)
            log.error("Status code", groups_responce.status_code)
        except rexcept.ConnectionError as e:
            raise

    return list_of_groups

def get_cildren_groups(headers, groups_url_query_params, group_id):
    groups_url = f'{groups_url}/{group_id}/children'
    while True:
        try:
            groups_responce = common.s.get(groups_url, headers=headers, params=groups_url_query_params)
            groups_responce.raise_for_status() 
            list_of_groups = groups_responce.json()
            log.debug("Type of list of groups", type(list_of_groups))
            for group in list_of_groups:
                print(group['name'])
            total = sum(total, len(list_of_groups))
            with open('list_of_groups.json', 'w') as json_file:
                json_file.truncate(0) 
                json.dump(list_of_groups, json_file)
            groups_url_query_params['first'] += page_size
            log.info("Page: %s", groups_url_query_params['first'])
            log.info("Page size: %s", page_size)
            log.info("The amount returned by the server: %s", len(list_of_groups))           
            if len(list_of_groups) < page_size:
                break  
        except rexcept.Timeout as e:
                log.error("Timeout error: ", e)
                continue
        except rexcept.JSONDecodeError as e:
            log.error("Json decoding error: %s", e)
        except rexcept.HTTPError as e:
            log.error("HTTP exception %s", e)
            log.error("Status code %s", groups_responce.status_code)
        except rexcept.ConnectionError as e:
            raise
        finally:
            log.info("total gotten groups %s", total)
    return list_of_groups

if __name__ == "__main__":    
    validator = KeycloakTokenValidator()
    access_token = validator.read_token()
    headers = set_headers(access_token)
    groups = get_groups(headers)