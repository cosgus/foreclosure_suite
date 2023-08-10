import pandas as pd
from DataCleanse import timeFilterData
import itertools



def regPrep(DF, iVar, dVar=None, third=False, single=False, condo=False, plaintiff=False, zeroz = False):

    name = DF.name

    filename = name+'_'+iVar.replace(' ','')

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

    if dVar == None:
        categories = []
        categories.append(iVar)
        if iVar == 'Sold Amount':
            DF = DF.drop(['Plaintiff Max Bid', 'Status Binary', 'Time Sold'], axis=1)  #Time Sold should be included - dropped temporarily
        if iVar == 'Plaintiff Max Bid':
            DF = DF.drop(['Sold Amount', 'Status Binary', 'Time Sold'], axis=1)
        if iVar == 'Status Binary':
            DF = DF.drop(['Plaintiff Max Bid','Sold Amount', 'Time Sold'], axis=1)
    else:
        if iVar == 'Sold Amount':
            DF = DF.drop(['Status Binary', 'Time Sold'], axis = 1)  #Time Sold should be included - dropped temporarily
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
        if not zeroz:
            categories.append('ZEstimate')
    elif zeroz:
        categories.append('Lot Size')
        categories.append('Living Area')
    else:
        categories.append('ZEstimate')


    dropped = []

    DF = DF.reset_index(drop=True)

    for index, data in DF.iterrows():# You should manually check that no good data is being tossed out with the bad
        for item in categories:
            try:
                float(data.loc[item])
                if pd.isna(data.loc[item]):
                    DF = DF.drop([index])
                    dropped.append(index)
                elif float(data.loc[item]) == 0 and iVar != 'Status Binary':
                    DF = DF.drop([index])
                    dropped.append(index)
            except:
                if index not in dropped:
                    DF = DF.drop([index])
                    dropped.append(index)
        if third:
            if '3rd' not in data.loc['Status'] and index not in dropped:
                DF = DF.drop([index])
                dropped.append(index)
        if plaintiff:
            if 'Plaintiff' not in data.loc['Status'] and index not in dropped:
                DF = DF.drop([index])
                dropped.append(index)
        if condo:
            if float(data.loc['Lot Size']) > 0 and index not in dropped:
                DF = DF.drop([index])
                dropped.append(index)
        if zeroz:
            if float(data.loc['ZEstimate']) == 0 and index not in dropped:
                DF = DF.drop([index])
                dropped.append(index)

    DF = DF.drop(['Status'], axis=1)

    if zeroz:
        DF = DF.drop(['ZEstimate'], axis=1)
    if condo:
        DF =DF.drop(['Lot Size'], axis=1)

    iVarColumn = DF.pop(iVar)

    DF[iVar] = iVarColumn
    dVar = None
    print('Preparing '+filename+ '.csv')
    DF.to_csv('./Data/Regression Data/Test/' + filename + '.csv', encoding='utf-8')

def classification_checker(values):
    if values[3] is True and values[3] == values[4]:
        return False
    elif values[2] is True and values[2] == values[5]:
        return False
    else:
        return True

def prepareSubData(DF):

    print('\nIn prepare sub data')

    periods = [6, 12, 18]

    params = {
        'iVar': ['Sold Amount', 'Status Binary', 'Plaintiff Max Bid'],
        'dVar': [None, ['Plaintiff Max Bid']],
        'third': [True, False],
        'single': [True, False],
        'condo': [True, False],
        'plaintiff': [True, False],
        'zeroz': [True, False]
    }

    keys = list(params)
    for period in periods:
        sixDF = timeFilterData(DF, period * 30)

        for values in itertools.product(*map(params.get, keys)):
            if classification_checker(values):
                sixDF.name = str(period)+"_Months"
                regPrep(sixDF, values[0], values[1], values[2], values[3], values[4], values[5], values[6])


DF = pd.read_csv('./Data/MASTER DATA - Cleansed.csv', encoding='utf-8', error_bad_lines=False)
DF = DF.drop(
    ['Plaintiff', 'Defendant', 'Case Number', 'Street Address', 'City/ZIP', 'Association', 'Parcel ID'],
    axis=1)
prepareSubData(DF)

