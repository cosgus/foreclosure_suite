from datetime import datetime

from sqlalchemy import func

from foreclosure_suite.database import models
from foreclosure_suite.database.config import session, engine
from foreclosure_suite import scrapers
from foreclosure_suite.logger import get_logger
from utils import daterange

BATCH_SIZE = 100

class DataSeed:

    def __init__(self, alchemy_session = session):

        self.session = alchemy_session
        self.tables = models.Table
        self.start_date = self.get_start_date()

        self.foreclosure_scraper = scrapers.foreclosure.ForeclosureScraper()
        self.appraiser_scraper = scrapers.appraiser.AppraiserScraper()
        self.court_scraper = scrapers.courts.CourtScraper()

        self.logger = get_logger(__name__)

    def seed_data(self):

        batched = 0
        
        for single_date in daterange(self.start_date, datetime.now()):
            aids_list = self.foreclosure_scraper.get_days_aids(single_date)
            self.logger.info(single_date)
            for aid in aids_list:

                self.logger.info(f'     {batched+1} - {aid}')
                aid_data = self.handle_auction(aid)
                auction_data = self.foreclosure_scraper.parser.extract_auction_property_data(aid_data['html'])

                parcel_id = auction_data['parcel_id']
                case_number = auction_data['case_number']
                
                if parcel_id:
                    self.logger.info('         ' + parcel_id)
                    self.handle_appraiser(parcel_id)

                if case_number:
                    self.logger.info('         ' + case_number)
                    self.handle_court(case_number)

                batched += 1
                if batched % BATCH_SIZE == 0:
                    self.session.commit()
            self.session.add(models.Scraped(date = single_date))
        self.session.commit()

    def insert(self, data: models.Model):
        if not self.check_if_exists(data):
            self.session.add(data)

    
    def get_start_date(self) -> datetime:

        start_date = self.session.query(func.max(models.Scraped.date)).scalar()
        if not start_date: 
            start_date = datetime(2010,1,1)
        return start_date

    def create_aid_data(self, aid):
        aid_data = {
            'id': aid,
            'xhr': self.foreclosure_scraper.get_aid_xhr_response(aid).json(),
            'html': self.foreclosure_scraper.get_aid_url_response(aid).text
        }
        return aid_data
    
    def create_appraiser_data(self, parcel_id):
        id = int(parcel_id.replace('-',''))
        self.appraiser_scraper.set_parcel_id(parcel_id)
        appraiser_data = {
            'id': id,
            'json': self.appraiser_scraper.get_appraisers_json()
        }
        return appraiser_data
    
    def create_court_data(self, case_number):
        return {
            'case_number': case_number,
            'html': self.court_scraper.post_court(case_number=case_number, timeout = 30)
        }
    
    def handle_auction(self, aid):
        if not self.exists_in_table(aid, models.AuctionLake):
            aid_data = self.create_aid_data(aid)
            self.session.add(models.AuctionLake(**aid_data))
        return aid_data
    
    def handle_appraiser(self, parcel_id):
        if not self.exists_in_table(parcel_id, models.AppraiserLake):
            appraiser_data = self.create_appraiser_data(parcel_id)
            self.session.add(models.AppraiserLake(**appraiser_data))
            
    def handle_court(self, case_number):
        if not self.exists_in_table(case_number, models.CourtLake):
            court_data = self.create_court_data(case_number)
            self.session.add(models.CourtLake(**court_data))

    def exists_in_table(self, id: int, table: models.Model):
        return False
    
if __name__ == '__main__':

    models.Model.metadata.create_all(bind=engine)
    seeder = DataSeed(session)
    seeder.seed_data()
    