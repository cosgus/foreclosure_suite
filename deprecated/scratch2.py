import pandas as pd
import itertools
from DataCleanse import analyzeData
import os
import statsmodels.api as sm

def test_analysis():

    var = 'Plaintiff Max Bid'

    df = pd.read_csv('./Data/Regression Data/48_Months_'+var.replace(' ','')+'.csv', error_bad_lines=False, encoding='utf-8')

    df.reset_index(drop=True, inplace=True)
    cols = df.columns.values  # 16 columns


    lst = list(itertools.product([0, 1], repeat=len(cols)-3))

    for switch in lst:

        labels = list(cols[0:2])

        for index in range(len(switch)):
            if switch[index] == 1:
                labels.append(cols[index+2])

        labels.append(var)
        temp_df = df[labels]
        temp_df.name = str(switch).replace(',', '')
        if len(labels) > 3:
            analyzeData(temp_df, testing=True)


test_analysis()

path = './backups&test/analyzedata_test2_Status/pickles/'
best_r = 0

for filename in os.listdir(path):
    regr = sm.load(path + filename)

    regr = regr.model
    regr = regr.fit()
    if regr.rsquared > best_r:
        best_r = regr.rsquared
        best_n = filename
        print(regr.summary())

print('\n')
print(best_n)