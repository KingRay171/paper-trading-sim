import os
import yfinance as yf
import mplfinance as mpf
import matplotlib.pyplot as plt
import json

data = yf.download(tickers="SPY", period="1d", interval="2m")

fig = mpf.figure()
axes = fig.add_subplot(1, 1, 1)

while True:
    axes.clear()
    data = yf.download(tickers="SPY", period="1d", interval="2m", prepost=True)
    mpf.plot(data, ax=axes, type='candle', block=False)
    plt.pause(5)

