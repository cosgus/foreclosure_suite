import pandas as pd
import statsmodels.api as sm
import itertools
import os

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', -1)


i=0
wierdlist = []
for filename in os.listdir('./Data/Regression Data/'):



    df = pd.read_csv('./Data/Regression Data/'+filename, index_col=0)

    pickle_file = filename.replace('.csv', '.pickle')

    try:
        best_regr = sm.load('./Data/Collinearity Processed Data/pickles/' +pickle_file)
    except:
        print('ERREPRE')
        pass


    df = df.reset_index(drop=True)
    df = df.drop(['Date'], axis=1)

    print('\n')
    print('\n')
    print(filename)
    print('--------------------------------------')

    y = df[df.columns.values.tolist()[-1]]

    for label in df.columns:
        if label not in best_regr.params.index:
            df = df.drop([label], axis=1)


    columns = df.columns.values.tolist()
    ind_variables = columns

    collinearity_df = pd.DataFrame(columns=ind_variables,index=ind_variables)
    coeff_df = pd.DataFrame(columns=ind_variables,index=ind_variables)

    max_vif = 0
    max_pair = []

    for pair in itertools.product(collinearity_df, repeat=2):
        regr = sm.OLS(df[pair[0]], df[pair[1]])
        regr = regr.fit()
        vif = 1/(1-regr.rsquared)
        if vif > max_vif and vif != float('inf'):
            max_vif = vif
            max_pair = pair
        coeff_df.loc[pair[0], pair[1]] = regr.rsquared
        collinearity_df.loc[pair[0], pair[1]] = vif

    try:
        df = df.drop([max_pair[0]], axis=1)
    except:
        pass
    X = df
    columns = df.columns.values.tolist()
    regr = sm.OLS(y, df)
    regr = regr.fit()
    print(coeff_df)
    print('\n')
    print(collinearity_df)
    print('\n')


    if max_vif > 10:
        print('Dropped:', str(max_pair[0]))
        regr = sm.OLS(y, df)
        regr = regr.fit()
        refining = True
        while refining:
            highestP = 0
            currentAdjR = regr.rsquared_adj
            # print(regr.summary())
            # print('\n')
            for key, value in regr.params.items():
                if regr.pvalues[key] > highestP:
                    highestP = regr.pvalues[key]
                    worstV = key
            try:
                print('Removing', worstV, str(highestP))
                columns.remove(worstV)
            except:
                pass

            X = df[columns]
            bestregr = regr
            regr = sm.OLS(y, X)
            regr = regr.fit()
            if regr.rsquared_adj < currentAdjR or len(regr.params) == 1:
                print('not!')
                refining = False

        X = df[columns]

        regr = sm.OLS(y, X)
        regr = regr.fit()

        for key, value in regr.params.items():
            print('Testing', key)
            currentAdjR = regr.rsquared_adj

            if regr.pvalues[key] > 0.05:

                columns.remove(key)
                X = df[columns]
                regr = sm.OLS(y, X)
                regr = regr.fit()

                if regr.rsquared_adj > currentAdjR:
                    print('2 - Removing', key)
                    bestregr = regr
                else:
                    midpoint = len(columns) // 2
                    columns = columns[0:midpoint] + [worstV] + columns[midpoint:]

        print(bestregr.summary())

        f = open('./Data/Collinearity Processed Data/' + filename.replace('csv', 'txt'), 'w')
        f.write(bestregr.summary().as_text())
        f.close()
        bestregr.save('./Data/Collinearity Processed Data/pickles/' + pickle_file)
        i+=1
        if len(best_regr.params) == 1:
            wierdlist.append(filename.replace('csv', 'txt'))


    else:
        print('Kept regression as is')
        f = open('./Data/Regression Results/Results_' + filename.replace('csv', 'txt'), 'w')
        f.write(regr.summary().as_text())
        f.close()
        regr.save('./Data/Collinearity Processed Data/pickles/' + pickle_file)
        if len(regr.params) == 1:
            wierdlist.append(filename.replace('csv', 'txt'))

print('Repaired', str(i), 'Regressions')

print('\n')
for wierd in wierdlist:
    print(wierd)