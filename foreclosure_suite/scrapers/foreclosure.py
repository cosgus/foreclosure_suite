"""
Scraper class built for scraping data from realforeclose.miamidade.gov
"""
import math
from datetime import datetime

import requests

from bs4 import BeautifulSoup

from foreclosure_suite.scrapers.payloads import foreclosure_payloads
from foreclosure_suite.scrapers.base import Scraper
from foreclosure_suite.scrapers.urls import foreclosure_urls
from foreclosure_suite.scrapers.helpers import MyAdapter

class ForeclosureScraper(Scraper):
    """
    Scraper built for scraping from realforeclose.miamidade.gov. Pulls data
    from a few different urls to collect property data, auction results, and bidder_data. Uses
    a requests session to track login credentials and movement throughout site.
    """

    def __init__(self):
        super().__init__()
        self.urls = foreclosure_urls.URLS()
        self.payloads = foreclosure_payloads
        self.session = requests.Session()
        self.session.mount(self.urls.main_url, MyAdapter())
        self.days_aid_list = None
        self.days_page_count = None
        self.login()

    def post_login(self) -> requests.Response:
        """
        Method for posting login credentials
        """
        return self.post(self.urls.main_url, self.payloads.login)

    def clear_notice(self, nid:int = 8045) -> requests.Response:
        """
        There are a few notices that must be accepted once a user logs in to the foreclosure site.
        This method posts a payload to the url of the OK button on these notices. If these notices
        are not cleared, all requests to the site result in the notice page.

        :param nid: A notice id associated with each notice OK button. Required in the payload
                    to succesfully clear the notice.
        :type nid:  int or str
        """
        self.payloads.splash_notice['NID'] = nid
        return self.post(self.urls.main_url, self.payloads.splash_notice)

    def login(self) -> None:
        """
        Complete login protocol
        1 - post login credentials
        2 - clear notice 1
        3 - clear notice 2
        """
        self.post_login()
        self.clear_notice()
        self.clear_notice(nid = 9208)

    def get_days_soup(self, date:datetime) -> BeautifulSoup:
        """
        Returns a BeautifulSoup object containing the hypertext for a given auction calendar day
        """
        self.urls.set_date_url(date)
        return self.post_soup(self.urls.date_url, self.payloads.cookie)

    def get_days_aids(self, date:datetime = None, soup:BeautifulSoup = None, ) -> list:
        """
        Gets all the auction id's for a particular day and returns a list. 
        Accepts BeautifulSoup object or a datetime object from which it will 
        request its own soup
        """
        if not soup:
            soup = self.get_days_soup(date)
        aids = soup.find(id = 'ALB').text.split(',')
        return aids

    def get_days_page_count(self, soup:BeautifulSoup=None, date:datetime = None) -> int:
        """
        Gets the total number of pages of a days auctions. The foreclosure website limits auctions
        to 10 per page
        """
        aids = self.get_days_aids(soup, date)
        total_pages = math.ceil(len(aids)/10)
        return total_pages

    def parse_days_page(self, date:datetime) -> None:
        """
        Parses desired information from a given days auction page. Gets both the auction id
        list as well as the total page count and stores them in class attributes.
        """
        self.urls.set_date_url(date)
        soup = self.post_soup(self.urls.date_url)
        self.days_page_count = self.get_days_page_count(soup = soup)
        self.days_aid_list = self.get_days_aids(soup = soup)

    def get_auction_property_data(self, auction_id:str) -> dict:
        """
        Posts to the aid_url and extracts desired data. 
        Contains data about the property being auctioned
        """
        data = {}
        self.urls.set_aid_url(auction_id)
        soup = self.post_soup(self.urls.aid_url)
        auction_details = soup.find_all("tr", {'valign': "top"})

        for detail in auction_details:
            key = detail.find('th', class_='bLab').text.lower().replace(' ', '_').replace(':','')
            value = detail.find('td', class_='bDat').text
            data.update({key: value})

        legal_soup = soup.find(id = "mgTab1")

        parties_soup = legal_soup.find_all('tr')

        data['defendant'] = []
        data['plaintiff'] = []

        for party in parties_soup:
            details = party.find_all('td')
            if len(details) == 2:
                if 'DEFENDANT' in details[0].text:
                    data['defendant'].append(details[1].text)
                if 'PLAINTIFF' in details[0].text:
                    data['plaintiff'].append(details[1].text)
        return data

    def get_auction_sale_data(self, auction_id:str) -> dict:
        """
        Posts to aid_xhr_url and extracts desired data. Contains data about the auction sale
        """

        data = {
            'status': '',
            'time': '',
            'sale': '',
            'plaintiff_max_bid': ''
        }

        self.urls.set_aid_xhr_url(auction_id)
        sale_data = self.post(self.urls.aid_xhr, self.payloads.cookie).json()

        auction_data = sale_data['ADATA']
        auction_item = auction_data['AITEM'][0]
        sold_to = auction_item['ST']
        b_entry = auction_item['B']

        # print(auction_item)

        if sold_to:
            data.update({'status': sold_to})
            data.update({'time':  b_entry})
            data.update({'sale': auction_item['D']})
        else:
            data.update({'status': b_entry})

        data.update({'plaintiff_max_bid': auction_item['P']})

        return data

    def get_auction_data(self, auction_id:str) -> dict:
        """
        Performs both get_property_data and get_auction_data
        """

        data = {}

        property_data = self.get_auction_property_data(auction_id)
        sale_data = self.get_auction_sale_data(auction_id)

        data.update(property_data)
        data.update(sale_data)

        return data

    def get_bidder_data(self, auction_id:str) -> dict:
        """
        Returns the name of the winning bidder. Only works on
        a closed auction that sold to 3rd party or to plaintiff
        """
        self.urls.set_bidder_url(auction_id)
        data = self.post_soup(self.urls.bidder_url)
        return data
