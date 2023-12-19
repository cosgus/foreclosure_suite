from datetime import datetime
import enum

from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, DateTime, Integer, JSON, String, Boolean

from foreclosure_suite.database.my_alchemy import session, engine

Model = declarative_base()
Model.query = session.query_property()
print(__name__)
class Table(enum.Enum):

    SCRAPED             = 'dates_scraped'
    AUCTION_RAW_DATA    = 'auction_raw_data'
    COURT_RAW_DATA      = 'court_raw_data'
    APPRAISER_RAW_DATA  = 'appraiser_raw_data'
    

class TimeStampedModel(Model):
    __abstract__ = True

    created_at = Column(DateTime, default=datetime.utcnow())
    updated_at = Column(DateTime, onupdate=datetime.utcnow())

class DataLake(TimeStampedModel):
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

    id = Column(Integer, primary_key = True)
    json = Column(JSON)

    def __repr__(self):
        return f'{self.__class__.__name__}, Folio: {self.id}'


class CourtLake(DataLake):
    __tablename__ = "court_raw_data"

    id = Column(Integer, primary_key = True, autoincrement = True)
    case_number = Column(String)
    html = Column(String)

    def __repr__(self):
        return f'{self.__class__.__name__}, AID: {self.id}'

if __name__ == "__main__":
    Model.metadata.create_all(engine)
