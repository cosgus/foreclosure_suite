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

    SCRAPED             = 'dates_scraped'
    AUCTION_RAW_DATA    = 'auction_raw_data'
    COURT_RAW_DATA      = 'court_raw_data'
    APPRAISER_RAW_DATA  = 'appraiser_raw_data'
    
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
    def exists_in_table(cls, session, **kwargs):
        if session.query(cls).filter_by(**kwargs).first():
            logger.debug(f'{cls} - Already Inserted')
            return True
        pending = [entry for entry in session.new]
class DataLake(ModelMixin):
    __abstract__ = True

    parsed = Column(Boolean, default=False)

class Scraped(Model):
    __tablename__ = 'dates_scraped'

    id = Column(Integer, primary_key = True)
    date = Column(DateTime)

class AuctionLake(DataLake):
    __tablename__ ='auction_raw_data'

    id = Column(Integer, primary_key = True)
    xhr = Column(JSON)
    html = Column(String)

    def __repr__(self):
        return f'{self.__class__.__name__}, AID: {self.id}'

class AppraiserLake(DataLake):
    __tablename__ = 'appraiser_raw_data'

    id = Column(BigInteger, primary_key = True)
    json = Column(JSON)

    def __repr__(self):
        return f'{self.__class__.__name__}, Folio: {self.id}'


class CourtLake(DataLake):
    __tablename__ = "court_raw_data"

    id = Column(Integer, primary_key = True, autoincrement = True)
    case_number = Column(String, unique = True)
    html = Column(String)

    def __repr__(self):
        return f'{self.__class__.__name__}, Case Number: {self.case_number}'

if __name__ == "__main__":
    Model.metadata.create_all(engine)
