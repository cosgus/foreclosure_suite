from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager
from bs4 import BeautifulSoup
import ssl
import requests
from time import sleep
from datetime import datetime
from datetime import timedelta
import math
import re
from fuzzywuzzy import fuzz
import json
import csv
from deprecated.courtform import courtForm, getViewState, header,loginForm
import pandas as pd
import sys

# Open TLS Adapter (Whataver that means)

class MyAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = PoolManager(num_pools=connections,
                                       maxsize=maxsize,
                                       block=block,
                                       ssl_version=ssl.PROTOCOL_TLS)


class Fstruc(object):
    def __init__(self):
        self.AID = []
        self.date = []
        self.status = []
        self.caseN = []
        self.finalJudge = []
        self.parcelID = []
        self.street = []
        self.cityzip = []
        self.zip = []
        self.pmax = []
        self.assessed = []
        self.saleAmount = []
        self.legal = []
        self.zestimate = []
        self.bed = []
        self.bath = []
        self.lot = []
        self.living = []
        self.assoc = []
        self.defendant = []
        self.plaintiff = []
        self.sale = []
        self.time = []
        self.bidder_count = []
        self.end_time = []
        self.docket_count = []
        self.totalday = []
        self.placeinline = []

Cookie = {
    'cfid': 'ec7e22be-0981-4f1e-8447-33c513aa82b6',
    'cftoken':'0',
    '_ga': 'GA1.2.809838089.1572371936',
    '__utmz': '156495143.1579813001.69.2.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided)',
    '_gcl_au':'1.1.184605138.1580149038',
    '_gid':'GA1.2.725269267.1581437759',
    'AWSALB' : 'FSVXen2sZRjuTXKQL8u7Y28bLH0TteGiRyl7N0P5VORdZW/cfROJOpwXRlKlaqQcMQWdrsFXE5XfNbyc+Yg2A4i+aZSU6+oPuFOFHHUYFtbZ13Qecoh8FLaTXTi5',
    'AWSALBCORS': 'I4+QwgjHmDBotcRCAjuffeVoY1kl/03zLxTY3tgLjGiXpIGHydU2yeKgO8m/ShtADDGUhnP2GYnZ5W3opKT07hYJ71Dygn1ikGySBo5yrhrEQ63ro1znj/d/WLmb',
    '__utmc':'156495143',
    'CF_CLIENT_MIAMIDADE_REALFORECLOSE_TC':'1610817783764',
    '__utma':'156495143.809838089.1572371936.1581627165.1581703305.95',
    '__utmt_UA-51657054-1':'1',
    'testcookiesenabled':'enabled',
    '__utmb':'156495143.18.10.1581703305',
    'CF_CLIENT_MIAMIDADE_REALFORECLOSE_LV':'1610823164810',
    'CF_CLIENT_MIAMIDADE_REALFORECLOSE_HC':'580'
}

#Setting todays date into YYYY-MM-DD variables



#returns a list with all Auction ID's on a specific page
def get_pages_AID(Pcount,aid_list,n):
    #Pcount is the number of items on the page
    #n is the page number/index starting from 0
    AID = []
    AID = aid_list.split(',')
    #print(n)
    #print(Pcount)
    AID = AID[n*10:(Pcount)+(n*10)]
    #print(AID)
    """aid_list=aid_list[80*n:(80*n+1)+(Pcount*8-1)] # assumes all AID are 8 digits which is wrong
    if aid_list[-1] is ',':
        aid_list = aid_list[0:-1]
    AID = aid_list[0:-1].split(",")
    print(aid_list[0:-1])
    print(aid_list)
    for x in range(Pcount):
        AID.append(aid_list[8*x:8*x+7])
        #print("     Item " + str(x+1) + " is AID#: "+ aid_list[8*x:8*x+7])"""
    return AID

def fuzzy_contains_word(word,phrase,threshold):
    count = 0
    span = word.count(' ')
    temp=''
    previous = ''
    for x in range(0,len(phrase)):
        for parsed in phrase[x].text.split():
            if span > 0:
                temp=parsed
                parsed = previous + " " + parsed
                previous = temp
                #print(parsed)
            if fuzz.token_sort_ratio(word,parsed) > threshold:
                count +=1
            #print(word + ' x '+ str(parsed))
    return count

def condo_check(parties):
    HOA = ['HOA', 'Association', 'Homeowners', 'Condominium', 'Gardens', "Condo", 'Townhomes', 'Villas', 'Club', 'Assn']
    threshold = 50
    assoc = 0
    for word in (HOA):
        if 0 < fuzzy_contains_word(word,parties,80) >= fuzzy_contains_word("NATIONAL ASSOCIATION",parties,80):
            assoc +=1
            M.assoc.append('Y')
            return 0
    if assoc == 0:
        M.assoc.append('N')


def get_AIDUrl_data(AID,s):
    AIDUrl = 'https://www.miamidade.realforeclose.com/index.cfm?zaction=auction&zmethod=details&AID=' + AID + '&bypassPage=1'

    r = s.post(AIDUrl, data=Cookie)
    #print(r.text)
    if 'START HERE' in r.text:
        login(s)
        r = s.post(AIDUrl, data=Cookie)
        print('LOGGED BACK IN')
    soup = BeautifulSoup(r.text,'lxml')
    x=0
    #print(html.text[0:1000])
    auction_details = soup.find_all("td", class_="bDat")
    #print("Auction Details:")
    #print("________________\n")
    if "Case Number" in r.text:
        M.caseN.append(auction_details[x].text)
        #print("Case Number Found: " + str(auction_details[x].text))
        x+=3
    else:
        M.caseN.append('')
    if "Final Judgment" in r.text:
        #print("Final Judgement found: " + str(auction_details[x].text))
        M.finalJudge.append(auction_details[x].text)
        x+=1
    else:
        M.finalJudge.append('')
    if "Parcel ID" in r.text:
        #print("Parcel ID found: "+ str(auction_details[x].text))
        if len(auction_details[x].text) == 0:
            M.parcelID.append('N/A')
        else:
            try:
                int(auction_details[x].text[0])
                M.parcelID.append(auction_details[x].text)
            except:
                M.parcelID.append('N/A')

        x+=2
    else:
        M.parcelID.append('N/A')
    if "Property Address" in r.text:
        #print("Property Address found: "+ str(auction_details[x].text) + " " + str(auction_details[x+1].text))
        M.street.append(auction_details[x].text)
        M.cityzip.append(auction_details[x+1].text)
        x+=2
    else:
        M.street.append('')
        M.cityzip.append('')
    if "Assessed Value" in r.text:
        M.assessed.append(auction_details[x].text)
        #print("Assessed value found: "+ str(auction_details[x].text))
        x+=1
    else:
        M.assessed.append('')
    if "Property Appraiser Legal" in r.text:
        M.legal.append(auction_details[x].text)
    else:
        M.legal.append('')
    soup = soup.find(id="mgTab1")
    try:
        party_details = soup.find_all('td')
    except Exception as e:
        print(e)
        print(r)
        print(r.text)
    defendant = []
    plaintiff = []
    condo_check(party_details)
    for x in range(int(len(party_details)/2)):
        if "ATTORNEY" not in party_details[2*x].text:
            if "DEFENDANT" in party_details[2*x].text:
                defendant.append(party_details[2*x+1].text)
            if "PLAINTIFF" in party_details[2*x]:
                plaintiff.append(party_details[2*x+1].text)
    M.plaintiff.append(plaintiff)
    M.defendant.append(defendant)
            #print(str(party_details[2*x].text) + ": " + str(party_details[2*x+1].text))


def get_docket_count(caseNumber):

    try:
        if caseNumber[0] != '2':
            caseNumber = '20' + caseNumber
        caseNumber = caseNumber.replace('-','')

        s = requests.Session()

        courtUrl = 'https://www2.miami-dadeclerk.com/PremierServices/login.aspx'

        s.post(courtUrl, data=loginForm, cookies = header)

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

        M.docket_count.append(docketcount)
    except:
        M.docket_count.append('N/A')

    return M.docket_count[-1]

def get_AIDXHR_data(AID,s):
    AIDXHR = 'https://www.miamidade.realforeclose.com/index.cfm?zaction=AUCTION&ZMETHOD=UPDATE&FNC=UPDATESINGLE&AID=' + AID + '&tx=1582314005699&_=1582314005569'
    #print(AIDXHR)

    r = s.post(AIDXHR, data = Cookie)
    #print(r.text)
    if 'START HERE' in r.text:
        login(s)

        r = s.post(AIDXHR, data=Cookie)
        print('LOGGED BACK IN')
    soup = BeautifulSoup(r.text, 'lxml')
    soup = soup.find('p')
    #print(soup.text)
    if "Party" in r.text:
        #print("3rd Party Sale")
        M.status.append("Sold to 3rd Party")
        result = re.search(r'{"B":"(.+?)"',r.text)
        M.time.append(result.group(1)[11:19])
        result = re.search(r'"P":"(.+?)"', r.text)
        if result.group(1) == "A":
            M.pmax.append('HIDDEN')
            #print("HIDDEN")
        else:
            M.pmax.append(result.group(1))
            #print(result.group(1))
        result = re.search(r'"D":"(.+?)"', r.text)
        M.sale.append(result.group(1))
        #print(result.group(1))
    elif "Plaintiff" in soup.text:
        #print("Plaintiff Sale")
        M.status.append("Sold to Plaintiff")
        result = re.search(r'{"B":"(.+?)"',r.text)
        M.time.append(result.group(1)[11:19])
        #print(result.group(1))
        result = re.search(r'{"B":"(.+?)"', r.text)
        M.time.append(result.group(1)[11:19])
        result = re.search(r'"P":"(.+?)"', r.text)
        if result.group(1) == "A":
            M.pmax.append('HIDDEN')
            #print("HIDDEN")
        else:
            #print(result.group(1))
            M.pmax.append(result.group(1))
        result = re.search(r'"D":"(.+?)"', r.text)
        M.sale.append(result.group(1))
        #print(result.group(1))
    elif "Canceled" in soup.text:
        #print("Canceled sale")
        result = re.search(r'{"B":"(.+?)"',r.text)
        M.status.append(result.group(1))
        M.time.append('N/A')
        M.sale.append('N/A')
        result = re.search(r'"P":"(.+?)"', r.text)
        if result.group(1) == "A":
            M.pmax.append('HIDDEN')
            #print("HIDDEN")
        else:
            #print(result.group(1))
            M.pmax.append(result.group(1))
    else:
        M.status.append('Other')
        M.time.append('N/A')
        M.sale.append('N/A')
        M.pmax.append('HIDDEN')
        #print(result.group(1))


def get_bidder_data(AID,s):
    #r = s.post('https://www.miamidade.realforeclose.com/index.cfm?zaction=AUCTION&Zmethod=DAYLIST&AUCTIONDATE=02/03/2020', data=Cookie)

    r = s.post('https://www.miamidade.realforeclose.com/index.cfm?zaction=AJAX&zmethod=POPUP&p_Name=BID&p_id=pWin4&p_List='+AID+'&t=1582414530976')
    soup = BeautifulSoup(r.text, 'lxml').find_all('tr')
    bidders = []
    del soup[0:3]
    for x in range(len((soup))):
        #print(soup[x].text.split('\n'))
        #print(len(soup[x].text.split('\n')))
        #print('\n')
        tsoup = soup[x].text.split('\n')
        bidder_number = soup[x].text[1:8].replace('\n', '')
        #bidder_number = soup[x].text[1:8].replace(' ', '')
        try:
            bidder_number = tsoup[2]
            int(bidder_number)
            #print("Bidder for Item #" + str(x) + ": " + str(int(bidder_number)))
            bidders.append(str(int(bidder_number)))
        except ValueError:
            pass
        except IndexError:
            pass
        """for i in range(len(tsoup)):
            if "final bid" in tsoup[i]:
                print(len(tsoup))
                print(tsoup)"""
    return bidders

    #print("Getting bidder info for: " + str(AID))


def get_appraiser_data(FOLIO):

    if 'N/A' in FOLIO:
        M.bed.append('N/A')
        M.bath.append('N/A')
        M.lot.append('N/A')
        M.living.append('N/A')
    else:
        FOLIO = FOLIO.replace('-','')
        appraiserUrl = 'https://www.miamidade.gov/Apps/PA/PApublicServiceProxy/PaServicesProxy.ashx?Operation=GetPropertySearchByFolio&clientAppName=PropertySearch&folioNumber=' + FOLIO

        #print(type(FOLIO))
        #print(len(FOLIO))
        try:
            if int(FOLIO[0]) == 0:
             FOLIO = FOLIO[1:]
        except ValueError:
            return('No Folio Available')

        r = requests.get(appraiserUrl)

        data = json.loads(r.text)
        data = data['PropertyInfo']

        area = data['BuildingHeatedArea']

        if area == -1:
            area = data['BuildingActualArea']

        M.bed.append(str(data['BedroomCount']))
        M.bath.append(str(data['BathroomCount']))
        M.lot.append(str(data['LotSize']))
        M.living.append(str(area))

def get_Zestimate(address,cityzip):

    ZWSID = 'X1-ZWz1a6zfv8kaa3_7lwvq'
    if len(address) == 0:
        M.zestimate.append([0, 0, 0])
    else:
        cityzip = cityzip.replace(',','%2C+')
        cityzip = cityzip.replace(' ','')
        address = address.replace(' ','+')
        address = address
        #print(address)
        zillowURL = 'http://www.zillow.com/webservice/GetSearchResults.htm?zws-id=' + ZWSID + '&address=' + address + '&citystatezip='+cityzip[:-5]
        print(zillowURL)
        r = requests.get(zillowURL)
        soup = BeautifulSoup(r.text, features= 'lxml')
        #print(soup.prettify())
        status = soup.find('message')
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
                    print('SUCCESSFUL HOMESTEAD REPAIR')
            if 'UNINCORPORATED' in cityzip or cityzip[0] == ',':
                cityzip = 'MIAMI%2C+FL'
                zillowURL = 'http://www.zillow.com/webservice/GetSearchResults.htm?zws-id=' + ZWSID + '&address=' + address + '&citystatezip=' + cityzip
                r = requests.get(zillowURL)
                soup = BeautifulSoup(r.text, features='lxml')
                # print(soup.prettify())
                status = soup.find('message')
                errorcode = int(soup.find('code').text)
                if errorcode == 0:
                    print('SUCCESSFUL UNINCORPORATED REPAIR')
        if errorcode == 0:
            soup = soup.find('zestimate')
            zestimate = soup.find('amount').text
            high = soup.find('high').text
            low = soup.find('low').text
            if len(zestimate) > 0:
                zestimate = [int(low),int(zestimate),int(high)]
                M.zestimate.append(zestimate)
            else:
                M.zestimate.append([0,0,0])
                #print(zillowURL)
        elif errorcode == 7:
            print('\n')
            print('Zillow daily call limit hit')
            sleep(30000)
            get_Zestimate(address, cityzip)
        else:
            print(address)
            print(cityzip)
            print(status.text)
            print('ERROR CODE:' + str(errorcode))
            print('\n')
            print(soup.prettify())
            print('\n')
            print(r)
            print('\n')
            M.zestimate.append([0, 0, 0])
            print(zillowURL)


def writeCsv():

    defendants = []
    plaintiff = []

    for i in range(len(M.defendant[-1])):
        defendants.append(M.defendant[-1][i])

    for i in range(len(M.plaintiff[-1])):
        plaintiff.append(M.plaintiff[-1][i])

    defendants = str(defendants).replace(',', ' ')
    plaintiff = str(plaintiff).replace(',', ' ')

    finalJudge = M.finalJudge[-1].replace(',','')
    sale = M.sale[-1].replace(',','')
    zestimate = str(M.zestimate[-1][1]).replace(',','')
    assessed = M.assessed[-1].replace(',','')
    cityzip = M.cityzip[-1].replace(',',' ')
    pmax = M.pmax[-1].replace(',','')



    with open('./Data/Foreclosure.csv', 'a', newline = '', encoding='utf-8') as csvfile:

        writer = csv.writer(csvfile, delimiter = ',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)

        writer.writerow([M.date[-1],
                         M.caseN[-1],
                         M.AID[-1],
                         finalJudge,
                         M.parcelID[-1],
                         M.street[-1],
                         cityzip,
                         assessed,
                         pmax,
                         M.status[-1],
                         sale,
                         M.time[-1],
                         M.assoc[-1],
                         plaintiff,
                         defendants,
                         M.bed[-1],
                         M.bath[-1],
                         M.living[-1],
                         M.lot[-1],
                         zestimate,
                         M.docket_count[-1],
                         M.totalday[-1],
                         M.placeinline[-1]
                         ])


def populate_historic(oldest_d= None, recent_d = None, s = None, auto=False):

    testing = False
    updating = False
    freshstart = False
    responding = True

    while responding:

        if auto:
            response = '1'
        else:
            print('\n')
            print('Choose an Option')
            print('----------------')
            print('1 - Update')
            print('2 - Fresh Scan')
            print('3 - Continued Scan')
            print('4 - Troubleshooting')
            print('5 - Main Menu')
            response = input()

        if response == '1':
            if oldest_d is None:
                print('Foreclosure file is empty. Start a fresh scan? (y/n)')
                response2 = input()
                if response2 == 'y':
                    freshstart = True
                    responding = False
                else:
                    pass
            else:
                updating = True
                responding = False
        elif response == '2':
            print('Are you sure? This will overwrite existing file (y/n)')
            response2 = input()
            if response2 == 'y':
                freshstart = True
                responding = False
            else:
                print('Canceling request')
        elif response == '3':
            if oldest_d is None:
                print('Foreclosure file is empty. Start a fresh scan? (y/n)')
                response2 = input()
                if response2 == 'y':
                    freshstart = True
                    responding = False
                else:
                    pass
            else:
                responding = False
        elif response == '4':
            testing = True
            print('Enter a timedelta')
            try:
                testdelta = int(input())
                responding = False
            except:
                print('Must be an integer (1-5) - Try again')
        elif response == '5':
            exit()
        else:
            print('Invalid Response - Try again')
            print('\n')



    if updating:
        startdate = datetime.today()
        enddate = datetime.strptime(recent_d, '%m/%d/%Y')
        delta = (startdate - enddate).days
    elif testing:
        startdate = datetime.today() - timedelta(testdelta)
        delta = 1000000
    elif freshstart:
        with open('./Data/Foreclosure.csv', 'w', newline='') as csvfile:

            writer = csv.writer(csvfile, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)

            writer.writerow(['Date',
                             'Case Number',
                             'Auction ID',
                             'Final Judgment',
                             'Parcel ID',
                             'Street Address',
                             'City/ZIP',
                             'Assessed Value',
                             'Plaintiff Max Bid',
                             'Status',
                             'Sold Amount',
                             'Time Sold',
                             'Association',
                             'Plaintiff',
                             'Defendant',
                             'Beds',
                             'Bath',
                             'Living Area',
                             'Lot Size',
                             'ZEstimate',
                             'Docket Count',
                             'Day Count',
                             'Place in Line'
                             ])
        startdate = datetime.today()
        delta = 1000000
    else:
        startdate = datetime.strptime(oldest_d, '%m/%d/%Y')
        delta = 1000000

    print('Scan starting at',str(startdate))
    if updating:
        print('Scanning through', str(enddate))


    FRequestURL = "https://www.miamidade.realforeclose.com/index.cfm?zaction=AUCTION&Zmethod=UPDATE&FNC=LOAD&AREA=C&PageDir=0&doR=1&tx=1581711468971&bypassPage=0&test=1&_=1581711468726"
    for single_date in (startdate - timedelta(n) for n in range(delta)):
        print(single_date)
        YYYY=single_date.strftime("%Y-%m-%d")[0:4]
        MM=single_date.strftime("%Y-%m-%d")[5:7]
        DD=single_date.strftime("%Y-%m-%d")[8:10]
        DayURL = 'https://www.miamidade.realforeclose.com/index.cfm?zaction=AUCTION&Zmethod=DAYLIST&AUCTIONDATE=' + MM + '/' + DD + '/' + YYYY
        #print(DayURL)

        r = s.post(DayURL, data = Cookie)
        if 'START HERE' in r.text:
            login(s)
            r = s.post(DayURL, data=Cookie)
            print('LOGGED BACK IN')
        #print(DayURL)
        if len(r.text) > 19730:  #this filters out days with no Auctions at all - length of DayURL.text  is always bigger than 19730 if there is even one auction
            soup = BeautifulSoup(r.text, 'lxml')
            r=s.post(FRequestURL, data = Cookie)
            if "FORECLOSURE" in r.text:# this filters out days that are only TAX DEED auctions
                # print('\n\n                                                        DATA CHECK--------------------------------------------------------\n--------\n')
                ptext = soup.prettify()
                div = soup.find(id='ALB')
                div = str(div)[48:-6]
                #print(div)
                Tcount = str(div).count(',')+1
                print(Tcount)
                Tpages = math.ceil(Tcount / 10)
                rem = (Tcount) % 10
                if rem == 0:
                    rem = 10
                # print("\n"+str(single_date))
                for n in range(Tpages):
                    if n+1 == Tpages:
                        Pcount = rem
                    else:
                        Pcount = 10
                    # print(str(single_date)+": Checking pages " + str(n + 1) + "(" + str(Pcount) + " Items)")
                    # print(div)
                    AID = get_pages_AID(Pcount,div,n) # Returns list of AID for the given page
                    for x in range(len(AID)):
                        #single_date = datetime.strftime('%Y-%')
                        M.date.append(str(datetime.strftime(single_date,'%Y-%m-%d')))
                        M.AID.append(AID[x])
                        M.totalday.append(Tcount)
                        M.placeinline.append(n*10+x+1)
                        # print('AID: ' + str(AID[x]))
                        get_AIDUrl_data(AID[x], s)
                        get_AIDXHR_data(AID[x], s)
                        if M.status[-1][0] != 'CC':
                            get_bidder_data(AID[x], s)
                        else:
                            #print("No sale ")
                            M.bidder_count.append('N/A')
                        get_appraiser_data((M.parcelID[-1]))
                        if not testing:
                            get_docket_count(M.caseN[-1])
                        else:
                            M.docket_count.append('5')

                        if False:
                            pass
                        else: # M.plaintiff[-1][0][0].lower() == 'd' and M.sale[-1][0] == '$':     #float(M.finalJudge[-1][1:].replace(',','')) > 1000000:
                            print('\n\n**********************************' + str(single_date) + ":  Page # " + str(
                                n + 1) + " item number " + str(x + 1) + "*******************************************\n")
                            get_Zestimate(M.street[-1], M.cityzip[-1])
                            print("Case Number: " + M.caseN[-1])
                            print("Final Judgement: " + M.finalJudge[-1])
                            print("Parcel ID: " + M.parcelID[-1])
                            print("Street Address: " + M.street[-1])
                            print("City/Zip: " + M.cityzip[-1])
                            print("Assessed Value: " + M.assessed[-1])
                            print("Plaintiff Max bid: "+ M.pmax[-1])
                            print("Status: " + M.status[-1][0])
                            print("Sold for: " + M.sale[-1])
                            print("Time Sold: " + M.time[-1])
                            print("Auction ID: " + M.AID[-1])
                            print("Date: " + M.date[-1])
                            print("Beds: " + M.bed[-1])
                            print("Baths: " + M.bath[-1])
                            print('Living Area: ' + M.living[-1] + ' sqft')
                            print('Lot Size: ' + M.lot[-1] + ' sqft')
                            print('Zestimate: ' + "${:,.2f}".format(M.zestimate[-1][1]))
                            print('Assoc?:' + M.assoc[-1])
                            print('Docket Count:' + M.docket_count[-1])
                            #print("Legal description: " + M.legal[-1])
                            for i in range(len(M.defendant[-1])):
                                print("Defendant: " + str(M.defendant[-1][i]))
                            for i in range(len(M.plaintiff[-1])):
                                print("Plaintiff: " + str(M.plaintiff[-1][i]))
                            print("Association?: " + M.assoc[-1])
                            if not testing:
                                writeCsv()
                        #print("Defendants: " +  str(M.defendant[(n*10)+x]))
                        #populate_from_AIDUrl()
                        #print(AIDUrl)
            #else:
                #print(str(single_date) + " is a TAXDEED day")
        #else:
            #print("No Auctions on " + str(single_date))

def login(s):
    # Logging in
    LOGINpayload = {
        'ZACTION': 'AJAX',
        'ZMETHOD': 'LOGIN',
        'func': 'LOGIN',
        'USERNAME': 'Churchill54',
        'USERPASS': '159ne54'
    }
    NOTICEpayload = {
        'zaction': 'AJAX',
        'ZMETHOD': 'COM',
        'process': 'NOTICE',
        'func': 'ACCEPT',
        'showjson': 'false',
        'NID': 8045
    }

    MainURL = "https://www.miamidade.realforeclose.com/index.cfm?"


    r = s.post(MainURL, data=LOGINpayload)
    print(r.text)
    exit()
    # Clearing Notice, updating NID, and repeat till passed all notices
    r = s.post(MainURL, data=NOTICEpayload)
    NOTICEpayload.update({'NID': 9208})
    r = s.post(MainURL, data=NOTICEpayload)
    NOTICEpayload.update({'NID': 9299})
    r = s.post(MainURL, data=NOTICEpayload)
    NOTICEpayload.update({'NID': 9147})
    r = s.post(MainURL, data=NOTICEpayload)


LOGINpayload = {
    'ZACTION': 'AJAX',
    'ZMETHOD': 'LOGIN',
    'func': 'LOGIN',
    'USERNAME': 'Churchill54',
    'USERPASS': '159ne54'
}

NOTICEpayload = {
    'zaction': 'AJAX',
    'ZMETHOD': 'COM',
    'process': 'NOTICE',
    'func': 'ACCEPT',
    'showjson': 'false',
    'NID': 8045
}

def main(auto=False):

    try:
        DF = pd.read_csv('./Data/Foreclosure.csv', error_bad_lines=False, encoding='utf-8')
        DF = DF.drop_duplicates(subset=DF.columns.difference(['Docket Count']))
        DF['Date'] = pd.to_datetime(DF.Date)
        DF = DF.sort_values(by='Date', ascending=False)
        DF.to_csv('./Data/Foreclosure.csv', index=False, encoding='utf-8')
    except Exception as e:
        print('Excepting Date Sort & Duplicate drop in HistoricDataCollector')
        print(e)

    try:
        with open('./Data/Foreclosure.csv', newline='', encoding='utf-8') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',',
                                quotechar='|')
            dates = []
            rowlist = list(spamreader)
            mostrecent = rowlist[1][0]
            oldest = rowlist[-1][0]

        oldest_d = datetime.strftime(datetime.strptime(oldest, "%Y-%m-%d"), "%m/%d/%Y")
        recent_d = datetime.strftime(datetime.strptime(mostrecent, "%Y-%m-%d"), "%m/%d/%Y")

    except Exception as e:
        print(e)
        delta = 0
        today_d = datetime.strftime(datetime.today(), '%m/%d/%Y')
        recent_d = today_d
        oldest_d = None

    print('oldest:', oldest_d)
    print('recent:', recent_d)

    MainURL = "https://www.miamidade.realforeclose.com/index.cfm?"
    s = requests.Session()
    s.mount(MainURL, MyAdapter())

    headers = {
        'Referer': "https://www.miamidade.realforeclose.com",
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
    }

    #Logging in
    r = s.post(MainURL, data=LOGINpayload, headers = headers)
    print(r.text)
    exit()
    #Clearing Notice, updating NID, and repeat till passed all notices
    s.post(MainURL, data=NOTICEpayload)
    NOTICEpayload.update({'NID': 9208})
    s.post(MainURL, data=NOTICEpayload)
    NOTICEpayload.update({'NID': 9299})
    s.post(MainURL, data=NOTICEpayload)
    NOTICEpayload.update({'NID': 9147})
    s.post(MainURL, data=NOTICEpayload)

    populate_historic(oldest_d, recent_d, s, auto)


M = Fstruc()

if __name__ == "__main__":
    main()

