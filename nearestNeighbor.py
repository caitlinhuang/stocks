#Caitlin Huang
#caitlinh
#section G

import csv
import pandas as pd
import math
import random
from datetime import datetime, timedelta
from scipy import stats
from scipy.optimize import curve_fit
import numpy

def antiError():
    columns = ["sentimentPositive", "relevance", "returnsClosePrevRaw1"]
    data = \
    pd.read_csv("/Users/caitlinhuang/Desktop/15112/termproject/marketDemoTrain.csv",
    names = columns)
    sent = data.sentimentPositive.tolist()[1:]
    rel = data.relevance.tolist()[1:]
    returns = data.returnsClosePrevRaw1.tolist()[1:]
    slopeSent = numpy.polyfit(numpy.array(sent).astype(float), numpy.array(returns).astype(float), 1)
    slopeRel = numpy.polyfit(numpy.array(rel).astype(float), numpy.array(returns).astype(float), 1)
    return slopeSent[0], slopeRel[1]

#the algorithm is nonweighted by default. The weights can be adjusted.
def nearestNeighbor(dataIn, steps, randomness, weights = [1]):
    weights = weights * (len(dataIn) - 1)
    train = \
    pd.read_csv("/Users/caitlinhuang/Desktop/15112/termproject/marketDemoTrain.csv")
    distance = list()
    #train
    for i in range(len(train.index)):
        individualDistance = 0
        for j in range(len(dataIn) - 1):
            individualDistance += (float(dataIn[j][1]) - train.iloc[[i],
            :].get(dataIn[j][0]).values[0])**2 * weights[j]
        distance.append(math.sqrt(individualDistance))
    minDistance = min(distance)
    minIndex = distance.index(minDistance)
    #scale the difference to the price of the stock you are comparing to and 
    #the stock price of the thing you are training with.
    difference = train.iloc[minIndex].get("returnsClosePrevRaw1") * \
    (dataIn[2]/train.iloc[minIndex].get("close"))
    predictions = list()
    prevValue = dataIn[-1] #last index is the predicted value
    slopeSent, slopeRel = antiError()
    weightedSlope = (slopeSent * weights[0] + slopeRel * \
    weights[1])/(weights[0] + weights[1])
    for i in range(steps):
        prevValue = prevValue + (weightedSlope * minDistance * difference) + \
        (random.random() * random.choice([-1, 1]) * randomness/10)
        predictions.append(round(prevValue, 2))
    todayExact = datetime.now()
    days = pd.date_range(todayExact, todayExact + timedelta(steps-1), freq='D')
    forecastPrices = pd.DataFrame({'date': days, 'Price': predictions})
    forecastPrices = forecastPrices.set_index('date')
    return forecastPrices
#gets error from the estimate of the nearest neighbor and takes that in account

def convertReturnsToDifferences(close1, close2, data):
    pass