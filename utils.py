def convert_currency_to_float(currency:str) -> float:
    currency = currency.replace('$','').replace(',','')
    return float(currency)