import math
import sys
import mplfinance as mpf
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import MultiCursor
from matplotlib import axes

import ta_addplot
import readassets as ra
# pylint: disable-msg=E1101
# pylint: disable-msg=W0123
# pylint: disable-msg=W0603
# pylint: disable-msg=C0103
import talib
import ta
import yfinance as yf
import pandas as pd

pd.options.mode.chained_assignment = None

isclosed = False
data = None
xlims = None
scaled_xlims = ()
default_xlims = (0, 0)


func_map = {
    talib.ADX : ta_addplot.adx_addplot,
    talib.ADXR : ta_addplot.adxr_addplot,
    talib.APO : ta_addplot.apo_addplot,
    talib.AROON : ta_addplot.aroon_addplot,
    talib.AROONOSC : ta_addplot.aroonosc_addplot,
    talib.BOP : ta_addplot.bop_addplot,
    talib.CCI : ta_addplot.cci_addplot,
    talib.CMO : ta_addplot.cmo_addplot,
    talib.DX : ta_addplot.dx_addplot,
    talib.MACDEXT : ta_addplot.macdext_addplot,
    talib.MFI : ta_addplot.mfi_addplot,
    talib.MINUS_DI : ta_addplot.minusdi_addplot,
    talib.MINUS_DM : ta_addplot.minusdm_addplot,
    talib.MOM : ta_addplot.mom_addplot,
    talib.PLUS_DI : ta_addplot.plusdi_addplot,
    talib.PLUS_DM : ta_addplot.plusdm_addplot,
    talib.PPO : ta_addplot.ppo_addplot,
    talib.ROC : ta_addplot.roc_addplot,
    talib.ROCP : ta_addplot.rocpercentage_addplot,
    talib.ROCR : ta_addplot.rocratio_addplot,
    talib.ROCR100 : ta_addplot.rocratio100_addplot,
    talib.RSI : ta_addplot.rsi_addplot,
    talib.STOCH : ta_addplot.slowstoch_addplot,
    talib.STOCHF : ta_addplot.faststoch_addplot,
    talib.STOCHRSI : ta_addplot.stochrsi_addplot,
    talib.ULTOSC : ta_addplot.ultosc_addplot,
    talib.WILLR : ta_addplot.willr_addplot,
    ta.momentum.tsi : ta_addplot.tsi_addplot,
    ta.momentum.awesome_oscillator : ta_addplot.ao_addplot,
    ta.momentum.kama : ta_addplot.kama_addplot,
    ta.trend.IchimokuIndicator : ta_addplot.ichimoku_addplot,
    ta.trend.dpo : ta_addplot.dpo_addplot,
    ta.trend.VortexIndicator : ta_addplot.vortex_addplot,
    ta.trend.stc : ta_addplot.schaff_addplot,
    ta.trend.PSARIndicator : ta_addplot.parabolicsar_addplot,
    ta.trend.KSTIndicator : ta_addplot.kst_addplot,
    ta.trend.trix : ta_addplot.trix_addplot,
    ta.trend.mass_index : ta_addplot.mi_addplot,
    ta.momentum.pvo : ta_addplot.pvo_addplot
}


def onclose(fig):
    global isclosed
    print("closed")
    isclosed = True

def on_xlims_change(event_ax):
    global xlims
    global scaled_xlims
    print(f"xlims changed: {event_ax.get_xlim()}")


    # if user is zooming in
    if(event_ax.get_xlim()[0] > default_xlims[0] and event_ax.get_xlim()[1] < default_xlims[1]):

        if(scaled_xlims[0] < 0 and event_ax.get_xlim()[0] > 0):
            scaled_xlims = (math.ceil(event_ax.get_xlim()[0]), math.ceil(event_ax.get_xlim()[1]))
        else:
            scaled_xlims = (
                round(scaled_xlims[0]) + math.ceil(event_ax.get_xlim()[0]),
                round(scaled_xlims[0]) + math.floor(event_ax.get_xlim()[0]) + (math.ceil(event_ax.get_xlim()[1]) - math.floor(event_ax.get_xlim()[0]))
            )
    else: # if user is zooming out
        scaled_xlims = event_ax.get_xlim()

    xlims = (int(event_ax.get_xlim()[0]), int(event_ax.get_xlim()[1]) )

    scaled_xlims = xlims

def startChart(ticker_symbol: str, interval: str, ta_indicators: list, prepost: bool, adjust_ohlc: bool, split_dividend: bool, volume: bool, period=None, start_date=None, end_date=None):

    global axes
    global data
    global xlims
    global scaled_xlims

    plot = []

    up_color = ra.get_xml_data('assets/settings.xml', 'upcolor')
    down_color = ra.get_xml_data('assets/settings.xml', 'downcolor')
    base_style = ra.get_xml_data('assets/settings.xml', 'basestyle')
    colors = mpf.make_marketcolors(
        up=up_color[0].text.lower(), down=down_color[0].text.lower(), inherit=True
    )

    s = mpf.make_mpf_style(base_mpf_style=base_style[0].text, marketcolors=colors)


    def update_data(ival):
        global plot
        global data
        global scaled_xlims
        global default_xlims

        ax_main = axes[0]

        ax_vol = axes[2] if volume else None

        old_data_size = data['Close'].size


        if period is not None:
            data = yf.download(
                tickers=ticker_symbol,
                period=period,
                interval=interval,
                prepost=prepost,
                auto_adjust=adjust_ohlc
            )
        else:
            data = yf.download(
                tickers=ticker_symbol,
                start=start_date,
                end=end_date,
                interval=interval,
                prepost=prepost,
                auto_adjust=adjust_ohlc
            )

        if data['Close'].size > old_data_size:
            scaled_xlims = (scaled_xlims[0], scaled_xlims[1] + 1)

        if data['Close'].size < old_data_size:
            scaled_xlims = (scaled_xlims[0], scaled_xlims[1] - 1)

        plot = []

        for indicator in ta_indicators:
            indicator = (eval(indicator[0]), indicator[1], indicator[2])
            indicator_plot = func_map[indicator[0]](data=data, settings=indicator[2], ax=axes[indicator[1] * 2])
            plot += indicator_plot
        for i in range(0, len(axes), 1):

            axes[i].clear()
            axes[i].set_xlim(scaled_xlims)

        ax_main.callbacks.connect('xlim_changed', on_xlims_change)

        if volume:
            mpf.plot(data,type='candle',addplot=plot,ax=ax_main,volume=ax_vol,style=s)
        else:
            mpf.plot(data,type='candle',addplot=plot,ax=ax_main,style=s)
        return axes


    if period is not None:
        data = yf.download(tickers=ticker_symbol, period=period, interval=interval, prepost=prepost, auto_adjust=adjust_ohlc)
    else:
        data = yf.download(tickers=ticker_symbol, start=start_date, end=end_date, interval=interval, prepost=prepost, auto_adjust=adjust_ohlc)

    xlims = (-2, data['Close'].size + 2)
    scaled_xlims = xlims



    for idx, indicator in enumerate(ta_indicators):

        indicator_plot = func_map[eval(indicator[0])](data=data, settings=indicator[2], panel=indicator[1])

        indicator_plot_isempty = True
        for i in range(len(indicator_plot)):
            if not all(math.isnan(val) for val in indicator_plot[i]['data']):
                indicator_plot_isempty = False
                break

        if indicator_plot_isempty:
            for i in range(ta_indicators.index(indicator), len(ta_indicators)):
                ta_indicators[i] = (ta_indicators[i][0], ta_indicators[i][1] - 1)
            ta_indicators[idx] = None
        else:
            plot += indicator_plot

    ta_indicators = [x for x in ta_indicators if x is not None]

    if ta_indicators != []:
        fig, axes = mpf.plot(data, volume=volume, returnfig=True, addplot=plot, type='candle', style=s)
    else:
        fig, axes = mpf.plot(data, volume=volume, returnfig=True, type='candle', style=s)

    axes[0].callbacks.connect('xlim_changed', on_xlims_change)


    ani = animation.FuncAnimation(fig, update_data, interval=50)

    mpf.show()

print(sys.argv)



if len(sys.argv) == 9:
    startChart(
        sys.argv[1],
        sys.argv[2],
        eval(sys.argv[3]),
        eval(sys.argv[5]),
        eval(sys.argv[6]),
        eval(sys.argv[7]),
        eval(sys.argv[8]),
        period=sys.argv[4]
    )
elif len(sys.argv) == 10:
    startChart(
        sys.argv[1],
        sys.argv[2],
        eval(sys.argv[3]),
        eval(sys.argv[6]),
        eval(sys.argv[7]),
        eval(sys.argv[8]),
        eval(sys.argv[9]),
        start_date=sys.argv[4],
        end_date=sys.argv[5]
    )
