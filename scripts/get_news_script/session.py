import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def make_session() -> requests.Session:
    s = requests.Session()
    retry = Retry(
        total=6, connect=6, read=6, # total retries
        backoff_factor=1.5,                         
        status_forcelist=(403,429, 500, 502, 503, 504), #retry error codes
        respect_retry_after_header=True,
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    s.mount("https://", adapter)
    s.mount("http://", adapter)
    return s

SESSION = make_session()
