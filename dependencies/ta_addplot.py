import talib
import ta
from ta import momentum, trend

import pandas as pd
import mplfinance as mpf

# pylint: disable-msg=E1101

def adx_addplot(data, settings, axis=None, panel=None):
    adx = talib.ADX(data['High'], data['Low'], data['Close'], settings[0])
    adx_talib = pd.DataFrame(index=data.index,
                            data={"adx": adx})

    if axis is None:
        plot = [
            mpf.make_addplot((adx_talib["adx"]), panel=panel, ylabel='Avg Directional Movement')
        ]

    elif panel is None:
        plot = [
            mpf.make_addplot((adx_talib["adx"]), ax=axis, ylabel='Avg Directional Movement')
        ]
    return plot

def adxr_addplot(data, settings, axis=None, panel=None):
    adxr = talib.ADXR(data['High'], data['Low'], data['Close'], settings[0])
    adxr_talib = pd.DataFrame(index=data.index,
                            data={"adxr": adxr})

    if axis is None:
        plot = [
            mpf.make_addplot((adxr_talib["adxr"]), panel=panel, ylabel='Avg Directional Movement Rating')
        ]

    elif panel is None:
        plot = [
            mpf.make_addplot((adxr_talib["adxr"]),  ax=axis, ylabel='Avg Directional Movement Rating')
        ]
    return plot

def apo_addplot(data, settings, axis=None, panel=None):
    apo = talib.APO(data['Close'], settings[0], settings[1], settings[2])
    apo_talib = pd.DataFrame(index=data.index,
                            data={"apo": apo})

    if axis is None:
        plot = [
            mpf.make_addplot((apo_talib["apo"]),  panel=panel, ylabel='Absolute Price Oscillator')
        ]

    elif panel is None:
        plot = [
            mpf.make_addplot((apo_talib["apo"]),  ax=axis, ylabel='Absolute Price Oscillator')
        ]
    return plot

def aroon_addplot(data, settings, axis=None, panel=None):
    aroondown, aroonup = talib.AROON(data['High'], data['Low'], settings[0])
    aroon_talib = pd.DataFrame(index=data.index,
                            data={"aroon_down": aroondown,
                                  "aroon_up" : aroonup})

    if axis is None:
        plot = [
            mpf.make_addplot((aroon_talib["aroon_down"]),  panel=panel, ylabel='Aroon'),
            mpf.make_addplot((aroon_talib["aroon_up"]),  panel=panel)
        ]

    elif panel is None:
        plot = [
            mpf.make_addplot((aroon_talib["aroon_down"]), ax=axis, ylabel='Aroon'),
            mpf.make_addplot((aroon_talib["aroon_up"]), ax=axis)
        ]

    return plot

def aroonosc_addplot(data, settings, axis=None, panel=None):
    aroonosc = talib.AROONOSC(data['High'], data['Low'], settings[0])
    aroon_talib = pd.DataFrame(index=data.index,
                            data={"aroonosc": aroonosc})

    if axis is None:
        plot = [
            mpf.make_addplot((aroon_talib["aroonosc"]),  panel=panel, ylabel='Aroon Oscillator')
        ]

    elif panel is None:
        plot = [
            mpf.make_addplot((aroon_talib["aroonosc"]), ax=axis, ylabel='Aroon Oscillator')
        ]

    return plot

def ao_addplot(data, axis=None, panel=None, fastma_period=5, slowma_period=34):
    ao = momentum.awesome_oscillator(data['High'], data['Low'], fastma_period, slowma_period)
    ao_ta = pd.DataFrame(index=data.index,
                            data={"ao": ao})

    if axis is None:
        plot = [
            mpf.make_addplot((ao_ta["ao"]),  panel=panel, ylabel='Awesome Oscillator')
        ]

    elif panel is None:
        plot = [
            mpf.make_addplot((ao_ta["ao"]), ax=axis, ylabel='Awesome Oscillator')
        ]

    return plot

def bop_addplot(data, _, axis=None, panel=None):
    bop = talib.BOP(data['Open'], data['High'], data['Low'], data['Close'])
    bop_talib = pd.DataFrame(index=data.index,
                            data={"bop": bop})
    if axis is None:
        plot = [
            mpf.make_addplot((bop_talib["bop"]),  panel=panel, ylabel='Balance of Power')
        ]

    elif panel is None:
        plot = [
            mpf.make_addplot((bop_talib["bop"]), ax=axis, ylabel='Balance of Power')
        ]

    return plot

def cci_addplot(data, settings, axis=None, panel=None):
    cci = talib.CCI(data['High'], data['Low'], data['Close'], settings[0])
    cci_talib = pd.DataFrame(index=data.index,
                            data={"cci": cci})

    if axis is None:
        plot = [
            mpf.make_addplot((cci_talib["cci"]), panel=panel, ylabel='Commodity Channel Index')
        ]

    elif panel is None:
        plot = [
            mpf.make_addplot((cci_talib["cci"]), ax=axis, ylabel='Commodity Channel Index')
        ]

    return plot

def cmo_addplot(data, settings, axis=None, panel=None):
    cmo = talib.CMO(data['Close'], settings[0])
    cmo_talib = pd.DataFrame(index=data.index,
                            data={"cmo": cmo})

    if axis is None:
        plot = [
            mpf.make_addplot((cmo_talib["cmo"]),  panel=panel, ylabel='Chande Momentum Oscillator')
        ]

    elif panel is None:
        plot = [
            mpf.make_addplot((cmo_talib["cmo"]), ax=axis, ylabel='Chande Momentum Oscillator')
        ]

    return plot

def dx_addplot(data, settings, axis=None, panel=None):
    dx = talib.DX(data['High'], data['Low'], data['Close'], settings[0])
    dx_talib = pd.DataFrame(index=data.index,
                            data={"dx": dx})

    if axis is None:
        plot = [
            mpf.make_addplot((dx_talib["dx"]),  panel=panel, ylabel='Directional Movement Index')
        ]

    elif panel is None:
        plot = [
            mpf.make_addplot((dx_talib["dx"]), ax=axis, ylabel='Directional Movement Index')
        ]

    return plot

def kama_addplot(data, settings, axis=None, panel=None):
    kama = momentum.kama(data['Close'], settings[0], settings[1], settings[2])
    kama_ta = pd.DataFrame(index=data.index,
                            data={"kama": kama})

    if axis is None:
        plot = [
            mpf.make_addplot((kama_ta["kama"]),  panel=panel, ylabel='KAMA Indicator')
        ]

    elif panel is None:
        plot = [
            mpf.make_addplot((kama_ta["kama"]), ax=axis, ylabel='Kama Indicator')
        ]

    return plot


def macdext_addplot(data, settings, axis=None, panel=None):
    macd, macdsignal, macdhist = talib.MACDEXT(data['Close'], settings[0], settings[1], settings[2], settings[3], settings[4], settings[5])
    macd_talib = pd.DataFrame(index=data.index,
                            data={"macd": macd,
                                  "macd_signal" : macdsignal,
                                  "macd_hist" : macdhist})

    if axis is None:
        plot = [
            mpf.make_addplot((macd_talib["macd"]),  panel=panel, ylabel='MACD'),
            mpf.make_addplot((macd_talib["macd_signal"]),  panel=panel),
            mpf.make_addplot((macd_talib["macd_hist"]), type='bar',  panel=panel)
        ]

    elif panel is None:
        plot = [
            mpf.make_addplot((macd_talib["macd"]), ax=axis, ylabel='MACD'),
            mpf.make_addplot((macd_talib["macd_signal"]),  ax=axis),
            mpf.make_addplot((macd_talib["macd_hist"]), type='bar', ax=axis)
        ]

    return plot

def macdfix_addplot(data, axis=None, panel=None, signalperiod=9):
    macd, macdsignal, macdhist = talib.MACDFIX(data['Close'], signalperiod)
    macd_talib = pd.DataFrame(index=data.index,
                            data={"macd": macd,
                                  "macd_signal" : macdsignal,
                                  "macd_hist" : macdhist})

    if axis is None:
        plot = [
            mpf.make_addplot((macd_talib["macd"]),  panel=panel, ylabel='Fixed MACD'),
            mpf.make_addplot((macd_talib["macd_signal"]),  panel=panel),
            mpf.make_addplot((macd_talib["macd_hist"]), type='bar',  panel=panel)
        ]

    elif panel is None:
        plot = [
            mpf.make_addplot((macd_talib["macd"]), ax=axis, ylabel='Fixed MACD'),
            mpf.make_addplot((macd_talib["macd_signal"]),  ax=axis),
            mpf.make_addplot((macd_talib["macd_hist"]), type='bar', ax=axis)
        ]

    return plot

def mfi_addplot(data, settings, axis=None, panel=None):
    mfi = talib.MFI(data['High'], data['Low'], data['Close'], data['Volume'], settings[0])
    mfi_talib = pd.DataFrame(index=data.index,
                            data={"mfi": mfi})

    if axis is None:
        plot = [
            mpf.make_addplot((mfi_talib["mfi"]), panel=panel, ylabel='Money Flow Index')
        ]

    elif panel is None:
        plot = [
            mpf.make_addplot((mfi_talib["mfi"]), ax=axis, ylabel='Money Flow Index')
        ]

    return plot

def minusdi_addplot(data, settings, axis=None, panel=None):
    minusdi = talib.MINUS_DI(data['High'], data['Low'], data['Close'], settings[0])
    minusdi_talib = pd.DataFrame(index=data.index,
                            data={"minus_di": minusdi})

    if axis is None:
        plot = [
            mpf.make_addplot((minusdi_talib["minus_di"]), panel=panel, ylabel='Minus Directional Indicator')
        ]

    elif panel is None:
        plot = [
            mpf.make_addplot((minusdi_talib["minus_di"]), ax=axis, ylabel='Minus Directional Indicator')
        ]

    return plot

def minusdm_addplot(data, settings, axis=None, panel=None):
    minusdm = talib.MINUS_DM(data['High'], data['Low'], settings[0])
    minusdm_talib = pd.DataFrame(index=data.index,
                            data={"minus_dm": minusdm})

    if axis is None:
        plot = [
            mpf.make_addplot((minusdm_talib["minus_dm"]), panel=panel, ylabel='Minus Directional Movement')
        ]

    elif panel is None:
        plot = [
            mpf.make_addplot((minusdm_talib["minus_dm"]), ax=axis, ylabel='Minus Directional Movement')
        ]

    return plot

def mom_addplot(data, settings, axis=None, panel=None):
    mom = talib.MOM(data['Close'], settings[0])
    mom_talib = pd.DataFrame(index=data.index,
                            data={"mom": mom})

    if axis is None:
        plot = [
            mpf.make_addplot((mom_talib["mom"]), panel=panel, ylabel='Momentum')
        ]

    elif panel is None:
        plot = [
            mpf.make_addplot((mom_talib["mom"]), ax=axis, ylabel='Momentum')
        ]

    return plot

def plusdi_addplot(data, settings, axis=None, panel=None):
    plusdi = talib.PLUS_DI(data['High'], data['Low'], data['Close'], settings[0])
    plusdi_talib = pd.DataFrame(index=data.index,
                            data={"plusdi": plusdi})

    if axis is None:
        plot = [
            mpf.make_addplot((plusdi_talib["plusdi"]), panel=panel, ylabel='Plus Directional Indicator')
        ]

    elif panel is None:
        plot = [
            mpf.make_addplot((plusdi_talib["plusdi"]), ax=axis, ylabel='Plus Directional Indicator')
        ]

    return plot

def plusdm_addplot(data, settings, axis=None, panel=None):
    plusdm = talib.PLUS_DM(data['High'], data['Low'], settings[0])
    plusdm_talib = pd.DataFrame(index=data.index,
                            data={"plusdm": plusdm})

    if axis is None:
        plot = [
            mpf.make_addplot((plusdm_talib["plusdm"]), panel=panel, ylabel='Plus Directional Movement')
        ]

    elif panel is None:
        plot = [
            mpf.make_addplot((plusdm_talib["plusdm"]), ax=axis, ylabel='Plus Directional Movement')
        ]

    return plot

def ppo_addplot(data, axis=None, panel=None, fastperiod=12, slowperiod=26, matype=0):
    ppo = talib.PPO(data['Close'], fastperiod, slowperiod, matype)
    ppo_talib = pd.DataFrame(index=data.index,
                            data={"ppo": ppo})

    if axis is None:
        plot = [
            mpf.make_addplot((ppo_talib["ppo"]), panel=panel, ylabel='Percentage Price Oscillator')
        ]

    elif panel is None:
        plot = [
            mpf.make_addplot((ppo_talib["ppo"]), ax=axis, ylabel='Percentage Price Oscillator')
        ]

    return plot

def pvo_addplot(data, settings, axis=None, panel=None):
    pvo = momentum.pvo(data['Volume'], settings[0], settings[1], settings[2])
    pvo_ta = pd.DataFrame(index=data.index,
                            data={"pvo": pvo})

    if axis is None:
        plot = [
            mpf.make_addplot((pvo_ta["pvo"]), panel=panel, ylabel='Percentage Volume Oscillator')
        ]

    elif panel is None:
        plot = [
            mpf.make_addplot((pvo_ta["pvo"]), ax=axis, ylabel='Percentage Volume Oscillator')
        ]

    return plot

def roc_addplot(data, settings, axis=None, panel=None):
    roc = talib.ROC(data['Close'], settings[0])
    roc_talib = pd.DataFrame(index=data.index,
                            data={"roc": roc})

    if axis is None:
        plot = [
            mpf.make_addplot((roc_talib["roc"]), panel=panel, ylabel='Rate of Change ($)')
        ]

    elif panel is None:
        plot = [
            mpf.make_addplot((roc_talib["roc"]), ax=axis, ylabel='Rate of Change ($)')
        ]

    return plot

def rocpercentage_addplot(data, settings, axis=None, panel=None):
    rocp = talib.ROCP(data['Close'], settings[0])
    rocp_talib = pd.DataFrame(index=data.index,
                            data={"rocp": rocp})

    if axis is None:
        plot = [
            mpf.make_addplot((rocp_talib["rocp"]), panel=panel, ylabel='Rate of Change (%)')
        ]

    elif panel is None:
        plot = [
            mpf.make_addplot((rocp_talib["rocp"]), ax=axis, ylabel='Rate of Change (%)')
        ]

    return plot

def rocratio_addplot(data, settings, axis=None, panel=None):
    rocr = talib.ROCR(data['Close'], settings[0])
    rocr_talib = pd.DataFrame(index=data.index,
                            data={"rocr": rocr})

    if axis is None:
        plot = [
            mpf.make_addplot((rocr_talib["rocr"]), panel=panel, ylabel='Rate of Change (Ratio)')
        ]

    elif panel is None:
        plot = [
            mpf.make_addplot((rocr_talib["rocr"]), ax=axis, ylabel='Rate of Change (Ratio)')
        ]

    return plot

def rocratio100_addplot(data, settings, axis=None, panel=None):
    rocr = talib.ROCR100(data['Close'], settings[0])
    rocr_talib = pd.DataFrame(index=data.index,
                            data={"rocr": rocr})

    if axis is None:
        plot = [
            mpf.make_addplot((rocr_talib["rocr"]), panel=panel, ylabel='Rate of Change (Ratio, 100 scale)')
        ]

    elif panel is None:
        plot = [
            mpf.make_addplot((rocr_talib["rocr"]), ax=axis, ylabel='Rate of Change (Ratio, 100 scale)')
        ]

    return plot

def rsi_addplot(data, settings, axis=None, panel=None):
    rsi = talib.RSI(data['Close'], settings[0])
    rsi_talib = pd.DataFrame(index=data.index,
                            data={"rsi": rsi})

    if axis is None:
        plot = [
            mpf.make_addplot((rsi_talib["rsi"]), panel=panel, ylabel='Relative Strength Index')
        ]

    elif panel is None:
        plot = [
            mpf.make_addplot((rsi_talib["rsi"]), ax=axis, ylabel='Relative Strength Index')
        ]

    return plot

def slowstoch_addplot(data, settings, axis=None, panel=None):
    slowk, slowd = talib.STOCH(data['High'], data['Low'], data['Close'], settings[0], settings[1], settings[2], settings[3], settings[4])
    stoch_talib = pd.DataFrame(index=data.index,
                            data={"slowk" : slowk,
                                  "slowd" : slowd})

    if axis is None:
        plot = [
            mpf.make_addplot((stoch_talib["slowk"]), panel=panel, ylabel='Slow Stochastic'),
            mpf.make_addplot((stoch_talib["slowd"]), panel=panel)
        ]

    elif panel is None:
        plot = [
            mpf.make_addplot((stoch_talib["slowk"]), ax=axis, ylabel='Slow Stochastic'),
            mpf.make_addplot((stoch_talib["slowd"]), ax=axis)
        ]

    return plot

def faststoch_addplot(data, settings, axis=None, panel=None):
    fastk, fastd = talib.STOCHF(data['High'], data['Low'], data['Close'], settings[0], settings[1], settings[2])
    stoch_talib = pd.DataFrame(index=data.index,
                            data={"fastk" : fastk,
                                  "fastd" : fastd})

    if axis is None:
        plot = [
            mpf.make_addplot((stoch_talib["fastk"]), panel=panel, ylabel='Fast Stochastic'),
            mpf.make_addplot((stoch_talib["fastd"]), panel=panel)
        ]

    elif panel is None:
        plot = [
            mpf.make_addplot((stoch_talib["fastk"]), ax=axis, ylabel='Fast Stochastic'),
            mpf.make_addplot((stoch_talib["fastd"]), ax=axis)
        ]

    return plot

def stochrsi_addplot(data, settings, axis=None, panel=None):
    fastk, fastd = talib.STOCHRSI(data['Close'], settings[0], settings[1], settings[2], settings[3])
    stoch_talib = pd.DataFrame(index=data.index,
                            data={"fastk" : fastk,
                                  "fastd" : fastd})

    if axis is None:
        plot = [
            mpf.make_addplot((stoch_talib["fastk"]), panel=panel, ylabel='Stochastic RSI'),
            mpf.make_addplot((stoch_talib["fastd"]), panel=panel)
        ]

    elif panel is None:
        plot = [
            mpf.make_addplot((stoch_talib["fastk"]), ax=axis, ylabel='Stochastic RSI'),
            mpf.make_addplot((stoch_talib["fastd"]), ax=axis)
        ]

    return plot

def tsi_addplot(data, settings, axis=None, panel=None):
    tsi = ta.momentum.tsi(data['Close'], settings[0], settings[1])
    tsi_ta = pd.DataFrame(index=data.index,
                            data={"tsi": tsi})
    if axis is None:
        plot = [
            mpf.make_addplot((tsi_ta["tsi"]), panel=panel, ylabel='True Strength Index')
        ]

    elif panel is None:
        plot = [
            mpf.make_addplot((tsi_ta["tsi"]), ax=axis, ylabel='True Strength Index')
        ]
    return plot


def ultosc_addplot(data, settings, axis=None, panel=None):
    ultosc = talib.ULTOSC(data['High'], data['Low'], data['Close'], settings[0], settings[1], settings[2])
    ultosc_talib = pd.DataFrame(index=data.index,
                            data={"ultosc": ultosc})

    if axis is None:
        plot = [
            mpf.make_addplot((ultosc_talib["ultosc"]), panel=panel, ylabel='Ultimate Oscillator')
        ]

    elif panel is None:
        plot = [
            mpf.make_addplot((ultosc_talib["ultosc"]), ax=axis, ylabel='Ultimate Oscillator')
        ]

    return plot


def willr_addplot(data, settings, axis=None, panel=None):
    willr = talib.WILLR(data['High'], data['Low'], data['Close'], settings[0])
    willr_talib = pd.DataFrame(index=data.index,
                            data={"willr": willr})

    if axis is None:
        plot = [
            mpf.make_addplot((willr_talib["willr"]), panel=panel, ylabel="Williams' %R")
        ]

    elif panel is None:
        plot = [
            mpf.make_addplot((willr_talib["willr"]), ax=axis, ylabel="Williams' %r")
        ]

    return plot


####################
# Trend Indicators #
####################


def dpo_addplot(data, settings, axis=None, panel=None):
    dpo = trend.dpo(data['Close'], settings[0])
    dpo_ta = pd.DataFrame(index=data.index,
                            data={"dpo": dpo})
    if axis is None:
        plot = [
            mpf.make_addplot((dpo_ta["dpo"]), panel=panel, ylabel="Detrended Price Oscillator")
        ]

    elif panel is None:
        plot = [
            mpf.make_addplot((dpo_ta["dpo"]), ax=axis, ylabel="Detrended Price Oscillator")
        ]
    return plot


def ichimoku_addplot(data, settings, axis=None, panel=None):
    ichimoku = trend.IchimokuIndicator(data['High'], data['Low'], settings[0], settings[1], settings[2], settings[3])
    ichimoku_ta = pd.DataFrame(index=data.index,
                            data={"ichimoku_a" : ichimoku.ichimoku_a(),
                                  "ichimoku_b" : ichimoku.ichimoku_b(),
                                  "ichimoku_conversion" : ichimoku.ichimoku_conversion_line(),
                                  "ichimoku_baseline" : ichimoku.ichimoku_base_line()})

    if axis is None:
        plot = [
            mpf.make_addplot((ichimoku_ta["ichimoku_a"]), panel=panel),
            mpf.make_addplot((ichimoku_ta["ichimoku_b"]), panel=panel),
            mpf.make_addplot((ichimoku_ta["ichimoku_conversion"]), panel=panel),
            mpf.make_addplot((ichimoku_ta["ichimoku_baseline"]), panel=panel)
        ]

    elif panel is None:
        plot = [
            mpf.make_addplot((ichimoku_ta["ichimoku_a"]), ax=axis),
            mpf.make_addplot((ichimoku_ta["ichimoku_b"]), ax=axis),
            mpf.make_addplot((ichimoku_ta["ichimoku_conversion"]), ax=axis),
            mpf.make_addplot((ichimoku_ta["ichimoku_baseline"]), ax=axis)
        ]

    return plot


def schaff_addplot(data, settings, axis=None, panel=None):
    """
    settings: a list with 5 items (MACD slow period length, MACD fast period length, cycle length, stochk EMA period, stockd EMA period)
    """
    schaff = trend.stc(data['Close'], settings[0], settings[1], settings[2], settings[3], settings[4])
    schaff_ta = pd.DataFrame(index=data.index,
                            data={"schaff": schaff})
    if axis is None:
        plot = [
            mpf.make_addplot((schaff_ta["schaff"]), panel=panel, ylabel="Schaff Trend Cycle")
        ]

    elif panel is None:
        plot = [
            mpf.make_addplot((schaff_ta["schaff"]), ax=axis, ylabel="Schaff Trend Cycle")
        ]
    return plot


def parabolicsar_addplot(data, settings, axis=None, panel=None):
    """
    settings: a list with two items (the acceleration factor and the maximum allowed acceleration factor)
    """
    psar = trend.PSARIndicator(data['High'], data['Low'], data['Close'], settings[0], settings[1])
    psar_ta = pd.DataFrame(index=data.index,
                            data={"up" : psar.psar_up(),
                                  "down" : psar.psar_down()})
    if axis is None:
        plot = [
            mpf.make_addplot((psar_ta["up"]), panel=panel),
            mpf.make_addplot((psar_ta["down"]), panel=panel)
        ]

    elif panel is None:
        plot = [
            mpf.make_addplot((psar_ta["up"]), ax=axis),
            mpf.make_addplot((psar_ta["down"]), ax=axis)
        ]
    return plot


def kst_addplot(data, settings, axis=None, panel=None):
    kst = trend.KSTIndicator(data['Close'], settings[0], settings[1], settings[2], settings[3], settings[4], settings[5], settings[6], settings[7], settings[8])
    kst_ta = kst_ta = pd.DataFrame(index=data.index,
                            data={"kst" : kst.kst(),
                                  "signal" : kst.kst_sig()})
    if axis is None:
        plot = [
            mpf.make_addplot((kst_ta["kst"]), panel=panel),
            mpf.make_addplot((kst_ta["signal"]), panel=panel)
        ]

    elif panel is None:
        plot = [
            mpf.make_addplot((kst_ta["kst"]), ax=axis),
            mpf.make_addplot((kst_ta["signal"]), ax=axis)
        ]
    return plot


def trix_addplot(data, settings, axis=None, panel=None):
    """
    settings: a list with one item (the lookback period)
    """
    trix = trend.trix(data['Close'], settings[0])
    trix_ta = pd.DataFrame(index=data.index,
                            data={"trix": trix})
    if axis is None:
        plot = [
            mpf.make_addplot((trix_ta["trix"]), panel=panel, ylabel="Trix Indicator")
        ]

    elif panel is None:
        plot = [
            mpf.make_addplot((trix_ta["trix"]), ax=axis, ylabel="Trix Indicator")
        ]
    return plot


def mi_addplot(data, settings, axis=None, panel=None):
    """
    settings: a list with two items (the fast window value and the slow window value)
    """

    mi = trend.mass_index(data['High'], data['Low'], settings[0], settings[1])
    mi_ta = pd.DataFrame(index=data.index,
                            data={"mi": mi})
    if axis is None:
        plot = [
            mpf.make_addplot((mi_ta["mi"]), panel=panel, ylabel="Mass Index")
        ]

    elif panel is None:
        plot = [
            mpf.make_addplot((mi_ta["mi"]), ax=axis, ylabel="Mass Index")
        ]
    return plot


def vortex_addplot(data, settings, axis=None, panel=None):
    """
    settings: a list with one item (the lookback period)
    """
    vortex = trend.VortexIndicator(data['High'], data['Low'], data['Close'], settings[0])
    vortex_ta = pd.DataFrame(index=data.index,
                            data={"vortex_pos" : vortex.vortex_indicator_pos(),
                                  "vortex_neg" : vortex.vortex_indicator_neg()})
    if axis is None:
        plot = [
            mpf.make_addplot((vortex_ta["vortex_pos"]), panel=panel, ylabel="Vortex"),
            mpf.make_addplot((vortex_ta["vortex_neg"]), panel=panel)
        ]

    elif panel is None:
        plot = [
            mpf.make_addplot((vortex_ta["vortex_pos"]), ax=axis, ylabel="Vortex"),
            mpf.make_addplot((vortex_ta["vortex_neg"]), ax=axis)
        ]
    return plot