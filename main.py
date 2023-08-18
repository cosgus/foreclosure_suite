from foreclosure_suite.scrapers.foreclosure import ForeclosureScraper
from foreclosure_suite.scrapers.appraiser import AppraiserScraper
from foreclosure_suite.scrapers.courts import CourtScraper

from datetime import datetime, timedelta

def main():
    
    foreclosure_scraper = ForeclosureScraper()

    date = datetime(2023,8,9)
    aids_list = foreclosure_scraper.get_days_aids(date=date)

    auction_id = aids_list[0]

    auction_data = foreclosure_scraper.get_all_auction_data(auction_id)

    case_number = auction_data["case_number"]
    print(f'Case Number: {case_number}')

    parcel_id = auction_data["parcel_id"]
    print(f'Parcel ID (folio): {parcel_id}')

    court_scraper = CourtScraper(case_number)
    # court_scraper.login()
    dc = court_scraper.get_docket_count()
    print(f'Docket Count: {dc}')

    appraiser_scraper = AppraiserScraper(parcel_id)
    property_data = appraiser_scraper.get_appraisers_json()
    
    for key, value in property_data['PropertyInfo'].items():
        print(f'{key}: {value}')

if __name__ == '__main__':
    main()