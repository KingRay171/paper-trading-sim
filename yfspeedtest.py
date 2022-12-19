import yfinance as yf
import yahoofinancials as yahoo
import time
import pandas as pd

t1 = time.perf_counter()
spy1 = yf.Ticker("SPY").info
t2 = time.perf_counter()

spy2 = yf.download("SPY", period='5d')
t3 = time.perf_counter()

print(f"yf.Ticker: {t2 - t1}")
print(f"yf.download: {t3 - t2}")

print(spy1)
print(spy2)
