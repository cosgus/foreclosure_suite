"""
Scraper class built scraping for Miami-Dade appraisers office
"""
import requests

from foreclosure_suite.scrapers.base import Scraper
from foreclosure_suite.scrapers.urls import appraiser_urls

class AppraiserScraper(Scraper):
    """
    Scraper for the Miami-Dade county property appraisers office. Requests
    and parses data for a particular folio (parcel_id). This class can be initalized
    with a folio but folio can be set or changed after initialization

    :param parcel_id:   The Miami-Dade folio number or parcel identification number. 
    :type parcel_id:    str or None
    """

    def __init__(self, parcel_id:str = None) -> None:
        super().__init__()
        self.urls = appraiser_urls.AppraiserUrls()
        self.json = None
        self.loaded_parcel_id = None
        if parcel_id:
            self.set_parcel_id(parcel_id)

    def get_appraisers(self) -> requests.Response:
        """
        GET request to Miami-Dade appraisers office for a folio number
        """
        return self.get(self.urls.appraiser_url)

    def get_appraisers_json(self) -> dict:
        """
        GET request for folio, but returns JSON object
        """
        if self.is_loaded():
            return self.json 
        
        self.json = self.get_appraisers().json()
        self.loaded_parcel_id = self.parcel_id
        return self.json
    
    def get_building_info(self) -> dict:
        return self.get_appraisers_json()['Building']['BuildingInfos']
    
    def get_assessment_info(self) -> dict:
        return self.get_appraisers_json()['Assessment']['AssessmentInfos']
    
    def get_property_info(self) -> dict:
        return self.get_appraisers_json()['PropertyInfo']
    
    def get_taxable_info(self) -> dict:
        return self.get_appraisers_json()['Taxable']['TaxableInfos']
    
    def get_extra_features(self) -> dict:
        return self.get_appraisers_json()['ExtraFeature']['ExtraFeatureInfos']

    def set_parcel_id(self, parcel_id:str = None) -> None:
        """
        Sets a folio number as an attribut and also updates the request url with same
        """
        self.parcel_id = parcel_id
        self.urls.set_appraiser_url(parcel_id.replace('-',''))

    def is_loaded(self) -> bool:
        if self.loaded_parcel_id == self.parcel_id:
            return True
        else:
            return False
