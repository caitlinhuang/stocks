#Caitlin Huang
#caitlinh
#section G

import csv
import pandas as pd
import math
import random
from datetime import datetime, timedelta

dataIn = [0.65, 0.18, 175]
#the algorithm is nonweighted by default. The weights can be adjusted.
def nearestNeighbor(dataIn, steps, randomness, weights = [1] * (len(dataIn) - 1)):
    train = \
    pd.read_csv("/Users/caitlinhuang/Desktop/15112/termproject/marketDemoTrain.csv")
    #sentiment receives a weight of 3. Relevancy receives a weight of 1
    distance = list()
    #train
    for i in range(len(train.index)):
        distance.append(math.sqrt((dataIn[0] - train.iloc[[i], 
        :].get('sentimentPositive').values[0])**2 * weights[0] \
         + ((dataIn[1] - train.iloc[[i],:].get("relevance"))**2 * weights[1])))
    minDistance = min(distance)
    minIndex = distance.index(minDistance)
    #scale the difference to the price of the stock you are comparing to and 
    #the stock price of the thing you are training with.
    difference = train.iloc[minIndex].get("returnsClosePrevRaw1") * \
    (dataIn[2]/train.iloc[minIndex].get("close"))
    predictions = list()
    prevValue = dataIn[-1] #last index is the predicted value
    for i in range(steps):
        # a momentum term is used to determine how long the increase will last
        prevValue = prevValue + difference + random.uniform(-randomness * 100,
        randomness * 100)
        predictions.append(round(prevValue, 2))
    todayExact = datetime.now()
    days = pd.date_range(todayExact, todayExact + timedelta(steps-1), freq='D')
    forecastPrices = pd.DataFrame({'date': days, 'Price': predictions})
    forecastPrices = forecastPrices.set_index('date')
    return forecastPrices

nearestNeighbor(dataIn, 30, 0.018, [1, 3])

def convertReturnsToDifferences(close1, close2, data):
    pass