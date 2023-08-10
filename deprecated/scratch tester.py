import pandas as pd
import statsmodels.api as sm
import numpy as np
from DataCleanse import *
from ForeclosureScanner import *

file = 'preclean post populateforwadonrd.csv'

DF = pd.read_csv(file)

DF = cleanMaster(DF, aux=True)

timing.log('Done Cleaning', elapsed=True)
DF.to_csv('forward test.csv', index=False, encoding='utf-8')
DF = regrPredict('Sold Amount', DF)
DF = regrPredict('Status Binary', DF)
DF = regrPredict('Plaintiff Max Bid', DF)
DF.to_csv('PreFilter test.csv', encoding='utf-8')
DF = filterNotable(DF)
DF = DF.reset_index(drop=True)

DF.to_csv('Test with notable predictions.csv', encoding='utf-8', index=False)

uploadtrello(DF)