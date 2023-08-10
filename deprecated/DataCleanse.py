import pandas as pd
import requests
import json
from datetime import timedelta, datetime
from itertools import islice
import os
import itertools
import statsmodels.api as sm
import csv
import numpy as np
import sys
import deprecated.timing as timing



# cleans the data in master csv to prepare it for sub-data.
#
# 1 - Fills Empty appraised value (previously collected from miamidade.realforeclose and sometimes empty.
# 2 - remove duplicates
# 3 - remove non-numeric data contained in columns that should only have
# numeric data. If non-numeric cells cant be filled then whole row is removed from data


def getAssessedValue(FOLIO):

    #print('In getAppraisedValue')
    FOLIO = FOLIO.replace('-', '')
    appraiserUrl = 'https://www.miamidade.gov/Apps/PA/PApublicServiceProxy/PaServicesProxy.ashx?Operation=GetPropertySearchByFolio&clientAppName=PropertySearch&folioNumber=' + FOLIO
    # print(type(FOLIO))
    # print(len(FOLIO))
    try:
        if len(str(FOLIO)) == 12:
            FOLIO = '0' + str(FOLIO)
        if len(str(FOLIO)) > 13:
            FOLIO = FOLIO[:13]
    except:
        return ('No Folio Available')
    r = requests.get(appraiserUrl)
    data = json.loads(r.text)
    data = data['Assessment']['AssessmentInfos'][0]
    appraisedvalue = data['AssessedValue']

    #print(appraisedvalue)

    if appraisedvalue == 0:
        return False
    else:
        return appraisedvalue


def removeNonNumeric(DF, label):
    pass


def timeFilterData(DF, period):

    #creates a new subset DataFrame from the master DF using only data points in within a certain amount of time from today (period # of days)

    print('\n')
    print('Filtering data:', str(round(period/30)), 'months')
    print('-------------------------')
    try:
        timeSeries = pd.to_datetime(DF['Date'], format='%Y-%m-%d')
    except ValueError:
        # print('exception')
        DF['Date'] = pd.to_datetime(DF['Date']).dt.strftime('%Y-%m-%d')
        timeSeries = pd.to_datetime(DF['Date'], format='%Y-%m-%d')

    DF['Date'] = timeSeries

    today = datetime.today()
    enddate = today + timedelta(days=-period)

    DF = (DF[DF['Date'] >= enddate])

    return DF


def regPrep(DF, iVar, dVar=None, third=False, single=False, condo=False, plaintiff=False, zeroz=False, log=False):

    name = DF.name

    filename = name+'_'+iVar.replace(' ','')

    DF = DF.drop(['Docket Count'], axis=1)

    if dVar != None:
        filename = filename + '_conditions_' + str(dVar)
    if third:
        filename = filename + '_3rd'
    if single:
        filename = filename + '_single'
    if condo:
        filename = filename + '_condo'
    if plaintiff:
        filename = filename + '_plaintiff'
    if zeroz:
        filename = filename + '_zeroz'
    if log:
        filename = filename + '_log'

    print('Preparing ' + filename + '.csv')

    if dVar is None:
        categories = []
        categories.append(iVar)
        if iVar == 'Sold Amount':
            DF = DF.drop(['Plaintiff Max Bid', 'Status Binary', 'Time Sold'], axis=1)  #Time Sold should be included - dropped temporarily
        if iVar == 'Plaintiff Max Bid':
            DF = DF.drop(['Sold Amount', 'Status Binary', 'Time Sold'], axis=1)
        if iVar == 'Status Binary':
            DF = DF.drop(['Plaintiff Max Bid', 'Sold Amount', 'Time Sold'], axis=1)
    else:
        if iVar == 'Sold Amount':
            DF = DF.drop(['Status Binary', 'Time Sold'], axis=1)  #Time Sold should be included - dropped temporarily
        if iVar == 'Plaintiff Max Bid':
            DF = DF.drop(['Sold Amount', 'Status Binary', 'Time Sold'], axis=1)
        if iVar == 'Status Binary':
            DF = DF.drop(['Sold Amount', 'Time Sold'], axis=1)
        categories = []
        for item in dVar:
            categories.append(item)
        categories.append(iVar)

    if single:
        categories.append('Lot Size')
        categories.append('Living Area')
        if not zeroz:
            categories.append('ZEstimate')
    elif condo:
        categories.append('Living Area')
        DF = DF.drop(['Association Binary'], axis=1)
        if not zeroz:
            categories.append('ZEstimate')
    elif zeroz:
        categories.append('Lot Size')
        categories.append('Living Area')
    else:
        categories.append('ZEstimate')


    DF = DF.reset_index(drop=True)

    DF = DF.dropna(subset=categories, axis=0)  # DROP 2

    if 'Status Binary' in categories:

        temp = categories
        temp.remove('Status Binary')

        DF = DF.replace(0, pd.np.nan).dropna(axis=0, subset=temp, how='any').fillna(0)
        DF.to_csv('testytesty2.csv')
    else:
        DF = DF.replace(0, pd.np.nan).dropna(axis=0, subset=categories, how='any').fillna(0)

    if zeroz:
        if 'ZEstimate' in categories:
            DF = DF.replace(0, pd.np.nan).dropna(axis=0, subset=categories.remove('ZEstimate'), how='any').fillna(0)
            categories.append('ZEstimate')
        else:
            DF = DF.replace(0, pd.np.nan).dropna(axis=0, subset=categories, how='any').fillna(0)
    else:
        DF = DF.replace(0, pd.np.nan).dropna(axis=0, subset=categories, how='any').fillna(0)

    if 'Plaintiff Max Bid' in categories:
        DF = DF[~DF['Plaintiff Max Bid'].str.contains('H')]

    if third:
        DF = DF[DF['Status'].str.contains('3rd')]

    if plaintiff:
        DF = DF[DF['Status'].str.contains('Plaintiff')]

    if condo:
        DF = DF[DF['Lot Size'] == 0]

    if zeroz:
        DF = DF[DF['ZEstimate'] == 0]

    DF = DF.drop(['Status'], axis=1)

    if zeroz:
        DF = DF.drop(['ZEstimate'], axis=1)
    if condo:
        DF = DF.drop(['Lot Size'], axis=1)

    if log:
        DF[iVar] = np.log(DF[iVar].astype('float64'))

    iVarColumn = DF.pop(iVar)

    DF[iVar] = iVarColumn
    DF.to_csv('./Data/Regression Data/' + filename + '.csv', encoding='utf-8')


def classification_checker(values):
    if values[3] is True and values[3] == values[4]:
        return False
    elif values[2] is True and values[2] == values[5]:
        return False
    elif values[1] == ['Plaintiff Max Bid'] and values[0] == 'Plaintiff Max Bid':
        return False
    elif values[0] == 'Status Binary' and values[2]:
        return False
    elif values[0] == 'Status Binary' and values[5]:
        return False
    elif values[0] == 'Status Binary' and values[7]:
        return False
    else:
        return True


def prepareSubData(DF):

    print('\nIn prepare sub data')

    periods = [48, 60]

    params = {
        'iVar': ['Sold Amount', 'Status Binary', 'Plaintiff Max Bid'],
        'dVar': [None, ['Plaintiff Max Bid']],
        'third': [True, False],
        'single': [True, False],
        'condo': [True, False],
        'plaintiff': [True, False],
        'zeroz': [True, False],
        'log': [True, False]
    }

    keys = list(params)

    for period in periods:
        sixDF = timeFilterData(DF, period * 30)
        for values in itertools.product(*map(params.get, keys)):
            if classification_checker(values):
                sixDF.name = str(period) + "_Months"
                regPrep(sixDF, values[0], values[1], values[2], values[3], values[4], values[5], values[6], values[7])

def fillNewData(DF, index):

    # Year Court date started, # of docket entries, Status Binary, # of defendants, # of previous auctions
    # print('In Fill Data')

    if DF.loc[index,'Case Number'][0:2] == '20':
        DF.loc[index, 'Court Year'] = DF.loc[index, 'Case Number'][0:4]
    else:
        DF.loc[index, 'Court Year'] = '20' + DF.loc[index, 'Case Number'][0:2]

    if DF.loc[index, 'Status'][0] == 'C':
        DF.loc[index, 'Status Binary'] = 0
    elif DF.loc[index,'Status'][0] == 'S':
        DF.loc[index, 'Status Binary'] = 1
    else:
        pass

    if DF.loc[index, 'Association'] == 'Y':
        DF.loc[index, 'Association Binary'] = 1
    elif DF.loc[index, 'Association'] == 'N':
        DF.loc[index, 'Association Binary'] = 0
    else:
        pass
    DF.loc[index, 'Defendant Count'] = DF.loc[index,'Defendant'].count('\'')/2

    masterDF = pd.read_csv('./Data/MASTER DATA - Cleansed.csv', error_bad_lines=False, encoding = 'utf-8')
    masterDF = masterDF.set_index('Case Number')

    casen = DF.loc[index, 'Case Number']

    try:
        DF.loc[index, 'Previous Auctions'] = len(masterDF.loc[casen, 'Previous Auctions'])
    except TypeError:
        DF.loc[index, 'Previous Auctions'] = 1
    except KeyError:
        DF.loc[index, 'Previous Auctions'] = 0

    return DF


def cleanMaster(DF=None, start=0, aux=False):

    # aux = True assumes that fillNewData has already been done when DF is incoming from another function

    if DF is None:
        # DF = pd.read_csv('./Data/Foreclosure - BACKUP.csv', error_bad_lines= False, encoding = 'utf-8')
        DF = pd.read_csv('./Data/Foreclosure.csv', error_bad_lines=False, encoding='utf-8')
        # DF = pd.read_csv('./Data/cleasetest.csv', error_bad_lines= False, encoding= 'utf-8')
        # DF = pd.read_csv('./Data/SixMonths - Master.csv', error_bad_lines= False, encoding = 'utf-8')

    logIndex = len(DF)

    DF = DF[DF.index > start]

    before = len(DF)

    DF = DF.drop_duplicates()
    DF = DF.replace({'\$':''}, regex=True)
    MP_DF = pd.DataFrame

    # This can be simplified - do all the drops through vectorization then iterate only for getAssessedValue(data)
    #
    # There are 6 drops
    # 3 of those drops can be combined - drop nan in subset ['Final Judgment', 'Parcel ID', 'Docket Count']  - First replace all 'N/A' with nan
    # 1 is drop MultiParcel folio
    # 1 is drop misc cant float parcel
    # 1 is drop if getAssessedValue returns False

    # DF = DF.dropna(subset=['Final Judgment', 'Parcel ID', 'Docket Count'], axis=0)
    for index, auction in islice(DF.iterrows(), start, None):

        print(auction.loc['Date'])

        if not aux:
            DF = fillNewData(DF, index)

        if pd.isna(auction.loc['Final Judgment']):
            DF = DF.drop([index])
            print('Dropping no Final judgment')
            continue

        if pd.isna(auction.loc['Parcel ID']) or auction.loc['Parcel ID'] == '' or auction.loc['Parcel ID'] == 'N/A':
            DF = DF.drop([index])
            print('Dropping bad Folio')
        else:
            try:
                float(auction.loc['Parcel ID'][0])
                assessedValue = getAssessedValue(auction.loc['Parcel ID'])
                if not assessedValue:
                    print('Dropping False assessed')
                    DF = DF.drop([index])
                else:
                    DF.loc[index, 'Assessed Value'] = assessedValue
            except:
                if str(auction.loc['Parcel ID'])[0:2] == 'MU':
                    # Should eventually load Multiple Parcel into a separate database
                    #
                    # Possibly categorize every
                    # MP_DF[index] = DF[index] # Broke during foreclosurescanner.py
                    DF = DF.drop([index])
                    print('Dropping MultiParcel')
                else:
                    DF = DF.drop([index])
                    print('Dropping misc couldnt float parcel id:', auction.loc['Parcel ID'])
        try:
            if pd.isna(auction.loc['Docket Count']) or auction.loc['Docket Count'] == 'N/A':
                DF = DF.drop([index])
                print('Dropping no docket count',auction.loc['Auction ID'])
        except KeyError:
            print('Not dropping NA')
            pass

    if not aux:
        try:
            print('TRYING -', index, logIndex)
            if index != 0:
                f = open('cleanse log.txt', 'w')
                f.write(str(logIndex))
                f.close()
        except:
            pass

    after = len(DF)

    if before == 0:
        pass
    else:
        print(after/before)
        print(before - after)

    return DF

def analyzeData(DF, constant = False, testing=False):

    # as it stands, this function does a regression and then removes failed p-tests one by one until the r_squared value decreases
    # the problem with this is that the next variable that might have been removed could possibly lead to an improved model
    # it should still check the other p-values even though removing the ˆworstˆ variable results in a decreased correlation

    #print('\n')
    #print(DF.name)

    if constant:
        DF.insert(DF.shape[1]-1, 'Constant', 1)

    try:
        DF.insert(DF.shape[1]-1, 'JoverZ', DF['Final Judgment']/DF['ZEstimate'])
    except:
        pass

    columns = DF.columns.values.tolist()

    if len(DF.index) < 14:
        return 0

    y = DF[columns[-1]]
    X = DF[columns[2:-1]]


    try:
        regr = sm.OLS(y, X)
    except:
        columns.remove('JoverZ')
        y = DF[columns[-1]]
        X = DF[columns[2:-1]]
        regr = sm.OLS(y, X)
    regr = regr.fit()
    refining = True
    highestP = 0
    #print('\n')
    print(regr.summary())


    while refining:
        i = 0
        for key, value in regr.params.items():
            if regr.pvalues[key] == 0:
                #columns.remove(key)
                if 'log' not in DF.name:
                    print('FOUND ZERO P VALUE', key)
                #i += 1
        y = DF[columns[-1]]
        X = DF[columns[2:-1]]
        regr = sm.OLS(y, X)
        regr = regr.fit()
        if i == 0:
            refining = False

    y = DF[columns[-1]]
    X = DF[columns[2:-1]]
    regr = sm.OLS(y, X)
    regr = regr.fit()
    refining = True

    while refining:
        highestP = 0
        currentAdjR = regr.rsquared_adj
        #print(regr.summary())
        #print('\n')
        for key, value in regr.params.items():
            if regr.pvalues[key] > highestP:
                highestP = regr.pvalues[key]
                worstV = key
        try:
            print(columns)
            if len(columns) > 4:
                print('Removing', worstV, str(highestP))
                columns.remove(worstV)
            elif len(columns) == 4:
                refining = False
        except:
            return 0
        y = DF[columns[-1]]
        X = DF[columns[2:-1]]
        bestregr = regr
        regr = sm.OLS(y, X)
        regr = regr.fit()
        if regr.rsquared_adj < currentAdjR:
            refining = False
            print('not!')
            # midpoint = len(columns)//2
            # columns = columns[0:midpoint] + [worstV] + columns[midpoint:]

    y = DF[columns[-1]]
    X = DF[columns[2:-1]]
    regr = sm.OLS(y, X)
    regr = regr.fit()

    for key, value in regr.params.items():
        print('Testing', key)
        currentAdjR = regr.rsquared_adj
        print(regr.pvalues[key])
        if regr.pvalues[key] > 0.05:

            columns.remove(key)
            y = DF[columns[-1]]
            X = DF[columns[2:-1]]

            regr = sm.OLS(y, X)
            regr = regr.fit()

            if regr.rsquared_adj > currentAdjR:
                print('2 - Removing', key)
                bestregr = regr
            else:
                midpoint = len(columns) // 2
                columns = columns[0:midpoint] + [key] + columns[midpoint:]

    if testing:
        try:
            f = open('./backups&test/analyzedata_test2_Status/Results_' + DF.name + '.txt', 'w')
            f.write(bestregr.summary().as_text())
            f.close()
            print('Pickling', DF.name)
            print('\n')
            bestregr.save('./backups&test/analyzedata_test2_Status/pickles/' + DF.name + '.pickle')
            return 0
        except:
            return 0
    else:
        try:
            f = open('./Data/Regression Results/Results_'+DF.name[0:-4]+'.txt','w')
            f.write(bestregr.summary().as_text())
            f.close()
            print('Pickling', DF.name[0:-4])
            print('\n')
            bestregr.save('./Data/Regression Results/pickles/' + DF.name[0:-4] + '.pickle')
        except:
            return 0


def main(auto=False):

    if auto:
        response = ''
    else:
        print('Start from Beginning?')

        response = input()

    if response == 'y':
        start = 0

        DF = cleanMaster()
        DF.to_csv('./Data/MASTER DATA - Cleansed.csv', index=False, encoding='utf-8')

    else:
        DF = pd.read_csv('./Data/Foreclosure.csv', error_bad_lines= False, encoding = 'utf-8')

        try:
            with open('./Data/MASTER DATA - Cleansed.csv', newline='', encoding='utf-8') as csvfile:
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

        DF_clean = pd.read_csv('./Data/MASTER DATA - Cleansed.csv')

        try:
            timeSeries = pd.to_datetime(DF['Date'], format='%Y-%m-%d')
        except ValueError:
            # print('exception')
            DF['Date'] = pd.to_datetime(DF['Date']).dt.strftime('%Y-%m-%d')
            timeSeries = pd.to_datetime(DF['Date'], format='%Y-%m-%d')

        DF['Date'] = timeSeries

        try:

            DF_top = (DF[DF['Date'] > recent_d])
            DF_top = cleanMaster(DF=DF_top)

        except:
            pass
        try:
            DF_bottom = (DF[DF['Date'] <= oldest_d])
            DF_bottom = cleanMaster(DF=DF_bottom)
            DF = pd.concat([DF_top, DF_clean, DF_bottom], sort=False)
            DF = DF.reset_index(drop=True)
            DF['Date'] = pd.to_datetime(DF['Date']).dt.strftime('%Y-%m-%d')

        except Exception as e:
            DF = pd.concat([DF_clean, DF_bottom], sort=False)
            DF = DF.reset_index(drop=True)
            DF['Date'] = pd.to_datetime(DF['Date']).dt.strftime('%Y-%m-%d')

        DF = DF.drop_duplicates()
        DF.to_csv('./Data/MASTER DATA - Cleansed.csv', index=False, encoding='utf-8')

    # I don't want to actually drop Plaintiff and Defendant data until after time filter (I dont remember why)
    DF = DF.drop(
        ['Plaintiff', 'Defendant', 'Case Number', 'Street Address', 'City/ZIP', 'Association', 'Parcel ID'],
        axis=1)

    DF.to_csv('./backups&test/PRESUBDATATEST.csv', index=False, encoding='utf-8')

    prepareSubData(DF)

    directory = './Data/Regression Data/'
    for filename in os.listdir(directory):
        DF = pd.read_csv(directory + filename)
        DF.name = filename
        analyzeData(DF)


if __name__ == "__main__":

    main()
