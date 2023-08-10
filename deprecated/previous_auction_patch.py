import pandas as pd
from datetime import  datetime

# This script takes the cleansed master data file and repairs the 'Previous Auction' column.

df = pd.read_csv('./Data/MASTER DATA - Cleansed.csv', error_bad_lines=False, encoding='utf-8')

for index, data in df.iterrows():

    try:
        timeSeries = pd.to_datetime(df['Date'], format='%Y-%m-%d')
    except ValueError:
        # print('exception')
        df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')
        timeSeries = pd.to_datetime(df['Date'], format='%Y-%m-%d')

    df['Date'] = timeSeries

    today = datetime.today()
    enddate = data['Date']

    masterdf = (df[df['Date'] < enddate])
    masterdf = masterdf.set_index('Case Number')

    casen = data['Case Number']

    try:
        df.loc[index, 'Previous Auctions'] = len(masterdf.loc[casen, 'Previous Auctions'])
    except TypeError:
        df.loc[index, 'Previous Auctions'] = 1
    except KeyError:
        df.loc[index, 'Previous Auctions'] = 0

    print(str(index+1)+':', 'Number of previous auctions:', str(df.loc[index, 'Previous Auctions']))

df.to_csv('./Data/MASTER DATA - Cleansed.csv', index=False, encoding='utf-8')