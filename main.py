from requests.exceptions import ConnectionError
from time import sleep

from foreclosure_suite.database.seed import DataSeed
from foreclosure_suite.database import models
from foreclosure_suite.database.config import engine
from foreclosure_suite.utils import get_logger

def main():
    
    logger = get_logger
    models.Model.metadata.create_all(bind = engine)
    seeder = DataSeed()
    while True:
        try:
            seeder.seed_data()
        except ConnectionError as e:
            logger.warning(f'Connection Error - Restarting seeder\n {e}')
            sleep(30)

if __name__ == '__main__':
    main()