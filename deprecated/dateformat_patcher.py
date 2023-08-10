import pandas as pd
import sys


# This works to fix any errant date formatting in first column of a spreadsheet

df = pd.read_csv('Foreclosure.csv', error_bad_lines=False, encoding='utf-8')


for index, data in df.iterrows():
    print(len(data['City/ZIP'][-5:]))
    sys.exit()
    try:
        oldest = data.iloc[0]
        datetime.strftime(datetime.strptime(oldest, '%Y-%m-%d'), "%m/%d/%Y")
    except:
        oldest = datetime.strftime(datetime.strptime(oldest, "%m/%d/%Y"), "%Y-%m-%d")
        df.loc[index, 'Date'] = oldest

df.to_csv('Foreclosure.csv', encoding='utf-8', index=False)
