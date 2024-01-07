from datetime import datetime

from foreclosure_suite.scrapers import CourtParser
from foreclosure_suite.database import session
from foreclosure_suite.database.models import CourtLake
from foreclosure_suite.logger import get_logger

UPDATE_FROM_DATE = datetime(2024, 1, 7, 1, 57, 8)
BATCH_SIZE = 100

def reduce_size_court_lake_html():

    def query_to_be_updated(session):
        return session.query(CourtLake).filter(CourtLake.updated_at < UPDATE_FROM_DATE).limit(BATCH_SIZE).all()

    parser = CourtParser()
    logger = get_logger(__name__)

    batch = 0

    to_be_updated = query_to_be_updated(session)

    while to_be_updated:

        for idx, entry in enumerate(to_be_updated):

            entry.html = parser.remove_large_tags(entry.html)
            logger.info(f'{entry.case_number} - {batch * BATCH_SIZE + idx + 1}')
            session.commit()    

        to_be_updated = query_to_be_updated(session)
        batch += 1
        
if __name__ == '__main__':
    
    reduce_size_court_lake_html()
