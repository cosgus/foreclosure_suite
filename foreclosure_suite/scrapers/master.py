from datetime import datetime, timedelta
from typing import List

import foreclosure_suite.database.handler as db_handler
from foreclosure_suite import scrapers

class Master:

    def __init__(self):

        self.foreclosure_scraper = scrapers.ForeclosureScraper()
        self.appraiser_scraper = scrapers.AppraiserScraper()
        self.court_scraper = scrapers.CourtScraper()
        self.db_handler = db_handler.PostgresHandler()

    def scrape_all(self, dates:List[datetime] = None):
        
        for date in dates:
            
            auction_id_list = self.foreclosure_scraper.get_days_aids(date)
            
            for idx, auction_id in enumerate(auction_id_list):

                auction_data = self.foreclosure_scraper.get_auction_data(auction_id)
            
                parcel_id = auction_data['parcel_id']
                self.appraiser_scraper.set_parcel_id(parcel_id)
                property_data = self.appraiser_scraper.get_property_info()

                case_number = auction_data['case_number_(count)']
                docket_count = self.court_scraper.get_docket_count(case_number)

                data = {
                    'auction_data': auction_data,
                    'property_data': property_data,
                    'docket_count': docket_count
                }

                db_handler.insert_data(data)