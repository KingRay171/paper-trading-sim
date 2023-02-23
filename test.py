import sys
import numpy as np
import talib
import ta
from yahoo_fin import stock_info
from ta.volatility import BollingerBands
from ta.momentum import tsi
from matplotlib.backends.qt_compat import QtWidgets
from matplotlib.backends.backend_qt5agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from bs4 import BeautifulSoup
from matplotlib.figure import Figure
from matplotlib import animation
import pandas as pd
import yahooquery as yq
import time
from yahooquery import Ticker
import dis

def append_list(ls):
        ls.append(2)

t1 = time.perf_counter()
ls = [0, 2, 5]
append_list(ls)
print(ls)
print(yq.Ticker('BTC-USD').history('1wk').iloc[-2][5])
print(stock_info.get_day_gainers())
t2 = time.perf_counter()

t3 = time.perf_counter()

print(f"yfinance: {t2 - t1}")