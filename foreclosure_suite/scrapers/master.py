from datetime import datetime, timedelta
from typing import List

import foreclosure_suite.database.handler as db_handler
from foreclosure_suite.scrapers.foreclosure import ForeclosureScraper
from foreclosure_suite.scrapers.appraiser import AppraiserScraper
from foreclosure_suite.scrapers.courts import CourtScraper

class Master:

    def __init__(self):

        self.foreclosure_scraper = ForeclosureScraper()
        self.appraiser_scraper = AppraiserScraper()
        self.court_scraper = CourtScraper()
        self.db_handler = db_handler.PostgresHandler()
        self.auction_data = None
        self.appraiser_data = None
        self.court_data = None

    def scrape_all(self, dates:List[datetime] = None):
        
        for date in dates:
            
            print(date.strftime('%Y-%m-%d'))
            auction_id_list = list(filter(None,(self.foreclosure_scraper.get_days_aids(date))))
            
            for idx, auction_id in enumerate(auction_id_list):

                auction_primary_key = self.handle_auction_data(auction_id)
                property_primary_key = self.handle_property_data()
                case_primary_key = self.handle_case_data()
        

                if idx%10 == 0:
                    self.db_handler.conn.commit()
                # case_number = auction_data['case_number_(count)']
                # docket_count = self.court_scraper.get_docket_count(case_number)

    def handle_property_data(self) -> int:

        parcel_id = self.auction_data['parcel_id']
        if parcel_id:
            if parcel_id == 'MULTIPLE PARCEL':
                self.db_handler.insert('multiple_parcel',{'auction_id':self.auction_id})
            else:
                self.appraiser_scraper.set_parcel_id(parcel_id)
                property_data = self.appraiser_scraper.get_property_info()
                if self.db_handler.insert('property', property_data, returning='id'):
                    primary_key = self.db_handler.cursor.fetchone()[0]
                    return primary_key
        else:
            self.db_handler.insert('no_folio', {'auction_id':self.auction_id})

    def handle_auction_data(self):
        
        

                
def main():

    master = Master()
    dates = [datetime.now() - timedelta(n) for n in range(10)]
    master.scrape_all(dates)


if __name__ == '__main__':
    main()