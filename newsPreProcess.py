#Caitlin Huang
#caitlinh
#section G

import math
import pandas as pd
import numpy as np
import os
import json

def isFloat(x):
    try:
        possFloat = float(x)
        if math.isnan(possFloat):
            return False
        else:
            return True
    except ValueError:
        return False

def convertDate(dateBeforeClean):
    year = dateBeforeClean.split('/')[2]
    month = dateBeforeClean.split('/')[1]
    day = dateBeforeClean.split('/')[0]
    if len(year) == 2 and int(year) < 40:
        year = '20'+year
    else:
        year = '19'+year
    if len(month) == 1:
        month = '0'+month
    if len(day) == 1:
        day = '0'+day
    return year+month+day

#calculates the average sentiment and relevancy of the articles to the company
#gets the most relevant article titles and content
def newsPreProcess(file, keyWord01, keyWord02, startDate, endDate):
    df = pd.read_csv(file,encoding='latin-1')
    df['mentioned'] = ''
    (sentimentScore, relevanceScore, newsTitlesCount)  = (0, 0, 0)
    newsTitles, stories = list(), list()
    (sCount, rCount) = (0, 0)
    for i in range(len(df.index)):
        text = df.iloc[[i], :].get('text').values[0]
        if (keyWord01 in text or keyWord02 in text):
            sentiment = df.iloc[[i], :].get('positivity').values[0]
            relevance = df.iloc[[i], :].get('relevance').values[0]
            if(isFloat(sentiment)):
                sentimentScore = float(sentiment) + sentimentScore
                sCount += 1
            if relevance == 'no': relevance = 0
            else:
                relevance = 1
                if (newsTitlesCount < 3):
                    newsTitles.append(df.iloc[[i], :].get('headline').values[0])
                    newsTitlesCount += 1
                    stories.append(df.iloc[[i], :].get("text").values[0])
            relevanceScore = float(relevance) + relevanceScore
            rCount += 1
    if(sCount != 0): sScore = format(sentimentScore/sCount,".2f")
    else: sScore = 0
    if(rCount != 0): rScore = format(relevanceScore/rCount,".2f")
    else: rScore = 0
    return sScore, rScore, newsTitles, stories
