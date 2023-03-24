
import yahooquery as yq
from dependencies import finviznews as fn
import time
import yfinance as yf

t1 = time.perf_counter()
news = yf.Ticker('AAPL').news
t2 = time.perf_counter()
print(f"{t2 - t1} seconds")
print(news)