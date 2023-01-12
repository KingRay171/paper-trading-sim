import yfinance as yf
from datetime import date
from datetime import timedelta
import numpy as np

#most growth, most loss, most volume, most volitality, most realized volitility

#All of the bellow accept a list of stock names and returns them sorted by the name of the method. i.e. if you use 'Volitilitiy' it will output a 2d list organized by its volitility. The name will be the first colomn will be the names and the second will show the volitility
def Volitility(stockNameList):
  topname = []
  
  for stockName in stockNameList:
    stockData = yf.download(tickers = [stockName], period = '1mo', interval = '1d')
    
    closePrices = stockData['Close']
    a = np.array(closePrices)
    standard = np.std(a)
    
    topname.append([stockName, standard])

  topname = sorted(topname,key=lambda l:l[1], reverse=True)
  return topname

def Growth(stockNameList):
  today = date.today() + timedelta(days = 1)
  yesterday = today - timedelta(days = 3)
  topname = []

  for stockName in stockNameList:
    stockData = yf.download(tickers = [stockName], start = yesterday, end = today, interval = '1d')
    
    start = stockData['Close'][0]
    end = stockData['Close'][-1]

    growth = end/start - 1
    
    topname.append([stockName, growth])

  topname = sorted(topname,key=lambda l:l[1], reverse=True)
  return topname

def Volume(stockNameList):
  topname = []

  for stockName in stockNameList:
    stockData = yf.download(tickers = [stockName], period = '1d')
    
    volume = stockData['Volume'][-1]
    
    topname.append([stockName, volume])

  topname = sorted(topname,key=lambda l:l[1], reverse=True)
  return topname
  
