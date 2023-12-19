from foreclosure_suite.database.seed import DataSeed

def main():
    
    seeder = DataSeed()
    seeder.seed_data()

if __name__ == '__main__':
    main()