#Caitlin Huang
#caitlinh
#section G

import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.backends.tkagg as tkagg
from matplotlib.backends.backend_tkagg import FigureCanvasAgg
from webScraper import *
from matplotlib.figure import Figure
import matplotlib.pyplot
import matplotlib.dates
import matplotlib.ticker
from tkinter import *
import string
import quandl
import time
import datetime
from newsPreProcess import newsPreProcess
import linearPrediction
import nearestNeighbor
import math
import dateutil.relativedelta
from tickerPreProcess import getCompanyName, insertCompanyName

#referenced https://matplotlib.org/gallery/user_interfaces/embedding_in_
#tk_canvas_sgskip.html, lib/matplotlib/backends/backend_tkagg.py,
# and the 15112 website

#a Stock object has a symbol, company, graph, prices,
#and start and end dates displayed
class Stock(object):
    #intializes the symbol, company, graph, prices, and dates
    def __init__(self, symbol, startDate, endDate, timeFrame):
        self.symbol = symbol
        self.company = None
        self.graph = None
        today = endDate.split('-')
        self.endTime = today[0] + today[1] + today[2]
        sDate = startDate.split('-')
        self.startTime = sDate[0] + sDate[1] + sDate[2]
        self.price = self.getPrices("Adj_Close")
        (self.sScore, self.rScore, self.newsTitles, 
        self.stories) = self.getStockNewsData()
        self.lowPrice = 0
        self.highPrice = 0
        self.early = 0
        self.recent = 0
        self.buy = True
        self.timeFrame = timeFrame
        self.yearStockData = None
        self.fiftyDayMovingAvg = 0
        self.twoHundredMovingAvg = 0
        self.dividend = 0
        self.volatility = self.getVolatility()

    #sets the company
    def setCompany(self):
        try:
            if self.company != None:
                return self.company
            self.company = getCompanyName('./cname/companyName.csv',
            self.symbol)
        except:
            uncleanedName = \
            parse_finance_page(str(self.symbol)).get("company_name")
            separatedName = uncleanedName.split(" ")
            name = ""
            for word in separatedName[:-7]:
                name += word + " "
            self.company = name
            insertCompanyName('./cname/companyName.csv', self.symbol,
            self.company)
        return self.company
    
    #draws a matplotlib graph on the canvas
    def drawStockFigure(self, canvas, loc=(50, 140)):
        self.chart = FigureCanvasAgg(self.figure)
        self.chart.draw()
        (self.chartX, self.chartY, self.chartWidth, 
        self.chartHeight) = (self.figure.bbox.bounds)
        (self.chartY, self.chartWidth) = (int(self.chartY), 
        int(self.chartWidth))
        self.display = PhotoImage(master = canvas, width = int(self.chartWidth), 
        height = int(self.chartHeight))
        canvas.delete(self.graph)
        self.graph = canvas.create_image(loc[0] + self.chartWidth/2,
            loc[1] + self.chartHeight/2, image = self.display)
        tkagg.blit(self.display, self.chart.get_renderer()._renderer,
        colormode = 2)

    #gets the stock prices depending on the dates, symbol, and fieldname
    def getPrices(self, fieldName):
        auth_tok = "c2V_sVydLtbotC8xN8sH"
        uncleanedDate = str(datetime.datetime.now())
        lstDate = uncleanedDate.split(" ")
        stockRawData = quandl.get("EOD/" + self.symbol,
            authtoken = auth_tok, collapse = "annually")
        if self.startTime == "19800101":
            pass
        elif int(self.endTime[:4]) - int(self.startTime[:4]) == 5:
            stockRawData = quandl.get("EOD/" + self.symbol,
            trim_start = self.startTime, trim_end = lstDate[0],
            authtoken = auth_tok, collapse = "monthly")
        else:
            stockRawData = quandl.get("EOD/"+ self.symbol, 
            trim_start = self.startTime, trim_end = lstDate[0],
            authtoken=auth_tok)
        self.dividend = stockRawData.get("Dividend")
        return stockRawData.get(fieldName)

    #sets up the graph
    def drawStockGraph(self):
        chart = matplotlib.pyplot.figure(facecolor = "green",
        figsize = (7, 4), dpi = 86)
        graph = matplotlib.pyplot.subplot(1, 1, 1)
        if self.timeFrame == "30 Day Prediction":
            forecast = linearPrediction.forecast30Days(self.symbol)
            graph.plot(forecast, label = "Forecasted 30-Day Closing Prices",
            linestyle = "-")
        elif self.timeFrame == "50 Day Prediction":
            #self.price = self.getPrices("Adj_Close")
            dataIn = [['sentimentPositive', self.sScore], ["relevance",
            self.rScore], self.price.iloc[-1]]
            forecast = nearestNeighbor.nearestNeighbor(dataIn, 50,
            self.volatility, [3, 1])
            graph.plot(forecast, label = "Forecasted 50-Day Closing Prices",
            linestyle = "-")
        else:
            #self.price = self.getPrices('Adj_Close')
            graph.plot(self.price, label = "Close Price", linestyle = '-')
        graph.grid(True, which = "major", axis = "both", color = "blue")
        graph.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(6))
        graph.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%Y-%m-%d"))
        labelsx = graph.get_xticklabels()
        matplotlib.pyplot.setp(labelsx, rotation=30, fontsize=9)
        matplotlib.pyplot.xlabel("Date", color = "blue", fontsize = 12)
        matplotlib.pyplot.ylabel("Prices", color = "blue", fontsize = 12)
        matplotlib.pyplot.title(self.company, color = "blue")
        self.lowPrice, self.highPrice = graph.get_ylim()
        self.early, self.recent = graph.get_xlim()
        matplotlib.pyplot.tight_layout()
        self.figure = chart
    
    #displays the price of where the user puts the mouse
    def drawPricesAndDate(self, canvas, x, y):
        highPixel = 171
        lowPixel = 404
        lowDatePix = 113 #135
        highDatePix = 613
        yChange = abs(y - lowPixel)
        difference = abs(self.highPrice - self.lowPrice)
        priceDisplay = (difference * yChange)/(lowPixel - highPixel)
        pixelsFromToday = abs(x - highDatePix)
        if priceDisplay < 0:
            priceDisplay = 0
        #high and low are everything on the whole graph
        forecast = 0
        if self.timeFrame == "30 Day Prediction":
            forecast = 30
        elif self.timeFrame == "50 Day Prediction":
            forecast = 50
        daysFromMax = round((pixelsFromToday * \
        (self.recent - self.early))/(highDatePix - lowDatePix))
        dateDisplay = str(datetime.datetime.today() - \
        datetime.timedelta(days = daysFromMax) +\
        datetime.timedelta(days = forecast))
        dateDisplay = dateDisplay[:10]
        canvas.create_text(x, y - 20, text = dateDisplay + ", " + \
        str(round(float(priceDisplay) + self.lowPrice, 2)))

    #displays the statistical analysis
    def drawStockAnalysisFigure(self, canvas, loc=(50,140)):
        canvas.create_rectangle(loc[0], loc[1] + 380,
        loc[0] + 250, loc[1] + 550, outline = "DarkOrchid3",
        fill = "white", width = 4)
        canvas.create_text((loc[0] + 10, loc[1] + 400),
        text = "Stock Statistics Analysis Data", anchor = W,
        font = "Symbol 16 bold")
        (self.fiftyDayMovingAvg, 
        self.twoHundredMovingAvg) = self.get50And200DayMovingAvg()
        canvas.create_text((loc[0] + 10, loc[1] + 430),
        text = "50-Day Moving Average: " + str(round(self.fiftyDayMovingAvg,
        2)),
        anchor = W)
        canvas.create_text((loc[0] + 10, loc[1] + 460),
        text = "200-Day Moving Average: " + str(round(self.twoHundredMovingAvg,
        2)),
        anchor = W)
        canvas.create_text((loc[0] + 10, loc[1] + 490),
        text = "Volatility: " + str(round(self.volatility, 3)), anchor = W)
        
    def getStockAnalysisData(self):
        pass
    
    #gets moving averages
    def get50And200DayMovingAvg(self):
        recentPrices = self.getPricesInOverOneYear('Adj_Close')
        last50 = recentPrices[-50:]
        fiftyMoveAvg = self.mean(last50)
        last200 = recentPrices[-200:]
        twoHundredMoveAvg = self.mean(last200)
        if fiftyMoveAvg < twoHundredMoveAvg:
            self.buy = False
        return fiftyMoveAvg, twoHundredMoveAvg
    
    #gets prices for statistical analysis because self.price
    #may skip certain numbers
    def getPricesInOverOneYear(self, fieldname):
        if self.yearStockData is not None:
            return self.yearStockData.get(fieldname)
        auth_tok = "c2V_sVydLtbotC8xN8sH"
        uncleanedDate = str(datetime.datetime.now())
        uncleanedStart = str(datetime.datetime.now() - \
        dateutil.relativedelta.relativedelta(months = 14))
        end = uncleanedDate[:10]
        start = uncleanedStart[:10]
        year = quandl.get("EOD/"+ self.symbol, trim_start = start,
        trim_end = end, authtoken=auth_tok)
        self.yearStockData = year
        return year.get(fieldname)
        
    #calculates the volatility for the stock prices
    def getVolatility(self):
        recentPrices = self.getPricesInOverOneYear('Adj_Close')
        volatility = list()
        avgTradingDaysInYear = 252
        for i in range(avgTradingDaysInYear):
            volatility.append(math.log(recentPrices[-(avgTradingDaysInYear - \
            i)]/recentPrices[-(avgTradingDaysInYear - i + 1)]))
        meanReturn = self.mean(volatility)
        deviations = list()
        for i in range(avgTradingDaysInYear):
            deviations.append(volatility[i] - meanReturn)
        #finding the variance
        squaresOfDeviations = list()
        for i in range(avgTradingDaysInYear):
            squaresOfDeviations.append(deviations[i]**2)
        sqDeviationsTotal = sum(squaresOfDeviations)
        variance = sqDeviationsTotal/(len(squaresOfDeviations) - 1)
        #volality is the square root of the variance
        self.volatility = 1000 * math.sqrt(variance)
        return self.volatility
    
    #does the name of the function. finds the mean
    def mean(self, lst):
        count = 0
        total = 0
        for item in lst:
            total += item
            count += 1
        return total/count
    
    #displays analysis of relevant news articles and the 
    #top 3 most relevant articles
    def drawStockNewsFigure(self, canvas, scroll):
        startNewsBoxX = 670
        startNewsBoxY = 95
        newsBoxWidth = 280
        newsBoxHeight = 400
        canvas.create_rectangle(startNewsBoxX, startNewsBoxY,
        950, startNewsBoxY + newsBoxHeight,
        outline = "DarkOrchid3", fill = "white", width = 4)
        newspaper = ""
        for i in range(len(self.stories)):
            newspaper = newspaper + \
            self.justifyText(self.stories[i], 38) + "\n" + ("_" * 45) + "\n"
        canvas.create_text(startNewsBoxX + 3, startNewsBoxY + 3 - scroll,
        text = newspaper, anchor = NW)
        #covers unneeded text when being scrolled
        canvas.create_rectangle(startNewsBoxX, 0, 950,
        startNewsBoxY - 3, outline = "deep sky blue", fill = "deep sky blue")
        canvas.create_rectangle(startNewsBoxX,
        startNewsBoxY + newsBoxHeight + 2, 1000, 700,
        outline = "deep sky blue", fill = "deep sky blue")
        self.drawTextBoxOutlines(canvas, startNewsBoxX, startNewsBoxY,
        newsBoxWidth, newsBoxHeight)
        
    def drawNewsStats(self, canvas):
        newsStatsX = 350
        newsStatsY = 520
        newsStatsWidth = 400
        newsStatsHeight = 170
        canvas.create_rectangle(newsStatsX, newsStatsY,
        950, newsStatsY + newsStatsHeight,
        outline = "DarkOrchid3", fill = "white", width = 4)
        sentimentText = "Sentiment = "+ str(float(self.sScore)/10)
        relevanceText = " Relevance = " + str(self.rScore)
        canvas.create_text(newsStatsX + 5, newsStatsY + 5,
        text = "NEWS SUMMARY:", anchor = NW, font = "Symbol 14 bold")
        canvas.create_text(newsStatsX + 122, newsStatsY + 3,
        text = sentimentText + relevanceText, anchor = NW)
        canvas.create_text(newsStatsX + 5, newsStatsY + 18,
        text = "Relevance and Sentiment are scored on a scale from 0 - 1.\n0 is least relevant and most negative sentiment.\n1 is most relevant and most positive sentiment.", anchor = NW)
        canvas.create_text(newsStatsX + 5, newsStatsY + 70,
        text = "News Titles: ", anchor = NW, font = "Symbol 14 bold")
        titles = ""
        for i in range(len(self.newsTitles)):
            titles = titles + self.justifyText(self.newsTitles[i], 90) + "\n"
        canvas.create_text(newsStatsX + 5, newsStatsY + 85, text = titles,
        anchor = NW)
    
    def drawAdvisor(self, canvas, yes, no):
        if yes == False and no == False:
            canvas.create_rectangle(980, 95, 1200, 495, fill = "white",
            outline = "DarkOrchid3", width = 4)
            canvas.create_text(985, 100,
            text = "Do you think\nyou should buy\nthe stock? Click\nyes or no.",
            anchor = NW, fill = "gold", font = "Symbol 22 bold")
            canvas.create_rectangle(1000, 225, 1180, 325, fill = "green")
            canvas.create_text(1090, 275, text = "YES", fill = "gold",
            font = "Symbol 16 bold")
            canvas.create_rectangle(1000, 360, 1180, 460, fill = "red")
            canvas.create_text(1090, 410, text = "NO", fill = "gold",
            font = "Symbol 16 bold")
        else:
            text = ""
            if self.buy == False:
                text = text + "You should not buy the stock because\n" 
                if self.fiftyDayMovingAvg < self.twoHundredMovingAvg:
                    text = text + "the fifty day moving average is less than the\ntwo hundred day moving average.\n"
                    text = text + "This is known as the death cross. This\n"
                    text = text + "indicates that stock prices will decrease."
                text = text + "You are estimated a return of "
            
        
    def drawTextBoxOutlines(self, canvas, x, y, width, height):
        canvas.create_line(x, y, x + width, y, fill = "DarkOrchid3", width = 4)
        canvas.create_line(x + width, y, x + width, y + height,
        fill = "DarkOrchid3", width = 4)
        canvas.create_line(x, y, x, y + height, fill = "DarkOrchid3", width = 4)
        canvas.create_line(x, y + height, x + width, y + height,
        fill = "DarkOrchid3", width = 4)

    #searches in the dataset for articles relevant to the company and calls a 
    #function that does analysis on the sentiment and relevance
    def getStockNewsData(self):
        companyName = ''
        if(self.company==None):
            companyName = self.setCompany()
        else:
            companyName = self.company
        companyNameList = companyName.split(" ")
        keyWord01 = ' '+companyNameList[0]+' '
        if len(companyNameList) > 1:
            keyWord02 = ' ' + companyNameList[0] + ' ' + \
            companyNameList[1] + ' '
        else:
            keyWord02 = ' '
        (sScore, rScore, newsTitles,
        stories) = newsPreProcess("./news/Full-Economic-News-DFE-839861.csv",
        keyWord01, keyWord02, self.startTime, self.endTime)
        return sScore, rScore, newsTitles, stories
    
    #modified version of justify text from HW 3
    def justifyText(self, text, width):
        #returns a string with same width on each line
        justified = ""
        text = self.antiParagraphBreak(text)
        #slice lines from the text while it is greater than the width
        while len(text) > width:
            for c in range(width, 0, -1):
                if text[c].isspace():
                    line = text[0: c]
                    text = text[c + 1:]
                    break
            justified = justified + line + "\n"
        justified = justified + text
        return justified

    def antiParagraphBreak(self, text):
        #gets rid of paragraph break characters in text
        newText = ""
        for word in text.split("</br></br>"):
            newText += word.strip()
            newText += " "
        return newText[: -1] #gets rid of extra space at the end

    def __eq__(self,other):
        return isinstance(other,Stock) and self.symbol==other.symbol

    """def __hash__(self):
        hash((self.symbol))"""