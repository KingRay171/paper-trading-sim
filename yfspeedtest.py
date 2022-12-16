import yfinance as yf
import time
import pandas as pd
t1 = time.perf_counter()

spy1 = yf.Ticker("SPY").info['regularMarketPrice']

t2 = time.perf_counter()

spy2 = yf.download("SPY", period='1d').iloc[0][3]

t3 = time.perf_counter()

print(f"yf.Ticker time: {t2 - t1}")
print(f"yf.download time: {t3 - t2}")