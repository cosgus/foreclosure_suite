import pandas as pd
from datetime import datetime
import zillow_api

from time import sleep
from fake_useragent import UserAgent
from random import randint
#  THIS SCRIPT REPAIRS THE MASTER FORECLOSURE.CSV
#
#  The master file originally scraped zillow estimates from the date of sraping
#  the script should have found the value of ZEstimate on the date of the auction
#  this script repairs the master data file so that it has the appropriate ZEstimate date
#
#  This data is not available through API


def repair_fixed_csv():
    df = pd.read_csv('./backups&test/zestimatepatch-test.csv', error_bad_lines=False, encoding = 'utf-8')

    ua = UserAgent()

    master_df1 = pd.read_csv('./Data/Foreclosure.csv', error_bad_lines=False, encoding='utf-8')

    print('Original master length:', str(len(master_df1)))

    recent_date=(df.loc[len(df)-1,'Date'])
    master_df = master_df1[master_df1['Date'] <= recent_date]
    print('Master length with dates past', recent_date+':',str(len(master_df)))
    print('\n')
    master_df.reset_index(drop=True)

    print('Length of fixed df:',len(df))
    df = pd.concat([df, master_df], sort=False)
    print('Length of concatenated df:', len(df))
    print('\n')
    print('Discrepancy:', len(df)-len(master_df1))
    print('\n')

    df = df.drop_duplicates(subset=df.columns.difference(['fixed', 'ZEstimate']))
    master_df1 = master_df1.drop_duplicates(subset=master_df1.columns.difference(['ZEstimate']))
    print('Len of concat df after duplicate drop:',str(len(df)))
    print('Difference between concat and original master:', str(len(master_df1)-len(df)))
    diff_df = pd.concat([df, master_df1], sort=False).drop_duplicates(subset=df.columns.difference(['fixed', 'ZEstimate']), keep=False)

    print(len(diff_df))

    if len(master_df1) == len(df):
        print('OK to write')
        df.to_csv('./backups&test/zestimatepatch-test.csv', index=False, encoding='utf-8')
    print()
    exit()


def main():

    df = pd.read_csv('./backups&test/zestimatepatch-test.csv', error_bad_lines=False, encoding='utf-8')

    ua = UserAgent()

    try:
        i = 0
        for index, data in df.iterrows():

            if df.loc[index, 'fixed'] == 'Yes':
                pass
            else:
                print(data['Date'],data['Street Address'])
                sleep(randint(2,7)/10)
                zpid = (zillow_api.get_zpid(data))

                if not zpid:
                    df.loc[index, 'fixed'] = 'Yes'
                    continue

                historic_z = zillow_api.historic_zdata(zpid, ua)

                print(historic_z)
                for item in historic_z:
                    datestamp = datetime.fromtimestamp(item['x']/1000).strftime('%b%Y')
                    if datestamp == datetime.strptime(data['Date'],"%Y-%m-%d").strftime('%b%Y'):
                        zestimate = item['y']
                        df.loc[index, 'ZEstimate'] = zestimate
                df.loc[index, 'fixed'] = 'Yes'
                i+=1
                if i % 50 == 0:
                    df.to_csv('./backups&test/zestimatepatch-test.csv', encoding='utf-8', index=False)

        df.to_csv('./backups&test/zestimatepatch-test.csv', encoding='utf-8', index=False)

    except:
        print('RECURSION')
        df.to_csv('./backups&test/zestimatepatch-test.csv', encoding='utf-8', index=False)
        main()


if __name__ == '__main__':
    main()