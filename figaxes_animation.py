import yfinance as yf
import pandas as pd
pd.options.mode.chained_assignment = None
import mplfinance as mpf
from matplotlib import artist
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from threading import Thread
import time
import math
import talib

isclosed = False
data = yf.download(tickers="BTC-USD", period="1d", interval="30m", ignore_tz=False)
xlims = (0, data['Close'].size)
scaled_xlims = (0, 0)
default_xlims = (0, 0)

upper, middle, lower = talib.BBANDS(data["Close"], timeperiod=20)
bbands_talib = pd.DataFrame(index=data.index,
                        data={"bb_low": lower,
                              "bb_ma": middle,
                              "bb_high": upper})
plot = [
    mpf.make_addplot((bbands_talib["bb_low"]), color='#606060', panel=0),
    mpf.make_addplot((bbands_talib["bb_ma"]), color='#1f77b4', panel=0),
    mpf.make_addplot((bbands_talib["bb_high"]), color='#1f77b4', panel=0),
    
]
fig, axes = mpf.plot(data, volume=True, volume_panel=1, returnfig=True, addplot=plot, type='candle')


def onclose(fig):
    global isclosed
    print("closed")
    isclosed = True

def update_data(ival):
    global plot
    global bbands_talib
    global data
    global upper
    global axes
    global middle
    global lower
    global isclosed
    global scaled_xlims
    global default_xlims

    ax_main = axes[0]
    ax_main.callbacks.connect('xlim_changed', on_xlims_change)
    ax_bb = ax_main
    ax_bb.callbacks.connect('xlim_changed', on_xlims_change)
    ax_vol = axes[2]
    ax_vol.callbacks.connect('xlim_changed', on_xlims_change)

    
    data = yf.download(tickers="BTC-USD", period="1d", interval="30m", ignore_tz=False)
    upper, middle, lower = talib.BBANDS(data["Close"], timeperiod=20)
    
    
    
    if(xlims[0]) > 0 and xlims[1] < data['Close'].size:
        bbands_talib = pd.DataFrame(index=data.index,
                            data={"bb_low": lower,
                                  "bb_ma": middle,
                                  "bb_high": upper}).iloc[slice(xlims[0], xlims[1])]
        data = data.iloc[slice(xlims[0], xlims[1])]
    else:
        bbands_talib = pd.DataFrame(index=data.index,
                            data={"bb_low": lower,
                                  "bb_ma": middle,
                                  "bb_high": upper})
    plot = [
        mpf.make_addplot((bbands_talib["bb_low"]), color='#606060', ax=ax_bb),
        mpf.make_addplot((bbands_talib["bb_ma"]), color='#1f77b4', ax=ax_bb),
        mpf.make_addplot((bbands_talib["bb_high"]), color='#1f77b4', ax=ax_bb),
    ]
    for ax in axes:
        ax.clear()
    mpf.plot(data,type='candle',addplot=plot,ax=ax_main,volume=ax_vol)


    


def on_xlims_change(event_ax):
    global xlims
    global axes
    global scaled_xlims
    global plot
    print(f"xlims changed: {event_ax.get_xlim()}")

    
    # if user is zooming in
    if(event_ax.get_xlim()[0] > default_xlims[0] and event_ax.get_xlim()[1] < default_xlims[1]):

        if(scaled_xlims[0] < 0 and event_ax.get_xlim()[0] > 0):
            scaled_xlims = (math.ceil(event_ax.get_xlim()[0]), math.ceil(event_ax.get_xlim()[1]))
        else:
            scaled_xlims = (round(scaled_xlims[0]) + math.ceil(event_ax.get_xlim()[0]), round(scaled_xlims[0]) + math.floor(event_ax.get_xlim()[0]) + (math.ceil(event_ax.get_xlim()[1]) - math.floor(event_ax.get_xlim()[0])))
    else: # if user is zooming out
        scaled_xlims = event_ax.get_xlim()

    xlims = (int(event_ax.get_xlim()[0]), int(event_ax.get_xlim()[1]) )

    xlims = scaled_xlims
    
axes[0].callbacks.connect('xlim_changed', on_xlims_change)

ani = animation.FuncAnimation(fig, update_data, interval=50)        
mpf.show()


