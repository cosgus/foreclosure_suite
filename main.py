from foreclosure_suite.database.seed import DataSeed
from foreclosure_suite.database import models
from foreclosure_suite.database.config import engine

def main():
    
    models.Model.metadata.create_all(bind = engine)
    seeder = DataSeed()
    seeder.seed_data()

if __name__ == '__main__':
    main()