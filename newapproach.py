#Caitlin Huang
#caitlinh
#section G

from tkinter import *
import webScraper
import tkinter.messagebox
import datetime
import dateutil.relativedelta
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from stock import *

####################################
# customize these functions
####################################

#intializes variables like the stock symbol and date
def init(data):
    data.stockSym = ""
    data.now = datetime.datetime.now()
    endDateUncleaned = str(data.now)
    data.endDate = endDateUncleaned[:10]
    data.startDate = '1980-01-01'
    data.clickStockEntry = False
    data.timeFrameStatus = "Max"
    data.timeFrames = ["1 Week", "1 Month", "6 Months", "1 Year", "5 Years",
    "Max", "30 Day Prediction", "50 Day Prediction"]
    data.retrieving = False
    data.graphAvailable = False
    data.stock = None
    data.mouseOnGraph = False
    #parameters for where the mouse is pointing to on the figure
    (data.figX, data.figY) = (0, 0)
    data.action = 'yes'
    #photo from https://www.flickr.com/photos/pictures-of-money/16678606754
    data.pig = PhotoImage(file = "pig.png")
    #photo from 
    #https://www.vectorstock.com/royalty-free-vector/up-bull-market-rise-bullish-stock-chart-graph-vector-510738
    data.bullGraph = PhotoImage(file = "bull.png")
    data.bullGraph = data.bullGraph.subsample(2, 2)
    (data.scroll, data.scrollAmount) = (0, 30)
    (data.xStartButtons, data.yStartButtons) = (52, 95)
    (data.buttonHeight, data.buttonWidth) = (40, 75)
    data.numButtons = 8
    (data.chooseYes, data.chooseNo) = (False, False)
    data.score = 0
    data.term = None

#tracks which time periods the user wants to see
def mousePressedZoom(event, data):
    data.action = 'yes'
    if event.x > data.xStartButtons and \
    event.x < data.xStartButtons + (data.numButtons * data.buttonWidth) and \
    event.y > data.yStartButtons and \
    event.y < data.yStartButtons + data.buttonHeight:
        data.clickStockEntry = False
        indexZoomClick = (event.x - data.xStartButtons)//data.buttonWidth
        data.timeFrameStatus = data.timeFrames[indexZoomClick]
        setDates(data)
        data.stock.setStartDate(data.startDate)
        data.stock.setEndDate(data.endDate)
        data.stock.setTimeFrame(data.timeFrameStatus)
        data.stock.setPrice(data.stock.getPrices("Adj_Close"))
        data.stock.drawStockGraph()
        data.clickStockEntry = True

#sets the dates that the graph will display
def setDates(data):
    if data.timeFrameStatus == "1 Week":
        startDateUncleaned = str(data.now - datetime.timedelta(days = 7))
        data.startDate = startDateUncleaned[:10]
    elif data.timeFrameStatus == "1 Month":
        data.startDate = data.now - \
        dateutil.relativedelta.relativedelta(months = 1)
        data.startDate = str(data.startDate)
        data.startDate = data.startDate[:10]
    elif data.timeFrameStatus == "6 Months":
        data.startDate = data.now - \
        dateutil.relativedelta.relativedelta(months = 6)
        data.startDate = str(data.startDate)
        data.startDate = data.startDate[:10]
    elif data.timeFrameStatus == "1 Year" or data.timeFrameStatus == "5 Years":
        uncleanedNow = str(data.now)
        currYear = int(uncleanedNow[:4])
        if data.timeFrameStatus == "1 Year":
            data.startDate = str(currYear - 1) + uncleanedNow[4: 10]
        else:
            data.startDate = str(currYear - 5) + uncleanedNow[4: 10]
    elif data.timeFrameStatus == "Max":
        data.startDate = "1980-01-01"
    elif data.timeFrameStatus == "30 Day Prediction" or \
    data.timeFrameStatus == "50 Day Prediction":
        startDateUncleaned = str(data.now - datetime.timedelta(days = 7))
        data.startDate = startDateUncleaned[:10]

#general mouse pressed that checks if the user is 
#in the areas that demand change on the screen            
def mousePressed(event, data):
    data.action = 'yes'
    if event.x > data.width/2 - 100 and event.x < data.width/2 + 100 and \
    event.y > 40 and event.y < 60:
        data.clickStockEntry = True
    elif event.x > 1000 and event.x < 1180 and event.y > 225 and event.y < 325:
        data.chooseYes = True
        data.score += data.stock.moneyMade()
    elif event.x > 1000 and event.x < 1180 and event.y > 360 and event.y < 460:
        data.chooseNo = True
        data.score -= data.stock.moneyMade()
    mousePressedZoom(event, data)

#tracks mouse movements on the graph so that 
#the stock price can be displayed where the user's mouse is
def mouseMovement(event, data):
    data.term = None
    if event.y > 171 and event.y < 404 and event.x > 135 and event.x < 612:
        data.action = 'yes'
        data.figX = event.x
        data.figY = event.y
        data.mouseOnGraph = True
    elif event.y > 150 and event.y < 165 and event.x < 1095 and event.x > 1060:
        data.action = "yes"
        data.term = "CD"
    elif event.y > 165 and event.y < 178 and event.x < 1170 and event.x < 1030:
        data.action = "yes"
        data.term = "APR"
    elif event.x > 60 and event.x < 240 and event.y < 575 and event.y > 565:
        data.action = "yes"
        data.term = "50"
    elif event.x > 60 and event.x < 240 and event.y < 605 and event.y > 595:
        data.action = "yes"
        data.term = "200"
    elif event.x > 60 and event.x < 100 and event.y < 635 and event.y > 625:
        data.action = "yes"
        data.term = "vol"

#allows the user to type in the stock symbol
def keyPressed(event, data):
    data.action = 'yes'
    if data.clickStockEntry == True:
        if event.keysym == "BackSpace":
            if len(data.stockSym) > 0:
                data.stockSym = data.stockSym[: -1]
        elif event.keysym == "Up":
            data.scroll -= data.scrollAmount
            if data.scroll <= 0:
                data.scroll = 0
        elif event.keysym == "Down":
            data.scroll += data.scrollAmount
            if data.scroll >= 8 * data.stock.newsLines:
                data.scroll = 8 * data.stock.newsLines
        elif event.keysym != "Return" and event.keysym != "BackSpace" and \
        len(data.stockSym) < 25:
            data.stockSym += event.char
        elif event.keysym == "Return":
            data.retrieving = True
            data.chooseNo = False
            data.chooseYes = False
            data.scroll = 0
            isValidStockSym(data)

#tries to make a Stock object. If the user typed something 
#that is invalid, there is a warning message
def isValidStockSym(data):
    try:
        data.stock = Stock(data.stockSym, data.startDate, data.endDate,
        data.timeFrameStatus)
        if (data.stock.company == None):
            data.stock.setCompany()
        data.stock.drawStockGraph()
    except Exception as e:
        print("Exception:", str(e))
        invalidStockSym(data)

def timerFired(data):
    pass

#displays a warning message        
def invalidStockSym(data):
    #global canvas
    tkinter.messagebox.showwarning("Warning", 
    "The Stock Symbol is invalid! Please try again.")

#draws buttons, statistics, graphs
def redrawAll(canvas, data):
    if data.stock != None:
        drawZoomButtons(canvas, data)
        data.stock.drawStockFigure(canvas)
        data.stock.drawStockAnalysisFigure(canvas)
        data.stock.drawStockNewsFigure(canvas, data.scroll)
        data.stock.drawNewsStats(canvas)
        if data.mouseOnGraph == True:
            data.stock.drawPricesAndDate(canvas, data.figX, data.figY)
        data.stock.drawAdvisor(canvas, data.chooseYes, data.chooseNo)
        canvas.create_text(1090, 600,
        text = "Score: $ " + str(round(data.score, 2)), font = "Arial 30 bold")
    else:
        #draws start page items
        canvas.create_rectangle(100, 100, data.width - 100, data.height - 100,
        outline = "white", fill = "white")
        canvas.create_text(data.width/2, 150, text = "Stockometer",
        fill = "purple", font = "Symbol 45 bold")
        canvas.create_image(data.width/2, data.height/4, image = data.pig,
        anchor = NW)
        canvas.create_image(150, data.height/4, image = data.bullGraph,
        anchor = NW)
    drawSearchBars(canvas, data)
    drawUserInput(canvas, data)
    drawDefinitions(canvas, data)
    data.action = 'no'
    
def drawDefinitions(canvas, data):
    if (data.chooseYes == True or data.chooseNo == True) and \
    data.stock.buy == False:
        if data.term == "CD":
            drawCDDef(canvas, data)
        elif data.term == "APR":
            defn = "The effective annual rate of return "
            defn = defn + "taking in account compounding interest"
            canvas.create_rectangle(1000, 120, 1180, 165, fill = "white",
            outline = "DarkOrchid3", width = 4)
            canvas.create_text(1003, 123, text = defn, anchor = NW,
            font = "Times 12 italic", width = 175)
    elif data.stockSym != None:
        y = 0
        if data.term == "50" or data.term == "200" or data.term == "vol":
            if data.term == "50":
                y = 500
                defn = "The average closing price over the last 50 days"
            elif data.term == "200":
                y = 530
                defn = "The average closing price over the last 200 days"
            else:
                defn = "The measure of the range of values of returns"
                defn = defn + " of a security."
                y = 560
            canvas.create_rectangle(45, y, 200, y + 60, fill = "white",
            outline = "DarkOrchid3", width = 4)
            canvas.create_text(50, y + 3, text = defn, anchor = NW,
            font = "Times 14 italic", width = 145)
        
def drawCDDef(canvas, data):
    #referenced https://www.bankrate.com/glossary/c/certificate-of-deposit/
    defn = "A CD (certificate of deposit) is a kind of savings account that"
    defn = defn + " restricts your access to the money you invest but has "      
    defn = defn + "higher interest rates than those of regular savings"
    defn = defn + " accounts. The deposit gains value over a period of time"
    defn = defn + " that was agreed upon."
    canvas.create_rectangle(1000, 30, 1180, 145, 
    fill = "white", outline = "DarkOrchid3", width = 4)
    canvas.create_text(1003, 33, text = defn, anchor = NW,
    font = "Times 12 italic", width = 175)
        
def drawZoomButtons(canvas, data):
    timespans = ["1 Week", "1 Month", "6 Months", "1 Year", "5 Years", 
    "Max", "30-day\nForecast", "50-day\nForecast"]
    for i in range(data.numButtons):
        color = "khaki1"
        if data.timeFrameStatus == data.timeFrames[i]:
            color = "forest green"
        canvas.create_rectangle(data.xStartButtons + i * data.buttonWidth,
        data.yStartButtons, data.xStartButtons + (i + 1) * data.buttonWidth,
        data.yStartButtons + data.buttonHeight, 
        fill = color, outline = "grey", width = 3)
        canvas.create_text(data.xStartButtons + data.buttonWidth/2 + data.buttonWidth * i, 
        data.yStartButtons + data.buttonHeight/2, text = timespans[i])
    
def drawSearchBars(canvas, data):
    canvas.create_text(data.width/2 - 200, 50, 
    text = "Enter a stock ticker symbol")
    canvas.create_rectangle(data.width/2 - 100, 40, data.width/2 + 100, 60, 
    outline = "green2", fill = "white", width = 4)
    
def drawUserInput(canvas, data):
    canvas.create_text(data.width/2, 50, text = data.stockSym)

# I added mouseMovement and referenced 
#https://stackoverflow.com/questions/22925599/mouse-position-python-tkinter and
#the 15112 website!
####################################
# use the run function as-is
####################################

def run(width=300, height=300):
    def redrawAllWrapper(canvas, data):
        if(data.action == 'yes'):
            canvas.delete(ALL)
        #deal with this part. tkinter documentation. 
        #canvas.delete() add or delete certain tags.
        #canvas.create_rectangle(0, 0, data.width, data.height,
                                #fill='white', width=0)
            redrawAll(canvas, data)
            canvas.update()    

    def mousePressedWrapper(event, canvas, data):
        mousePressed(event, data)
        redrawAllWrapper(canvas, data)
        
    def mouseMovementWrapper(event, canvas, data):
        mouseMovement(event, data)
        redrawAllWrapper(canvas, data)

    def keyPressedWrapper(event, canvas, data):
        keyPressed(event, data)
        redrawAllWrapper(canvas, data)

    def timerFiredWrapper(canvas, data):
        timerFired(data)
        redrawAllWrapper(canvas, data)
        # pause, then call timerFired again
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)
    # Set up data and call init
    class Struct(object): pass
    data = Struct()
    data.width = width
    data.height = height
    data.timerDelay = 100 # milliseconds
    root = Tk()
    root.resizable(width=False, height=False) # prevents resizing window
    init(data)
    # create the root and the canvas
    canvas = Canvas(root, width=data.width, height=data.height)
    canvas.configure(background = "deep sky blue", bd=0, highlightthickness=0)
    canvas.pack()
    # set up events
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    canvas.bind("<Motion>", lambda event: mouseMovementWrapper(event, canvas,
    data))
    timerFiredWrapper(canvas, data)
    # and launch the app
    root.mainloop()  # blocks until window is closed
    print("bye!")

run(1250, 700)