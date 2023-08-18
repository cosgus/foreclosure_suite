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
        self.db_handler = db_handler.ForeclosureHandler()


    def scrape_all(self, dates:List[datetime] = None):
        
        for date in dates:
            
            print(date.strftime('%Y-%m-%d'))
            auction_id_list = list(filter(None,(self.foreclosure_scraper.get_days_aids(date))))
            
            for idx, auction_id in enumerate(auction_id_list):
                print('    ' + auction_id)
                auction_data = self.foreclosure_scraper.get_all_auction_data(auction_id)

                parcel_id = auction_data['parcel_id']
                self.appraiser_scraper.set_parcel_id(parcel_id)
                property_info = self.appraiser_scraper.get_property_info()

                case_number = auction_data['case_number']
                docket_count = self.court_scraper.get_docket_count(case_number)

                data = {
                    'aid': auction_id,
                    'aid_list': auction_id_list,
                    'idx': idx,
                    'auction_data': auction_data,
                    'property_info': property_info,
                    'docket_count': docket_count
                }
                self.db_handler.handle_data(data)
                
                if idx % 10 == 0:
                    self.db_handler.conn.commit()
def main():

    master = Master()
    dates = [datetime.now() - timedelta(n) for n in range(10)]
    master.scrape_all(dates)


if __name__ == '__main__':
    main()