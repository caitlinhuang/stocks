#Caitlin Huang
#caitlinh
#section G

import csv
import pandas as pd
import math
import random
from datetime import datetime, timedelta
from scipy import stats
import numpy

def antiError():
    columns = ["sentimentPositive", "relevance", "returnsClosePrevRaw1"]
    data = \
    pd.read_csv("/Users/caitlinhuang/Desktop/15112/termproject/marketDemoTrain.csv",
    names = columns)
    sent = data.sentimentPositive.tolist()
    rel = data.relevance.tolist()
    returns = data.returnsClosePrevRaw1.tolist()
    sent.sort()
    rel.sort()
    returns.sort()
    slopeSent = stats.linregress(numpy.array(sent), numpy.array(returns))[0]
    slopeRel = stats.linregress(numpy.array(rel), numpy.array(returns))[0]
    return slopeSent, slopeRel

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
            individualDistance += (dataIn[j][1] - train.iloc[[i],
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
    weightedSlope = (slopeSent * weight[0] + slopeRel * \
    weight[1])/(weight[0] + weight[1])
    for i in range(steps):
        prevValue = prevValue + (weightedSlope * minDistance) + difference + \
        (random.choice([-1,1]) * random.random())
        predictions.append(round(prevValue, 2))
    todayExact = datetime.now()
    days = pd.date_range(todayExact, todayExact + timedelta(steps-1), freq='D')
    forecastPrices = pd.DataFrame({'date': days, 'Price': predictions})
    forecastPrices = forecastPrices.set_index('date')
    return forecastPrices
#print(nearestNeighbor([['sentimentPositive', 0.18], ["relevance", 0.5], 179],
#30, 16, weights = [3, 1]))
#gets error from the estimate of the nearest neighbor and takes that in account


def convertReturnsToDifferences(close1, close2, data):
    pass