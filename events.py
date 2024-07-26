
import json, os, common
from vars.env_vars import events_url_query_params, events_url, users_to_keep, client_scopes_url, page_size, events_file_path, keycloak_url, realm_name, events_url
from requests import exceptions as rexcept
from access_token import KeycloakTokenValidator
from keycloak_users import set_headers

log = common.logging.getLogger(__name__)
common.configure_logging()

def get_events(headers, events_url_query_params=events_url_query_params, **kwargs):
    log.debug("events_url_query_params: %s", events_url_query_params)
    if os.path.isfile(events_file_path):
        with open(events_file_path, 'w') as json_file:
            json_file.truncate(0) 
    while True:
        try:
            log.debug("query starts")
            events_response = common.s.get(events_url, headers=headers, params=events_url_query_params, timeout=(2, 20))
            log.debug("query responce: %s ", events_response.status_code)
            events_response.raise_for_status()
            list_of_events = events_response.json()
         #   print(f"Список пользователей: {list_of_events}")
            with open(events_file_path, 'a') as json_file:
               json.dump(list_of_events, json_file)
            log.info("Total: %s", events_url_query_params['first'])
            log.info("Page size: %s", page_size)
            log.info("The amount returned by the server: %s", len(list_of_events))
            events_url_query_params['first'] += page_size
        #    all_users = all_users.extend(list_of_events)
       #     log.info("Найдено пользователей: %" {len(all_users)})
            if len(list_of_events) < page_size:
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
    return list_of_events

if __name__ == "__main__":    
    validator = KeycloakTokenValidator()
    access_token = validator.read_token()
    headers = set_headers(access_token)
    events = get_events(headers)
    