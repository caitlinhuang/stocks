#Caitlin Huang
#caitlinh
#section G

#learned from this tutorial:
#https://enlight.nyc/projects/stock-market-prediction/ 

from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import quandl
import sklearn
from sklearn.linear_model import LinearRegression
from sklearn import preprocessing

#forecasts stock prices 30 days into the future through linear regression
def forecast30Days(symbol):
    auth_tok = "c2V_sVydLtbotC8xN8sH"
    today = datetime.now()
    today = str(today)[:10]
    eightYearsAgo = str(int(today[:4]) - 8) + today[4:10]
    dataStocks = quandl.get("EOD/" + symbol, trim_start = eightYearsAgo,
    trim_end = today, authtoken=auth_tok)
    dataStocks = dataStocks[['Adj_Close']]
    predictionDays = 30 # predicting 30 days into future
    #label column with data shifted 30 units up to make a space for the data
    dataStocks['Prediction'] = dataStocks[['Adj_Close']].shift(-predictionDays) 
    X = np.array(dataStocks.drop(['Prediction'], 1))
    X = preprocessing.scale(X)
    priceForecast = X[-predictionDays:]
    X = X[:-predictionDays] #remove the number predicted from X
    y = np.array(dataStocks['Prediction'])
    y = y[:-predictionDays]
    (xTrain, xTest, yTrain,
    yTest) = sklearn.model_selection.train_test_split(X, y, test_size = 0.2)
    # Training
    clf = LinearRegression()
    clf.fit(xTrain,yTrain)
    # Testing
    confidence = clf.score(xTest, yTest)
    predictions = clf.predict(priceForecast)
    todayExact = datetime.now()
    days = pd.date_range(todayExact, todayExact + timedelta(29), freq='D')
    forecastPrices = pd.DataFrame({'date': days, 'Price': predictions})
    forecastPrices = forecastPrices.set_index('date')
    return forecastPrices