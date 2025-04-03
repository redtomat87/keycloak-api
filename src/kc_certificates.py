import common, base64
from metrics.metrics_model import CERT_EXPIRY_GAUGE, CERT_VALID_GAUGE, LAST_UPDATE_GAUGE
from vars.env_vars import (
    keycloak_url, realm_name, saml_assertion_cert_file, 
    certs_validation_file_path, client_uuid, cert_type
)
from cryptography.x509 import load_der_x509_certificate, load_pem_x509_certificate
from prometheus_client import Gauge, generate_latest, REGISTRY
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from requests import exceptions as rexcept
from access_token import validator
from datetime import datetime, timezone, timedelta
from fastapi import FastAPI,  Response
from typing import Dict, Any
from threading import RLock
from models.settings_model import config

cert_cache: Dict[str, Dict[str, Any]] = {}
cache_lock = RLock()

app = FastAPI()

log = common.logging.getLogger(__name__)
common.configure_logging()

def read_pem_certificate() -> str:
    try:
        with open(saml_assertion_cert_file, "r", encoding="utf-8") as cert_file:
            return cert_file.read().strip()
    except FileNotFoundError as e:
        log.error(f"Certificate file not found: {saml_assertion_cert_file}")
        raise

def post_certificate(client_uuid: str, attr: str, headers: dict) -> None:
    with open(saml_assertion_cert_file, 'rb') as cert_file:
        files = {
            'keystoreFormat': (None, 'Certificate PEM'),
            'file': ('cert.pem', cert_file, 'application/x-pem-file')
        }
        upload_headers = {'Authorization': headers['Authorization']}
        client_cert_update_url = f'{keycloak_url}/admin/realms/{realm_name}/clients/{client_uuid}/certificates/{attr}/upload-certificate'
        
        try:
            response = common.s.post(
                client_cert_update_url,
                headers=upload_headers,
                files=files,
                timeout=(2, 20)
            )
            log.debug("query responce: %s ", response.status_code)
            response.raise_for_status()
        except rexcept.HTTPError as e:
            log.error("Response content: %s", e.response.text)
            log.error("HTTP exception: %s", e)
        except rexcept.ConnectionError as e:
            log.error("HTTP exception connection error: %s", e)
        except rexcept.RequestException as e:
            log.error("Request failed: %s", str(e))
            raise
        except KeyboardInterrupt as e:
            log.error("Iterrupted by user: %s", e)
            raise

def get_list_of_clients(headers: dict) -> list:
    all_clients = []
    page = 0
    page_size = 100
    get_clients_url = f'{config.keycloak_url}/admin/realms/{config.realm_name}/clients'
    query_parameters =  {
                          'max': page_size,
                          'first': page,
                          'briefRepresentation': 'true',
                          'search': 'true'
                          }

    while True:
        try:
            log.debug("query starts %d", query_parameters['first'])
            response = common.s.get(
                get_clients_url,
                headers=headers,
                params=query_parameters,
                timeout=(2, 60)
            )
            response.raise_for_status()
            if response.status_code == 401:
                access_token = validator.read_token()
                validator.validate_token(access_token)
              
            clients_chunk = response.json()

            if not isinstance(clients_chunk, list):
                log.error("Invalid response format: %s", type(clients_chunk))
                break
            if not clients_chunk:
                log.debug("Received empty chunk, ending pagination")
                break
            all_clients.extend(clients_chunk)
            log.info(
                "Fetched chunk: %d clients | Total collected: %d", 
                len(clients_chunk),
                len(all_clients)
            )
            if len(clients_chunk) < query_parameters['max']:
                log.debug("Last chunk received, ending pagination")
                break
            query_parameters['first'] += len(clients_chunk)
        except rexcept.HTTPError as e:
            log.error("Response content: %s", e.response.text)
            log.error("HTTP exception: %s", e)
        except rexcept.ConnectionError as e:
            log.error("HTTP exception connection error: %s", e)
        except rexcept.RequestException as e:
            log.error("Request failed: %s", str(e))
            raise
        except KeyboardInterrupt as e:
            log.error("Iterrupted by user: %s", e)
            raise
        if not isinstance(all_clients, list):
            log.error("Invalid response format: %s", type(all_clients))
            break
        #log.info("clients returned: %s", all_clients)
        log.info(
        "Total clients fetched: %d", 
        len(all_clients)
        )
    return all_clients

def get_clients_certificates_info(headers: dict) -> dict:
    """Retrieves client certificates information at format:
    {
        "client_id": {
            "valid": bool,
            "expiry_date": datetime | None,
            "error": str | None
        }
    }
    """
    clients = get_list_of_clients(headers)
    results = {}

    for client in clients:
        client_id = client['id']
        client_name = client['clientId']
        results[client_name] = {"valid": False, "expiry_date": None, "error": None}

        cert_url = (
            f"{config.keycloak_url}/admin/realms/{config.realm_name}/clients/"
            f"{client_id}/certificates/saml.encryption"
        )

        try:
            response = common.s.get(cert_url, headers=headers, timeout=10)
            response.raise_for_status()
            cert_info = response.json()
            log.debug("Raw cert info: %s", cert_info)

            cert_data = cert_info.get('certificate')
            log.debug("Raw cert_data: %s", cert_data)
            if not cert_data:
                results[client_name]['error'] = "No certificate found"
                continue

            try:
                if '-----BEGIN CERTIFICATE-----' in cert_data:
                    cert = load_pem_x509_certificate(cert_data)
                else:
                    der_data = base64.b64decode(cert_data)
                    cert = load_der_x509_certificate(der_data)
            except Exception as e:
                results[client_name]['error'] = f"Certificate decode error: {str(e)}"
                continue

            expiry_date_aware = cert.not_valid_after_utc
            now = datetime.now(timezone.utc)
            
            results[client_name]['expiry_date'] = expiry_date_aware
            results[client_name]['valid'] = expiry_date_aware > now

        except rexcept.HTTPError as e:
            if e.response.status_code == 404:
                results[client_name]['error'] = "No certificates found"
            else:
                results[client_name]['error'] = f"HTTP Error: {e.response.status_code}"
        except Exception as e:
            results[client_name]['error'] = f"Unexpected error: {str(e)}"
    log.debug("Results: %s", results)

    # with open(certs_validation_file_path, 'a') as f:
    #     json.dump(results, f, default=str, indent=2)
    return results

def update_cert_cache():
    global cert_cache
    try:
        access_token = validator.read_token()
        validator.validate_token(access_token)
        headers = common.set_headers(access_token)
        new_data = get_clients_certificates_info(headers)
        
        with cache_lock:
            cert_cache.clear()
            cert_cache = new_data
            LAST_UPDATE_GAUGE.set(int(datetime.now(timezone.utc).timestamp()))
            log.info("Certificate cache updated successfully")
        
        update_prometheus_metrics(new_data)
        
    except Exception as e:
        log.error(f"Failed to update certificate cache: {str(e)}")

def update_prometheus_metrics(data):
    CERT_EXPIRY_GAUGE.clear()
    CERT_VALID_GAUGE.clear()
    now = datetime.now(timezone.utc)
    
    for client_id, info in data.items():
        error_label = info['error'] or 'none'
        
        if info['expiry_date']:
            delta = info['expiry_date'] - now
            expiry_days = delta.days
            CERT_EXPIRY_GAUGE.labels(client_id=client_id, error=error_label).set(expiry_days)
            CERT_VALID_GAUGE.labels(client_id=client_id, error=error_label).set(1 if info['valid'] else 0)


scheduler = BackgroundScheduler()
scheduler.add_job(
    update_cert_cache,
    trigger=IntervalTrigger(hours=24),
    next_run_time=datetime.now(timezone.utc) + timedelta(seconds=10),
    id='certificate_validation_job',
    replace_existing=True
)
scheduler.start()


@app.get("/metrics", description="Return certificate expiration metrics from Keycloak")
def metrics():
    return Response(
        content=generate_latest(REGISTRY),
        media_type="text/plain; version=0.0.4; charset=utf-8"
    )


if __name__ == "__main__":    
    
    import uvicorn
    import os
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level=os.getenv("UVICORN_LOG_LEVEL", "info").lower(),
        access_log=os.getenv("UVICORN_ACCESS_LOG", "false").lower() == "true"
    )
    # log.debug(f"datetime.now(timezone.utc): {datetime.now(timezone.utc)}")
    # log.debug(f"timedelta 10: {timedelta(seconds=10)}")
