from prometheus_client import Gauge

CERT_EXPIRY_GAUGE = Gauge(
    'keycloak_client_cert_expiry_days',
    'Seconds until certificate expiration',
    ['client_id', 'error']
)

CERT_VALID_GAUGE = Gauge(
    'keycloak_client_cert_valid',
    'Certificate validity status (1=valid, 0=invalid)',
    ['client_id', 'error']
)

LAST_UPDATE_GAUGE = Gauge(
    'keycloak_cert_check_last_update',
    'Timestamp of last successful certificate check'
)
