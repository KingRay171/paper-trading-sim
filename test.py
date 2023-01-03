import os
import yfinance as yf
import json

ticker = yf.Ticker('msft')

rev = ticker.info
rev = ticker.get_analyst_price_target()

rev2 = ticker.get_financials()
rev3 = ticker.get_rev_forecast()
print(rev2)

