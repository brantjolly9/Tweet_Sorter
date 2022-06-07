
from math import sqrt
from statistics import stdev, mean
# import statsmodels.api as sm
# from statsmodels.formula.api import ols
# import numpy as np
import pandas as pd
# import pingouin as po


# dataframe = pd.read_csv('data.csv')
# country1 = dataframe['Country1']
# country2 = dataframe['Country2']
# country3 = dataframe['Country3']
# # a = po.anova(data=dataframe,between='Country1' )


# for col in dataframe.columns:
#     std = stdev(dataframe[col])
#     m = mean(dataframe[col])
#     print(m)
#     print(std)
# print(dataframe)

# model = ols('model ~ Country1 + Country2 + Country3', data=dataframe).fit()
# result = sm.stats.anova_lm(model, type=2)
# print(result)
# o = sm.stats.anova_oneway(dataframe, groups=['Country1', 'Country2', 'Country3'])
# print(o)

answers = [

"yes",
"yes",
"no",
"yes",
"yes",
"yes",
"yes",
"yes",
"yes",
"yes",
"yes",
"yes",
"yes",
"yes",
"no",
"yes",
"yes",
"yes",
"yes",
"yes",
"no",
"yes",
"yes",
"yes",
"yes",
"yes",
"no",
"no",
"yes",
"yes",
"yes",
"yes",
"yes",
"yes",
"no",
"yes",
"yes",
"no",
"yes",
"no",
"no",
"yes",
"yes",
"yes",
"yes",
"yes",
"no",
"yes",
"yes",
"yes",
"yes",
"no",
"no",
"no",
"no",
"yes",
"no",
"yes",
"no",
"yes",
"yes",
"no",
"no",
"no",
"yes",
"yes",
"yes",
"no",
"yes",
"yes",
"yes",
"yes",
"no",
"yes",
"no",
"yes",
"yes",
"yes",
"yes",
"yes",
"yes",
"yes",
"yes",
"no",
"no",
"yes",
"yes",
"yes",
"yes",
"yes",
"no",
"no",
"yes",
"yes",
"yes",
"no",
"no",
"yes",
"yes",
"no",
"no",
"yes",
"yes",
"yes",
"yes",
"yes",
"yes",
"yes",
"no",
"no",
"yes",
"yes",
"yes",
"yes",
"yes",
"no",
"no",
"no",
"yes",
"yes",
]
yesCount = answers.count('yes')
noCount = answers.count('no')
numAns = len(answers)

noProp = noCount/numAns
yesProp = yesCount/numAns

print(f'No Prop: {noProp.__round__(3)}')
print(f'Yes Prop: {yesProp.__round__(3)}')
print(f'Num Answers: {numAns}')

def calc_z_test(p, pHat, n):
    num = pHat - p
    den = sqrt((p*(1-p))/n)
    final = num/den
    return round(final, 3)

def marg_of_error(pHat, n, ci):
    if ci == 95:
        multiplyer = 1.96
    elif ci == 99:
        multiplyer = 2.58
    else:
        multiplyer = 1
        
    numerator = (pHat*(1-pHat))/n
    print(numerator)
    me = sqrt(numerator) * multiplyer
    me = round(me, 3)
    return me

p = float(input('P: '))
pHat = float(input('P Hat: '))
n = int(input('Sample Size: '))
ci = float(input('ci in whole num: '))
# z = calc_z_test(p, pHat, n)
# print(z)
me = marg_of_error(pHat, n, ci)
top = pHat + me
bot = pHat - me
print(f'top: {top}')
print(f'bot: {bot}')

print(f'ME: {me}')