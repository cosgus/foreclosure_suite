"""
Scraper class built for scraping data from realforeclose.miamidade.gov
"""
import math
from datetime import datetime
from typing import List

import requests

from bs4 import BeautifulSoup

import utils
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
        self.parser = ForeclosureParser()
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

    def post(self,url:str, payload:dict = None) -> requests.Response:
        """
        Uses session method to post. User can still access
        self.session but this method automates the headers argument
        """ 
        res = super().post(url, payload = payload)
        if "START HERE" in res.text:
            self.login()
            res = super().post(url, payload = payload)
        return res

    def get_days_response(self, date:datetime) -> requests.Response:
        """
        Returns response from foreclosure website containing data for a given date
        """
        self.urls.set_date_url(date)
        return self.post(self.urls.date_url, self.payloads.cookie)
    
    def get_aid_url_response(self, auction_id:str) -> requests.Response:
        self.urls.set_aid_url(auction_id)
        return self.post(self.urls.aid_url, self.payloads.cookie)
    
    def get_aid_xhr_response(self, auction_id:int) -> requests.Response:
        self.urls.set_aid_xhr_url(auction_id)
        return self.post(self.urls.aid_xhr, self.payloads.cookie)
    
    def get_bidder_response(self, auction_id:int) -> requests.Response:
        self.urls.set_bidder_url(auction_id)
        return self.post(self.urls.bidder_url, self.payloads.cookie)
    
    def get_days_aids(self, date:datetime=None) -> List:
        """
        Takes a datetime and returns a list of auction_id's on that date
        """
        html_content = self.get_days_response(date).text
        return self.parser.extract_days_aids(html_content)

    def get_auction_data(self, auction_id:int) -> requests.Response:
        html_content = self.get_aid_url_response(auction_id).text
        return self.parser.extract_auction_property_data(html_content)
    
    def get_sale_data(self, auction_id:int) -> dict:
        json_data = self.get_aid_xhr_response(auction_id).json()
        return self.parser.extract_sale_data(json_data)
    
    def get_bidder_data(self, auction_id:int) -> dict:
        html_content = self.get_bidder_response(auction_id).text
        return self.parser.extract_bidder_data(html_content)
    
    def get_all_auction_data(self, auction_id:int) -> dict:
        auction_data = self.get_auction_data(auction_id)
        sale_data = self.get_sale_data(auction_id)
        return {**auction_data, **sale_data}
    

class ForeclosureParser:

    def extract_days_aids(self, html_content:str) -> list:
        """
        Gets all the auction id's for a particular day and returns a list. 
        Accepts BeautifulSoup object or a datetime object from which it will 
        request its own soup
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        aids = soup.find(id = 'ALB').text.split(',')
        return aids

    def extract_days_page_count(self, html_content:str) -> int:
        """
        Gets the total number of pages of a days auctions. The foreclosure website limits auctions
        to 10 per page
        """
        aids = self.extract_days_aids(html_content)
        total_pages = math.ceil(len(aids)/10)
        return total_pages


    def extract_auction_property_data(self, html_content:str) -> dict:
        """
        Posts to the aid_url and extracts desired data. 
        Contains data about the property being auctioned
        """
        data = {}
        soup = BeautifulSoup(html_content, 'html.parser')
        auction_details = soup.find_all("tr", {'valign': "top"})

        for detail in auction_details:
            key = detail.find('th', class_='bLab').text.lower().replace(' ', '_').replace(':','').replace('_(count)','')
            value = detail.find('td', class_='bDat').text
            if key in ['final_judgment_amount', 'assessed_value', 'plaintiff_max_bid']:
                value = utils.convert_currency_to_float(value)
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

    def extract_sale_data(self, json_response:dict) -> dict:
        """
        Extracts desired data. Contains data about the auction sale
        """

        data = {
            'status': None,
            'time': None,
            'sale_amount': None,
            'plaintiff_max_bid': None,
        }

        auction_data = json_response['ADATA']
        auction_item = auction_data['AITEM'][0]
        sold_to = auction_item['ST']
        b_entry = auction_item['B']

        if sold_to:
            data.update({'status': sold_to})
            data.update({'time':  b_entry})
            sale_amount = utils.convert_currency_to_float(auction_item['D'])
            data.update({'sale_amount': sale_amount})
        else:
            data.update({'status': b_entry})

        try:
            plaintiff_max_bid = utils.convert_currency_to_float(auction_item['P'])
        except ValueError:
            plaintiff_max_bid = 0
            
        data.update({'plaintiff_max_bid': plaintiff_max_bid})

        return data


    def get_extract_bidder_data(self, html_content:str) -> dict:
        """
        Returns the name of the winning bidder. Only works on
        a closed auction that sold to 3rd party or to plaintiff
        """
        return BeautifulSoup(html_content)