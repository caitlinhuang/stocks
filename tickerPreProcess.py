#Caitlin Huang
#caitlinh
#section G

import pandas as pd
import os

#load the ticker and company name mapping file
#and get company name by ticker
def getCompanyName(file, tickerIn):
    df = pd.read_csv(file)
    df.set_index('ticker', inplace=True)
    companyName = (df.loc[tickerIn]).values[0]
    return companyName

def insertCompanyName(file, tickerIn, companyNameIn):
    df = pd.read_csv(file)
    df.set_index('ticker', inplace=True)
    df.loc[tickerIn] = [companyNameIn]
    df.to_csv(file, index=True, header=True)