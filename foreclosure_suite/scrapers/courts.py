"""
Class for scraping Miami Dade court system
"""
import requests

from bs4 import BeautifulSoup

from foreclosure_suite.scrapers.base import Scraper
from foreclosure_suite.scrapers.payloads import court_payloads
from foreclosure_suite.scrapers.urls import court_urls
from foreclosure_suite.scrapers.helpers import get_view_state

class CourtScraper(Scraper):
    """
    Narrow scope scraper for pulling a few items from court records

    :param case_number: Miami-Dade court number
    :type case_number:  str
    """
    def __init__(self, case_number:str = None) -> None:
        super().__init__()
        self.session = requests.session()
        self.payloads = court_payloads.CourtPayloads()
        self.urls = court_urls.URLS()
        self.parser = CourtParser()
        self.case_number = ''
        self.login()
        if case_number:
            self.ready_search(case_number)

    def get_docket_count(self, case_number:str = None) -> int:
        """
        Takes a case number and returns the total number of entries in the court docket.
        self.session.login and self.set_court_form must have been run first
        """
        if case_number:
            self.ready_search(case_number)
        html_content = self.post(self.urls.search_url, self.payloads.court_form, timeout = 30).text
        return self.parser.extract_docket_count(html_content)

    def login(self) -> requests.Response:
        """
        Posts login credentials to login_url with session.
        1 - Sets aspx login_form
        2 - Posts credentials to login_url
        3 - Updates cookies in header to include ASPXFORMSAUTH4DADE
        """
        self.set_login_form()
        res = self.post(url = self.urls.login_url,
                        payload = self.payloads.login,
                        headers = self.payloads.headers,
                        allow_redirects=False)
        new_cookie = '; .ASPXFORMSAUTH4DADE=' + res.cookies.get(".ASPXFORMSAUTH4DADE")
        self.payloads.headers.update({'Cookie': self.payloads.headers['Cookie'] + new_cookie})
        return res

    def set_login_form(self) -> None:
        """
        Gets aspx view state and event validation and updates aspx login_form
        """
        view_state, event_validation = get_view_state(self.urls.login_url)
        self.payloads.set_login_form(view_state, event_validation)

    def set_case_number(self, case_number) -> None:
        """
        Sets case_number attribute after checking and repairing format
        """
        if case_number[0] != '2':
            case_number = '20' + case_number
        self.case_number = case_number.replace('-','')

    def set_court_form(self, case_number:str = None):
        """
        Gets aspx view state and event validation and updates aspx login_form with pre set attribute.
        Optionally, can pass a case_number to re-set attribute
        """
        if case_number:
            self.set_case_number(case_number)
        view_state, event_validation = get_view_state(self.urls.search_url)
        self.payloads.set_court_form(view_state, event_validation, case_number)

    def ready_search(self, case_number:str) -> None:
        """
        Prepares everything for a post to search url. By setting case_number
        attribute and setting aspx court_form.
        """
        self.set_case_number(case_number)
        self.set_court_form(self.case_number)


    def post_court_soup(self, case_number:str = None) -> BeautifulSoup:
        """
        Returns a BeautifulSoup object for response from search.
        By default uses pre-set case_number attribute but optionally can
        receive a new case_number which is then set to attribute and aspx form
        """
        if case_number:
            self.ready_search(case_number)
        return self.post_soup(self.urls.search_url, self.payloads.court_form)

    def post_court(self, case_number:str = None, timeout:int = 10) -> requests.Response:
        """
        Post to search_url for a specific case_number.
        By default uses pre-set case_number attribute but optionally can
        receive a new case_number which is then set to attribute and aspx form
        """
        if case_number:
            self.ready_search(case_number)
        return self.post(self.urls.search_url, self.payloads.court_form, timeout=timeout)
        

class CourtParser:

    def extract_docket_count(self, html_content:str) -> int:
        soup = BeautifulSoup(html_content, 'html.parser')
        docket_count = soup.select('#ctl00_ContentPlaceHolder1_lblDocketCount')[0].text
        return docket_count
    
    def remove_large_tags(self, html_content:str) -> str:
        soup = BeautifulSoup(html_content, 'html.parser')

        logo_anchor = soup.find('a', {'id': 'ctl00_logoAnchor'})
        logo_anchor.decompose()

        footer_logo_anchor = soup.find('a', {'id': 'FooterLogoAnchor'})
        footer_logo_anchor.decompose()

        return str(soup)