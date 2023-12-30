import json
from datetime import datetime, timedelta
from requests.exceptions import ConnectionError
from time import sleep

from fuzzywuzzy import fuzz
from sqlalchemy import func

from foreclosure_suite.database.models import AppraiserLake, AuctionLake, CourtLake, AuctionDateLake, Model
from foreclosure_suite.database.config import session, engine
from foreclosure_suite.scrapers import ForeclosureScraper, AppraiserScraper, CourtScraper
from foreclosure_suite.logger import get_logger
from foreclosure_suite.utils import daterange, convert_folio_to_int, load_config

BATCH_SIZE = load_config()['batch_size']
MULTIPLE_PARCEL = 'MULTIPLE PARCEL'

class DataSeed:

    def __init__(self, alchemy_session = session):

        self.session = alchemy_session
        self.start_date = self.get_start_date()

        self.foreclosure_scraper = ForeclosureScraper()
        self.appraiser_scraper = AppraiserScraper()
        self.court_scraper = CourtScraper()

        self.logger = get_logger(__name__)

    def seed_data(self):

        batched = 0
        
        for single_date in daterange(self.start_date, datetime.now()):
            aids_list = self.handle_date(single_date)
            self.logger.info(single_date)
            for aid in aids_list:

                self.logger.info(f'     {batched+1} - {aid}')
                aid_data = self.handle_auction(aid)
                auction_data = self.foreclosure_scraper.parser.extract_auction_property_data(aid_data.html)

                parcel_id = self.validate_parcel_id(auction_data['parcel_id'])
                case_number = auction_data['case_number']
                
                if parcel_id:
                    self.logger.info(f'         {parcel_id}')
                    self.handle_appraiser(parcel_id)
                   
                if case_number:
                    self.logger.info(f'         {case_number}')
                    self.handle_court(case_number)

                batched += 1
                if batched % BATCH_SIZE == 0:
                    self.session.commit()
        self.session.commit()

    def insert(self, data: Model):
        if not self.check_if_exists(data):
            self.session.add(data)

    
    def get_start_date(self) -> datetime:

        most_recent_date_scraped = self.session.query(func.max(AuctionDateLake.date)).scalar()
        if not most_recent_date_scraped: 
            start_date = datetime(2010,1,11)
        else:
            start_date = most_recent_date_scraped
        return start_date

    def validate_parcel_id(self, parcel_id):
        try:
            return convert_folio_to_int(parcel_id)
        except ValueError:
            return None
        
    def create_base_data(self, res):
        return {
            'status_code': res.status_code,
            'response_headers': json.dumps(dict(res.headers))
        }
    
    def create_aid_data(self, aid):
        res = self.foreclosure_scraper.get_aid_url_response(aid)
        aid_data = self.create_base_data(res)
        aid_data.update({
            'id': int(aid),
            'xhr': json.dumps(self.foreclosure_scraper.get_aid_xhr_response(aid).json()),
            'html': res.text
        })
        return aid_data
    
    def create_appraiser_data(self, parcel_id):
        self.appraiser_scraper.set_parcel_id(parcel_id)
        res = self.appraiser_scraper.get_appraisers()
        appraiser_data = self.create_base_data(res)
        appraiser_data.update({
            'id': convert_folio_to_int(parcel_id),
            'json': json.dumps(res.json())
        })
        return appraiser_data
    
    
    def create_court_data(self, case_number):
        res = self.court_scraper.post_court(case_number=case_number, timeout = 30)
        court_data = self.create_base_data(res)
        court_data.update(
            {
            'case_number': case_number,
            'html': res.text,
            }
        )
        return court_data
    
    def create_date_data(self, single_date):
        res = self.foreclosure_scraper.get_days_response(single_date)
        date_data = self.create_base_data(res)
        date_data.update(
            {
                'date': single_date,
                'html': res.text
            }
        )
        return date_data
    
    def handle_date(self, single_date):
        date_data = self.create_date_data(single_date)
        entry = AuctionDateLake(**date_data)
        if not AuctionDateLake.exists_in_table(self.session, ident = single_date):
            self.session.add(entry)
        return self.foreclosure_scraper.parser.extract_days_aids(entry.html)
    
    def handle_auction(self, aid):
        aid_data = self.create_aid_data(aid)
        entry = AuctionLake(**aid_data)
        if not AuctionLake.exists_in_table(self.session, ident = aid):
            self.session.add(entry)
        return entry
        

    def handle_appraiser(self, parcel_id):
        context_id = convert_folio_to_int(parcel_id)
        if not AppraiserLake.exists_in_table(self.session, ident = context_id):
            appraiser_data = self.create_appraiser_data(parcel_id)
            entry = AppraiserLake(**appraiser_data)
            self.session.add(entry)

    def handle_court(self, case_number):
        if not CourtLake.exists_in_table(self.session, ident = case_number):
            court_data = self.create_court_data(case_number)
            entry = CourtLake(**court_data)
            self.session.add(entry)
    
    def handle_multiple_parcel(self):
        pass

    def handle_no_parcel_id(self):
        pass


def drop_all_tables():
    # AppraiserLake.__table__.drop(bind = engine)
    CourtLake.__table__.drop(bind = engine)
    AuctionLake.__table__.drop(bind = engine)
    AuctionDateLake.__table__.drop(bind = engine)

if __name__ == '__main__':
    drop_all_tables()
    Model.metadata.create_all(bind=engine)
    seeder = DataSeed(session)
    while True:
        try:
            seeder.seed_data()
        except ConnectionError as e:
            seeder.logger.warning(f'CONNECTION ERROR - RESTARTING SEEDER\n{e}')
            sleep(30)
            seeder.seed_data()