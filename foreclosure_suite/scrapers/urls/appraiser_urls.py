"""
Class for storing and editing urls used in scraping county appraisers office
"""
class AppraiserUrls:
    """
    Class for storing and editing urls used in scraping county appraisers office
    """
    def __init__(self, parcel_id:str = None) -> None:
        if parcel_id:
            self.set_appraiser_url(parcel_id)

    def set_appraiser_url(self, parcel_id:str = None) -> None:
        """
        Takes a property parcel id, or folio, (str)
        and sets appraiser_url attribute
        """
        self.appraiser_url = 'https://www.miamidade.gov/Apps/PA/PApublicServiceProxy/PaServicesProxy.ashx?Operation=GetPropertySearchByFolio&clientAppName=PropertySearch&folioNumber=' + parcel_id
