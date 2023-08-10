import statsmodels.api as sm
import requests
import pandas as pd
import json
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from time import sleep
from deprecated.HistoricDataCollector import MyAdapter, LOGINpayload, NOTICEpayload, Cookie, fuzzy_contains_word, login
from deprecated.courtform import courtForm, getViewState, header,loginForm
import os
from deprecated.DataCleanse import cleanMaster
import progressbar
import deprecated.timing as timing
import re
import time
import sys
import numpy as np

def get_Zdata(zpid):

    url = "https://www.zillow.com/homedetails/"+zpid+"_zpid/"

    header = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
        'referer': 'https://www.google.com/'
    }

    r = requests.get(url, headers=header)
    soup = BeautifulSoup(r.text, features='lxml')

    tax = 0
    hoa = 0

    for element in soup(text=re.compile('Annual tax amount')):
        tax = element.parent.text
        tax = tax.split(' ')
        tax = tax[3]
        tax = tax.replace('$', '')
        tax = tax.replace(',', '')

    for element in soup(text=re.compile('HOA fee')):
        hoa = element.parent.text
        hoa = hoa.split(' ')
        if len(hoa) < 3:
            hoa = 0
        else:
            hoa = hoa[2]
            hoa = hoa.replace('$', '')
            hoa = hoa.replace(',', '')
            hoa = hoa.replace('/mo', '')

    try:
        float(hoa)
    except:
        hoa = 0
    return [hoa, tax]


def get_Zestimate(data, url=False, finance=False):


    # http://www.zillow.com/webservice/GetUpdatedPropertyDetails.htm?zws-id=X1-ZWz1a6zfv8kaa3_7lwvq&zpid=62930509

    address = data.loc['Street Address']
    cityzip = data.loc['City/ZIP']

    ZWSID = 'X1-ZWz1a6zfv8kaa3_7lwvq'
    if len(address) == 0:
        return [0, 0, 0, 0, 0]
    else:
        cityzip = cityzip.replace(',','%2C+')
        cityzip = cityzip.replace(' ','')
        address = address.replace(' ','+')
        address = address
        #print(address)
        zillowURL = 'http://www.zillow.com/webservice/GetSearchResults.htm?zws-id=' + ZWSID + '&address=' + address + '&citystatezip='+cityzip[:-5]
        r = requests.get(zillowURL)
        soup = BeautifulSoup(r.text, features= 'lxml')
        errorcode = int(soup.find('code').text)
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
                    #print('SUCCESSFUL UNINCORPORATED REPAIR')
            else:
                temp=address.split('+')
                address = temp[0] +' '
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
        if url:
            try:
                return soup.find('homedetails').text
            except:
                return False

        if errorcode == 0:
            zpid = soup.find('zpid').text
            hoa, tax = get_Zdata(zpid)
            soup = soup.find('zestimate')
            zestimate = soup.find('amount').text
            high = soup.find('high').text
            low = soup.find('low').text
            if len(zestimate) > 0:
                zestimate = [int(low), int(zestimate), int(high), hoa, tax]
                return zestimate
            else:
                return [0, 0, 0, 0, 0]
        elif errorcode == 7:
            print('\n')
            print('Zillow daily call limit hit')
            sleep(30000)
            get_Zestimate(address, cityzip)
        else:
            return [0, 0, 0, 0, 0]


def condo_check(parties):
    HOA = ['HOA', 'Association', 'Homeowners', 'Condominium', 'Gardens', "Condo", 'Townhomes', 'Villas', 'Club', 'Assn']
    threshold = 50
    assoc = 0
    for word in (HOA):
        if 0 < fuzzy_contains_word(word, parties, 80) >= fuzzy_contains_word("NATIONAL ASSOCIATION",parties,80):
            return 1
    if assoc == 0:
        return 0

def get_appraiser_data(FOLIO):

    list = []
    if 'N/A' in FOLIO:
        return [0, 0, 0, 0]
    else:
        FOLIO = FOLIO.replace('-','')
        appraiserUrl = 'https://www.miamidade.gov/Apps/PA/PApublicServiceProxy/PaServicesProxy.ashx?Operation=GetPropertySearchByFolio&clientAppName=PropertySearch&folioNumber=' + FOLIO

        #print(type(FOLIO))
        #print(len(FOLIO))
        try:
            if int(FOLIO[0]) == 0:
             FOLIO = FOLIO[1:]
        except:
            return('No Folio Available')
        sleep(0.3)
        r = requests.get(appraiserUrl)
        try:
            data = json.loads(r.text)
        except:
            print(appraiserUrl)
            print(r)
            print(r.text)
            print(FOLIO)
            return [False, False, False, False]
        data = data['PropertyInfo']

        area = data['BuildingHeatedArea']

        if area == -1:
            area = data['BuildingActualArea']


        list.append(str(data['BedroomCount']))
        list.append(str(data['BathroomCount']))
        list.append(str(data['LotSize']))
        list.append(str(area))

        return list


def get_AIDUrl_data(aid, DF,s):


    AIDUrl = 'https://www.miamidade.realforeclose.com/index.cfm?zaction=auction&zmethod=details&AID=' + aid + '&bypassPage=1'

    r = s.post(AIDUrl, data=Cookie)
    # print(r.text)


    if 'START HERE' in r.text:
        login(s)
        sleep(0.3)
        r = s.post(AIDUrl, data=Cookie)
        print('LOGGED BACK IN')
    soup = BeautifulSoup(r.text,'lxml')
    x=0
    # print(html.text[0:1000])
    auction_details = soup.find_all("td", class_="bDat")
    # print("Auction Details:")
    # print("________________\n")
    if "Case Number" in r.text:
        DF.loc[int(aid),'Case Number'] = auction_details[x].text
        # print("Case Number Found: " + str(auction_details[x].text))
        x+=3
    else:
        DF.loc[int(aid),'Case Number'] = ''
    if "Final Judgment" in r.text:
        # print("Final Judgement found: " + str(auction_details[x].text))
        DF.loc[int(aid),'Final Judgment'] = auction_details[x].text
        x+=1
    else:
        DF.loc[int(aid),'Final Judgment'] = ''
    if "Parcel ID" in r.text:
        # print("Parcel ID found: "+ str(auction_details[x].text))
        if len(auction_details[x].text) == 0:
            DF.loc[int(aid),'Parcel ID'] = 'N/A'
        if 'MULTI' in r.text:
            DF.loc[int(aid), 'Parcel ID'] = 'MULTIPLE PARCEL'
        else:
            DF.loc[int(aid),'Parcel ID'] = auction_details[x].text
        x += 2
    else:
        DF.loc[int(aid),'Parcel ID'] = 'N/A'
    if "Property Address" in r.text:
        # print("Property Address found: "+ str(auction_details[x].text) + " " + str(auction_details[x+1].text))
        DF.loc[int(aid),'Street Address'] = auction_details[x].text
        DF.loc[int(aid),'City/ZIP'] = auction_details[x+1].text
        x+=2
    else:
        DF.loc[int(aid),'Street Address'] = ''
        DF.loc[int(aid),'City/ZIP'] = ''
    if "Assessed Value" in r.text:
        DF.loc[int(aid),'Assessed Value'] =auction_details[x].text
        #print("Assessed value found: "+ str(auction_details[x].text))
        x+=1
    else:
        DF.loc[int(aid),'Assessed Value'] = ''
    if "Property Appraiser Legal" in r.text:
        auction_details[x].text
    else:
        pass
    soup = soup.find(id="mgTab1")
    party_details = soup.find_all('td')
    defendant = []
    plaintiff = []

    DF.loc[int(aid),'Association Binary'] = condo_check(party_details)

    for x in range(int(len(party_details)/2)):
        if "ATTORNEY" not in party_details[2*x].text:
            if "DEFENDANT" in party_details[2*x].text:
                defendant.append(party_details[2*x+1].text)
            if "PLAINTIFF" in party_details[2*x]:
                plaintiff.append(party_details[2*x+1].text)
    DF.loc[int(aid),'Plaintiff'] = str(plaintiff)
    DF.loc[int(aid),'Defendant'] = str(defendant)

    return DF

def get_docket_count(caseNumber):

    try:
        if caseNumber[0] != '2':
            caseNumber = '20' + caseNumber
        caseNumber = caseNumber.replace('-','')

        s = requests.Session()

        courtUrl = 'https://www2.miami-dadeclerk.com/PremierServices/login.aspx'

        s.post(courtUrl, data=loginForm, cookies=header)

        courtUrl = 'https://www2.miami-dadeclerk.com/ocs/Search.aspx'
        viewState, eventValidation = getViewState(courtUrl)
        courtForm['__VIEWSTATE'] = viewState
        courtForm['__EVENTVALIDATION'] = eventValidation
        courtForm['ctl00$ContentPlaceHolder1$txtLCNYearSTD_localCaseContent'] = caseNumber[0:4]
        courtForm['ctl00$ContentPlaceHolder1$txtLCNSeqSTD_localCaseContent'] = caseNumber[4:10]
        courtForm['ctl00$ContentPlaceHolder1$localCaseCodesSelect_localCaseContent'] = caseNumber[10:12]
        courtForm['ctl00$ContentPlaceHolder1$txtLCNLocSTD_localCaseContent'] = '01'


        r = s.post(courtUrl, data=courtForm)
        soup = BeautifulSoup(r.text, features='lxml')
        docketcount = soup.select('#ctl00_ContentPlaceHolder1_lblDocketCount')[0].text

        return docketcount
    except:
        return 80


def populateForward(delta = 20):
    # get all active auction data from today up to (delta) days from now (defaults to 14 days)

    # X 1 - create login session for foreclosure website
    # 2 - iterate dates
    # 3 - pull all auction ID's for given date
    # 4 - get AID data
    # 5 - get appraiser data
    # 6 - get zillow data
    # 7 - get court data
    # 7 - cleanse data
    # 8 - return DF

    DF = pd.DataFrame()

    mainURL = "https://www.miamidade.realforeclose.com/index.cfm?"
    s = requests.Session()
    s.mount(mainURL, MyAdapter())

    #Logging in
    r = s.post(mainURL, data=LOGINpayload)
    NOTICEpayload.update({'NID': 8045})
    #Clearing Notice, updating NID, and repeat till passed all notices
    r = s.post(mainURL, data=NOTICEpayload)
    NOTICEpayload.update({'NID': 9208})
    r = s.post(mainURL, data=NOTICEpayload)
    NOTICEpayload.update({'NID': 9299})
    r = s.post(mainURL, data=NOTICEpayload)
    NOTICEpayload.update({'NID': 9147})
    r = s.post(mainURL, data=NOTICEpayload)

    d = datetime.today()


    for single_date in (d+timedelta(n) for n in range(delta)):
        YYYY = single_date.strftime("%Y-%m-%d")[0:4]
        MM = single_date.strftime("%Y-%m-%d")[5:7]
        DD = single_date.strftime("%Y-%m-%d")[8:10]

        dayURL = 'https://www.miamidade.realforeclose.com/index.cfm?zaction=AUCTION&Zmethod=DAYLIST&AUCTIONDATE=' + MM + '/' + DD + '/' + YYYY

        r = s.post(dayURL, data = Cookie)
        soup = BeautifulSoup(r.text, 'lxml')
        if 'START HERE' in r.text:
            login(s)
            sleep(0.3)
            r = s.post(dayURL, data=Cookie)
            print('LOGGED BACK IN')
        if len(r.text) > 19730:
            fRequestUrl = 'https://www.miamidade.realforeclose.com/index.cfm?zaction=AUCTION&Zmethod=UPDATE&FNC=LOAD&AREA=W&PageDir=0&doR=1&tx=1606337164997&bypassPage=1&test=1&_=1606337164793'
            r = s.post(fRequestUrl, data = Cookie)
            if 'FORECLOSURE' in r.text:
                div = str(soup.find(id='ALB'))[48:-6]
                aidList = div.split(',')
                print('\n')
                print(str(single_date),'is Foreclosure day with', str(len(aidList)), 'auctions')
                i = 0
                x = 0
                newlist = []
                for aid in aidList:
                    AIDXHR = 'https://www.miamidade.realforeclose.com/index.cfm?zaction=AUCTION&ZMETHOD=UPDATE&FNC=UPDATESINGLE&AID=' + aid + '&tx=1582314005699&_=1582314005569'
                    r = s.post(AIDXHR, data=Cookie)
                    data = json.loads(r.text)
                    ADATA = data['ADATA']
                    AITEM = ADATA['AITEM']
                    AITEM = AITEM[0]
                    data = data['RTIME']
                    data = data['COUNT']
                    if data == 1:
                        newlist.append(aid)
                    else:
                        i +=1


                aidList = newlist
                print('Removed', str(i), 'canceled auctions -', str(len(aidList)), 'active auctions on this day')
                i = 0

                Cookie2 = {
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36'
                }


                for aid in aidList:
                    tx = str(round(time.time()*1000))
                    Cookie2 = {
                        'referer': 'https://www.miamidade.realforeclose.com/index.cfm?zaction=auction&zmethod=details&AID='+aid+'&bypassPage=1',
                        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36',
                        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
                    }
                    AIDXHR = 'https://www.miamidade.realforeclose.com/index.cfm?zaction=AUCTION&ZMETHOD=UPDATE&FNC=UPDATESINGLE&AID=' + aid + '&tx=' + tx + '&_=' + tx

                    s.post(Cookie2['referer'])
                    r = s.post(AIDXHR, data=Cookie2)
                    data = json.loads(r.text)

                    if "Please Refresh" in r.text:
                        s.post(Cookie2['referer'])
                        r = s.post(AIDXHR, data=Cookie)
                        data = json.loads(r.text)

                    ADATA = data['ADATA']
                    AITEM = ADATA['AITEM']
                    AITEM = AITEM[0]
                    if AITEM['P'] == 'A':
                        DF.loc[int(aid), 'Plaintiff Max Bid'] = 'HIDDEN'
                    else:
                        pmax = AITEM['P'].replace('$','')
                        pmax = pmax.replace(',','')
                        DF.loc[int(aid), 'Plaintiff Max Bid'] = pmax

                    DF.loc[int(aid),'Date'] = single_date
                    DF.loc[int(aid),'Auction ID'] = aid
                    DF.loc[int(aid),'Day Count'] = len(aidList)
                    DF.loc[int(aid), 'Place in Line'] = i+1
                    DF = get_AIDUrl_data(aid, DF, s)
                    DF = DF.reset_index(drop = True)
                    i+=1
                print('Total Items: ',str(len(DF)))
        else:
            print('failing')


    print('\n')
    print('Filling additional data', str(len(DF)))
    k=0
    bar = progressbar.ProgressBar(maxval=len(DF),
                                  widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    bar.start()
    for index, data in DF.iterrows():
        bar.update(k+1)
        k+=1
        zdata = get_Zestimate(data)
        DF.loc[index, 'ZEstimate'] = zdata[1]
        DF.loc[index, 'Annual Tax'] = zdata[4]
        DF.loc[index, 'HOA'] = zdata[3]
        DF.loc[index, 'Beds']= get_appraiser_data(data.loc['Parcel ID'])[0]
        DF.loc[index, 'Bath']= get_appraiser_data(data.loc['Parcel ID'])[1]
        DF.loc[index, 'Lot Size']= get_appraiser_data(data.loc['Parcel ID'])[2]
        DF.loc[index, 'Living Area'] = get_appraiser_data(data.loc['Parcel ID'])[3]
        DF.loc[index, 'Docket Count'] = get_docket_count(data.loc['Case Number'])

        if float(DF.loc[index, 'ZEstimate']) == 0:
            DF.loc[index, 'JoverZ'] = 0
        else:
            DF.loc[index, 'JoverZ'] = float(DF.loc[index, 'Final Judgment'].replace(',','').replace('$',''))/float(DF.loc[index, 'ZEstimate'])
        if data.loc['Case Number'][0] == '2':
            DF.loc[index, 'Court Year'] = int(data.loc['Case Number'][0:4])
        else:
            DF.loc[index, 'Court Year'] = int('20' + data.loc['Case Number'][0:2])
        DF.loc[index, 'Defendant Count'] = data.loc['Defendant'].count('\'')/2


        masterDF = pd.read_csv('./Data/MASTER DATA - Cleansed.csv')
        masterDF = masterDF.set_index('Case Number')

        casen = DF.loc[index, 'Case Number']

        try:
            DF.loc[index, 'Previous Auctions'] = len(masterDF.loc[casen, 'Previous Auctions'])
        except TypeError:
            DF.loc[index, 'Previous Auctions'] = 1
        except KeyError:
            DF.loc[index, 'Previous Auctions'] = 0

    return DF

def regressionPicker(dVar,classification):
    # print('\n')
    # print('Choosing a regression for', dVar)
    # print('----------------------------------')
    # print('Dependant Variable:',dVar)
    # print('Conditions:', classification)
    # print('\n')

    potentials = ['48_Months_'+dVar.replace(' ', ''),
                  '60_Months_' + dVar.replace(' ', '')
                  ]

    for item in classification:
        for i in range(len(potentials)):
            if item == "['Plaintiff Max Bid']":
                potentials.append(potentials[i] + "_conditions_['Plaintiff Max Bid']")
            else:
                potentials.append(potentials[i] + '_'+item)

    for i in range(len(potentials)):
        potentials[i] = potentials[i] + '.pickle'

    for filename in os.listdir('./Data/Regression Results/pickles'):

        parameters = filename.split('_')
        parameters[-1] = parameters[-1].replace('.pickle','')
        if dVar.replace(' ','') in parameters[2]:
            if 'single' not in classification and 'single' in parameters:
                pass
            elif 'condo' not in classification and 'condo' in parameters:
                pass
            elif 'zeroz' not in classification and 'zeroz' in parameters:
                pass
            elif "['Plaintiff Max Bid']" in parameters and "['Plaintiff Max Bid']" not in classification:
                pass
            elif 'plaintiff' in parameters and 'plaintiff' not in classification:
                pass
            elif len(classification) == 0 and filename not in potentials:
                potentials.append(filename)
            elif filename not in potentials:
                potentials.append(filename)
            elif filename in potentials:
                pass
            else:
                print('Something Fucky - DROPPING ', filename)

    # for item in potentials:
    #     print(item)

    bestR = 0
    for regression in potentials:
        try:
            regr = sm.load('./Data/Regression Results/pickles/'+regression)

            name = regression
            regr=regr.model
            regr = regr.fit()

            if regr.rsquared > bestR and 'log' not in regression:
                bestregr = regr
                bestR = regr.rsquared
                bestname=name

        except FileNotFoundError:
            pass

    return bestregr, bestname


def regrPredict(dVar, DF, plaintiff=False):

    for index, data in DF.iterrows():
        classification = []
        if data['Plaintiff Max Bid'] != "HIDDEN":
            classification.append("['Plaintiff Max Bid']")
            if dVar == 'Plaintiff Max Bid':
                DF.loc[index, '(P) '+dVar] = data['Plaintiff Max Bid']
                continue

        try:
            if int(float(data['Lot Size'])) != 0 and int(data['Living Area']) != 0:
                classification.append('single')
            if int(float(data['Lot Size'])) == 0 and int(data['Living Area']) != 0:
                classification.append('condo')
            if int(data['ZEstimate']) == 0:
                classification.append('zeroz')
                print('ZEROZ IDENTIFIED')
            if plaintiff:
                classification.append('plaintiff')
        except ValueError as e:
            print('Value Error (ForeclosureScanner.regrPredict):        ', str(e))
            sys.exit()
            pass


        regr, name = regressionPicker(dVar, classification)



        psum = 0
        #print(name)
        for key, value in regr.params.iteritems():
            try:
                float(data[key])
                actual = data[key]
            except:
                actual = data[key].replace('$','')
                actual = actual.replace(',','')
            psum = psum + float(value)*float(actual)

        if dVar == 'Plaintiff Max Bid' and data['Plaintiff Max Bid'] != 'HIDDEN':
            DF.loc[index, '(P) ' + dVar] = data['Plaintiff Max Bid']
            DF.loc[index, '(R) ' + dVar] = 'None'
        else:
            DF.loc[index, '(P) ' + dVar] = psum
            DF.loc[index, '(R) ' + dVar] = name


    return DF

def filterNotable(DF):

    zips = ['33139', '33140', '33150', '33127', '33155', '33165', '33138', '33137', '33181']

    for index, data in DF.iterrows():
        triggers = []
        if 'log' in data['(R) Sold Amount']:
            DF.loc[index, '(P) Sold Amount'] = np.exp(DF.loc[index, '(P) Sold Amount'])
        try:
            float(data['Plaintiff Max Bid'])
        except ValueError:
            if 'log' in data['(R) Plaintiff Max Bid']:
                DF.loc[index, '(P) Plaintiff Max Bid'] = np.exp(DF.loc[index, '(P) Plaintiff Max Bid'])


        saleamount = 0.90 * float(data['ZEstimate'])  # 0.85 * 225,989.00  = $192,090.65
        closingcosts = 0.07 * saleamount # $13,446.3455

        assocfees = int(data['HOA']) * 12 # 200 * 12 = 2400.00
        taxes = int(data['Annual Tax'])/2 # 2493 / 2 = 1164.5
        incidentals = max(0.05*float(data['ZEstimate']), 25000) # 25000

        net = saleamount - closingcosts - assocfees - incidentals - taxes
        maxbid = net/1.2
        maxbid = maxbid/1.02

        if maxbid >= 0.93*float(data['(P) Sold Amount']):
            triggers.append('Regression')
            if float(data['(P) Sold Amount'] > maxbid > 0.93 * data['(P) Sold Amount']):
                triggers.append('Margin of Error')
        if float(data['ZEstimate']) > 750000:
            triggers.append('ZEstimate')
            triggers.append('Large Numbers')
        if float(data['Final Judgment'].replace(',', '')) > 750000:
            triggers.append('Judgment')
            if 'Large Numbers' not in triggers:
                triggers.append('Large Numbers')
        if float(data['Assessed Value']) > 750000:
            if 'Large Numbers' not in triggers:
                triggers.append('Large Numbers')
        if data['City/ZIP'][-5:] in zips:
            triggers.append('City/ZIP')
            DF.loc[index, 'Max Bid'] = maxbid
        if float(data['(P) Sold Amount']) < maxbid < 240000:
            triggers.append('Family Deal')
        if len(triggers) == 0:
            DF.drop([index], inplace=True)
            pass


        else:
            DF.loc[index, 'Trigger'] = str(triggers)
            DF.loc[index, 'Max Bid'] = maxbid
            DF.loc[index, 'Closing costs'] = closingcosts
            DF.loc[index, 'Sale amount'] = saleamount
            DF.loc[index, 'Fees'] = assocfees
            DF.loc[index, 'Incidentals'] = incidentals
            DF.loc[index, 'Net'] = net
        try:
            if float(data['ZEstimate']) != 0 and float(data['Final Judgment'].replace(',',''))/float(data['ZEstimate']) <= 0.3:
                DF.drop([index], inplace=True)
                pass
        except:
            pass

    return DF


def uploadtrello(DF):

    print('Uploading to Trello')
    bar = progressbar.ProgressBar(maxval=len(DF), widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    bar.start()
    oauthsecret = '2e6b69e0c60f90ffba944af1c11d886b07df1d8e967a9f1e73d8749c8b3b5bf7'

    params = {
        'key': 'f6b26b4a2b49d2c9296d1193fe633267',
        'token': '9e0ff7977f115394efac159594edd801dc9a77cd78f59d6cf743b490bd8dccbb',
        'idList': '5fc93d054cb39a8adfaa51e3',
        'name': '',
        'desc': '',
        'due': '',
        'fileSource': ''
    }

    requests.post("https://api.trello.com/1/lists/"+params['idList']+"/archiveAllCards", params=params)
    url = 'https://api.trello.com/1/cards'
    for index, auction in DF.iterrows():
        bar.update(index+1)
        params['name'] = auction['Street Address'] + ' ' + auction['City/ZIP']
        params['desc'] = "Auction ID: " + str(auction['Auction ID']) + '\n' +\
                         "ZEstimate: " + "${:,.2f}".format(float(auction['ZEstimate'])) + '\n' +\
                         "Judgment " + "${:,.2f}".format(float(auction['Final Judgment'].replace(',',''))) + '\n' +'\n' +\
                         "Sale: " + "${:,.2f}".format(float(auction['(P) Sold Amount'])) + '\n' +\
                         "Plaintiff Max: " + "${:,.2f}".format(float(auction['(P) Plaintiff Max Bid'])) + '\n' +\
                         "Your Bid: " + "${:,.2f}".format(float(auction['Max Bid'])) + '\n' + \
                         "Status" + str(float(auction['(P) Status Binary'])) + '\n' + '\n' +\
                         "Triggers: " + str(auction['Trigger']) + '\n'

        params['due'] = auction['Date']

        r = requests.post(url, params=params)
        data = json.loads(r.text)
        cardid = data['id']

        headers = {
            "Accept": "application/json",
        }

        path = './Data/Regression Results/Results_'+auction['(R) Sold Amount'].replace('.pickle', '.txt')

        params2 = {
            'key': 'f6b26b4a2b49d2c9296d1193fe633267',
            'token': '9e0ff7977f115394efac159594edd801dc9a77cd78f59d6cf743b490bd8dccbb',
        }

        files = {'file': (path[26:], open(path, 'rb').read())}

        cardurl = 'https://api.trello.com/1/cards/'+cardid+'/attachments'
        addmember = 'https://api.trello.com/1/cards/'+cardid+'/idMembers'

        r = requests.post(cardurl, params=params2, headers=headers, files=files)

        commenturl = 'https://api.trello.com/1/cards/' + cardid + '/actions/comments'
        params2['text'] = auction.to_string()
        r = requests.post(commenturl, params=params2)

        if auction['Plaintiff Max Bid'] != 'HIDDEN':
            params2['text']='Plaintiff Max Bid is Given'
            requests.post(commenturl, params=params2)
        else:
            path = './Data/Regression Results/Results_' + auction['(R) Plaintiff Max Bid'].replace('.pickle', '.txt')
            files = {'file': (path[26:], open(path, 'rb').read())}
            requests.post(cardurl, params=params2, headers=headers, files=files)

        path = './Data/Regression Results/Results_' + auction['(R) Status Binary'].replace('.pickle', '.txt')
        files = {'file': (path[26:], open(path, 'rb').read())}
        requests.post(cardurl, params=params2, headers=headers, files=files)

        zurl = get_Zestimate(auction, url=True)

        if not zurl:
            pass
        else:
            params2['url'] = zurl
            requests.post(cardurl, params=params2, headers=headers)
        params2['url'] = 'https://www.miamidade.realforeclose.com/index.cfm?zaction=auction&zmethod=details&AID=' + auction['Auction ID'] + '&bypassPage=1'
        requests.post(cardurl, params=params2, headers=headers)
        del params2['text']

        params2['value'] = '5fc93cf21258da48af1a5fff'
        labeladdurl = 'https://api.trello.com/1/cards/' + cardid + '/idLabels'

        if 'Regression' in auction['Trigger']:
            if float(auction['Max Bid']) > float(auction['(P) Plaintiff Max Bid']):
                requests.post(labeladdurl, params=params2)
        if 'City/ZIP' in auction['Trigger']:
            params2['value'] = '5fc93cf21258da48af1a600d'
            requests.post(labeladdurl, params=params2)
        if 'Large Numbers' in auction['Trigger']:
            params2['value'] = '5fc93cf21258da48af1a6002'
            requests.post(labeladdurl, params=params2)
        if 'Family Deal' in auction['Trigger']:
            params2['value'] = '5fc93cf21258da48af1a6008'
            requests.post(labeladdurl, params=params2)

        params2['value'] = '5b4a7b5950c0c0b96a7ede'
        requests.post(addmember, params=params2)
    bar.finish()

def main():

    testing = False
    #create dataframe with next 2 weeks worth of upcomingforeclosers

    if not testing:
        DF = populateForward(46)
        DF.to_csv('preclean post populateforwadonrd.csv', index=False, encoding='utf-8')
        DF = cleanMaster(DF, aux=True)
        timing.log('Done Cleaning', elapsed=True)
        DF.to_csv('forward test.csv', index=False, encoding='utf-8')
        DF = regrPredict('Sold Amount', DF)
        DF = regrPredict('Status Binary', DF)
        DF = regrPredict('Plaintiff Max Bid', DF)
        DF.to_csv('PreFilter test.csv', encoding='utf-8')

    else:
        DF = pd.read_csv('Test with notable predictions.csv', error_bad_lines= False, encoding = 'utf-8')

    DF = filterNotable(DF)
    timing.log('Done Filtering')
    DF = DF.reset_index(drop=True)
    DF.to_csv('Test with notable predictions.csv', encoding='utf-8', index = False)

    uploadtrello(DF)


if __name__ == "__main__":

    main()
