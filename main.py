from foreclosure_suite.scrapers.foreclosure import ForeclosureScraper
from foreclosure_suite.scrapers.appraiser import AppraiserScraper
from foreclosure_suite.scrapers.courts import CourtScraper

from datetime import datetime, timedelta

def main():
    
    # scraper = ForeclosureScraper()

    # date = datetime.now() + timedelta(-5)
    # aids = scraper.get_days_aids(date=date)

    # auction_id = aids[0]

    # data = scraper.get_auction_data(auction_id)

    # print(data['case_number_(count)'])

    court_scraper = CourtScraper('2010-052742-CA-01')
    court_scraper.login()
    dc = court_scraper.post_court()
    

    # print(dc.find('span',{'class', 'ctl00_ContentPlaceHolder1_lblDocketCount'}))
    # print(dc.select('#ctl00_ContentPlaceHolder1_lblDocketCount'))
    # print(data['case_number_(count)'])
    return dc

if __name__ == '__main__':
    main()