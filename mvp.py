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
    data.figX = 0
    data.figY = 0
    data.action = 'yes'
    #photo from https://www.flickr.com/photos/pictures-of-money/16678606754
    data.pig = PhotoImage(file = "pig.png")
    data.pig = data.pig.subsample(2, 2)
    data.scroll = 0
    data.scrollAmount = 30
    data.xStartButtons = 52
    data.yStartButtons = 95
    data.buttonHeight = 40
    data.buttonWidth = 75
    data.numButtons = 8

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
        isValidStockSym(data)

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
    elif data.timeFrameStatus == "30 Day Prediction":
        data.startDate = data.endDate

#general mouse pressed that checks if the user is 
#in the areas that demand change on the screen            
def mousePressed(event, data):
    data.action = 'yes'
    if event.x > data.width/2 - 100 and event.x < data.width/2 + 100 and \
    event.y > 40 and event.y < 60:
        data.clickStockEntry = True
    mousePressedZoom(event, data)

#tracks mouse movements on the graph so that 
#the stock price can be displayed where the user's mouse is
def mouseMovement(event, data):
    if event.y > 171 and event.y < 404 and event.x > 135 and event.x < 612:
        data.action = 'yes'
        data.figX = event.x
        data.figY = event.y
        data.mouseOnGraph = True

#allows the user to type in the stock symbol
def keyPressed(event, data):
    data.action = 'yes'
    if data.clickStockEntry == True:
        if event.keysym == "BackSpace":
            if len(data.stockSym) > 0:
                data.stockSym = data.stockSym[: -1]
        elif event.keysym == "Up":
            data.scroll -= data.scrollAmount
        elif event.keysym == "Down":
            data.scroll += data.scrollAmount
        elif event.keysym != "Return" and event.keysym != "BackSpace" and \
        len(data.stockSym) < 25:
            data.stockSym += event.char
        elif event.keysym == "Return":
            data.retrieving = True
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
        if data.timeFrameStatus == "5 Years" or data.timeFrameStatus == "Max":
            data.stock.drawStockNewsFigure(canvas, data.scroll)
        if data.mouseOnGraph == True:
            data.stock.drawPricesAndDate(canvas, data.figX, data.figY)
    else:
        #draws start page items
        canvas.create_rectangle(100, 100, data.width - 100, data.height - 100,
        outline = "white", fill = "white")
        canvas.create_text(data.width/2, 150, text = "Stockometer",
        fill = "purple", font = "Symbol 45 bold")
        canvas.create_image(data.width/2, data.width/4, image = data.pig,
        anchor = NW)
        drawFakeGraph(canvas, data)
    drawSearchBars(canvas, data)
    drawUserInput(canvas, data)
    data.action = 'no'

#draws a graph just for display on the start page
def drawFakeGraph(canvas, data):
    canvas.create_line(150, data.height/2 - 100, 150, data.height/2 + 100,
    width = 5)
    canvas.create_line(150, data.height/2 + 100, 350, data.height/2 + 100,
    width = 5)
    canvas.create_line(150, data.height/2 + 100,
    200, data.height/2, width = 2)
    canvas.create_line(200, data.height/2, 270, data.height/2 + 12,
    width = 2)
    canvas.create_line(270, data.height/2 + 12, 300, data.height/2 - 100,
    width = 2)
    
def drawZoomButtons(canvas, data):
    timespans = ["1 Week", "1 Month", "6 Months", "1 Year", "5 Years", 
    "Max", "30-day\nForecast", "50-day\nForecast"]
    for i in range(data.numButtons):
        color = "DarkOrchid1"
        if i % 2 == 0:
            color = "cyan"
        canvas.create_rectangle(data.xStartButtons + i * data.buttonWidth,
        data.yStartButtons, data.xStartButtons + (i + 1) * data.buttonWidth,
        data.yStartButtons + data.buttonHeight, 
        fill = color, outline = "spring green", width = 3)
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
    data.timerDelay = 300 # milliseconds
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