"""
Base class for other scrapers
"""
import requests

from foreclosure_suite.scrapers.payloads import base_payloads

class Scraper:
    """
    Super class used by other scrapers
    """

    def __init__(self):
        self.session = requests
        self.payloads = base_payloads

    def post(self,url:str, payload:dict = None, **args) -> requests.Response:
        """
        Uses session method to post. User can still access
        self.session but this method automates the headers argument
        """
        if 'headers' in args.keys():
            self.set_request_headers(args['headers'])
            args.pop('headers')
        res = self.session.post(url, data = payload, headers = self.payloads.headers, **args)
        return res

    def get(self, url:str, headers:dict = None) -> requests.Response:
        """
        Performs a GET request with pre set headers but optionally
        accepts header
        """
        if not headers:
            headers = self.payloads.headers
        return self.session.get(url, headers = headers, timeout=10)

    def set_request_headers(self, headers:dict) -> None:
        """
        Sets headers to attribute
        """
        self.payloads.headers = headers

    def update_headers(self, update:dict = None) -> dict:
        """
        Takes a dictionary and updates header
        """
        self.payloads.headers.update(update)
