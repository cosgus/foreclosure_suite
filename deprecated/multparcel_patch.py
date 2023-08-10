import pandas as pd
import sys

df = pd.read_csv('./Data/Foreclosure.csv', error_bad_lines=False, encoding='utf-8')
mp_df = pd.DataFrame(columns=df.columns)


i=0
for index, data in df.iterrows():
    try:
        if data.loc['Parcel ID'][0] is 'M':
            mp_df.loc[index] = data
            i+=1
    except TypeError as e:
        pass

mp_df.to_csv('./Data/Multiparcel Master.csv', encoding='utf-8', index=False)
print('Found', str(i),'Multiple Parcel auctions')