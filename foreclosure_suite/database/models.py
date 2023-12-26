from datetime import datetime
import enum

from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, DateTime, Integer, JSON, String, Boolean, BigInteger

from foreclosure_suite.database.config import session, engine
from foreclosure_suite.logger import get_logger

Model = declarative_base()
Model.query = session.query_property()

logger = get_logger(__name__)

class Table(enum.Enum):

    SCRAPED                 = 'dates_scraped'
    AUCTION_RAW_DATA        = 'auction_raw_data'
    COURT_RAW_DATA          = 'court_raw_data'
    APPRAISER_RAW_DATA      = 'appraiser_raw_data'
    AUCTION_DATE_RAW_DATA   = 'auction_date_raw_data'
    
class ModelMixin(Model):
    __abstract__ = True

    created_at = Column(DateTime, default=datetime.utcnow())
    updated_at = Column(DateTime, onupdate=datetime.utcnow())

    @classmethod
    def get_or_create(cls, session, **kwargs):
        entry = session.query(cls).filter_by(**kwargs).first()
        if not entry:
            logger.info('Inserting')
            entry = cls(**kwargs)
            session.add(entry)
        return entry

    @classmethod
    def exists_in_table(cls, session, ident):
        if session.get(cls, ident):
            logger.debug(f'{cls} - Already Inserted')
            return True

class RequestsDataLake(ModelMixin):
    __abstract__ = True

    status_code = Column(Integer)
    response_headers = Column(JSON)
    parsed = Column(Boolean, default=False)

class AuctionDateLake(RequestsDataLake):
    __tablename__ = 'auction_date_raw_data'

    id = Column(Integer, primary_key = True)
    date = Column(DateTime)
    html = Column(String)

    def __repr__(self):
        return f'{self.__class__.name}:, Date: {self.date}'

class AuctionLake(RequestsDataLake):
    __tablename__ ='auction_raw_data'

    id = Column(Integer, primary_key = True)
    xhr = Column(JSON)
    html = Column(String)

    def __repr__(self):
        return f'{self.__class__.__name__}, AID: {self.id}'

class AppraiserLake(RequestsDataLake):
    __tablename__ = 'appraiser_raw_data'

    id = Column(BigInteger, primary_key = True)
    json = Column(JSON)

    def __repr__(self):
        return f'{self.__class__.__name__}, Folio: {self.id}'


class CourtLake(RequestsDataLake):
    __tablename__ = "court_raw_data"

    case_number = Column(String, primary_key = True)
    html = Column(String)

    def __repr__(self):
        return f'{self.__class__.__name__}, Case Number: {self.case_number}'

if __name__ == "__main__":
    Model.metadata.create_all(engine)
