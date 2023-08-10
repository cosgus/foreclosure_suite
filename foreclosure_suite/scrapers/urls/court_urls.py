"""
Class for conformity with other scrapers that have dynamic url requirements
"""
class URLS:
    """
    Class for storing urls used in scraping miami dade courts
    """
    def __init__(self):
        self.base_url = 'https://www2.miamidadeclerk.gov'
        self.login_url = self.base_url + '/PremierServices/login.aspx'
        self.search_url = self.base_url + '/ocs/Search.aspx'
