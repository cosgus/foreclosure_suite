import requests
import json
from bs4 import BeautifulSoup
from time import sleep
import pandas as pd
from random import randint
import sys


def historic_zdata(zpid, ua):

    # returns JSON data for historic zestimate values over last ten years.

    historicurl = 'https://www.zillow.com/graphql/'

    referer_list = ['https://www.zillow.com',
                    'https://www.google.com',
                    'https://www.yahoo.com',
                    'https://www.duckduckgo.com']

    headers = {"user-agent":"",
               "accept-Encoding": "gzip, deflate, br",
               "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
               "content-type": "text/plain",
               "origin": "https://www.zillow.com",
               "sec-fetch-dest": "empty",
               "sec-fetch-mode": "cors",
               "sec-fetch-site": "same-origin",
               "referer": 'https://www.zillow.com'}


    agent_df = pd.read_csv('chrome-user-agents.csv', error_bad_lines=False, encoding='utf-8')

    variables = {
            "zpid": '',
            "timePeriod": "TEN_YEARS",
            "metricType": "LOCAL_HOME_VALUES",
            "forecast": "true"
            }

    variables.update({'zpid': zpid})
    #headers.update({'user-agent': ua.random})

    queryurl = 'https://www.zillow.com/graphql/?zpid='+zpid+'&timePeriod=TEN_YEARS&metricType=LOCAL_HOME_VALUES&forecast=true&operationName=HomeValueChartDataQuery'
    query = """
        query HomeValueChartDataQuery($zpid: ID!, $metricType: HomeValueChartMetricType, $timePeriod: HomeValueChartTimePeriod) {
            property(zpid: $zpid) {
                homeValueChartData(metricType: $metricType, timePeriod: $timePeriod) {
                    points {
                        x
                        y
                    }
                name
                }
            }
        }"""

    sleep(randint(2, 6)/10)
    r = requests.post(historicurl, json={'query': query, 'variables': variables}, headers=headers)
    print(r.text)
    sys.exit()
    print(headers['user-agent'])
    i = 0

    while 'Captcha' in r.text:
        print("Captcha'd", str(i+1))
        headers.update({'user-agent': ua.random})
        sleep(randint(2, 6)/10)
        r = requests.post(historicurl, json={'query': query, 'variables': variables}, headers=headers)
        i += 1
        if i % 5 == 0:
            sleep(30)
            headers.update({'referer': referer_list[randint(0, len(referer_list) - 1)]})
            print('New referer:', headers['referer'])
        if i % 25 == 0:
            headers.update({'referer': referer_list[randint(0, len(referer_list)-1)]})
            print('New referer:', headers['referer'])
            sleep(30)
        if i % 50 == 0:
            sleep(1000)




    print(headers['user-agent'])
    #print(r.text)
    data = json.loads(r.text)
    data = data['data']
    data = data['property']
    data = data['homeValueChartData']
    data = data[0]
    data = data['points']
    return data


def get_zpid(data):

    address = data.loc['Street Address']
    cityzip = data.loc['City/ZIP']

    ZWSID = 'X1-ZWz1a6zfv8kaa3_7lwvq'

    if pd.isna(address):
        return False
    else:
        cityzip = cityzip.replace(',', '%2C+')
        cityzip = cityzip.replace(' ', '')
        address = address.replace(' ', '+')
        address = address
        #print(address)
        #print(cityzip)
        zillowURL = 'http://www.zillow.com/webservice/GetSearchResults.htm?zws-id=' + ZWSID + '&address=' + address + '&citystatezip='+cityzip[-5:]
        #print(zillowURL)
        r = requests.get(zillowURL)
        soup = BeautifulSoup(r.text, features='lxml')
        errorcode = int(soup.find('code').text)
        #print(errorcode)
        if errorcode == 508:
            if 'MIAMI%2C+FL' in cityzip and 'NW' not in address:
                cityzip = 'HOMESTEAD%2C+FL'
                zillowURL = 'http://www.zillow.com/webservice/GetSearchResults.htm?zws-id=' + ZWSID + '&address=' + address + '&citystatezip=' + cityzip
                r = requests.get(zillowURL)
                soup = BeautifulSoup(r.text, features='lxml')
                # print(soup.prettify())
                status = soup.find('message')
                errorcode = int(soup.find('code').text)
                if errorcode == 0:
                    pass
                    #print('SUCCESSFUL HOMESTEAD REPAIR')
            elif 'UNINCORPORATED' in cityzip or cityzip[0] == ',':
                cityzip = 'MIAMI%2C+FL'
                zillowURL = 'http://www.zillow.com/webservice/GetSearchResults.htm?zws-id=' + ZWSID + '&address=' + address + '&citystatezip=' + cityzip
                r = requests.get(zillowURL)
                soup = BeautifulSoup(r.text, features='lxml')
                # print(soup.prettify())
                status = soup.find('message')
                errorcode = int(soup.find('code').text)
                if errorcode == 0:
                    pass
            else:
                temp=address.split('+')
                address = temp[0] + ' '
                for i in range(len(temp)-2):
                    address = address + temp[i+1]+' '
                address = address.replace(' ','+')[0:-1]
                zillowURL = 'http://www.zillow.com/webservice/GetSearchResults.htm?zws-id=' + ZWSID + '&address=' + address + '&citystatezip=' + cityzip
                r = requests.get(zillowURL)
                soup = BeautifulSoup(r.text, features='lxml')
                # print(soup.prettify())
                status = soup.find('message')
                errorcode = int(soup.find('code').text)
                if errorcode == 0:
                    pass

        #print(errorcode)
        if errorcode == 0:
            zpid = soup.find('zpid').text
            soup = soup.find('zestimate')
            zestimate = soup.find('amount').text
            return zpid

        elif errorcode == 7:
            print('\n')
            print('Zillow daily call limit hit')
            sleep(30000)
        else:
            return False
