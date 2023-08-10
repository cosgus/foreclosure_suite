"""
Class for managing urls used in scraping foreclosure site
"""
from datetime import datetime

class URLS:
    """
    Class to manage urls used in scraping foreclosure site.
    Has a few methods for setting dynamic urls
    """

    def __init__(self):
        self.base_url = "https://www.miamidade.realforeclose.com/"
        self.main_url = self.base_url + "index.cfm"
        self.first_request = self.main_url + "?zaction=AUCTION&Zmethod=UPDATE&FNC=LOAD&AREA=C&PageDir=0&doR=1&tx=1581711468971&bypassPage=0&test=1&_=1581711468726"
        self.aid_url = None
        self.aid_xhr = None
        self.date_url = None
        self.bidder_url = None

    def set_date_url(self, date:datetime) -> None:
        """
        Takes a datetime object and sets the calendar url for a specific date.
        This url will contain information about all the auctions on a given date.
        """

        year=date.strftime("%Y")
        month=date.strftime("%m")
        day=date.strftime("%d")

        self.date_url = self.main_url + f'?zaction=AUCTION&Zmethod=DAYLIST&AUCTIONDATE={month}/{day}/{year}'

    def set_aid_url(self, auction_id:str) -> None:
        """
        Accepts an 8 digit id number (str) and sets the aid_url
        """
        self.aid_url = self.main_url + f'?zaction=auction&zmethod=details&AID={auction_id}&bypassPage=1'

    def set_aid_xhr_url(self, auction_id:str) -> None:
        """
        Accepts an 8 digit id number (str) and sets the aid_xhr_url
        """
        self.aid_xhr = self.main_url + f'?zaction=AUCTION&ZMETHOD=UPDATE&FNC=UPDATESINGLE&AID={auction_id}&tx=1582314005699&_=1582314005569'

    def set_bidder_url(self, auction_id:str) -> None:
        """
        Accepts a bidder id number (str) and sets the bidder_url
        """
        self.bidder_url = self.main_url + f'?zaction=AJAX&zmethod=POPUP&p_Name=BID&p_id=pWin4&p_List={auction_id}&t=1582414530976'
