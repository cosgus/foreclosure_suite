"""
A few objects used to set up or aid the scraper classes
"""
import ssl
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager

from bs4 import BeautifulSoup

from foreclosure_suite.scrapers.payloads import court_payloads

class MyAdapter(HTTPAdapter):
    """
    Adapter for HTTP connection. SSL certificate was required for
    successful requests.
    """
    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = PoolManager(num_pools=connections,
                                       maxsize=maxsize,
                                       block=block,
                                       ssl_version=ssl.PROTOCOL_TLS)

def get_view_state(url:str) -> tuple:
    """
    Takes a url and returns viewstate and event validation
    Used in scraping asp.net sites
    """
    res = requests.post(url, cookies=court_payloads.headers, timeout=10)
    soup = BeautifulSoup(res.text, features='html.parser')

    view_state = soup.select("#__VIEWSTATE")[0]['value']
    event_validation = soup.select('#__EVENTVALIDATION')[0]['value']

    return (view_state, event_validation)
