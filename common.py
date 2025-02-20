import logging
from requests import Session
from urllib3.util import Retry
from requests.adapters import HTTPAdapter
from  vars.env_vars import BASE_DIR
# loggong config
# CRITICAL = 50
# ERROR    = 40
# WARNING  = 30
# INFO     = 20
# DEBUG    = 10


def configure_logging():
    logging.basicConfig(
        level=logging.DEBUG,
        datefmt="%Y-%m-%d %H:%M:%S",
        format="[%(asctime)s.%(msecs)03d] %(module)s:%(lineno)d %(levelname)s - %(message)s",
    )


#configuring retries

retries = Retry(
    total=10,
    backoff_factor=0.1,
    status_forcelist=[500, 501, 502, 503, 504],
    allowed_methods=frozenset({'DELETE', 'GET', 'HEAD', 'OPTIONS', 'PUT', 'TRACE'}),
    read=2,
    connect=2,
    status=2,
    other=2
)


#timeout = Timeout(connect=2.0, read=7.0)
#http = PoolManager(timeout=timeout)
# requests session
s = Session()
adapter = HTTPAdapter(max_retries=retries)
s.verify = False
# f'{BASE_DIR}\\vars\\ca.crt'
s.mount('https://',  HTTPAdapter(max_retries=retries))
s.mount('http://', adapter)
print("common!")
