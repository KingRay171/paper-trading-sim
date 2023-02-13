import talib
import ta
from ta import momentum, trend

import pandas as pd
import mplfinance as mpf
import math

def adx_addplot(data, ax=None, panel=None,  timeperiod=14):
    adx = talib.ADX(data['High'], data['Low'], data['Close'], timeperiod)
    adx_talib = pd.DataFrame(index=data.index,
                            data={"adx": adx})

    if(ax == None):
        plot = [
            mpf.make_addplot((adx_talib["adx"]), panel=panel, ylabel='Avg Directional Movement')
        ]

    elif(panel == None):
        plot = [
            mpf.make_addplot((adx_talib["adx"]), ax=ax, ylabel='Avg Directional Movement')
        ]
    return plot

def adxr_addplot(data, ax=None, panel=None, timeperiod=14):
    adxr = talib.ADXR(data['High'], data['Low'], data['Close'], timeperiod)
    adxr_talib = pd.DataFrame(index=data.index,
                            data={"adxr": adxr})

    if(ax == None):
        plot = [
            mpf.make_addplot((adxr_talib["adxr"]),  panel=panel, ylabel='Avg Directional Movement Rating')
        ]

    elif(panel == None):
        plot = [
            mpf.make_addplot((adxr_talib["adxr"]),  ax=ax, ylabel='Avg Directional Movement Rating')
        ]
    return plot

def apo_addplot(data, ax=None, panel=None, fastperiod=12, slowperiod=26, matype=0):
    apo = talib.APO(data['Close'], fastperiod, slowperiod, matype)
    apo_talib = pd.DataFrame(index=data.index,
                            data={"apo": apo})

    if(ax == None):
        plot = [
            mpf.make_addplot((apo_talib["apo"]),  panel=panel, ylabel='Absolute Price Oscillator')
        ]

    elif(panel == None):
        plot = [
            mpf.make_addplot((apo_talib["apo"]),  ax=ax, ylabel='Absolute Price Oscillator')
        ]
    return plot

def aroon_addplot(data, ax=None, panel=None, timeperiod=14):
    aroondown, aroonup = talib.AROON(data['High'], data['Low'], timeperiod)
    aroon_talib = pd.DataFrame(index=data.index,
                            data={"aroon_down": aroondown,
                                  "aroon_up" : aroonup})
    
    if(ax == None):
        plot = [
            mpf.make_addplot((aroon_talib["aroon_down"]),  panel=panel, ylabel='Aroon'), 
            mpf.make_addplot((aroon_talib["aroon_up"]),  panel=panel)
        ]

    elif(panel == None):
        plot = [
            mpf.make_addplot((aroon_talib["aroon_down"]), ax=ax, ylabel='Aroon'), 
            mpf.make_addplot((aroon_talib["aroon_up"]), ax=ax)
        ]

    return plot

def aroonosc_addplot(data, ax=None, panel=None, timeperiod=14):
    aroonosc = talib.AROONOSC(data['High'], data['Low'], timeperiod)
    aroon_talib = pd.DataFrame(index=data.index,
                            data={"aroonosc": aroonosc})

    if(ax == None):
        plot = [
            mpf.make_addplot((aroon_talib["aroonosc"]),  panel=panel, ylabel='Aroon Oscillator')
        ]

    elif(panel == None):
        plot = [
            mpf.make_addplot((aroon_talib["aroonosc"]), ax=ax, ylabel='Aroon Oscillator')
        ]

    return plot

def ao_addplot(data, ax=None, panel=None, fastma_period=5, slowma_period=34):
    ao = momentum.awesome_oscillator(data['High'], data['Low'], fastma_period, slowma_period)
    ao_ta = pd.DataFrame(index=data.index,
                            data={"ao": ao})

    if(ax == None):
        plot = [
            mpf.make_addplot((ao_ta["ao"]),  panel=panel, ylabel='Awesome Oscillator')
        ]

    elif(panel == None):
        plot = [
            mpf.make_addplot((ao_ta["ao"]), ax=ax, ylabel='Awesome Oscillator')
        ]

    return plot

def bop_addplot(data, ax=None, panel=None):
    bop = talib.BOP(data['Open'], data['High'], data['Low'], data['Close'])
    bop_talib = pd.DataFrame(index=data.index,
                            data={"bop": bop})
    if(ax == None):
        plot = [
            mpf.make_addplot((bop_talib["bop"]),  panel=panel, ylabel='Balance of Power')
        ]

    elif(panel == None):
        plot = [
            mpf.make_addplot((bop_talib["bop"]), ax=ax, ylabel='Balance of Power')
        ]

    return plot

def cci_addplot(data, ax=None, panel=None, timeperiod=14):
    cci = talib.CCI(data['High'], data['Low'], data['Close'], timeperiod)
    cci_talib = pd.DataFrame(index=data.index,
                            data={"cci": cci})
    
    if(ax == None):
        plot = [
            mpf.make_addplot((cci_talib["cci"]), panel=panel, ylabel='Commodity Channel Index')
        ]

    elif(panel == None):
        plot = [
            mpf.make_addplot((cci_talib["cci"]), ax=ax, ylabel='Commodity Channel Index')
        ]

    return plot

def cmo_addplot(data, ax=None, panel=None, timeperiod=14):
    cmo = talib.CMO(data['Close'], timeperiod)
    cmo_talib = pd.DataFrame(index=data.index,
                            data={"cmo": cmo})

    if(ax == None):
        plot = [
            mpf.make_addplot((cmo_talib["cmo"]),  panel=panel, ylabel='Chande Momentum Oscillator')
        ]

    elif(panel == None):
        plot = [
            mpf.make_addplot((cmo_talib["cmo"]), ax=ax, ylabel='Chande Momentum Oscillator')
        ]

    return plot

def dx_addplot(data, ax=None, panel=None, timeperiod=14):
    dx = talib.DX(data['High'], data['Low'], data['Close'], timeperiod)
    dx_talib = pd.DataFrame(index=data.index,
                            data={"dx": dx})

    if(ax == None):
        plot = [
            mpf.make_addplot((dx_talib["dx"]),  panel=panel, ylabel='Directional Movement Index')
        ]

    elif(panel == None):
        plot = [
            mpf.make_addplot((dx_talib["dx"]), ax=ax, ylabel='Directional Movement Index')
        ]

    return plot

def kama_addplot(data, ax=None, panel=None, efficiency_ratio_periods=10, fastema_periods=2, slowema_periods=30):
    kama = momentum.kama(data['Close'], efficiency_ratio_periods, fastema_periods, slowema_periods)
    kama_ta = pd.DataFrame(index=data.index,
                            data={"kama": kama})

    if(ax == None):
        plot = [
            mpf.make_addplot((kama_ta["kama"]),  panel=panel, ylabel='KAMA Indicator')
        ]

    elif(panel == None):
        plot = [
            mpf.make_addplot((kama_ta["kama"]), ax=ax, ylabel='Kama Indicator')
        ]

    return plot

def macd_addplot(data, ax=None, panel=None, fastperiod=12, slowperiod=26, signalperiod=9):
    macd, macdsignal, macdhist = talib.MACD(data['Close'], fastperiod, slowperiod, signalperiod)
    macd_talib = pd.DataFrame(index=data.index,
                            data={"macd": macd, 
                                  "macd_signal" : macdsignal, 
                                  "macd_hist" : macdhist})

    if(ax == None):
        plot = [
            mpf.make_addplot((macd_talib["macd"]),  panel=panel, ylabel='MACD'),
            mpf.make_addplot((macd_talib["macd_signal"]),  panel=panel),
            mpf.make_addplot((macd_talib["macd_hist"]), type='bar',  panel=panel)
        ]

    elif(panel == None):
        plot = [
            mpf.make_addplot((macd_talib["macd"]), ax=ax, ylabel='MACD'),
            mpf.make_addplot((macd_talib["macd_signal"]),  ax=ax),
            mpf.make_addplot((macd_talib["macd_hist"]), type='bar', ax=ax)
        ]

    return plot

def macdext_addplot(data, ax=None, panel=None, fastperiod=12, fastmatype=0, slowperiod=26, slowmatype=0, signalperiod=9, signalmatype=0):
    macd, macdsignal, macdhist = talib.MACDEXT(data['Close'], fastperiod, fastmatype, slowperiod, slowmatype, signalperiod, signalmatype)
    macd_talib = pd.DataFrame(index=data.index,
                            data={"macd": macd, 
                                  "macd_signal" : macdsignal, 
                                  "macd_hist" : macdhist})

    if(ax == None):
        plot = [
            mpf.make_addplot((macd_talib["macd"]),  panel=panel, ylabel='MACD'),
            mpf.make_addplot((macd_talib["macd_signal"]),  panel=panel),
            mpf.make_addplot((macd_talib["macd_hist"]), type='bar',  panel=panel)
        ]

    elif(panel == None):
        plot = [
            mpf.make_addplot((macd_talib["macd"]), ax=ax, ylabel='MACD'),
            mpf.make_addplot((macd_talib["macd_signal"]),  ax=ax),
            mpf.make_addplot((macd_talib["macd_hist"]), type='bar', ax=ax)
        ]

    return plot

def macdfix_addplot(data, ax=None, panel=None, signalperiod=9):
    macd, macdsignal, macdhist = talib.MACDFIX(data['Close'], signalperiod)
    macd_talib = pd.DataFrame(index=data.index,
                            data={"macd": macd, 
                                  "macd_signal" : macdsignal, 
                                  "macd_hist" : macdhist})

    if(ax == None):
        plot = [
            mpf.make_addplot((macd_talib["macd"]),  panel=panel, ylabel='Fixed MACD'),
            mpf.make_addplot((macd_talib["macd_signal"]),  panel=panel),
            mpf.make_addplot((macd_talib["macd_hist"]), type='bar',  panel=panel)
        ]

    elif(panel == None):
        plot = [
            mpf.make_addplot((macd_talib["macd"]), ax=ax, ylabel='Fixed MACD'),
            mpf.make_addplot((macd_talib["macd_signal"]),  ax=ax),
            mpf.make_addplot((macd_talib["macd_hist"]), type='bar', ax=ax)
        ]

    return plot

def mfi_addplot(data, ax=None, panel=None, timeperiod=14):
    mfi = talib.MFI(data['High'], data['Low'], data['Close'], data['Volume'], timeperiod)
    mfi_talib = pd.DataFrame(index=data.index,
                            data={"mfi": mfi})

    if(ax == None):
        plot = [
            mpf.make_addplot((mfi_talib["mfi"]), panel=panel, ylabel='Money Flow Index')
        ]

    elif(panel == None):
        plot = [
            mpf.make_addplot((mfi_talib["mfi"]), ax=ax, ylabel='Money Flow Index')
        ]

    return plot

def minusdi_addplot(data, ax=None, panel=None, timeperiod=14):
    minusdi = talib.MINUS_DI(data['High'], data['Low'], data['Close'], timeperiod)
    minusdi_talib = pd.DataFrame(index=data.index,
                            data={"minus_di": minusdi})

    if(ax == None):
        plot = [
            mpf.make_addplot((minusdi_talib["minus_di"]), panel=panel, ylabel='Minus Directional Indicator')
        ]

    elif(panel == None):
        plot = [
            mpf.make_addplot((minusdi_talib["minus_di"]), ax=ax, ylabel='Minus Directional Indicator')
        ]

    return plot

def minusdm_addplot(data, ax=None, panel=None, timeperiod=14):
    minusdm = talib.MINUS_DM(data['High'], data['Low'], timeperiod)
    minusdm_talib = pd.DataFrame(index=data.index,
                            data={"minus_dm": minusdm})

    if(ax == None):
        plot = [
            mpf.make_addplot((minusdm_talib["minus_dm"]), panel=panel, ylabel='Minus Directional Movement')
        ]

    elif(panel == None):
        plot = [
            mpf.make_addplot((minusdm_talib["minus_dm"]), ax=ax, ylabel='Minus Directional Movement')
        ]

    return plot

def mom_addplot(data, ax=None, panel=None, timeperiod=14):
    mom = talib.MOM(data['Close'], timeperiod)
    mom_talib = pd.DataFrame(index=data.index,
                            data={"mom": mom})

    if(ax == None):
        plot = [
            mpf.make_addplot((mom_talib["mom"]), panel=panel, ylabel='Momentum')
        ]

    elif(panel == None):
        plot = [
            mpf.make_addplot((mom_talib["mom"]), ax=ax, ylabel='Momentum')
        ]

    return plot

def plusdi_addplot(data, ax=None, panel=None, timeperiod=14):
    plusdi = talib.PLUS_DI(data['High'], data['Low'], data['Close'], timeperiod)
    plusdi_talib = pd.DataFrame(index=data.index,
                            data={"plusdi": plusdi})

    if(ax == None):
        plot = [
            mpf.make_addplot((plusdi_talib["plusdi"]), panel=panel, ylabel='Plus Directional Indicator')
        ]

    elif(panel == None):
        plot = [
            mpf.make_addplot((plusdi_talib["plusdi"]), ax=ax, ylabel='Plus Directional Indicator')
        ]

    return plot

def plusdm_addplot(data, ax=None, panel=None, timeperiod=14):
    plusdm = talib.PLUS_DM(data['High'], data['Low'], timeperiod)
    plusdm_talib = pd.DataFrame(index=data.index,
                            data={"plusdm": plusdm})

    if(ax == None):
        plot = [
            mpf.make_addplot((plusdm_talib["plusdm"]), panel=panel, ylabel='Plus Directional Movement')
        ]

    elif(panel == None):
        plot = [
            mpf.make_addplot((plusdm_talib["plusdm"]), ax=ax, ylabel='Plus Directional Movement')
        ]

    return plot

def ppo_addplot(data, ax=None, panel=None, fastperiod=12, slowperiod=26, matype=0):
    ppo = talib.PPO(data['Close'], fastperiod, slowperiod, matype)
    ppo_talib = pd.DataFrame(index=data.index,
                            data={"ppo": ppo})

    if(ax == None):
        plot = [
            mpf.make_addplot((ppo_talib["ppo"]), panel=panel, ylabel='Percentage Price Oscillator')
        ]

    elif(panel == None):
        plot = [
            mpf.make_addplot((ppo_talib["ppo"]), ax=ax, ylabel='Percentage Price Oscillator')
        ]

    return plot

def pvo_addplot(data, ax=None, panel=None, slowma_period=12, fastma_period=26, signal_period=9):
    pvo = momentum.pvo(data['Volume'], slowma_period, fastma_period, signal_period)
    pvo_ta = pd.DataFrame(index=data.index,
                            data={"pvo": pvo})

    if(ax == None):
        plot = [
            mpf.make_addplot((pvo_ta["pvo"]), panel=panel, ylabel='Percentage Volume Oscillator')
        ]

    elif(panel == None):
        plot = [
            mpf.make_addplot((pvo_ta["ppo"]), ax=ax, ylabel='Percentage Volume Oscillator')
        ]

    return plot

def roc_addplot(data, ax=None, panel=None, timeperiod=10):
    roc = talib.ROC(data['Close'], timeperiod)
    roc_talib = pd.DataFrame(index=data.index,
                            data={"roc": roc})

    if(ax == None):
        plot = [
            mpf.make_addplot((roc_talib["roc"]), panel=panel, ylabel='Rate of Change ($)')
        ]

    elif(panel == None):
        plot = [
            mpf.make_addplot((roc_talib["roc"]), ax=ax, ylabel='Rate of Change ($)')
        ]

    return plot

def rocpercentage_addplot(data, ax=None, panel=None, timeperiod=10):
    rocp = talib.ROCP(data['Close'], timeperiod)
    rocp_talib = pd.DataFrame(index=data.index,
                            data={"rocp": rocp})

    if(ax == None):
        plot = [
            mpf.make_addplot((rocp_talib["rocp"]), panel=panel, ylabel='Rate of Change (%)')
        ]

    elif(panel == None):
        plot = [
            mpf.make_addplot((rocp_talib["rocp"]), ax=ax, ylabel='Rate of Change (%)')
        ]

    return plot

def rocratio_addplot(data, ax=None, panel=None, timeperiod=10):
    rocr = talib.ROCR(data['Close'], timeperiod)
    rocr_talib = pd.DataFrame(index=data.index,
                            data={"rocr": rocr})

    if(ax == None):
        plot = [
            mpf.make_addplot((rocr_talib["rocr"]), panel=panel, ylabel='Rate of Change (Ratio)')
        ]

    elif(panel == None):
        plot = [
            mpf.make_addplot((rocr_talib["rocr"]), ax=ax, ylabel='Rate of Change (Ratio)')
        ]

    return plot

def rocratio100_addplot(data, ax=None, panel=None, timeperiod=10):
    rocr = talib.ROCR100(data['Close'], timeperiod)
    rocr_talib = pd.DataFrame(index=data.index,
                            data={"rocr": rocr})

    if(ax == None):
        plot = [
            mpf.make_addplot((rocr_talib["rocr"]), panel=panel, ylabel='Rate of Change (Ratio, 100 scale)')
        ]

    elif(panel == None):
        plot = [
            mpf.make_addplot((rocr_talib["rocr"]), ax=ax, ylabel='Rate of Change (Ratio, 100 scale)')
        ]

    return plot

def rsi_addplot(data, ax=None, panel=None, timeperiod=10):
    rsi = talib.RSI(data['Close'], timeperiod)
    rsi_talib = pd.DataFrame(index=data.index,
                            data={"rsi": rsi})

    if(ax == None):
        plot = [
            mpf.make_addplot((rsi_talib["rsi"]), panel=panel, ylabel='Relative Strength Index')
        ]

    elif(panel == None):
        plot = [
            mpf.make_addplot((rsi_talib["rsi"]), ax=ax, ylabel='Relative Strength Index')
        ]

    return plot

def slowstoch_addplot(data, ax=None, panel=None, fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0):
    slowk, slowd = talib.STOCH(data['High'], data['Low'], data['Close'], fastk_period, slowk_period, slowk_matype, slowd_period, slowd_matype)
    stoch_talib = pd.DataFrame(index=data.index,
                            data={"slowk" : slowk, 
                                  "slowd" : slowd})

    if(ax == None):
        plot = [
            mpf.make_addplot((stoch_talib["slowk"]), panel=panel, ylabel='Slow Stochastic'),
            mpf.make_addplot((stoch_talib["slowd"]), panel=panel)
        ]

    elif(panel == None):
        plot = [
            mpf.make_addplot((stoch_talib["slowk"]), ax=ax, ylabel='Slow Stochastic'),
            mpf.make_addplot((stoch_talib["slowd"]), ax=ax)
        ]

    return plot

def faststoch_addplot(data, settings, ax=None, panel=None, fastk_period=5, fastd_period=3, fastd_matype=0):
    fastk, fastd = talib.STOCHF(data['High'], data['Low'], data['Close'], settings[0], settings[1], settings[2])
    stoch_talib = pd.DataFrame(index=data.index,
                            data={"fastk" : fastk, 
                                  "fastd" : fastd})

    if(ax == None):
        plot = [
            mpf.make_addplot((stoch_talib["fastk"]), panel=panel, ylabel='Fast Stochastic'),
            mpf.make_addplot((stoch_talib["fastd"]), panel=panel)
        ]

    elif(panel == None):
        plot = [
            mpf.make_addplot((stoch_talib["fastk"]), ax=ax, ylabel='Fast Stochastic'),
            mpf.make_addplot((stoch_talib["fastd"]), ax=ax)
        ]

    return plot

def stochrsi_addplot(data, settings, ax=None, panel=None, fastk_period=5, fastd_period=3, fastd_matype=0):
    fastk, fastd = talib.STOCHRSI(data['Close'], fastk_period, fastd_period, fastd_matype)
    stoch_talib = pd.DataFrame(index=data.index,
                            data={"fastk" : fastk, 
                                  "fastd" : fastd})

    if(ax == None):
        plot = [
            mpf.make_addplot((stoch_talib["fastk"]), panel=panel, ylabel='Stochastic RSI'),
            mpf.make_addplot((stoch_talib["fastd"]), panel=panel)
        ]

    elif(panel == None):
        plot = [
            mpf.make_addplot((stoch_talib["fastk"]), ax=ax, ylabel='Stochastic RSI'),
            mpf.make_addplot((stoch_talib["fastd"]), ax=ax)
        ]

    return plot

def tsi_addplot(data, settings, ax=None, panel=None):
    tsi = ta.momentum.tsi(data['Close'], settings[0], settings[1])
    tsi_ta = pd.DataFrame(index=data.index,
                            data={"tsi": tsi})
    if(ax == None):
        plot = [
            mpf.make_addplot((tsi_ta["tsi"]), panel=panel, ylabel='True Strength Index')
        ]

    elif(panel == None):
        plot = [
            mpf.make_addplot((tsi_ta["tsi"]), ax=ax, ylabel='True Strength Index')
        ]
    return plot


def ultosc_addplot(data, settings, ax=None, panel=None):
    ultosc = talib.ULTOSC(data['High'], data['Low'], data['Close'], settings[0], settings[1], settings[2])
    ultosc_talib = pd.DataFrame(index=data.index,
                            data={"ultosc": ultosc})

    if(ax == None):
        plot = [
            mpf.make_addplot((ultosc_talib["ultosc"]), panel=panel, ylabel='Ultimate Oscillator')
        ]

    elif(panel == None):
        plot = [
            mpf.make_addplot((ultosc_talib["ultosc"]), ax=ax, ylabel='Ultimate Oscillator')
        ]

    return plot


def willr_addplot(data, settings, ax=None, panel=None):
    willr = talib.WILLR(data['High'], data['Low'], data['Close'], settings[0])
    willr_talib = pd.DataFrame(index=data.index,
                            data={"willr": willr})

    if(ax == None):
        plot = [
            mpf.make_addplot((willr_talib["willr"]), panel=panel, ylabel="Williams' %R")
        ] 

    elif(panel == None):
        plot = [
            mpf.make_addplot((willr_talib["willr"]), ax=ax, ylabel="Williams' %r")
        ]

    return plot


####################
# Trend Indicators #
####################


def dpo_addplot(data, settings, ax=None, panel=None):
    dpo = trend.dpo(data['Close'], settings[0])
    dpo_ta = pd.DataFrame(index=data.index,
                            data={"dpo": dpo})
    if(ax == None):
        plot = [
            mpf.make_addplot((dpo_ta["dpo"]), panel=panel, ylabel="Detrended Price Oscillator")
        ]

    elif(panel == None):
        plot = [
            mpf.make_addplot((dpo_ta["dpo"]), ax=ax, ylabel="Detrended Price Oscillator")
        ]
    return plot


def ichimoku_addplot(data, settings, ax=None, panel=None):
    ichimoku = trend.IchimokuIndicator(data['High'], data['Low'], settings[0], settings[1], settings[2], settings[3])
    ichimoku_ta = pd.DataFrame(index=data.index,
                            data={"ichimoku_a" : ichimoku.ichimoku_a(), 
                                  "ichimoku_b" : ichimoku.ichimoku_b(),
                                  "ichimoku_conversion" : ichimoku.ichimoku_conversion_line(),
                                  "ichimoku_baseline" : ichimoku.ichimoku_base_line()})

    if(ax == None):
        plot = [
            mpf.make_addplot((ichimoku_ta["ichimoku_a"]), panel=panel),
            mpf.make_addplot((ichimoku_ta["ichimoku_b"]), panel=panel),
            mpf.make_addplot((ichimoku_ta["ichimoku_conversion"]), panel=panel),
            mpf.make_addplot((ichimoku_ta["ichimoku_baseline"]), panel=panel)
        ]

    elif(panel == None):
        plot = [
            mpf.make_addplot((ichimoku_ta["ichimoku_a"]), ax=ax),
            mpf.make_addplot((ichimoku_ta["ichimoku_b"]), ax=ax),
            mpf.make_addplot((ichimoku_ta["ichimoku_conversion"]), ax=ax),
            mpf.make_addplot((ichimoku_ta["ichimoku_baseline"]), ax=ax)
        ]

    return plot


def schaff_addplot(data, settings, ax=None, panel=None):
    """
    settings: a list with 5 items (MACD slow period length, MACD fast period length, cycle length, stochk EMA period, stockd EMA period)
    """
    schaff = trend.stc(data['Close'], settings[0], settings[1], settings[2], settings[3], settings[4])
    schaff_ta = pd.DataFrame(index=data.index,
                            data={"schaff": schaff})
    if(ax == None):
        plot = [
            mpf.make_addplot((schaff_ta["schaff"]), panel=panel, ylabel="Schaff Trend Cycle")
        ]

    elif(panel == None):
        plot = [
            mpf.make_addplot((schaff_ta["schaff"]), ax=ax, ylabel="Schaff Trend Cycle")
        ]
    return plot


def parabolicsar_addplot(data, settings, ax=None, panel=None):
    """
    settings: a list with two items (the acceleration factor and the maximum allowed acceleration factor)
    """
    psar = trend.PSARIndicator(data['High'], data['Low'], data['Close'], settings[0], settings[1])
    psar_ta = pd.DataFrame(index=data.index,
                            data={"up" : psar.psar_up(),
                                  "down" : psar.psar_down()})
    if(ax == None):
        plot = [
            mpf.make_addplot((psar_ta["up"]), panel=panel),
            mpf.make_addplot((psar_ta["down"]), panel=panel)
        ]

    elif(panel == None):
        plot = [
            mpf.make_addplot((psar_ta["up"]), ax=ax),
            mpf.make_addplot((psar_ta["down"]), ax=ax)
        ]
    return plot


def kst_addplot(data, settings, ax=None, panel=None):
    kst = trend.KSTIndicator(data['Close'], settings[0], settings[1], settings[2], settings[3], settings[4], settings[5], settings[6], settings[7], settings[8])
    kst_ta = kst_ta = pd.DataFrame(index=data.index,
                            data={"kst" : kst.kst(),
                                  "signal" : kst.kst_sig()})
    if(ax == None):
        plot = [
            mpf.make_addplot((kst_ta["kst"]), panel=panel),
            mpf.make_addplot((kst_ta["signal"]), panel=panel)
        ]

    elif(panel == None):
        plot = [
            mpf.make_addplot((kst_ta["kst"]), ax=ax),
            mpf.make_addplot((kst_ta["signal"]), ax=ax)
        ]
    return plot


def trix_addplot(data, settings, ax=None, panel=None):
    """
    settings: a list with one item (the lookback period)
    """
    trix = trend.trix(data['Close'], settings[0])
    trix_ta = pd.DataFrame(index=data.index,
                            data={"trix": trix})
    if(ax == None):
        plot = [
            mpf.make_addplot((trix_ta["trix"]), panel=panel, ylabel="Trix Indicator")
        ]

    elif(panel == None):
        plot = [
            mpf.make_addplot((trix_ta["trix"]), ax=ax, ylabel="Trix Indicator")
        ]
    return plot


def mi_addplot(data, settings, ax=None, panel=None):
    """
    settings: a list with two items (the fast window value and the slow window value)
    """
    
    mi = trend.mass_index(data['High'], data['Low'], settings[0], settings[1])
    mi_ta = pd.DataFrame(index=data.index,
                            data={"mi": mi})
    if(ax == None):
        plot = [
            mpf.make_addplot((mi_ta["mi"]), panel=panel, ylabel="Mass Index")
        ]

    elif(panel == None):
        plot = [
            mpf.make_addplot((mi_ta["mi"]), ax=ax, ylabel="Mass Index")
        ]
    return plot


def vortex_addplot(data, settings, ax=None, panel=None):
    """
    settings: a list with one item (the lookback period)
    """
    vortex = trend.VortexIndicator(data['High'], data['Low'], data['Close'], settings[0])
    vortex_ta = pd.DataFrame(index=data.index,
                            data={"vortex_pos" : vortex.vortex_indicator_pos(),
                                  "vortex_neg" : vortex.vortex_indicator_neg()})
    if(ax == None):
        plot = [
            mpf.make_addplot((vortex_ta["vortex_pos"]), panel=panel, ylabel="Vortex"),
            mpf.make_addplot((vortex_ta["vortex_neg"]), panel=panel)
        ]

    elif(panel == None):
        plot = [
            mpf.make_addplot((vortex_ta["vortex_pos"]), ax=ax, ylabel="Vortex"),
            mpf.make_addplot((vortex_ta["vortex_neg"]), ax=ax)
        ]
    return plot