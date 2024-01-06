import sys

from foreclosure_suite.scrapers import CourtParser
from foreclosure_suite.database import session
from foreclosure_suite.database.models import CourtLake
from foreclosure_suite.logger import get_logger


def reduce_size_court_lake_html():

    parser = CourtParser()
    logger = get_logger(__name__)
    to_be_updated = session.query(CourtLake).filter(CourtLake.updated_at == None).all()

    for idx, entry in enumerate(to_be_updated):

        entry.html = parser.remove_large_tags(entry.html)
        logger.info(f'{entry.case_number} - {idx + 1}/{len(to_be_updated)}')
        session.commit()
        
if __name__ == '__main__':
    
    reduce_size_court_lake_html()
