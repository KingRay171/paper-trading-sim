import sys
import numpy as np
import talib
import ta
from ta.volatility import BollingerBands
from ta.momentum import tsi
from matplotlib.backends.qt_compat import QtWidgets
from matplotlib.backends.backend_qt5agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from bs4 import BeautifulSoup
from matplotlib.figure import Figure
from matplotlib import animation
import pandas as pd
import yfinance as yf
import yahooquery as yq
import time
from yahooquery import Ticker
import dis


t1 = time.perf_counter()
print(yq.Ticker('SPY').history('5d').iloc[4][3])

t2 = time.perf_counter()
print(yf.download(tickers='BTC-USD', period='5d', interval='1d'))
t3 = time.perf_counter()
print(dis.dis("yq.Ticker('SPY').history('5d')"))

print(f"yfinance: {t2 - t1}")