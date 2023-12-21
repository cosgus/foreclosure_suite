from datetime import datetime, timedelta


def daterange(start_date: datetime, end_date: datetime):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)

def convert_currency_to_float(currency:str) -> float:
    currency = currency.replace('$','').replace(',','')
    return float(currency)

def convert_folio_to_int(parcel_id:str) -> int:
    return int(parcel_id.replace('-',''))