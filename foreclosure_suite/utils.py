import yaml
import os

from datetime import datetime, timedelta


def daterange(start_date: datetime, end_date: datetime):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)

def convert_currency_to_float(currency:str) -> float:
    currency = currency.replace('$','').replace(',','')
    return float(currency)

def convert_folio_to_int(parcel_id:str) -> int:
    return int(parcel_id.replace('-',''))

def load_config():
    set_directory()
    with open('../config.yaml', 'rt') as f:
        config = yaml.safe_load(f.read())
    return config

def set_directory():
    FILE_PATH = os.path.abspath(__file__)
    CWD = os.path.dirname(FILE_PATH)
    os.chdir(CWD)