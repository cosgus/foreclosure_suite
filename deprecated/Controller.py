import deprecated.HistoricDataCollector as HistoricDataCollector
import deprecated.DataCleanse as DataCleanse
import deprecated.ForeclosureScanner as ForeclosureScanner
from deprecated.HistoricDataCollector import MyAdapter, LOGINpayload, NOTICEpayload, Cookie
import pandas as pd
import requests
import json
import traceback
import sys
from bs4 import BeautifulSoup
import os


def searchbyaid(aid):

    MainURL = "https://www.miamidade.realforeclose.com/index.cfm?"
    s = requests.Session()
    s.mount(MainURL, MyAdapter())


    #Logging in
    NOTICEpayload.update({'NID': 8045})
    s.post(MainURL, data=LOGINpayload)
    # Clearing Notice, updating NID, and repeat till passed all notices
    s.post(MainURL, data=NOTICEpayload)
    NOTICEpayload.update({'NID': 9208})
    s.post(MainURL, data=NOTICEpayload)
    NOTICEpayload.update({'NID': 9299})
    s.post(MainURL, data=NOTICEpayload)
    NOTICEpayload.update({'NID': 9147})
    s.post(MainURL, data=NOTICEpayload)

    print('\n'*80)
    print('Collecting data for AID: ', aid)

    DF = pd.DataFrame()
    DF = ForeclosureScanner.get_AIDUrl_data(aid, DF, s)


    AIDXHR = 'https://www.miamidade.realforeclose.com/index.cfm?zaction=AUCTION&ZMETHOD=UPDATE&FNC=UPDATESINGLE&AID=' \
             + aid + '&tx=1582314005699&_=1582314005569'
    r = s.post(AIDXHR, data=Cookie)
    data = json.loads(r.text)
    ADATA = data['ADATA']
    AITEM = ADATA['AITEM']
    AITEM = AITEM[0]

    d = AITEM['B']
    YYYY = d[6:10]
    DD = d[3:5]
    MM = d[0:2]

    if AITEM['P'] == 'A':
        DF.loc[int(aid), 'Plaintiff Max Bid'] = 'HIDDEN'
    else:
        pmax = AITEM['P'].replace('$', '')
        pmax = pmax.replace(',', '')
        DF.loc[int(aid), 'Plaintiff Max Bid'] = pmax


    DF.loc[int(aid), 'Auction ID'] = aid


    for index, data in DF.iterrows():
        zdata = ForeclosureScanner.get_Zestimate(data)
        DF.loc[int(aid),'ZEstimate'] = zdata[1]
        DF.loc[index, 'Annual Tax'] = zdata[4]
        DF.loc[index, 'HOA'] = zdata[3]
        DF.loc[int(aid), 'Beds'] = ForeclosureScanner.get_appraiser_data(data.loc['Parcel ID'])[0]
        DF.loc[int(aid), 'Bath'] = ForeclosureScanner.get_appraiser_data(data.loc['Parcel ID'])[1]
        DF.loc[int(aid), 'Lot Size'] = ForeclosureScanner.get_appraiser_data(data.loc['Parcel ID'])[2]
        DF.loc[int(aid), 'Living Area'] = ForeclosureScanner.get_appraiser_data(data.loc['Parcel ID'])[3]
        DF.loc[int(aid), 'Docket Count'] = ForeclosureScanner.get_docket_count(data.loc['Case Number'])
        if data.loc['Case Number'][0] == '2':
            DF.loc[int(aid), 'Court Year'] = int(data.loc['Case Number'][0:4])
        else:
            DF.loc[int(aid), 'Court Year'] = int('20' + data.loc['Case Number'][0:2])
        DF.loc[int(aid), 'Defendant Count'] = data.loc['Defendant'].count('\'') / 2

        if float(DF.loc[index, 'ZEstimate']) == 0:
            DF.loc[index, 'JoverZ'] = 0
        else:
            DF.loc[index, 'JoverZ'] = float(DF.loc[index, 'Final Judgment'].replace(',','').replace('$',''))/float(DF.loc[index, 'ZEstimate'])

        masterDF = pd.read_csv('./Data/MASTER DATA - Cleansed.csv')
        masterDF = masterDF.set_index('Case Number')

        casen = (DF.loc[int(aid), 'Case Number'])

        try:
           DF.loc[int(aid), 'Previous Auctions'] = len(masterDF.loc[casen, 'Previous Auctions'])
        except TypeError:
            DF.loc[int(aid), 'Previous Auctions'] = 1
        except KeyError:
            DF.loc[int(aid), 'Previous Auctions'] = 0

        DayURL = 'https://www.miamidade.realforeclose.com/index.cfm?zaction=AUCTION&Zmethod=DAYLIST&AUCTIONDATE=' + MM + '/' + DD + '/' + YYYY
        r = s.post(DayURL, data=Cookie)
        soup = BeautifulSoup(r.text, features='lxml')
        dayaidlist = soup.find(id='ALB').text.split(',')

        DF.loc[int(aid), 'Day Count'] = len(dayaidlist)

        for i in range(len(dayaidlist)):
            if dayaidlist[i] == aid:
                DF.loc[int(aid), 'Place in Line'] = (i+1)

    print('\n' * 80)



    DF = ForeclosureScanner.regrPredict('Sold Amount', DF)
    DF = ForeclosureScanner.regrPredict('Plaintiff Max Bid', DF)
    DF = ForeclosureScanner.regrPredict('Status Binary', DF)
    regressionlist = []



    soldamount = DF.loc[int(aid), '(P) Sold Amount']
    regressionlist.append(DF.loc[int(aid), '(R) Sold Amount'])
    try:
        pmax = DF.loc[int(aid), '(P) Plaintiff Max Bid']
        regressionlist.append(DF.loc[int(aid), '(R) Plaintiff Max Bid'])
    except:
        pmax = DF.loc[int(aid), 'Plaintiff Max Bid']
    status = DF.loc[int(aid), '(P) Status Binary']
    regressionlist.append(DF.loc[int(aid), '(R) Status Binary'])


    for key, value in DF.iteritems():
        print(key, value)

    print('Prediction Summary')
    print('------------------')
    print('Sale Amount:', '${:,.2f}'.format(soldamount))
    try:
        print('Plaintiff Max Bid:', '${:,.2f}'.format(pmax))
    except:
        print('Plaintiff Max Bid (Given):', '${:,.2f}'.format(float(pmax)))
    print('Status:', str(status))

    print('\n')
    if soldamount >= float(pmax):
        print('Likely Outcome: Sold to 3rd party for', '${:,.2f}'.format(soldamount))
    else:
        print('Likely Outcome: Sold to Plaintiff')
    if DF.loc[int(aid), 'ZEstimate'] == 0:
        print('ZEstimate is 0 - Regression damaged')



    print('\n')
    print('1 - View Regression names')
    print('2 - View Regression Summariess')
    print('3 - Force a Regression')
    print('4 - Calculate Max Bid')
    print('5 - Exit')

    responding = True

    while responding:
        response = input()
        if response == '1':
            for regression in regressionlist:
                print(regression)
        elif response == '2':
            for regression in regressionlist:
                regression = regression.replace('.pickle','.txt')
                f = open('./Data/Regression Results/Results_' + regression ,'r')
                reader = f.read()
                print(reader)
                print('\n')
                f.close()
        elif response == '3':
            print('Cant do that yet')
        elif response == '4':
            value = input('What is the target sale price? ')
            value = value.replace('$', '')
            value = value.replace(',', '')
            value = float(value)
            closing_costs = 0.07 * value
            hoa = float(DF.loc[int(aid),'HOA'])
            taxes = float(DF.loc[int(aid), 'Annual Tax'])/2
            maxbid = value - closing_costs - hoa - taxes
            maxbid = maxbid/1.2
            maxbid = maxbid/1.02
            print('Your max bid: ', '${:,.2f}'.format(maxbid))
            input()
        elif response == '5':
            responding = False


def historicdatascan(all=False):
    try:
        HistoricDataCollector.main()
        try:
            DF = pd.read_csv('./Data/Foreclosure.csv', error_bad_lines=False, encoding='utf-8')
            DF['Date'] = pd.to_datetime(DF.Date)
            DF = DF.sort_values(by='Date', ascending=False)
            DF = DF.drop_duplicates()
            DF.to_csv('./Data/Foreclosure.csv', index=False, encoding='utf-8')
        except Exception as e:
            print('Excepting Date Sort & Duplicate drop in Controller')
            print(e)
    except Exception as e:
        print('\n')
        print('Historic data collection failed')
        print(traceback.print_exc())


def datacleanse():
    try:
        DataCleanse.main()
    except Exception as e:
        print('\n')
        print('Data Cleanse failed')
        print(traceback.print_exc())


def forwardscanner():
        try:
            ForeclosureScanner.main()
        except Exception as e:
            print('\n')
            print('Forward Scanner failed')
            print(traceback.print_exc())


while True:

    print('\n'*80)
    print('Choose an Option')
    print('----------------')
    print('1 - Historic Data Scan')
    print('2 - Data Cleanse')
    print('3 - Forward Scanner')
    print('4 - Search by AID')
    print('5 - Analyze data tester')
    response = input('')

    if response == '1':
        historicdatascan()
    elif response == '2':
        datacleanse()
    elif response == '3':
        forwardscanner()
    elif response == '4':
        response2 = input('Enter AID:')
        try:
            int(response2)
        except:
            print('Invalid response try again')
        try:
            searchbyaid(response2)
            print('\n'*80)
        except Exception as e:
            print('\n')
            print('AID Search failed')
            print(traceback.print_exc())
    elif response == '5':
        directory = './Data/Regression Data/'
        for filename in os.listdir(directory):
            DF = pd.read_csv(directory + filename)
            DF.name = filename
            DataCleanse.analyzeData(DF)


