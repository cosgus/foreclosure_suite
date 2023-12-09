from datetime import datetime

from sqlalchemy import func

from foreclosure_suite.database import models
from foreclosure_suite.database.my_alchemy import session
from foreclosure_suite import scrapers
from utils import daterange

class DataSeed:

    def __init__(self, alchemy_session):

        self.session = alchemy_session
        self.tables = models.Table
        self.start_date = self.get_start_date()

        self.foreclosure_scraper = scrapers.foreclosure.ForeclosureScraper()
        self.appraiser_scraper = scrapers.appraiser.AppraiserScraper()
        self.court_scraper = scrapers.courts.CourtScraper()

    def seed_data(self):
        
        for single_date in daterange(self.start_date, datetime.now()):
            aids_list = self.foreclosure_scraper.get_days_aids(single_date)
            print(single_date)
            for aid in aids_list:

                print(f'     {aid}')
                aid_data = {
                    'id': aid,
                    'xhr': self.foreclosure_scraper.get_aid_xhr_response(aid).json(),
                    'html': self.foreclosure_scraper.get_aid_url_response(aid).text
                }
                self.insert(models.AuctionLake(**aid_data))
                session.add(models.AuctionLake(**aid_data))

            session.add(models.Scraped(date = single_date))
            print(single_date)
        session.commit()

    def insert(table: models.Model, data:dict):
        pass        

    
    def get_start_date(self) -> datetime:

        start_date = self.session.query(func.max(models.Scraped.date)).scalar()
        if not start_date: 
            start_date = datetime(2010,1,11)
        return start_date


if __name__ == '__main__':
    session.commit()
    exit()
    seeder = DataSeed(session)
    seeder.seed_data()
    