# Started by Ray Ikome on 11/16/22
import sys
from locale import atof, setlocale, LC_NUMERIC
from threading import Thread, Event
import time
import pandas as pd
import os

from PySide6.QtCharts import QChart, QChartView, QPieSlice, QPieSeries, QLineSeries, QDateTimeAxis, QValueAxis, QAbstractAxis, QBarSeries, QBarSet
from PySide6.QtWidgets import (QWidget, QTabWidget, QGroupBox, QLabel, QTableWidget, QTableWidgetItem, QAbstractItemView,
                                QSplashScreen, QPushButton, QDialog, QLineEdit, QComboBox, QRadioButton, QCalendarWidget, QCheckBox, QSizePolicy
                                , QApplication, QProgressBar, QVBoxLayout, QHeaderView, QTableView, QScrollArea, QButtonGroup, QSlider)
from PySide6.QtGui import QFont, QFontDatabase, QPixmap, QIcon, QPainter, QColor
from PySide6.QtCore import QRect, QCoreApplication, QStringListModel, QAbstractItemModel, QDateTime, Qt, SIGNAL
import yfinance as yf
import talib
import mplfinance as mpf
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import xml.etree.ElementTree as et

from dependencies import autocomplete as ac
from dependencies import IsMarketOpen as mktopen
from dependencies import dcfmodel as dcf
from dependencies import numberformat as nf

tab2_isloaded = False
tab3_isloaded = False
tab4_isloaded = False

currentdir = os.getcwd() + '\\'

current_ticker = ''

def spy_button_clicked():
    """Is called when the "Chart SPY" button is clicked. Charts SPY with the current user settings"""
    chart_dialog.search_bar_groupbox.searchBar.setText("SPY - SPDR S&P 500 ETF Trust")
    searchButtonClicked()


def qqq_button_clicked():
    """Is called when the "Chart QQQ" button is clicked. Charts QQQ with the current user settings"""
    chart_dialog.search_bar_groupbox.searchBar.setText("QQQ - Invesco QQQ Trust")
    searchButtonClicked()


def dia_button_clicked():
    """Is called when the "Chart DIA" button is clicked. Charts DIA with the current user settings"""
    chart_dialog.search_bar_groupbox.searchBar.setText("DIA - SPDR Dow Jones Industrial Average ETF Trust")
    searchButtonClicked()


def vix_button_clicked():
    """Is called when the "Chart VIX" button is clicked. Charts VIX with the current user settings"""
    chart_dialog.search_bar_groupbox.searchBar.setText("^VIX ")
    searchButtonClicked()


def update_ui():
    """
    TO BE RUN BY THE UI UPDATE THREAD ONLY
    Updates each element of the portfolio dialog 
    if the user is on the portfolio dialog, updates
    each element of the wallet dialog if the user
    is on the wallet dialog. Runs as long as the
    program is running
    """
    while True:
        if(mktopen.isMarketOpen()):
            if widget.currentWidget() == portfolio_dialog:
                update_portfolio_table()
                update_watchlist_tickers()
                update_portfolio_nav()
                update_portfolio_piechart()
            elif widget.currentWidget() == wallet_dialog:
                update_wallet_table()
                time.sleep(5)
            else:
                time.sleep(1)
        else:
            time.sleep(1)
        
        
def update_portfolio_piechart():
    """
    Updates the asset class piechart on the portfolio dialog
    """

    # gets the present value of the portfolio broken down by asset type
    cash_amount = 0
    etf_amount = 0
    stock_amount = 0
    option_amount = 0
    futures_amount = 0
    
    # can't use enumerate, index is useful here
    for idx, amount in enumerate(portfolio_amts):
        match portfolio_asset_types[idx].text:
            case "ETF":
                etf_amount += int(amount.text) * float(portfolio_dialog.positions_view_groupbox.positions_view.item(idx - 1, 2).text()[1:])
            case "Liquidity":
                cash_amount += float(amount.text)
            case "Stock":
                stock_amount += int(amount.text) * float(portfolio_dialog.positions_view_groupbox.positions_view.item(idx - 1, 2).text()[1:])
            case "Futures":
                futures_amount += int(amount.text) * float(portfolio_dialog.positions_view_groupbox.positions_view.item(idx - 1, 2).text()[1:])
            case "Option":
                option_amount += int(amount.text) * float(portfolio_dialog.positions_view_groupbox.positions_view.item(idx - 1, 2).text()[1:])

    # loads values into pie chart and displays them
    asset_class_chart.slices()[0].setValue(round(etf_amount / portfolio_nav * 100, 2))
    if(etf_amount != 0):
        asset_class_chart.slices()[0].setLabel(f"ETFs: {round(etf_amount / portfolio_nav * 100, 2)}%")
        asset_class_chart.slices()[0].setLabelVisible(True)
    
    asset_class_chart.slices()[1].setValue(round(stock_amount / portfolio_nav * 100, 2))
    if(stock_amount != 0):
        asset_class_chart.slices()[1].setLabel(f"Stocks: {round(stock_amount / portfolio_nav * 100, 2)}%")
        asset_class_chart.slices()[1].setLabelVisible(True)

    asset_class_chart.slices()[2].setValue(option_amount / portfolio_nav * 100)
    if(option_amount != 0):
        asset_class_chart.slices()[2].setLabel(f"Options: {round(option_amount / portfolio_nav * 100, 2)}%")
        asset_class_chart.slices()[2].setLabelVisible(True)

    asset_class_chart.slices()[3].setValue(futures_amount / portfolio_nav * 100)
    if(futures_amount != 0):
        asset_class_chart.slices()[3].setLabel(f"Futures: {round(futures_amount / portfolio_nav * 100, 2)}%")
        asset_class_chart.slices()[3].setLabelVisible(True)

    asset_class_chart.slices()[4].setValue(cash_amount / portfolio_nav * 100)
    if(cash_amount != 0):
        asset_class_chart.slices()[4].setLabel(f"Cash: {round(cash_amount / portfolio_nav * 100, 2)}%")
        asset_class_chart.slices()[4].setLabelVisible(True)
    

def update_wallet_table():
    """
    Updates the positions table on the crypto wallet dialog.
    """
    # can't use enumerate, index is useful here
    for i in range(1, len(wallet_tickers)):

            # get the current price and the price it last closed at
            ticker = yf.download(tickers=wallet_tickers[i].text, period='5d')

            # edge case where yf.download returns a dataframe of size 4
            try:
                ticker_current = ticker.iloc[4][3]
                ticker_last_close = ticker.iloc[3][3]
            except IndexError:
                ticker_current = ticker.iloc[3][3]
                ticker_last_close = ticker.iloc[2][3]

            # calculate the return since the position was opened in dollar and percent terms
            total_return = (ticker_current - float(wallet_costbases[i - 1].text)) * float(wallet_amts[i].text)
            percent_change = round(total_return / (float(wallet_costbases[i - 1].text) * float(wallet_amts[i].text)) * 100, 2)

            # update the table with the new information

            # first cell in the row is the coin symbol
            wallet_dialog.positions_view_groupbox.positions_view.setItem(i - 1, 0, QTableWidgetItem(wallet_tickers[i].text.upper()))

            # second cell is the coin's performance icon
            wallet_dialog.positions_view_groupbox.positions_view.setItem(i - 1, 1, updateTickerIcon(ticker))

            # third cell is the coin's current price
            wallet_dialog.positions_view_groupbox.positions_view.setItem(i - 1, 2, QTableWidgetItem('${:0,.2f}'.format(ticker_current)))

            # fourth cell is the change in the coin's price from it's last close, in dollar and percent terms
            wallet_dialog.positions_view_groupbox.positions_view.setItem(i - 1, 3, QTableWidgetItem('${:0,.2f}'.format(ticker_current - ticker_last_close) + " (" + str(round(((ticker_current - ticker_last_close) / ticker_last_close * 100), 2)) + "%)"))
            
            # fifth cell is the user's costbasis for the token
            wallet_dialog.positions_view_groupbox.positions_view.setItem(i - 1, 4, QTableWidgetItem('${:0,.2f}'.format(float(wallet_costbases[i - 1].text))))

            # sixth cell is the amount of the coin the user has (or is short)
            wallet_dialog.positions_view_groupbox.positions_view.setItem(i - 1, 5, QTableWidgetItem(wallet_amts[i].text))

            # seventh cell is the NLV the user has in the coin
            wallet_dialog.positions_view_groupbox.positions_view.setItem(i - 1, 6, QTableWidgetItem('${:0,.2f}'.format(ticker_current * float(wallet_amts[i].text))))

            # eighth cell is the user's net P/L on the position from when it was opened
            wallet_dialog.positions_view_groupbox.positions_view.setItem(i - 1, 7, QTableWidgetItem('${:0,.2f}'.format(((ticker_current - float(wallet_costbases[i - 1].text)) * float(wallet_amts[i].text)))))

            # ninth cell is the total return on the position in % terms
            wallet_dialog.positions_view_groupbox.positions_view.setItem(i - 1, 8, QTableWidgetItem('${:0,.2f}'.format(total_return) + " (" + str(percent_change) + "%)"))
        
    
def update_portfolio_table():
    """
    Updates the table with all the user's positions in the portfolio dialog
    """
    # for each asset in the portfolio
    for i in range(1, len(portfolio_tickers)):
    
        # get the current price and the price it last closed at
        ticker = yf.download(tickers=portfolio_tickers[i].text, period='5d')
        ticker_current = ticker.iloc[4][3]
        ticker_last_close = ticker.iloc[3][3]
        # calculate the return since the position was opened in dollar and percent terms
        total_return = (ticker_current - float(purchase_prices[i - 1].text)) * int(portfolio_amts[i].text)
        percent_change = round(total_return / (float(purchase_prices[i - 1].text) * float(portfolio_amts[i].text)) * 100, 2)
        # update the table with the new information
        portfolio_dialog.positions_view_groupbox.positions_view.setItem(i - 1, 0, QTableWidgetItem(portfolio_tickers[i].text.upper()))
        portfolio_dialog.positions_view_groupbox.positions_view.setItem(i - 1, 1, updateTickerIcon(ticker))
        portfolio_dialog.positions_view_groupbox.positions_view.setItem(i - 1, 2, QTableWidgetItem('${:0,.2f}'.format(ticker_current)))
        portfolio_dialog.positions_view_groupbox.positions_view.setItem(i - 1, 3, QTableWidgetItem('${:0,.2f}'.format(ticker_current - ticker_last_close) + " (" + str(round(((ticker_current - ticker_last_close) / ticker_last_close * 100), 2)) + "%)"))
        portfolio_dialog.positions_view_groupbox.positions_view.setItem(i - 1, 4, QTableWidgetItem('${:0,.2f}'.format(float(purchase_prices[i - 1].text))))
        portfolio_dialog.positions_view_groupbox.positions_view.setItem(i - 1, 5, QTableWidgetItem(portfolio_amts[i].text))
        portfolio_dialog.positions_view_groupbox.positions_view.setItem(i - 1, 6, QTableWidgetItem('${:0,.2f}'.format(ticker_current * int(portfolio_amts[i].text))))
        portfolio_dialog.positions_view_groupbox.positions_view.setItem(i - 1, 7, QTableWidgetItem('${:0,.2f}'.format(((ticker_current - float(purchase_prices[i - 1].text)) * int(portfolio_amts[i].text)))))
        portfolio_dialog.positions_view_groupbox.positions_view.setItem(i - 1, 7, QTableWidgetItem('${:0,.2f}'.format(total_return) + " (" + str(percent_change) + "%)"))
        

def update_watchlist_tickers():
    """
    Updates the table with all the tickers in the user's watchlist in the portfolio dialog
    """

    # for each ticker in the watchlist
    for idx, item in enumerate(watchlist_tickers):
        
        
        ticker = yf.download(tickers=item.text, period='5d')
        ticker_current = ticker.iloc[4][3]
        ticker_last_close = ticker.iloc[3][3]

        portfolio_dialog.watchlist_groupbox.watchlist_view.setItem(idx, 0, QTableWidgetItem(item.text.upper()))
        portfolio_dialog.watchlist_groupbox.watchlist_view.setItem(idx, 1, updateTickerIcon(ticker))
        portfolio_dialog.watchlist_groupbox.watchlist_view.setItem(idx, 2, QTableWidgetItem('${:0,.2f}'.format(ticker_current)))
        
        portfolio_dialog.watchlist_groupbox.watchlist_view.setItem(idx, 3, QTableWidgetItem('${:0,.2f}'.format(ticker_current - ticker_last_close) + " (" + str(round(((ticker_current - ticker_last_close) / ticker_last_close * 100), 2)) + "%)"))


def daterange_radiobutton_clicked():
    """
    Should run only when the player clicks the "Chart by Date Range" radiobutton on the "Chart Stocks" dialog.
    Disables the combobox that lets the user select a period to chart over and enables the calendars so that 
    the user can pick a start and end date for the chart.
    """
    chart_dialog.settings_groupbox.start_date.setEnabled(True)
    chart_dialog.settings_groupbox.end_date.setEnabled(True)
    chart_dialog.settings_groupbox.data_period_combobox.setEnabled(False)


def period_radiobutton_clicked():
    """
    Should run only when the player clicks the "Chart by Period" radiobutton on the "Chart Stocks" dialog.
    Disables the calendars that let the user select a start and end date for the chart and enables the period 
    combobox so that the user can pick a start and end date for the chart.
    """
    chart_dialog.settings_groupbox.start_date.setEnabled(False)
    chart_dialog.settings_groupbox.end_date.setEnabled(False)
    chart_dialog.settings_groupbox.data_period_combobox.setEnabled(True)


def searchTextChanged(txt: str):
    """
    Executed when text is typed into the search bar on the "Chart Stocks" tab.
    The function takes the entered text and appends it to the search bar.
    """
    chart_dialog.search_bar_groupbox.searchBar.setText(txt.upper())


def searchButtonClicked():
    """
    Shows graph for the ticker in the search bar when the search button is pressed.
    """
    # gets the stock ticker from the search bar
    ticker = ''
    i = 0
    while chart_dialog.search_bar_groupbox.searchBar.text()[i] != ' ':
        ticker += chart_dialog.search_bar_groupbox.searchBar.text()[i]
        i += 1

    # get the interval the user selected
    interval = chart_dialog.settings_groupbox.data_timeframe_combobox.currentText()

    # get all chart settings the user selected on the chart menu
    include_prepost = False
    if(chart_dialog.settings_groupbox.prepost_checkbox.isChecked()):
        include_prepost = True

    adjust_ohlc = False
    if(chart_dialog.settings_groupbox.adjust_ohlc_checkbox.isChecked()):
        adjust_ohlc = True
    
    split_dividend = False
    if(chart_dialog.settings_groupbox.split_dividend_checkbox.isChecked()):
        split_dividend = True

    include_volume = False
    if(chart_dialog.settings_groupbox.volume_checkbox.isChecked()):
        include_volume = True

    non_trading = False
    if(chart_dialog.settings_groupbox.nontrading_checkbox.isChecked()):
        non_trading = True

    start_date = None
    end_date = None

   # shows the requested ticker's chart
    if(chart_dialog.settings_groupbox.daterange_radiobutton.isChecked()):
        start_date = chart_dialog.settings_groupbox.start_date.selectedDate().toString("yyyy-MM-dd")
        end_date = chart_dialog.settings_groupbox.end_date.selectedDate().toString("yyyy-MM-dd")
        show_graph(yf.download(tickers=ticker,
                              start=start_date,
                              end=end_date, 
                              interval=interval,
                              prepost=include_prepost,
                              auto_adjust=adjust_ohlc,
                              actions=split_dividend
                              ), ticker, include_volume, non_trading)
    else:
        # only get period if user chose to chart by period
        period = chart_dialog.settings_groupbox.data_period_combobox.currentText()
        show_graph(yf.download(tickers=ticker,
                              period=period,
                              interval=interval,
                              prepost=include_prepost,
                              auto_adjust=adjust_ohlc,
                              actions=split_dividend
                              ), ticker, include_volume, non_trading)
                              

def updateTickerIcon(ticker) -> QTableWidgetItem:
    """
    Updates the performance icon for the given stock

        ticker : pandas.DataFrame
            A Pandas dataframe representing a ticker's price history. 
            Obtained through a call to yf.download
    """
    # initializes new table widget item and gets the ticker's open, last close, and current prices
    w = QTableWidgetItem()
    try:
        ticker_open = ticker.iloc[4][0]
        ticker_current = ticker.iloc[4][3]
        ticker_last_close = ticker.iloc[3][3]
    except IndexError:
        ticker_open = ticker.iloc[3][0]
        ticker_current = ticker.iloc[3][3]
        ticker_last_close = ticker.iloc[2][3]

    # calculates the percent change in price from open and from yesterday's close
    open_change = (ticker_current - ticker_open) / ticker_open * 100
    close_change = (ticker_current - ticker_last_close) / ticker_last_close * 100

    # decides if the stock is up, down, or flat compared to open and yesterday's close
    open_pos = "UP"
    close_pos = "UP"
    if open_change < -.1:
        open_pos = "DOWN"
    elif open_change > -.1 and open_change < .1:
        open_pos = "FLAT"
    
    if close_change < -.1:
        close_pos = "DOWN"
    elif close_change > -.1 and close_change < .1:
        close_pos = "FLAT"

    match open_pos:
        case "UP":
            match close_pos:
                case "UP":
                    w.setIcon(QIcon(currentdir + 'icons/greenarrowgreenbox.png'))
                case "FLAT":
                    w.setIcon(QIcon(currentdir + 'icons/greenarrowflatbox.png'))
                case "DOWN":
                    w.setIcon(QIcon(currentdir + 'icons/greenarrowredbox.png'))

        case "FLAT":
            match close_pos:
                case "UP":
                    w.setIcon(QIcon(currentdir + 'icons/flatarrowgreenbox.png'))
                case "FLAT":
                    w.setIcon(QIcon(currentdir + 'icons/flatarrowflatbox.png'))
                case "DOWN":
                    w.setIcon(QIcon(currentdir + 'icons/flatarrowredbox.png'))

        case "DOWN":
            match close_pos:
                case "UP":
                    w.setIcon(QIcon(currentdir + 'icons/redarrowgreenbox.png'))
                case "FLAT":
                    w.setIcon(QIcon(currentdir + 'icons/redarrowflatbox.png'))
                case "DOWN":
                    w.setIcon(QIcon(currentdir + 'icons/redarrowredbox.png'))

    # returns a tablewidgetitem containing the new icon
    return w


def show_graph(ticker, title: str, volume: bool, non_trading: bool):
    """Plots a ticker from yfinance in a separate matplotfinance window.

        ticker : pandas.DataFrame
            A Pandas dataframe representing a ticker's price history. 
            Obtained through a call to yf.download
        title : str
            The title of the chart
        volume : bool
            Include volume bars in the chart?
        non_trading : bool
            Include non-trading days in the chart? (I don't know why you'd do this)
    """
    # retrieves user's chart style preferences from assets/settings.xml
    up_color = getXMLData('assets/settings.xml', 'upcolor')
    down_color = getXMLData('assets/settings.xml', 'downcolor')
    base_style = getXMLData('assets/settings.xml', 'basestyle')

    # creates a chart style based on the user's settings
    mc = mpf.make_marketcolors(up=up_color[0].text.lower(), down=down_color[0].text.lower(),inherit=True)
    s  = mpf.make_mpf_style(base_mpf_style=base_style[0].text,marketcolors=mc)
    # plots chart
    fig = mpf.figure()
    ax1 = fig.add_subplot(1,1,1)


    upper, middle, lower = talib.BBANDS(ticker["Close"], timeperiod=20)
    bbands_talib = pd.DataFrame(index=ticker.index,
                            data={"bb_low": lower,
                                  "bb_ma": middle,
                                  "bb_high": upper})
    plot = [
        mpf.make_addplot((bbands_talib["bb_low"]), color='#606060', panel=0),
        mpf.make_addplot((bbands_talib["bb_ma"]), color='#1f77b4', panel=0),
        mpf.make_addplot((bbands_talib["bb_high"]), color='#1f77b4', panel=0),
    ]
    
    mpf.plot(ticker, 
             show_nontrading = non_trading,
             type='candle', 
             style = s, 
             title = title,
             volume = volume, 
             tight_layout = True,
             addplot=plot, 
             block=False
             )
        

def update_portfolio_nav():
    """
    Updates the user's NAV tab. Buying power is calculated as 
    cash + (.5 * value of all long positions) - 
    (1.5 * value of all short positions).
    """
    
    # sets buying power to user's cash
    newVal = float(portfolio_amts[0].text)
    liabilities = 0
    assets = 0
    
    # for each stock in the portfolio, get its price and check if it's held long or sold short
    for idx, amt in enumerate(portfolio_amts[1:]):
        price = float(portfolio_dialog.positions_view_groupbox.positions_view.item(idx - 1, 2).text()[1:])

        if int(amt.text) > 0:
            # if it's long, add its value to the new value and to the assets tally
            newVal += float(price) * int(amt.text)
            assets += float(price) * float(amt.text)
        elif int(amt.text) < 0:
            # if it's short, subtract its value from the new value and add to the liabilities tally
            newVal -= float(price) * int(amt.text)
            liabilites += float(price) * float(amt.text)

    buying_power = get_portfolio_bp() 
    portfolio_dialog.currentNAV.liq.setText('${:0,.2f}'.format(float(str(newVal))))
    portfolio_dialog.currentNAV.buyingPower.setText('${:0,.2f}'.format(buying_power))
    portfolio_dialog.currentNAV.assets.setText('${:0,.2f}'.format(assets))
    portfolio_dialog.currentNAV.liabilities.setText('${:0,.2f}'.format(liabilities))
    portfolio_dialog.currentNAV.returnSinceInception.setText('{:0.2f}'.format((newVal / 10000 - 1) * 100) + "%")
        

def update_wallet_nav():
    """Updates the user's NAV tab. Calculated as cash + (.5 * value of all long positions) - 
    (1.5 * value of all short positions)."""
    
    # sets buying power to user's cash
    newVal = float(wallet_amts[0].text)
    liabilities = 0
    assets = 0
    for idx, amt in enumerate(wallet_amts[1:]):
        price = float(wallet_dialog.positions_view_groupbox.positions_view.item(idx - 1, 2).text()[1:])
        if float(amt.text) > 0:
            newVal += float(price) * float(amt.text)
            assets += float(price) * float(amt.text)
        elif float(amt.text) < 0:
            newVal -= float(price) * float(amt.text)
            liabilites += float(price) * float(amt.text)

    buying_power = get_wallet_bp() 
    wallet_dialog.currentNAV.liq.setText('${:0,.2f}'.format(float(str(newVal))))
    wallet_dialog.currentNAV.buyingPower.setText('${:0,.2f}'.format(buying_power))
    wallet_dialog.currentNAV.assets.setText('${:0,.2f}'.format(assets))
    wallet_dialog.currentNAV.liabilities.setText('${:0,.2f}'.format(liabilities))
    wallet_dialog.currentNAV.returnSinceInception.setText('{:0.2f}'.format((newVal / 10000 - 1) * 100) + "%")


def get_portfolio_bp() -> float:
    buying_power = portfolio_cash
    total_long = 0
    total_short = 0

    for i in range (1, len(portfolio_amts)):
        price = float(portfolio_dialog.positions_view_groupbox.positions_view.item(i - 1, 2).text()[1:])
        if int(portfolio_amts[i].text) > 0:
            total_long += float(price) * int(portfolio_amts[i].text)
        elif int(portfolio_amts[i].text) < 0:
            total_short += float(price) * int(portfolio_amts[i].text)
    
    buying_power += .5 * total_long
    buying_power -= 1.5 * total_short
    return buying_power


def get_wallet_bp() -> float:
    return wallet_cash * 10


def getXMLData(file, keyword):
    """Returns a ResultSet containing all instances of the given keyword in the given file"""
    currentdir = os.getcwd()
    
    return BeautifulSoup(open(currentdir + '\\' +  file, 'r').read(), "xml").find_all(keyword)
    

def applySettingsChanges():
    """Updates assets/settings.xml with the currently selected settings in the GUI"""
    # gets currently selected settings
    up = settings_dialog.up_color_combobox.currentText()
    down = settings_dialog.down_color_combobox.currentText()
    style = settings_dialog.chart_style_combobox.currentText()

    # parses XML file into an ElementTree
    tree = et.parse('assets/settings.xml')

    # replaces old data in the file with the current data
    for upcolor in tree.getroot().iter('upcolor'):
        upcolor.text = up

    for downcolor in tree.getroot().iter('downcolor'):
        downcolor.text = down

    for basestyle in tree.getroot().iter('basestyle'):
        basestyle.text = style

    tree.write('assets/settings.xml')


def stockinfo_searchbar_click(dialog: QDialog):
    global tab2_isloaded
    global tab3_isloaded
    tab2_isloaded = False
    tab3_isloaded = False
    ticker = ''
    i = 0
    while stockinfo_dialog_main.search_bar_groupbox.searchBar.text()[i] != ' ':
        ticker += stockinfo_dialog_main.search_bar_groupbox.searchBar.text()[i]
        i += 1
    
    yf_ticker = yf.Ticker(ticker)
    ticker_info = yf.Ticker(ticker).get_info()
    ticker_news = yf.Ticker(ticker).get_news()
    
    if(ticker_info['quoteType'] == 'ETF'):
        stockinfo_dialog.setTabEnabled(1, False)
        stockinfo_dialog.setTabEnabled(2, False)
        setup_etf_info(ticker_info, ticker_news)
    elif(ticker_info['quoteType'] == 'EQUITY'):
        stockinfo_dialog.setTabEnabled(1, True)
        stockinfo_dialog.setTabEnabled(2, True)
        setup_stock_info(yf_ticker)


def get_etf_weights(ticker_info: dict) -> list:
    weights_list = []
    weights_list.append(["Real Estate", ticker_info['sectorWeightings'][0]['realestate']])
    weights_list.append(["Consumer Cyclicals", ticker_info['sectorWeightings'][1]['consumer_cyclical']])
    weights_list.append(["Basic Materials", ticker_info['sectorWeightings'][2]['basic_materials']])
    weights_list.append(["Consumer Defensives", ticker_info['sectorWeightings'][3]['consumer_defensive']])
    weights_list.append(["Technology", ticker_info['sectorWeightings'][4]['technology']])
    weights_list.append(["Communication Services", ticker_info['sectorWeightings'][5]['communication_services']])
    weights_list.append(["Financial Services", ticker_info['sectorWeightings'][6]['financial_services']])
    weights_list.append(["Utilities", ticker_info['sectorWeightings'][7]['utilities']])
    weights_list.append(["Industrials", ticker_info['sectorWeightings'][8]['industrials']])
    weights_list.append(["Energy", ticker_info['sectorWeightings'][9]['energy']])
    weights_list.append( ["Healthcare", ticker_info['sectorWeightings'][10]['healthcare']])
    return weights_list


def clear_layout(layout: QVBoxLayout):
    for i in reversed(range(layout.count())): 
        layout.itemAt(i).widget().setParent(None)


def setup_etf_info(ticker_info: dict, ticker_news: dict):
    stockinfo_dialog_main.about_groupbox.setVisible(True)
    stockinfo_dialog_main.asset_info_groupbox.setVisible(True)
    stockinfo_dialog_main.news_groupbox.setVisible(True)

    clear_layout(about_scrollarea_widget.layout())
    clear_layout(assetinfo_scrollarea_widget.layout())
    clear_layout(stockinfo_dialog_main.news_groupbox.layout())
    etf_weights = get_etf_weights(ticker_info)

    full_name_label = QLabel(f"Full Name: {ticker_info['longName']}", about_scrollarea_widget)
    full_name_label.adjustSize()

    full_name_label.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed))
    full_name_label.setStyleSheet("border:1px solid rgb(0, 255, 0);")

    category_label = QLabel(f"Category: {ticker_info['category']}", about_scrollarea_widget)
    category_label.adjustSize()
    category_label.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed))
    category_label.setStyleSheet("border:1px solid rgb(0, 255, 0);")

    exchange_label = QLabel(f"Exchange: {ticker_info['exchange']}", about_scrollarea_widget)
    exchange_label.adjustSize()
    exchange_label.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed))

    market_label = QLabel(f"Market: {ticker_info['market']}", about_scrollarea_widget)
    market_label.adjustSize()
    market_label.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed))

    total_assets_label = QLabel(f"Total Assets: {ticker_info['totalAssets']}")
    total_assets_label.adjustSize()
    total_assets_label.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed))

    description_label = QLabel(f"Description: " + ticker_info['longBusinessSummary'], about_scrollarea_widget)
    description_label.adjustSize()
    description_label.setWordWrap(True)
    description_label.setStyleSheet("border:1px solid rgb(0, 255, 0);")

    date_inception = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ticker_info['fundInceptionDate']))
    inception_label = QLabel(f"Date of Inception: " + date_inception, about_scrollarea_widget)
    inception_label.adjustSize()
    inception_label.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed))
    weights_piechart = QPieSeries()
    
    for i in range(len(etf_weights)):
        weights_piechart.append(etf_weights[i][0], i + 1)
        weights_piechart.slices()[i].setValue(etf_weights[i][1] * 100)
        weights_piechart.slices()[i].setLabelVisible(True)

    weights_chart = QChart()
    weights_chart.addSeries(weights_piechart)
    weights_chart.setTitle(f"{ticker_info['symbol']} Holdings by Sector")
    weights_chart.setVisible(True)

    weights_chartview = QChartView(weights_chart)
    weights_chartview.adjustSize()
    weights_chartview.setStyleSheet("border:1px solid rgb(0, 255, 0);")

    current_price_label = QLabel(f"Current Price: {ticker_info['regularMarketPrice']}", assetinfo_scrollarea_widget)
    open_price_label = QLabel(f"\tOpen: {ticker_info['open']}", assetinfo_scrollarea_widget)
    high_price_label = QLabel(f"\tHigh: {ticker_info['dayHigh']}", assetinfo_scrollarea_widget)
    low_price_label = QLabel(f"\tLow: {ticker_info['dayLow']}", assetinfo_scrollarea_widget)
    close_price_label = QLabel(f"\tLast Close: {ticker_info['previousClose']}", assetinfo_scrollarea_widget)
    nav_price_label = QLabel(f"NAV Price: {ticker_info['navPrice']}", assetinfo_scrollarea_widget)

    bid_label = QLabel(f"Bid: {ticker_info['bid']} ({ticker_info['bidSize']})", assetinfo_scrollarea_widget)
    ask_label = QLabel(f"Ask: {ticker_info['ask']} ({ticker_info['askSize']})", assetinfo_scrollarea_widget)

    volume_label = QLabel(f"Volume: {ticker_info['volume']}", assetinfo_scrollarea_widget)
    avg_volume_label = QLabel(f"Average Volume (10d): {ticker_info['averageVolume10days']}", assetinfo_scrollarea_widget)
    long_avg_volume_label = QLabel(f"Average Volume (1y): {ticker_info['averageVolume']} ", assetinfo_scrollarea_widget)


    year_high_label = QLabel(f"52 Week High: {ticker_info['fiftyTwoWeekHigh']}", assetinfo_scrollarea_widget)
    year_low_label = QLabel(f"52 Week Low: {ticker_info['fiftyTwoWeekLow']}", assetinfo_scrollarea_widget)

    averages_label = QLabel("Price Averages: ", assetinfo_scrollarea_widget)
    fifty_avg_label = QLabel(f"\t50d MA: {ticker_info['fiftyDayAverage']}", assetinfo_scrollarea_widget)
    twohundred_avg_label = QLabel(f"\t200d MA: {ticker_info['twoHundredDayAverage']}", assetinfo_scrollarea_widget)

    threeyear_return_label = QLabel(f"Three-Year CAGR: {ticker_info['threeYearAverageReturn'] * 100}% per annum", assetinfo_scrollarea_widget)
    fiveyear_return_label = QLabel(f"Five-Year CAGR: {ticker_info['fiveYearAverageReturn'] * 100}% per annum", assetinfo_scrollarea_widget)

    try:
        dividend_label = QLabel(f"Trailing Annual Dividend Yield: {ticker_info['trailingAnnualDividendYield'] * 100}% per annum", assetinfo_scrollarea_widget)
    except TypeError: # ETF does not pay a dividend
        dividend_label = QLabel(f"Trailing Annual Dividend Yield: 0% per annum", assetinfo_scrollarea_widget)

    dividend_rate_label = QLabel(f"Trailing Annual Dividend Rate: ${ticker_info['trailingAnnualDividendRate']}", assetinfo_scrollarea_widget)
    current_div_label = QLabel(f"Current Dividend Yield: {ticker_info['yield']}", assetinfo_scrollarea_widget)

    beta_3y_label = QLabel(f"3-Year Beta (Relative to SPY): {ticker_info['beta3Year']}", assetinfo_scrollarea_widget)


    for news_item in ticker_news:

        l = QLabel(f"<a href=\"{news_item['link']}\"> <font face=verdana size=1 color=black> {news_item['title']}</font> </a> <br> <a>{news_item['relatedTickers']} <br> {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(news_item['providerPublishTime']))} </a>")
        l.setOpenExternalLinks(True)
        l.setStyleSheet("""QToolTip { 
                           font-size: 12px
                           }""")
        l.setToolTip(news_item['link'])
        stockinfo_dialog_main.news_groupbox.layout().addWidget(l)
        


    about_scrollarea_widget.layout().addWidget(full_name_label)
    about_scrollarea_widget.layout().addWidget(category_label)
    about_scrollarea_widget.layout().addWidget(exchange_label)
    about_scrollarea_widget.layout().addWidget(market_label)
    about_scrollarea_widget.layout().addWidget(total_assets_label)
    about_scrollarea_widget.layout().addWidget(inception_label)
    about_scrollarea_widget.layout().addWidget(description_label)
    about_scrollarea_widget.layout().addWidget(weights_chartview)
    about_scrollarea_widget.adjustSize()

    assetinfo_scrollarea_widget.layout().addWidget(current_price_label)
    assetinfo_scrollarea_widget.layout().addWidget(open_price_label)
    assetinfo_scrollarea_widget.layout().addWidget(high_price_label)
    assetinfo_scrollarea_widget.layout().addWidget(low_price_label)
    assetinfo_scrollarea_widget.layout().addWidget(close_price_label)
    assetinfo_scrollarea_widget.layout().addWidget(nav_price_label)
    assetinfo_scrollarea_widget.layout().addWidget(bid_label)
    assetinfo_scrollarea_widget.layout().addWidget(ask_label)
    assetinfo_scrollarea_widget.layout().addWidget(volume_label)
    assetinfo_scrollarea_widget.layout().addWidget(avg_volume_label)
    assetinfo_scrollarea_widget.layout().addWidget(long_avg_volume_label)
    assetinfo_scrollarea_widget.layout().addWidget(year_high_label)
    assetinfo_scrollarea_widget.layout().addWidget(year_low_label)
    assetinfo_scrollarea_widget.layout().addWidget(averages_label)
    assetinfo_scrollarea_widget.layout().addWidget(fifty_avg_label)
    assetinfo_scrollarea_widget.layout().addWidget(twohundred_avg_label)
    assetinfo_scrollarea_widget.layout().addWidget(threeyear_return_label)
    assetinfo_scrollarea_widget.layout().addWidget(fiveyear_return_label)
    assetinfo_scrollarea_widget.layout().addWidget(dividend_label)
    assetinfo_scrollarea_widget.layout().addWidget(dividend_rate_label)
    assetinfo_scrollarea_widget.layout().addWidget(current_div_label)
    assetinfo_scrollarea_widget.layout().addWidget(beta_3y_label)
    

def setup_stock_info(ticker: yf.Ticker):
    t1 = time.perf_counter()
    ticker_info = ticker.get_info()
    ticker_news = ticker.get_news()
    t2 = time.perf_counter()
    print(f"{t2 - t1} seconds")
    stockinfo_dialog_main.about_groupbox.setVisible(True)
    stockinfo_dialog_main.asset_info_groupbox.setVisible(True)
    stockinfo_dialog_main.news_groupbox.setVisible(True)
    stockinfo_dialog_recs.analyst_rec_groupbox.setVisible(True)
    stockinfo_dialog_recs.iandi_groupbox.setVisible(True)
    stockinfo_dialog_recs.mutfund_groupbox.setVisible(True)

    clear_layout(about_scrollarea_widget.layout())
    clear_layout(assetinfo_scrollarea_widget.layout())
    clear_layout(stockinfo_dialog_main.news_groupbox.layout())
    clear_layout(stockinfo_dialog_recs.analyst_rec_groupbox.layout())
    clear_layout(stockinfo_dialog_recs.iandi_groupbox.layout())
    clear_layout(stockinfo_dialog_recs.mutfund_groupbox.layout())

    full_name_label = QLabel(f"Full Name: {ticker_info['longName']}")
    
    sector_label = QLabel(f"Sector: {ticker_info['sector']}: {ticker_info['industry']}")
    
    country_label = QLabel(f"Country: {ticker_info['country']}")

    description_label = QLabel(f"Description: " + ticker_info['longBusinessSummary'])
    
    description_label.setWordWrap(True)

    location_label = QLabel(f"Location: {ticker_info['city']}, {ticker_info['state']}")

    website_label =  QLabel(f"Website: <a href=\"{ticker_info['website']}\"> {ticker_info['website']} </a>")

    current_price_label = QLabel(f"Current Price: {ticker_info['regularMarketPrice']}")
    open_price_label = QLabel(f"\tOpen: {ticker_info['open']}")
    high_price_label = QLabel(f"\tHigh: {ticker_info['dayHigh']}")
    low_price_label = QLabel(f"\tLow: {ticker_info['dayLow']}")
    close_price_label = QLabel(f"\tLast Close: {ticker_info['previousClose']}")
    
    bid_label = QLabel(f"Bid: {ticker_info['bid']} ({ticker_info['bidSize']})")
    ask_label = QLabel(f"Ask: {ticker_info['ask']} ({ticker_info['askSize']})")

    volume_label = QLabel(f"Volume: {ticker_info['volume']}")
    avg_volume_label = QLabel(f"Average Volume (10d): {ticker_info['averageVolume10days']}")
    long_avg_volume_label = QLabel(f"Average Volume (1y): {ticker_info['averageVolume']} ")


    year_high_label = QLabel(f"52 Week High: {ticker_info['fiftyTwoWeekHigh']}")
    year_low_label = QLabel(f"52 Week Low: {ticker_info['fiftyTwoWeekLow']}")

    averages_label = QLabel("Price Averages: ")
    fifty_avg_label = QLabel(f"\t50d MA: {ticker_info['fiftyDayAverage']}")
    twohundred_avg_label = QLabel(f"\t200d MA: {ticker_info['twoHundredDayAverage']}")


    for news_item in ticker_news:

        l = QLabel(f"<a href=\"{news_item['link']}\"> <font face=verdana size=1 color=black> {news_item['title']}</font> </a> <br> <a>{news_item['relatedTickers']} <br> {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(news_item['providerPublishTime']))} </a>")
        l.setOpenExternalLinks(True)
        l.setStyleSheet("""QToolTip { 
                           font-size: 12px
                           }""")
        l.setToolTip(news_item['link'])
        
        stockinfo_dialog_main.news_groupbox.layout().addWidget(l)

    about_scrollarea_widget.layout().addWidget(full_name_label)
    about_scrollarea_widget.layout().addWidget(sector_label)
    about_scrollarea_widget.layout().addWidget(country_label)
    about_scrollarea_widget.layout().addWidget(description_label)
    about_scrollarea_widget.layout().addWidget(location_label)
    about_scrollarea_widget.layout().addWidget(website_label)

    assetinfo_scrollarea_widget.layout().addWidget(current_price_label)
    assetinfo_scrollarea_widget.layout().addWidget(open_price_label)
    assetinfo_scrollarea_widget.layout().addWidget(high_price_label)
    assetinfo_scrollarea_widget.layout().addWidget(low_price_label)
    assetinfo_scrollarea_widget.layout().addWidget(close_price_label)
    assetinfo_scrollarea_widget.layout().addWidget(bid_label)
    assetinfo_scrollarea_widget.layout().addWidget(ask_label)
    assetinfo_scrollarea_widget.layout().addWidget(volume_label)
    assetinfo_scrollarea_widget.layout().addWidget(avg_volume_label)
    assetinfo_scrollarea_widget.layout().addWidget(long_avg_volume_label)
    assetinfo_scrollarea_widget.layout().addWidget(year_high_label)
    assetinfo_scrollarea_widget.layout().addWidget(year_low_label)
    assetinfo_scrollarea_widget.layout().addWidget(averages_label)
    assetinfo_scrollarea_widget.layout().addWidget(fifty_avg_label)
    assetinfo_scrollarea_widget.layout().addWidget(twohundred_avg_label)


def stockinfo_dialog_changed(tab_id: int):
    t = ''
    i = 0
    while stockinfo_dialog_main.search_bar_groupbox.searchBar.text()[i] != ' ':
        t += stockinfo_dialog_main.search_bar_groupbox.searchBar.text()[i]
        i += 1
    
    ticker = yf.Ticker(t)

    global tab2_isloaded
    global tab3_isloaded
    global tab4_isloaded

    if(tab_id == 1 and not tab2_isloaded):
        ticker_recommendations = ticker.recommendations
        ticker_instholders = ticker.institutional_holders
        ticker_mutfundholders = ticker.mutualfund_holders

        length = ticker_recommendations.count().iloc[0]
        recs_number = min(10, length)
        dates = list(ticker_recommendations.tail(10).index)

        for i in range(recs_number):
            date = dates[len(dates) - 1 - i].to_pydatetime()
            firm = ticker_recommendations.iloc[length - 1 - i][0]
            grade_to = ticker_recommendations.iloc[length - 1 - i][1]

            l = QLabel(f"{firm}: {grade_to} <br> {date}")
            stockinfo_dialog_recs.analyst_rec_groupbox.layout().addWidget(l)

        for i in range(10):
            holder = ticker_instholders.iloc[i][0]
            shareno = ticker_instholders.iloc[i][1]
            date_reported = ticker_instholders.iloc[i][2]
            percent = ticker_instholders.iloc[i][3]
            value = ticker_instholders.iloc[i][4]

            l = QLabel(f"{holder}: {shareno} shares ({percent * 100}%) <br> {date_reported}")
            stockinfo_dialog_recs.iandi_groupbox.layout().addWidget(l)

        for i in range(10):
            holder = ticker_mutfundholders.iloc[i][0]
            shareno = ticker_mutfundholders.iloc[i][1]
            date_reported = ticker_mutfundholders.iloc[i][2]
            percent = ticker_mutfundholders.iloc[i][3]
            value = ticker_mutfundholders.iloc[i][4]

            l = QLabel(f"{holder}: {shareno} shares ({percent * 100}%) <br> {date_reported}")
            stockinfo_dialog_recs.mutfund_groupbox.layout().addWidget(l)
            
            
            tab2_isloaded = True

    elif(tab_id == 2 and not tab3_isloaded):
        t1 = time.perf_counter()
        ticker_pts = ticker.get_analyst_price_target()
        ticker_hist = ticker.history(period="2y", interval="1wk")
        ticker_earnings_dates = ticker.get_earnings_dates()
        ticker_qtr_earnings = ticker.get_earnings(freq="quarterly")
        ticker_yr_earnings = ticker.get_earnings(freq="yearly")
        ticker_yr_eps = ticker.get_financials().loc["BasicEPS"]
        ticker_eps_forecast = ticker.get_earnings_forecast()
        ticker_rev_forecast = ticker.get_rev_forecast()

        ptchart.removeAxis(ptchart.axes(Qt.Orientation.Horizontal)[0])
        ptchart.removeAxis(ptchart.axes(Qt.Orientation.Vertical)[0])

        ptchart.removeAllSeries()

        series = QLineSeries()
        
        series2 = QLineSeries()
        
        series3 = QLineSeries()

        series4 = QLineSeries()

        current_dt = QDateTime().currentDateTime().toMSecsSinceEpoch()
        prediction_date = QDateTime().currentDateTime().addYears(1).toMSecsSinceEpoch()
        date_format = "yyyy-MM-dd hh:mm:ss"
        for i in range(ticker_hist.count().iloc[0]):
            series.append(float(QDateTime().fromString(str(ticker_hist.index[i])[0:19], date_format).toMSecsSinceEpoch()), ticker_hist.iloc[i][3])
        series.append(float(prediction_date), ticker_pts.iloc[1][0])
        series.setName("Current Price")
        series.setColor(QColor("blue"))
        
        series2.setName("Worst Case")
        series2.setColor(QColor("red"))

        series3.setName("Mean Target Price")
        series3.setColor(QColor("black"))
        
        series4.setName("Best Case")
        series4.setColor(QColor("green"))

        series2.append(float(current_dt), ticker_hist.iloc[ticker_hist.count().iloc[0] - 1][3])
        series2.append(float(prediction_date), ticker_pts.iloc[0][0])

        series3.append(float(current_dt), ticker_hist.iloc[ticker_hist.count().iloc[0] - 1][3])
        series3.append(float(prediction_date), ticker_pts.iloc[2][0])

        series4.append(float(current_dt), ticker_hist.iloc[ticker_hist.count().iloc[0] - 1][3])
        series4.append(float(prediction_date), ticker_pts.iloc[3][0])

        ptchart.addSeries(series)
        ptchart.addSeries(series2)
        ptchart.addSeries(series3)
        ptchart.addSeries(series4)
        

        ptchart.createDefaultAxes()
        ptchart.axes(Qt.Orientation.Horizontal)[0].hide()

        x_axis = QDateTimeAxis()
        x_axis.setTickCount(7)
        x_axis.setFormat("MM-dd-yyyy")
        x_axis.setTitleText("Date")
        x_axis.setVisible(True)

        ptchart.addAxis(x_axis, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(x_axis)

        clear_layout(pt_label_container.layout())
        pt_label_container.layout().addWidget(QLabel(f"Current Price: {ticker_pts.iloc[1][0]}"))
        pt_label_container.layout().addWidget(QLabel(f"Target Low Price: {ticker_pts.iloc[0][0]}"))
        pt_label_container.layout().addWidget(QLabel(f"Target Mean Price: {ticker_pts.iloc[2][0]}"))
        pt_label_container.layout().addWidget(QLabel(f"Target High Price: {ticker_pts.iloc[3][0]}"))
        pt_label_container.layout().addWidget(QLabel(f"Number of Analyst Opinions: {ticker_pts.iloc[4][0]}"))
        t2 = time.perf_counter()
        print(f"{t2 - t1} seconds")

        qtr_earnings_chart.removeAllSeries()
        series = QBarSeries()

        set1 = QBarSet("Actual")
        set2 = QBarSet("Estimate")
        earnings_trend_max = 0
        earnings_trend_min = 0

        qtr_earnings_table.setRowCount(6)
        qtr_earnings_table.setColumnCount(3)
        qtr_earnings_table.setHorizontalHeaderItem(0, QTableWidgetItem("Actual"))
        qtr_earnings_table.setHorizontalHeaderItem(1, QTableWidgetItem("Expected"))
        qtr_earnings_table.setHorizontalHeaderItem(2, QTableWidgetItem("Surprise"))
        for i in range (qtr_earnings_table.columnCount()):
            
            qtr_earnings_table.horizontalHeaderItem(i).setFont(QFont('arial', 10))
            

        for i in range (qtr_earnings_table.rowCount()):
            qtr_earnings_table.setVerticalHeaderItem(i, QTableWidgetItem(str(i + 1)))
            qtr_earnings_table.verticalHeaderItem(i).setFont(QFont('arial', 10))

        set_number = ticker_earnings_dates.count()[0]
        for i in range(set_number):
            reported = ticker_earnings_dates.iloc[ticker_earnings_dates.index.size - 1 - i][1]
            set1.append(reported)
            if(reported > earnings_trend_max):
                earnings_trend_max = reported
            if(reported < earnings_trend_min):
                earnings_trend_min = reported

            estimate = ticker_earnings_dates.iloc[ticker_earnings_dates.index.size - 1 - i][0]
            if(estimate > earnings_trend_max):
                earnings_trend_max = estimate
            if(estimate < earnings_trend_min):
                earnings_trend_min = estimate
            set2.append(estimate)

            qtr_earnings_table.setItem(i, 0, QTableWidgetItem(str(reported)))
            qtr_earnings_table.setItem(i, 1, QTableWidgetItem(str(estimate)))
            qtr_earnings_table.setItem(i, 2, QTableWidgetItem(str(reported - estimate)))

        

        series.append(set1)
        series.append(set2)
        qtr_earnings_chart.addSeries(series)
        qtr_earnings_chart.createDefaultAxes()
        qtr_earnings_chart.axes(Qt.Orientation.Vertical)[0].setRange(earnings_trend_min * 1.1, earnings_trend_max * 1.1)

        qtr_revtrend_chart.removeAllSeries()
        s = QBarSeries()
        set = QBarSet("Revenue")
        number = ticker_qtr_earnings.count()[0]
        qtr_revtrend_max = 0
        qtr_revtrend_min = 0
        for i in range(number):
            set.append(ticker_qtr_earnings.iloc[i][0])
            if(ticker_qtr_earnings.iloc[i][0] > qtr_revtrend_max):
                qtr_revtrend_max = ticker_qtr_earnings.iloc[i][0]
            if(ticker_qtr_earnings.iloc[i][0] < qtr_revtrend_min):
                qtr_revtrend_min = ticker_qtr_earnings.iloc[i][0]
            qtr_revtrend_label_container.layout().addWidget(QLabel(f"{ticker_qtr_earnings.index[i]}: {ticker_qtr_earnings.iloc[i][0]}"))

        set.setPen(QColor("green"))
        set.append(ticker_rev_forecast.iloc[0][0])
        qtr_revtrend_label_container.layout().addWidget(QLabel(f"{str(ticker_rev_forecast.iloc[0][7])}: {ticker_rev_forecast.iloc[0][0]}"))

        set.append(ticker_rev_forecast.iloc[1][0])
        qtr_revtrend_label_container.layout().addWidget(QLabel(f"{str(ticker_rev_forecast.iloc[1][7])}: {ticker_rev_forecast.iloc[1][0]}"))

        s.append(set)
        
        qtr_revtrend_chart.addSeries(s)
        qtr_revtrend_chart.createDefaultAxes()
        qtr_revtrend_chart.axes(Qt.Orientation.Vertical)[0].setRange(qtr_revtrend_min * 1.1, qtr_revtrend_max * 1.1)

        yr_earnings_chart.removeAllSeries()
        clear_layout(yr_earnings_label_container.layout())
        s = QBarSeries()
        set = QBarSet("Earnings")
        number = ticker_yr_eps.index.size
        yr_eps_max = 0
        yr_eps_min = 0

        for i in range(number):
            eps = ticker_yr_eps[number - 1 - i]
            if(eps > yr_eps_max):
                yr_eps_max = eps
            if(eps < yr_eps_min):
                yr_eps_min = eps
            set.append(eps)
            yr_earnings_label_container.layout().addWidget(QLabel(f"{str(ticker_yr_eps.index[number - 1 - i])[0:4]}: {eps}"))

        set.append(ticker_eps_forecast.iloc[2][0])
        if(ticker_eps_forecast.iloc[2][0] > yr_eps_max):
            yr_eps_max = ticker_eps_forecast.iloc[2][0]
        if(ticker_eps_forecast.iloc[2][0] < yr_eps_min):
            yr_eps_min = ticker_eps_forecast.iloc[2][0]
        yr_earnings_label_container.layout().addWidget(QLabel(f"{str(ticker_eps_forecast.iloc[2][7])[0:4]}: {ticker_eps_forecast.iloc[2][0]}"))

        set.append(ticker_eps_forecast.iloc[3][0])
        if(ticker_eps_forecast.iloc[3][0] > yr_eps_max):
            yr_eps_max = ticker_eps_forecast.iloc[3][0]
        if(ticker_eps_forecast.iloc[3][0] < yr_eps_min):
            yr_eps_min = ticker_eps_forecast.iloc[3][0]
        yr_earnings_label_container.layout().addWidget(QLabel(f"{str(ticker_eps_forecast.iloc[3][7])[0:4]}: {ticker_eps_forecast.iloc[3][0]}"))

        s.append(set)
        yr_earnings_chart.addSeries(s)
        yr_earnings_chart.createDefaultAxes()
        yr_earnings_chart.axes(Qt.Orientation.Vertical)[0].setRange(yr_eps_min * 1.1, yr_eps_max * 1.1)



        yr_revtrend_chart.removeAllSeries()
        clear_layout(yr_revtrend_label_container.layout())
        s = QBarSeries()
        set = QBarSet("Revenue")
        number = ticker_yr_earnings.count()[0]

        yr_revtrend_max = 0
        yr_revtrend_min = 0
        for i in range(number):
            set.append(ticker_yr_earnings.iloc[i][0])
            if(ticker_yr_earnings.iloc[i][0] > yr_revtrend_max):
                yr_revtrend_max = ticker_yr_earnings.iloc[i][0]
            if(ticker_yr_earnings.iloc[i][0] < yr_revtrend_min):
                yr_revtrend_min = ticker_yr_earnings.iloc[i][0]
            yr_revtrend_label_container.layout().addWidget(QLabel(f"{ticker_yr_earnings.index[i]}: {ticker_yr_earnings.iloc[i][0]}"))

        set.setPen(QColor("green"))

        set.append(ticker_rev_forecast.iloc[2][0])
        yr_revtrend_label_container.layout().addWidget(QLabel(f"{str(ticker_rev_forecast.iloc[2][7])[0:4]}: {ticker_rev_forecast.iloc[2][0]}"))
        if(ticker_rev_forecast.iloc[2][0] > yr_revtrend_max):
            yr_revtrend_max = ticker_rev_forecast.iloc[2][0]
        if(ticker_rev_forecast.iloc[2][0] < yr_revtrend_min):
            yr_revtrend_min = ticker_rev_forecast.iloc[2][0]

        set.append(ticker_rev_forecast.iloc[3][0])
        yr_revtrend_label_container.layout().addWidget(QLabel(f"{str(ticker_rev_forecast.iloc[3][7])[0:4]}: {ticker_rev_forecast.iloc[3][0]}"))

        if(ticker_rev_forecast.iloc[3][0] > yr_revtrend_max):
            yr_revtrend_max = ticker_rev_forecast.iloc[3][0]
        if(ticker_rev_forecast.iloc[3][0] < yr_revtrend_min):
            yr_revtrend_min = ticker_rev_forecast.iloc[3][0]

        s.append(set)
        
        yr_revtrend_chart.addSeries(s)
        yr_revtrend_chart.createDefaultAxes()
        yr_revtrend_chart.axes(Qt.Orientation.Vertical)[0].setRange(yr_revtrend_min * 1.1, yr_revtrend_max * 1.1)
        
    
        tab3_isloaded = True
    elif(tab_id == 3 and not tab4_isloaded):
        t1 = time.perf_counter()
        ticker_financials = ticker.get_financials()
        financials_table.setRowCount(ticker_financials.index.size)
        financials_table.setColumnCount(5)

        for i in range(ticker_financials.index.size):
            financials_table.setVerticalHeaderItem(i, QTableWidgetItem(ticker_financials.index[i]))
            financials_table.verticalHeaderItem(i).setFont(QFont('arial', 10))

        for i in range(4):
            for j in range(ticker_financials.index.size):
                if(ticker_financials.iloc[j][3 - i] > 1000):
                    formatted_data = nf.simplify(ticker_financials.iloc[j][3 - i])
                    financials_table.setItem(j, i, QTableWidgetItem(formatted_data))
                else:
                    financials_table.setItem(j, i, QTableWidgetItem(str(ticker_financials.iloc[j][3 - i])))

        checkboxes = QButtonGroup()

        for i in range(ticker_financials.index.size):
            checkbox = QCheckBox()
            checkboxes.addButton(checkbox)
            
            checkbox.clicked.connect(on_financials_checkbox_click)
            
            financials_table.setCellWidget(i, 4, checkbox)
            

        t2 = time.perf_counter()
        print(f"{t2 - t1} seconds")
        tab4_isloaded = True


def on_financials_checkbox_click():
    financials_chart.removeAllSeries()
    series = QBarSeries()
    for i in range(financials_table.rowCount()):
        box = financials_table.cellWidget(i, 4)
        if box.isChecked():
            set = QBarSet(financials_table.verticalHeaderItem(i).text())
            for j in range(4):
                
                val = float(financials_table.item(i, j).text())
                set.append(val)
            series.append(set)
    financials_chart.addSeries(series)
    financials_chart.createDefaultAxes()


def dcf_findstock_button_click():
    global current_ticker
    ticker = ''
    i = 0
    while dcf_dialog.search_bar_groupbox.searchBar.text()[i] != ' ':
        ticker += dcf_dialog.search_bar_groupbox.searchBar.text()[i]
        i += 1
    current_ticker = ticker

    input_info = dcf.parse(ticker)
    dcf_dialog.inputs_groupbox.setVisible(True)
    dcf_dialog.inputs_groupbox.company_label.setText(f"Company: {input_info['company_name']}")
    dcf_dialog.inputs_groupbox.mkt_price.setText('${:0,.2f}'.format(input_info['mp']))
    dcf_dialog.inputs_groupbox.eps.setText(str(input_info['eps']))
    dcf_dialog.inputs_groupbox.growth.setText(str(input_info['ge']) + "% per annum")
    dcf_dialog.inputs_groupbox.growth_slider.setValue(input_info['ge'] * 100)
    dcf_dialog.inputs_groupbox.discount_rate.setText(str(dcf_dialog.inputs_groupbox.discount_rate_slider.value() / 100.0) + "%")
    dcf_dialog.inputs_groupbox.perpetual_rate.setText(str(dcf_dialog.inputs_groupbox.perpetual_rate_slider.value() / 100.0) + "%")
    dcf_dialog.inputs_groupbox.last_fcf.setText(nf.simplify(input_info['fcf']))
    dcf_dialog.inputs_groupbox.shares.setText(nf.simplify(input_info['shares']))

def growth_slider_moved():
    dcf_dialog.inputs_groupbox.growth.setText(str(dcf_dialog.inputs_groupbox.growth_slider.value() / 100.0) + "%")

def term_slider_moved():
    dcf_dialog.inputs_groupbox.term.setText(str(dcf_dialog.inputs_groupbox.term_slider.value()) + " years")

def discount_slider_moved():
    dcf_dialog.inputs_groupbox.discount_rate.setText(str(dcf_dialog.inputs_groupbox.discount_rate_slider.value() / 100.0) + "%")

def perpetual_slider_moved():
    dcf_dialog.inputs_groupbox.perpetual_rate.setText(str(dcf_dialog.inputs_groupbox.perpetual_rate_slider.value() / 100.0) + "%")

def dcf_getanalysis_button_click():
    global current_ticker
    discount_rate = dcf_dialog.inputs_groupbox.discount_rate_slider.value() / 100.0
    perpetual_rate = dcf_dialog.inputs_groupbox.perpetual_rate_slider.value() / 100.0
    growth_estimate = dcf_dialog.inputs_groupbox.growth_slider.value() / 100.0
    term = dcf_dialog.inputs_groupbox.term_slider.value()
    eps = float(dcf_dialog.inputs_groupbox.eps.text())

    dcf_analysis = dcf.get_fairval(current_ticker, discount_rate, perpetual_rate, growth_estimate, term, eps)
    future_cashflows_chartview.setVisible(True)

    future_cashflows_chart.removeAllSeries()
    future_cashflows_lineseries = QLineSeries()
    future_cashflows_lineseries.setName("Forecasted Cash Flows")
    future_cashflows_pv_lineseries = QLineSeries()
    future_cashflows_pv_lineseries.setName("Present Value of Forecasted Cash Flows")
    current_year = QDateTime().currentDateTime().date().year()

    for i in range(term):
        future_cashflows_lineseries.append(current_year + i, dcf_analysis['forecasted_cash_flows'][i])
        future_cashflows_pv_lineseries.append(current_year + i, dcf_analysis['cashflow_present_values'][i])

    future_cashflows_chart.addSeries(future_cashflows_lineseries)
    future_cashflows_chart.addSeries(future_cashflows_pv_lineseries)
    
    future_cashflows_chart.createDefaultAxes()
    future_cashflows_chart.axes(Qt.Orientation.Horizontal)[0].setTickCount(term)

    upside = round((dcf_analysis['fair_value'] / dcf_analysis['mp'] - 1) * 100, 2)
    dcf_dialog.outputs_groupbox.basic_model_output.fair_value.setText(f"${round(dcf_analysis['fair_value'], 2)} ({upside}%)")

    upside = round((dcf_analysis['graham_expected_value'] / dcf_analysis['mp'] - 1) * 100, 2)
    dcf_dialog.outputs_groupbox.graham_model_output.ev.setText(f"${round(dcf_analysis['graham_expected_value'], 2)} ({upside}%)")

    dcf_dialog.outputs_groupbox.graham_model_output.graham_growth_estimate.setText(f"{round(dcf_analysis['graham_growth_estimate'], 2)}% per annum")







def close_event(event):
    """Function that is called when the user exits the game. WIP"""
    print("closed")


app = QApplication(sys.argv)
widget = QTabWidget()
widget.setWindowTitle("Ray's Paper Trading Game")

splash = QSplashScreen(QPixmap(currentdir + 'splashscreen-images/splash.png'))
progressBar = QProgressBar(splash)
progressBar.setGeometry(420, 500, 400, 50)

splash.show()

progressBar.setValue(10)

progressBar.setValue(20)

setlocale(LC_NUMERIC, '')

progressBar.setValue(30)


#####################################################
# parse XML file data relating to user's portfolio, #
# watchlist, and settings                           #
#####################################################


progressBar.setValue(40)

up_color = getXMLData('assets\settings.xml', 'upcolor')
down_color = getXMLData('assets\settings.xml', 'downcolor')
base_style = getXMLData('assets\settings.xml', 'basestyle')

portfolio_tickers = getXMLData('assets\portfolio.xml', 'name')
portfolio_asset_types = getXMLData('assets\portfolio.xml', 'type')
portfolio_amts = getXMLData('assets\portfolio.xml', 'amount')
purchase_prices = getXMLData('assets\portfolio.xml', 'costbasis')

wallet_tickers = getXMLData('assets\wallet.xml', 'name')
wallet_amts = getXMLData('assets\wallet.xml', 'amount')
wallet_costbases = getXMLData('assets\wallet.xml', 'costbasis')

watchlist_tickers = getXMLData('assets\watchlist.xml', 'name')


all_tickers_list = pd.read_csv(currentdir + "assets\stock_list.csv")['Symbol'].tolist()
all_names_list = pd.read_csv(currentdir + "assets\stock_list.csv")['Name'].tolist()
all_tickers_list[5023] = 'NAN'

for i in range(len(all_tickers_list)):
    all_tickers_list[i] += ' - ' + all_names_list[i]
# set user's NAV equal to cash first, then iterate through stocks,
# find their current price, and add their values to user's NAV
portfolio_nav = float(portfolio_amts[0].text)
portfolio_cash = portfolio_nav

for i in range(1, len(portfolio_amts)):
    price = yf.download(tickers=portfolio_tickers[i].text, period='5d').iloc[4][3]
    portfolio_nav += float(price) * int(portfolio_amts[i].text)


wallet_nav = float(wallet_amts[0].text)
wallet_cash = wallet_nav

for i in range(1, len(wallet_amts)):
    try:
        price = yf.download(tickers=wallet_tickers[i].text, period='5d').iloc[4][3]
    except IndexError:
        price = yf.download(tickers=wallet_tickers[i].text, period='5d').iloc[3][3]
    wallet_nav += float(price) * float(wallet_amts[i].text)



# add genius font to database
QFontDatabase.addApplicationFont('fonts/genius.ttf')

progressBar.setValue(50)

####################
# portfolio dialog #
####################

# dialog settings
portfolio_dialog = QWidget()
portfolio_dialog.setObjectName("Dialog")
portfolio_dialog.resize(1000, 600)
portfolio_dialog.setAutoFillBackground(True)
portfolio_dialog.setStyleSheet('background-color: deepskyblue;')

# positions table settings
portfolio_dialog.positions_view_groupbox = QGroupBox(portfolio_dialog)
portfolio_dialog.positions_view_groupbox.setGeometry(10, 300, 900, 250)
portfolio_dialog.positions_view_groupbox.setTitle("Your Portfolio")
portfolio_dialog.positions_view_groupbox.setStyleSheet('background-color: white;')

portfolio_dialog.positions_view_groupbox.positions_view = QTableWidget(portfolio_dialog.positions_view_groupbox)
portfolio_dialog.positions_view_groupbox.positions_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
portfolio_dialog.positions_view_groupbox.positions_view.setFont(QFont('arial', 10))
portfolio_dialog.positions_view_groupbox.positions_view.setRowCount(len(portfolio_amts) - 1)
portfolio_dialog.positions_view_groupbox.positions_view.setColumnCount(8)
portfolio_dialog.positions_view_groupbox.positions_view.setGeometry(10, 20, 850, 200)
portfolio_dialog.positions_view_groupbox.positions_view.setStyleSheet('background-color: white;')
portfolio_dialog.positions_view_groupbox.positions_view.setHorizontalHeaderItem(0, QTableWidgetItem("Ticker"))
portfolio_dialog.positions_view_groupbox.positions_view.setHorizontalHeaderItem(1, QTableWidgetItem("Today's Performance"))
portfolio_dialog.positions_view_groupbox.positions_view.setHorizontalHeaderItem(2, QTableWidgetItem("Current Price"))
portfolio_dialog.positions_view_groupbox.positions_view.setHorizontalHeaderItem(3, QTableWidgetItem("Gain/Loss Per Share"))
portfolio_dialog.positions_view_groupbox.positions_view.setHorizontalHeaderItem(4, QTableWidgetItem("Purchase Price"))
portfolio_dialog.positions_view_groupbox.positions_view.setHorizontalHeaderItem(5, QTableWidgetItem("# of Shares"))
portfolio_dialog.positions_view_groupbox.positions_view.setHorizontalHeaderItem(6, QTableWidgetItem("Total Value"))
portfolio_dialog.positions_view_groupbox.positions_view.setHorizontalHeaderItem(7, QTableWidgetItem("Position Gain/Loss"))


for i in range (8):
    portfolio_dialog.positions_view_groupbox.positions_view.horizontalHeaderItem(i).setFont(QFont('arial', 10))

for i in range (portfolio_dialog.positions_view_groupbox.positions_view.rowCount()):
    portfolio_dialog.positions_view_groupbox.positions_view.setVerticalHeaderItem(0, QTableWidgetItem("1"))
    portfolio_dialog.positions_view_groupbox.positions_view.verticalHeaderItem(i).setFont(QFont('arial', 10))

update_portfolio_table()
    
portfolio_dialog.positions_view_groupbox.positions_view.resizeColumnsToContents()
progressBar.setValue(60)

# user's nav settings
portfolio_dialog.currentNAV = QGroupBox(portfolio_dialog)
portfolio_dialog.currentNAV.setTitle("Your NAV")
portfolio_dialog.currentNAV.setGeometry(10, 10, 250, 250)
portfolio_dialog.currentNAV.setStyleSheet('background-color: white;')

# net liquidation value labels
portfolio_dialog.currentNAV.netLiq = QLabel(portfolio_dialog.currentNAV)
portfolio_dialog.currentNAV.netLiq.setText("Net Liq: ")
portfolio_dialog.currentNAV.netLiq.setGeometry(10, 20, 80, 20)
portfolio_dialog.currentNAV.netLiq.setFont(QFont('genius', 10))
portfolio_dialog.currentNAV.liq = QLabel(portfolio_dialog.currentNAV)
portfolio_dialog.currentNAV.liq.setText('${:0,.2f}'.format(float(str(portfolio_nav))))
portfolio_dialog.currentNAV.liq.setGeometry(10, 40, 160, 40)
portfolio_dialog.currentNAV.liq.setFont(QFont('genius', 20))

# cash value labels
portfolio_dialog.currentNAV.cashLabel = QLabel(portfolio_dialog.currentNAV)
portfolio_dialog.currentNAV.cashLabel.setText("Cash: ")
portfolio_dialog.currentNAV.cashLabel.setGeometry(10, 90, 80, 20)
portfolio_dialog.currentNAV.cash = QLabel(portfolio_dialog.currentNAV)
portfolio_dialog.currentNAV.cash.setText('${:0,.2f}'.format(portfolio_cash))
portfolio_dialog.currentNAV.cash.setGeometry(100, 90, 80, 20)

progressBar.setValue(70)

# buying power labels
portfolio_dialog.currentNAV.buyingPowerLabel = QLabel(portfolio_dialog.currentNAV)
portfolio_dialog.currentNAV.buyingPowerLabel.setText("Buying Power: ")
portfolio_dialog.currentNAV.buyingPowerLabel.setGeometry(10, 110, 80, 20)
portfolio_dialog.currentNAV.buyingPower = QLabel(portfolio_dialog.currentNAV)
portfolio_dialog.currentNAV.buyingPower.setText('${:0,.2f}'.format(get_portfolio_bp()))
portfolio_dialog.currentNAV.buyingPower.setGeometry(100, 110, 80, 20)

# assets labels
portfolio_dialog.currentNAV.assetsLabel = QLabel(portfolio_dialog.currentNAV)
portfolio_dialog.currentNAV.assetsLabel.setText("Long Assets: ")
portfolio_dialog.currentNAV.assetsLabel.setGeometry(10, 130, 80, 20)
portfolio_dialog.currentNAV.assets = QLabel(portfolio_dialog.currentNAV)
total_long = 0
for i in range (1, len(portfolio_amts)):
    price = float(portfolio_dialog.positions_view_groupbox.positions_view.item(i - 1, 2).text()[1:])
    if int(portfolio_amts[i].text) > 0:
        total_long += float(price) * int(portfolio_amts[i].text)

portfolio_dialog.currentNAV.assets.setText('${:0,.2f}'.format(total_long))
portfolio_dialog.currentNAV.assets.setGeometry(100, 130, 80, 20)

# liabilities labels
portfolio_dialog.currentNAV.liabilitiesLabel = QLabel(portfolio_dialog.currentNAV)
portfolio_dialog.currentNAV.liabilitiesLabel.setText("Short Assets: ")
portfolio_dialog.currentNAV.liabilitiesLabel.setGeometry(10, 150, 80, 20)
portfolio_dialog.currentNAV.liabilities = QLabel(portfolio_dialog.currentNAV)
total_short = 0
for i in range (1, len(portfolio_amts)):
    price = float(portfolio_dialog.positions_view_groupbox.positions_view.item(i - 1, 2).text()[1:])
    if int(portfolio_amts[i].text) < 0:
        total_short -= float(price) * int(portfolio_amts[i].text)

portfolio_dialog.currentNAV.liabilities.setText('${:0,.2f}'.format(total_short))
portfolio_dialog.currentNAV.liabilities.setGeometry(100, 150, 80, 20)


# return since inception labels
portfolio_dialog.currentNAV.returnSinceInceptionLabel = QLabel(portfolio_dialog.currentNAV)
portfolio_dialog.currentNAV.returnSinceInceptionLabel.setText("Return Since Inception: ")
portfolio_dialog.currentNAV.returnSinceInceptionLabel.setGeometry(10, 170, 120, 20)
portfolio_dialog.currentNAV.returnSinceInception = QLabel(portfolio_dialog.currentNAV)
portfolio_dialog.currentNAV.returnSinceInception.setFont(QFont('genius', 20))
portfolio_dialog.currentNAV.returnSinceInception.setText('{:0.2f}'.format((portfolio_nav / 10000 - 1) * 100) + "%")
portfolio_dialog.currentNAV.returnSinceInception.setGeometry(10, 190, 120, 30)

progressBar.setValue(80)
# watchlist table settings
portfolio_dialog.watchlist_groupbox = QGroupBox(portfolio_dialog)
portfolio_dialog.watchlist_groupbox.setTitle("Your Watchlist")
portfolio_dialog.watchlist_groupbox.setGeometry(270, 10, 500, 250)
portfolio_dialog.watchlist_groupbox.setStyleSheet('background-color: white;')

portfolio_dialog.watchlist_groupbox.watchlist_view = QTableWidget(portfolio_dialog.watchlist_groupbox)
portfolio_dialog.watchlist_groupbox.watchlist_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
portfolio_dialog.watchlist_groupbox.watchlist_view.setRowCount(len(watchlist_tickers))
portfolio_dialog.watchlist_groupbox.watchlist_view.setColumnCount(4)
portfolio_dialog.watchlist_groupbox.watchlist_view.setHorizontalHeaderItem(0, QTableWidgetItem("Ticker"))
portfolio_dialog.watchlist_groupbox.watchlist_view.setHorizontalHeaderItem(1, QTableWidgetItem("Today's Performance"))
portfolio_dialog.watchlist_groupbox.watchlist_view.setHorizontalHeaderItem(2, QTableWidgetItem("Current Price"))
portfolio_dialog.watchlist_groupbox.watchlist_view.setHorizontalHeaderItem(3, QTableWidgetItem("Gain/Loss Per Share"))

for i in range (4):
    portfolio_dialog.watchlist_groupbox.watchlist_view.horizontalHeaderItem(i).setFont(QFont('arial', 10))
for i in range (portfolio_dialog.watchlist_groupbox.watchlist_view.rowCount()):
    portfolio_dialog.watchlist_groupbox.watchlist_view.setVerticalHeaderItem(i, QTableWidgetItem(str(i + 1)))
    portfolio_dialog.watchlist_groupbox.watchlist_view.verticalHeaderItem(i).setFont(QFont('arial', 10))

portfolio_dialog.watchlist_groupbox.watchlist_view.setFont(QFont('arial', 10))
portfolio_dialog.watchlist_groupbox.watchlist_view.setGeometry(10, 20, 500, 200)

update_watchlist_tickers()

portfolio_dialog.watchlist_groupbox.watchlist_view.resizeColumnsToContents()

# asset class pie chart
asset_class_chart = QPieSeries()
asset_class_chart.append("ETFs", 1)
asset_class_chart.append("Stocks", 2)
asset_class_chart.append("Options", 3)
asset_class_chart.append("Futures", 4)
asset_class_chart.append("Cash", 5)

chart = QChart()
chart.addSeries(asset_class_chart)
chart.setTitle("Positions by Asset Class")
chart.setVisible(True)

portfolio_dialog.chart_view = QChartView(chart)
portfolio_dialog.chart_view.setParent(portfolio_dialog)
portfolio_dialog.chart_view.setGeometry(780, 2, 500, 270)
portfolio_dialog.chart_view.setVisible(True)

update_portfolio_piechart()

################
# chart dialog #
################

progressBar.setValue(90)
chart_dialog = QDialog()
chart_dialog.setObjectName("Dialog")
chart_dialog.resize(1000, 600)
chart_dialog.setStyleSheet('background-color: deepskyblue;')

chart_dialog.broad_market_groupbox = QGroupBox(chart_dialog)
chart_dialog.broad_market_groupbox.setTitle("Broad Market Indicies")
chart_dialog.broad_market_groupbox.setStyleSheet('background-color: white;')
chart_dialog.broad_market_groupbox.setGeometry(10, 10, 700, 50)

chart_dialog.broad_market_groupbox.spyButton = QPushButton(text="Chart SPY", parent=chart_dialog.broad_market_groupbox)
chart_dialog.broad_market_groupbox.spyButton.setGeometry(QRect(10, 20, 150, 20))
chart_dialog.broad_market_groupbox.spyButton.clicked.connect(spy_button_clicked)

chart_dialog.broad_market_groupbox.qqqButton = QPushButton(text="Chart QQQ", parent=chart_dialog.broad_market_groupbox)
chart_dialog.broad_market_groupbox.qqqButton.setGeometry(QRect(170, 20, 150, 20))
chart_dialog.broad_market_groupbox.qqqButton.clicked.connect(qqq_button_clicked)

chart_dialog.broad_market_groupbox.diaButton = QPushButton(text="Chart DIA", parent=chart_dialog.broad_market_groupbox)
chart_dialog.broad_market_groupbox.diaButton.setGeometry(QRect(330, 20, 150, 20))
chart_dialog.broad_market_groupbox.diaButton.clicked.connect(dia_button_clicked)

chart_dialog.broad_market_groupbox.vixButton = QPushButton(text="Chart VIX", parent=chart_dialog.broad_market_groupbox)
chart_dialog.broad_market_groupbox.vixButton.setGeometry(QRect(490, 20, 150, 20))
chart_dialog.broad_market_groupbox.vixButton.clicked.connect(vix_button_clicked)

# search bar for searching for a stock to chart
chart_dialog.search_bar_groupbox = QGroupBox(chart_dialog)
chart_dialog.search_bar_groupbox.setStyleSheet('background-color: white;')
chart_dialog.search_bar_groupbox.setTitle("Find a Stock")
chart_dialog.search_bar_groupbox.setGeometry(10, 70, 960, 70)

chart_dialog.search_bar_groupbox.searchBar = QLineEdit(chart_dialog.search_bar_groupbox)
chart_dialog.search_bar_groupbox.searchBar.setGeometry(10, 20, 850, 40)
chart_dialog.search_bar_groupbox.searchBar.textChanged.connect(lambda txt: searchTextChanged(txt))
chart_dialog.search_bar_groupbox.searchBar.setFont(QFont('arial', 10))

chart_dialog.search_bar_groupbox.search_button = QPushButton(chart_dialog.search_bar_groupbox)
chart_dialog.search_bar_groupbox.search_button.setGeometry(870, 20, 80, 40)
chart_dialog.search_bar_groupbox.search_button.setText("Chart")
chart_dialog.search_bar_groupbox.search_button.setEnabled(False)
chart_dialog.search_bar_groupbox.search_button.clicked.connect(searchButtonClicked)

chart_dialog.settings_groupbox = QGroupBox(chart_dialog)
chart_dialog.settings_groupbox.setStyleSheet('background-color: white;')
chart_dialog.settings_groupbox.setGeometry(10, 150, 1280, 600)
chart_dialog.settings_groupbox.setTitle("Chart Settings")

periods = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]
timeframes = ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"]

chart_dialog.settings_groupbox.period_radiobutton = QRadioButton(chart_dialog.settings_groupbox)
chart_dialog.settings_groupbox.period_radiobutton.setText("Chart by Period")
chart_dialog.settings_groupbox.period_radiobutton.setGeometry(10, 50, 100, 30)
chart_dialog.settings_groupbox.period_radiobutton.setChecked(True)
chart_dialog.settings_groupbox.period_radiobutton.clicked.connect(period_radiobutton_clicked)

chart_dialog.settings_groupbox.daterange_radiobutton = QRadioButton(chart_dialog.settings_groupbox)
chart_dialog.settings_groupbox.daterange_radiobutton.setText("Chart by Date Range")
chart_dialog.settings_groupbox.daterange_radiobutton.setGeometry(10, 100, 170, 30)
chart_dialog.settings_groupbox.daterange_radiobutton.clicked.connect(daterange_radiobutton_clicked)

chart_dialog.settings_groupbox.data_period_combobox = QComboBox(chart_dialog.settings_groupbox)
chart_dialog.settings_groupbox.data_period_combobox.addItems(periods)
chart_dialog.settings_groupbox.data_period_combobox.setGeometry(120, 60, 50, 20)

chart_dialog.settings_groupbox.data_timeframe_combobox = QComboBox(chart_dialog.settings_groupbox)
chart_dialog.settings_groupbox.data_timeframe_combobox.addItems(timeframes)
chart_dialog.settings_groupbox.data_timeframe_combobox.setGeometry(850, 50, 50, 30)

chart_dialog.settings_groupbox.prepost_checkbox = QCheckBox(chart_dialog.settings_groupbox)
chart_dialog.settings_groupbox.prepost_checkbox.setText("Include Pre/Post Market Data")
chart_dialog.settings_groupbox.prepost_checkbox.setGeometry(10, 20, 180, 30)

chart_dialog.settings_groupbox.split_dividend_checkbox = QCheckBox(chart_dialog.settings_groupbox)
chart_dialog.settings_groupbox.split_dividend_checkbox.setText("Show Split and Dividend Actions")
chart_dialog.settings_groupbox.split_dividend_checkbox.setGeometry(200, 20, 190, 30)

chart_dialog.settings_groupbox.adjust_ohlc_checkbox = QCheckBox(chart_dialog.settings_groupbox)
chart_dialog.settings_groupbox.adjust_ohlc_checkbox.setText("Adjust OHLC")
chart_dialog.settings_groupbox.adjust_ohlc_checkbox.setGeometry(400, 20, 100, 30)

chart_dialog.settings_groupbox.volume_checkbox = QCheckBox(chart_dialog.settings_groupbox)
chart_dialog.settings_groupbox.volume_checkbox.setText("Include Volume Bars")
chart_dialog.settings_groupbox.volume_checkbox.setGeometry(500, 20, 140, 30)

chart_dialog.settings_groupbox.nontrading_checkbox = QCheckBox(chart_dialog.settings_groupbox)
chart_dialog.settings_groupbox.nontrading_checkbox.setText("Include Non-Trading Days")
chart_dialog.settings_groupbox.nontrading_checkbox.setGeometry(650, 20, 160, 30)

chart_dialog.settings_groupbox.timeframe_label = QLabel(chart_dialog.settings_groupbox)
chart_dialog.settings_groupbox.timeframe_label.setText("Chart Timeframe:")
chart_dialog.settings_groupbox.timeframe_label.setGeometry(820, 20, 100, 30)

chart_dialog.settings_groupbox.start_date = QCalendarWidget(chart_dialog.settings_groupbox)
chart_dialog.settings_groupbox.start_date.setGeometry(10, 130, 600, 370)
chart_dialog.settings_groupbox.start_date.setStyleSheet('background-color: deepskyblue; border: 3px solid black;')
chart_dialog.settings_groupbox.start_date.setEnabled(False)


chart_dialog.settings_groupbox.end_date = QCalendarWidget(chart_dialog.settings_groupbox)
chart_dialog.settings_groupbox.end_date.setGeometry(620, 130, 600, 370)
chart_dialog.settings_groupbox.end_date.setStyleSheet('background-color: deepskyblue; border: 3px solid black;')
chart_dialog.settings_groupbox.end_date.setEnabled(False)

model = QStringListModel()
model.setStringList(all_tickers_list)

completer = ac.CustomQCompleter()

completer.setModel(model)
chart_dialog.search_bar_groupbox.searchBar.setCompleter(completer)
completer.activated.connect(lambda: chart_dialog.search_bar_groupbox.search_button.setEnabled(True))
completer.setMaxVisibleItems(5)


################
# trade dialog #
################

trade_dialog = QDialog()
trade_dialog.setStyleSheet('background-color: deepskyblue;')


#####################
# stock info dialog #
#####################

stockinfo_dialog = QTabWidget()
stockinfo_dialog.setStyleSheet('background-color: deepskyblue;')

stockinfo_dialog_main = QDialog()
stockinfo_dialog_main.setStyleSheet('background-color: deepskyblue')
stockinfo_dialog_main.search_bar_groupbox = QGroupBox(stockinfo_dialog_main)
stockinfo_dialog_main.search_bar_groupbox.setStyleSheet('background-color: white;')
stockinfo_dialog_main.search_bar_groupbox.setTitle("Find a Stock")
stockinfo_dialog_main.search_bar_groupbox.setGeometry(10, 10, 960, 70)

stockinfo_dialog_main.search_bar_groupbox.searchBar = QLineEdit(stockinfo_dialog_main.search_bar_groupbox)
stockinfo_dialog_main.search_bar_groupbox.searchBar.setGeometry(10, 20, 850, 40)
stockinfo_dialog_main.search_bar_groupbox.searchBar.textChanged.connect(lambda txt: searchTextChanged(txt))
stockinfo_dialog_main.search_bar_groupbox.searchBar.setFont(QFont('arial', 10))
stockinfo_dialog_main.search_bar_groupbox.searchBar.setCompleter(completer)

stockinfo_dialog_main.search_bar_groupbox.search_button = QPushButton(stockinfo_dialog_main.search_bar_groupbox)
stockinfo_dialog_main.search_bar_groupbox.search_button.setGeometry(870, 20, 80, 40)
stockinfo_dialog_main.search_bar_groupbox.search_button.setText("Show Info")
stockinfo_dialog_main.search_bar_groupbox.search_button.clicked.connect(lambda: stockinfo_searchbar_click(stockinfo_dialog_main))

stockinfo_dialog_main.asset_info_groupbox = QGroupBox(stockinfo_dialog_main)
stockinfo_dialog_main.asset_info_groupbox.setStyleSheet('background-color: white')
stockinfo_dialog_main.asset_info_groupbox.setTitle("Asset Profile")
stockinfo_dialog_main.asset_info_groupbox.setGeometry(10, 90, 310, 550)
stockinfo_dialog_main.asset_info_groupbox.setVisible(False)
stockinfo_dialog_main.asset_info_groupbox.content_container = QScrollArea(stockinfo_dialog_main.asset_info_groupbox)

assetinfo_scrollarea_widget = QWidget()
assetinfo_scrollarea_widget.resize(300, 800)
assetinfo_scrollarea_widget.setLayout(QVBoxLayout())

stockinfo_dialog_main.asset_info_groupbox.content_container.setWidget(assetinfo_scrollarea_widget)
stockinfo_dialog_main.asset_info_groupbox.content_container.setGeometry(5, 15, 305, 520)
stockinfo_dialog_main.asset_info_groupbox.content_container.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

stockinfo_dialog_main.about_groupbox = QGroupBox(stockinfo_dialog_main)
stockinfo_dialog_main.about_groupbox.setStyleSheet('background-color: white')
stockinfo_dialog_main.about_groupbox.setTitle("About the Asset")
stockinfo_dialog_main.about_groupbox.setGeometry(330, 90, 470, 550)
stockinfo_dialog_main.about_groupbox.setVisible(False)
stockinfo_dialog_main.about_groupbox.content_container = QScrollArea(stockinfo_dialog_main.about_groupbox)

about_scrollarea_widget = QWidget()
about_scrollarea_widget.resize(400, 800)
about_scrollarea_widget.setLayout(QVBoxLayout())
stockinfo_dialog_main.about_groupbox.content_container.setWidget(about_scrollarea_widget)
stockinfo_dialog_main.about_groupbox.content_container.setGeometry(5, 15, 420, 520)
stockinfo_dialog_main.about_groupbox.content_container.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

stockinfo_dialog_main.news_groupbox = QGroupBox(stockinfo_dialog_main)
stockinfo_dialog_main.news_groupbox.setStyleSheet('background-color: white')
stockinfo_dialog_main.news_groupbox.setTitle("News")
stockinfo_dialog_main.news_groupbox.setGeometry(810, 90, 470, 550)
stockinfo_dialog_main.news_groupbox.setVisible(False)
stockinfo_dialog_main.news_groupbox.setLayout(QVBoxLayout())

stockinfo_dialog_recs = QDialog()
stockinfo_dialog_recs.setStyleSheet('background-color: deepskyblue')

stockinfo_dialog_recs.analyst_rec_groupbox = QGroupBox(stockinfo_dialog_recs)
stockinfo_dialog_recs.analyst_rec_groupbox.setStyleSheet('background-color: white')
stockinfo_dialog_recs.analyst_rec_groupbox.setTitle("Analyst Recommendations")
stockinfo_dialog_recs.analyst_rec_groupbox.setGeometry(10, 10, 310, 630)
stockinfo_dialog_recs.analyst_rec_groupbox.setVisible(False)
stockinfo_dialog_recs.analyst_rec_groupbox.setLayout(QVBoxLayout())

stockinfo_dialog_recs.iandi_groupbox = QGroupBox(stockinfo_dialog_recs)
stockinfo_dialog_recs.iandi_groupbox.setStyleSheet('background-color: white')
stockinfo_dialog_recs.iandi_groupbox.setTitle("Insiders and Institutions")
stockinfo_dialog_recs.iandi_groupbox.setGeometry(330, 10, 470, 630)
stockinfo_dialog_recs.iandi_groupbox.setVisible(False)
stockinfo_dialog_recs.iandi_groupbox.setLayout(QVBoxLayout())

stockinfo_dialog_recs.mutfund_groupbox = QGroupBox(stockinfo_dialog_recs)
stockinfo_dialog_recs.mutfund_groupbox.setStyleSheet('background-color: white')
stockinfo_dialog_recs.mutfund_groupbox.setTitle("Mutual Fund Holders")
stockinfo_dialog_recs.mutfund_groupbox.setGeometry(810, 10, 470, 630)
stockinfo_dialog_recs.mutfund_groupbox.setVisible(False)
stockinfo_dialog_recs.mutfund_groupbox.setLayout(QVBoxLayout())

stockinfo_dialog_forecasts = QDialog()
stockinfo_dialog_forecasts.setStyleSheet('background-color: deepskyblue')

stockinfo_dialog_forecasts.chart_groupbox = QGroupBox(stockinfo_dialog_forecasts)
stockinfo_dialog_forecasts.chart_groupbox.setTitle("Charts and Graphs")
stockinfo_dialog_forecasts.chart_groupbox.setGeometry(0, 0, 1300, 600)

stockinfo_dialog_forecasts.chart_groupbox.content_container = QScrollArea(stockinfo_dialog_forecasts)

prediction_chart_widget = QWidget()
prediction_chart_widget.resize(1300, 2000)
prediction_chart_widget.setLayout(QVBoxLayout())

stockinfo_dialog_forecasts.chart_groupbox.content_container.setWidget(prediction_chart_widget)
stockinfo_dialog_forecasts.chart_groupbox.content_container.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
stockinfo_dialog_forecasts.chart_groupbox.content_container.setGeometry(5, 15, 1290, 650)


ptchart = QChart()


ptlineseries = QLineSeries()
ptlineseries.setName("stock")
ptchart.addSeries(ptlineseries)

x_axis = QDateTimeAxis()
x_axis.setTickCount(7)
x_axis.setFormat("MM-dd-yyyy")
x_axis.setTitleText("Date")
x_axis.setVisible(True)

ptchart.addAxis(x_axis, Qt.AlignmentFlag.AlignBottom)
ptlineseries.attachAxis(x_axis)
y_axis = QValueAxis()

ptchart.addAxis(y_axis, Qt.AlignmentFlag.AlignLeft)
ptlineseries.attachAxis(y_axis)

ptchartview = QChartView(ptchart)

pt_groupbox = QGroupBox(prediction_chart_widget)
pt_groupbox.setTitle("Analyst Price Targets")
pt_groupbox.setGeometry(10, 10, 1200, 350)

ptchartview.setParent(pt_groupbox)
ptchartview.setGeometry(10, 15, 800, 300)

ptchartview.setVisible(True)

pt_label_container = QWidget(pt_groupbox)
pt_label_container.setStyleSheet('background-color: white')
pt_label_container.setGeometry(820, 22, 350, 285)
pt_label_container.setLayout(QVBoxLayout())

qtr_earnings_chart = QChart()
qtr_earnings_chart.setTitle("Quarterly EPS")

qtr_earnings_barseries = QBarSeries()
qtr_earnings_barseries.setName("Earnings")

qtr_earnings_chart.addSeries(qtr_earnings_barseries)

qtr_earnings_groupbox = QGroupBox(prediction_chart_widget)
qtr_earnings_groupbox.setTitle("Earnings History and Projections")
qtr_earnings_groupbox.setGeometry(10, 370, 1200, 350)

qtr_earnings_chartview = QChartView(qtr_earnings_chart)
qtr_earnings_chartview.setParent(qtr_earnings_groupbox)
qtr_earnings_chartview.setVisible(True)
qtr_earnings_chartview.setGeometry(10, 15, 800, 300)

qtr_earnings_table = QTableWidget(qtr_earnings_groupbox)
qtr_earnings_table.setGeometry(820, 20, 350, 290)
qtr_earnings_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
qtr_earnings_table.setFont(QFont('arial', 10))
qtr_earnings_table.setStyleSheet('background-color: white;')

qtr_revtrend_chart = QChart()
qtr_revtrend_chart.setTitle("Quarterly Revenue Trend")

qtr_revtrend_barseries = QBarSeries()
qtr_revtrend_chart.addSeries(qtr_revtrend_barseries)

qtr_revtrend_groupbox = QGroupBox(prediction_chart_widget)
qtr_revtrend_groupbox.setTitle("Revenue History and Projections")
qtr_revtrend_groupbox.setGeometry(10, 730, 1200, 350)

qtr_revtrend_chartview = QChartView(qtr_revtrend_chart)
qtr_revtrend_chartview.setParent(qtr_revtrend_groupbox)
qtr_revtrend_chartview.setVisible(True)
qtr_revtrend_chartview.setGeometry(10, 15, 800, 300)

qtr_revtrend_label_container = QWidget(qtr_revtrend_groupbox)
qtr_revtrend_label_container.setGeometry(820, 20, 350, 290)
qtr_revtrend_label_container.setStyleSheet('background-color: white;')
qtr_revtrend_label_container.setLayout(QVBoxLayout())

yr_earnings_chart = QChart()
yr_earnings_chart.setTitle("Yearly EPS")

yr_earnings_barseries = QBarSeries()
yr_earnings_barseries.setName("Earnings")

yr_earnings_chart.addSeries(yr_earnings_barseries)

yr_earnings_groupbox = QGroupBox(prediction_chart_widget)
yr_earnings_groupbox.setTitle("Earnings History and Projections")
yr_earnings_groupbox.setGeometry(10, 1090, 1200, 350)

yr_earnings_chartview = QChartView(yr_earnings_chart)
yr_earnings_chartview.setParent(yr_earnings_groupbox)
yr_earnings_chartview.setVisible(True)
yr_earnings_chartview.setGeometry(10, 15, 800, 300)

yr_earnings_label_container = QWidget(yr_earnings_groupbox)
yr_earnings_label_container.setGeometry(820, 20, 350, 290)
yr_earnings_label_container.setStyleSheet('background-color: white;')
yr_earnings_label_container.setLayout(QVBoxLayout())

yr_revtrend_chart = QChart()
yr_revtrend_chart.setTitle("Yearly Revenue Trend")

yr_revtrend_barseries = QBarSeries()
yr_revtrend_chart.addSeries(yr_revtrend_barseries)

yr_revtrend_groupbox = QGroupBox(prediction_chart_widget)
yr_revtrend_groupbox.setTitle("Revenue History and Projections")
yr_revtrend_groupbox.setGeometry(10, 1450, 1200, 360)

yr_revtrend_chartview = QChartView(yr_revtrend_chart)
yr_revtrend_chartview.setParent(yr_revtrend_groupbox)
yr_revtrend_chartview.setVisible(True)
yr_revtrend_chartview.setGeometry(10, 15, 800, 300)

yr_revtrend_label_container = QWidget(yr_revtrend_groupbox)
yr_revtrend_label_container.setGeometry(820, 20, 350, 290)
yr_revtrend_label_container.setStyleSheet('background-color: white;')
yr_revtrend_label_container.setLayout(QVBoxLayout())

stockinfo_dialog_financials = QDialog()
stockinfo_dialog_financials.setStyleSheet('background-color: deepskyblue')

stockinfo_dialog_financials.content_container = QScrollArea(stockinfo_dialog_financials)

financials_chart_widget = QWidget()
financials_chart_widget.resize(1300, 2000)
financials_chart_widget.setLayout(QVBoxLayout())

stockinfo_dialog_financials.content_container.setWidget(financials_chart_widget)
stockinfo_dialog_financials.content_container.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
stockinfo_dialog_financials.content_container.setGeometry(5, 15, 1290, 650)

financials_chart = QChart()
financials_chart.setTitle("Financial Statements")

financials_barseries = QBarSeries()
financials_chart.addSeries(financials_barseries)

financials_groupbox = QGroupBox(financials_chart_widget)
financials_groupbox.setTitle("Fundamentals")
financials_groupbox.setGeometry(10, 10, 1250, 1950)

financials_chartview = QChartView(financials_chart)
financials_chartview.setParent(financials_groupbox)
financials_chartview.setVisible(True)
financials_chartview.setGeometry(10, 15, 1200, 300)

financials_table = QTableWidget(financials_groupbox)
financials_table.setGeometry(10, 325, 1200, 1500)
financials_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
financials_table.setFont(QFont('arial', 10))
financials_table.setStyleSheet('background-color: white;')

stockinfo_dialog.addTab(stockinfo_dialog_main, "Overview")
stockinfo_dialog.addTab(stockinfo_dialog_recs, "Insiders and Institutions")
stockinfo_dialog.addTab(stockinfo_dialog_forecasts, "Forecasts")
stockinfo_dialog.addTab(stockinfo_dialog_financials, "Financials")


stockinfo_dialog.connect(stockinfo_dialog, SIGNAL('currentChanged(int)'), lambda: stockinfo_dialog_changed(stockinfo_dialog.currentIndex()))

####################
# DCF model dialog #
####################

dcf_dialog = QDialog()
dcf_dialog.setStyleSheet('background-color: deepskyblue;')

dcf_dialog.search_bar_groupbox = QGroupBox(dcf_dialog)
dcf_dialog.search_bar_groupbox.setStyleSheet('background-color: white;')
dcf_dialog.search_bar_groupbox.setTitle("Find a Stock")
dcf_dialog.search_bar_groupbox.setGeometry(10, 10, 960, 70)

dcf_dialog.search_bar_groupbox.searchBar = QLineEdit(dcf_dialog.search_bar_groupbox)
dcf_dialog.search_bar_groupbox.searchBar.setGeometry(10, 20, 850, 40)
dcf_dialog.search_bar_groupbox.searchBar.textChanged.connect(lambda txt: searchTextChanged(txt))
dcf_dialog.search_bar_groupbox.searchBar.setFont(QFont('arial', 10))
dcf_dialog.search_bar_groupbox.searchBar.setCompleter(completer)

dcf_dialog.search_bar_groupbox.search_button = QPushButton(dcf_dialog.search_bar_groupbox)
dcf_dialog.search_bar_groupbox.search_button.setGeometry(870, 20, 80, 40)
dcf_dialog.search_bar_groupbox.search_button.setText("Show Model")
dcf_dialog.search_bar_groupbox.search_button.clicked.connect(lambda: dcf_findstock_button_click())

dcf_dialog.inputs_groupbox = QGroupBox(dcf_dialog)
dcf_dialog.inputs_groupbox.setStyleSheet('background-color: white;')
dcf_dialog.inputs_groupbox.setTitle("Model Inputs")
dcf_dialog.inputs_groupbox.setGeometry(10, 90, 630, 570)

dcf_dialog.inputs_groupbox.company_label = QLabel(dcf_dialog.inputs_groupbox)
dcf_dialog.inputs_groupbox.company_label.setText("Company:")
dcf_dialog.inputs_groupbox.company_label.setGeometry(10, 20, 100, 50)

dcf_dialog.inputs_groupbox.mkt_price_label = QLabel(dcf_dialog.inputs_groupbox)
dcf_dialog.inputs_groupbox.mkt_price_label.setText("Market Price:")
dcf_dialog.inputs_groupbox.mkt_price_label.setGeometry(10, 70, 100, 50)

dcf_dialog.inputs_groupbox.mkt_price = QLabel(dcf_dialog.inputs_groupbox)
dcf_dialog.inputs_groupbox.mkt_price.setGeometry(570, 70, 100, 50)

dcf_dialog.inputs_groupbox.eps_label = QLabel(dcf_dialog.inputs_groupbox)
dcf_dialog.inputs_groupbox.eps_label.setText("Earnings per Share:")
dcf_dialog.inputs_groupbox.eps_label.setGeometry(10, 120, 100, 50)

dcf_dialog.inputs_groupbox.eps = QLabel(dcf_dialog.inputs_groupbox)
dcf_dialog.inputs_groupbox.eps.setGeometry(570, 120, 100, 50)

dcf_dialog.inputs_groupbox.growth_label = QLabel(dcf_dialog.inputs_groupbox)
dcf_dialog.inputs_groupbox.growth_label.setText("Growth Estimate:")
dcf_dialog.inputs_groupbox.growth_label.setGeometry(10, 170, 100, 50)

dcf_dialog.inputs_groupbox.growth_slider = QSlider(dcf_dialog.inputs_groupbox)
dcf_dialog.inputs_groupbox.growth_slider.setOrientation(Qt.Orientation.Horizontal)
dcf_dialog.inputs_groupbox.growth_slider.setTickPosition(QSlider.TickPosition.TicksBothSides)
dcf_dialog.inputs_groupbox.growth_slider.setGeometry(110, 170, 450, 50)
dcf_dialog.inputs_groupbox.growth_slider.setTickInterval(10)
dcf_dialog.inputs_groupbox.growth_slider.setRange(-500, 4000)
dcf_dialog.inputs_groupbox.growth_slider.setSliderPosition(0)
dcf_dialog.inputs_groupbox.growth_slider.valueChanged.connect(growth_slider_moved)

dcf_dialog.inputs_groupbox.growth = QLabel(dcf_dialog.inputs_groupbox)
dcf_dialog.inputs_groupbox.growth.setGeometry(570, 170, 100, 50)

dcf_dialog.inputs_groupbox.def_growth_button = QCheckBox(dcf_dialog.inputs_groupbox)
dcf_dialog.inputs_groupbox.def_growth_button.setText("Use Analyst 5-Year Growth Estimate")
dcf_dialog.inputs_groupbox.def_growth_button.setGeometry(1100, 170, 100, 50)

dcf_dialog.inputs_groupbox.term_label = QLabel(dcf_dialog.inputs_groupbox)
dcf_dialog.inputs_groupbox.term_label.setText("Term:")
dcf_dialog.inputs_groupbox.term_label.setGeometry(10, 220, 100, 50)

dcf_dialog.inputs_groupbox.term_slider = QSlider(dcf_dialog.inputs_groupbox)
dcf_dialog.inputs_groupbox.term_slider.setOrientation(Qt.Orientation.Horizontal)
dcf_dialog.inputs_groupbox.term_slider.setTickPosition(QSlider.TickPosition.TicksBothSides)
dcf_dialog.inputs_groupbox.term_slider.setGeometry(110, 220, 450, 50)
dcf_dialog.inputs_groupbox.term_slider.setTickInterval(1)
dcf_dialog.inputs_groupbox.term_slider.setRange(1, 10)
dcf_dialog.inputs_groupbox.term_slider.setSliderPosition(5)
dcf_dialog.inputs_groupbox.term_slider.valueChanged.connect(term_slider_moved)

dcf_dialog.inputs_groupbox.term = QLabel(dcf_dialog.inputs_groupbox)
dcf_dialog.inputs_groupbox.term.setText("5 years")
dcf_dialog.inputs_groupbox.term.setGeometry(570, 220, 100, 50)

dcf_dialog.inputs_groupbox.discount_rate_label = QLabel(dcf_dialog.inputs_groupbox)
dcf_dialog.inputs_groupbox.discount_rate_label.setText("Discount Rate: ")
dcf_dialog.inputs_groupbox.discount_rate_label.setGeometry(10, 270, 100, 50)

dcf_dialog.inputs_groupbox.discount_rate_slider = QSlider(dcf_dialog.inputs_groupbox)
dcf_dialog.inputs_groupbox.discount_rate_slider.setOrientation(Qt.Orientation.Horizontal)
dcf_dialog.inputs_groupbox.discount_rate_slider.setTickPosition(QSlider.TickPosition.TicksBothSides)
dcf_dialog.inputs_groupbox.discount_rate_slider.setGeometry(110, 270, 450, 50)
dcf_dialog.inputs_groupbox.discount_rate_slider.setTickInterval(10)
dcf_dialog.inputs_groupbox.discount_rate_slider.setRange(-500, 2000)
dcf_dialog.inputs_groupbox.discount_rate_slider.setSliderPosition(1000)
dcf_dialog.inputs_groupbox.discount_rate_slider.valueChanged.connect(discount_slider_moved)


dcf_dialog.inputs_groupbox.discount_rate = QLabel(dcf_dialog.inputs_groupbox)
dcf_dialog.inputs_groupbox.discount_rate.setGeometry(570, 270, 100, 50)

dcf_dialog.inputs_groupbox.perpetual_rate_label = QLabel(dcf_dialog.inputs_groupbox)
dcf_dialog.inputs_groupbox.perpetual_rate_label.setText("Perpetual Rate:")
dcf_dialog.inputs_groupbox.perpetual_rate_label.setGeometry(10, 320, 100, 50)

dcf_dialog.inputs_groupbox.perpetual_rate_slider = QSlider(dcf_dialog.inputs_groupbox)
dcf_dialog.inputs_groupbox.perpetual_rate_slider.setOrientation(Qt.Orientation.Horizontal)
dcf_dialog.inputs_groupbox.perpetual_rate_slider.setGeometry(110, 320, 450, 50)
dcf_dialog.inputs_groupbox.perpetual_rate_slider.setTickInterval(10)
dcf_dialog.inputs_groupbox.perpetual_rate_slider.setTickPosition(QSlider.TickPosition.TicksBothSides)
dcf_dialog.inputs_groupbox.perpetual_rate_slider.setRange(-500, 1000)
dcf_dialog.inputs_groupbox.perpetual_rate_slider.setSliderPosition(250)
dcf_dialog.inputs_groupbox.perpetual_rate_slider.valueChanged.connect(perpetual_slider_moved)

dcf_dialog.inputs_groupbox.perpetual_rate = QLabel(dcf_dialog.inputs_groupbox)
dcf_dialog.inputs_groupbox.perpetual_rate.setGeometry(570, 320, 100, 50)

dcf_dialog.inputs_groupbox.last_fcf_label = QLabel(dcf_dialog.inputs_groupbox)
dcf_dialog.inputs_groupbox.last_fcf_label.setText("Last Free Cash Flow:")
dcf_dialog.inputs_groupbox.last_fcf_label.setGeometry(10, 370, 100, 50)

dcf_dialog.inputs_groupbox.last_fcf = QLabel(dcf_dialog.inputs_groupbox)
dcf_dialog.inputs_groupbox.last_fcf.setGeometry(570, 370, 100, 50)

dcf_dialog.inputs_groupbox.shares_label = QLabel(dcf_dialog.inputs_groupbox)
dcf_dialog.inputs_groupbox.shares_label.setText("Shares in Circulation:")
dcf_dialog.inputs_groupbox.shares_label.setGeometry(10, 420, 100, 50)

dcf_dialog.inputs_groupbox.shares = QLabel(dcf_dialog.inputs_groupbox)
dcf_dialog.inputs_groupbox.shares.setGeometry(570, 420, 100, 50)

dcf_dialog.inputs_groupbox.get_analysis_button = QPushButton(dcf_dialog.inputs_groupbox)
dcf_dialog.inputs_groupbox.get_analysis_button.setGeometry(210, 480, 200, 100)
dcf_dialog.inputs_groupbox.get_analysis_button.setText("Get Fair Value")
dcf_dialog.inputs_groupbox.get_analysis_button.clicked.connect(dcf_getanalysis_button_click)


dcf_dialog.outputs_groupbox = QGroupBox(dcf_dialog)
dcf_dialog.outputs_groupbox.setStyleSheet('background-color: white;')
dcf_dialog.outputs_groupbox.setTitle("Model Outputs")
dcf_dialog.outputs_groupbox.setGeometry(650, 90, 630, 570)

dcf_dialog.outputs_groupbox.verdict_label = QLabel(dcf_dialog.outputs_groupbox)
dcf_dialog.outputs_groupbox.verdict_label.setGeometry(200, 10, 200, 50)

dcf_dialog.outputs_groupbox.basic_model_output = QGroupBox(dcf_dialog.outputs_groupbox)
dcf_dialog.outputs_groupbox.basic_model_output.setGeometry(10, 20, 610, 350)
dcf_dialog.outputs_groupbox.basic_model_output.setTitle("Basic Model")

future_cashflows_chart = QChart()
future_cashflows_lineseries = QLineSeries()
future_cashflows_lineseries.setName("Future Cashflows")
future_cashflows_chart.addSeries(future_cashflows_lineseries)


future_cashflows_chartview = QChartView(future_cashflows_chart)
future_cashflows_chartview.setParent(dcf_dialog.outputs_groupbox.basic_model_output)
future_cashflows_chartview.setGeometry(10, 20, 590, 200)

dcf_dialog.outputs_groupbox.basic_model_output.fair_value_label = QLabel(dcf_dialog.outputs_groupbox.basic_model_output)
dcf_dialog.outputs_groupbox.basic_model_output.fair_value_label.setText("Fair Value:")
dcf_dialog.outputs_groupbox.basic_model_output.fair_value_label.setGeometry(250, 230, 100, 50)

dcf_dialog.outputs_groupbox.basic_model_output.fair_value = QLabel(dcf_dialog.outputs_groupbox.basic_model_output)
dcf_dialog.outputs_groupbox.basic_model_output.fair_value.setGeometry(200, 280, 100, 50)

dcf_dialog.outputs_groupbox.graham_model_output = QGroupBox(dcf_dialog.outputs_groupbox)
dcf_dialog.outputs_groupbox.graham_model_output.setGeometry(10, 380, 610, 150)
dcf_dialog.outputs_groupbox.graham_model_output.setTitle("Graham Model")

dcf_dialog.outputs_groupbox.graham_model_output.ev_label = QLabel(dcf_dialog.outputs_groupbox.graham_model_output)
dcf_dialog.outputs_groupbox.graham_model_output.ev_label.setText("Expected value implied by growth rate:")
dcf_dialog.outputs_groupbox.graham_model_output.ev_label.setGeometry(10, 20, 200, 50)

dcf_dialog.outputs_groupbox.graham_model_output.ev = QLabel(dcf_dialog.outputs_groupbox.graham_model_output)
dcf_dialog.outputs_groupbox.graham_model_output.ev.setGeometry(490, 20, 100, 50)

dcf_dialog.outputs_groupbox.graham_model_output.graham_growth_estimate_label = QLabel(dcf_dialog.outputs_groupbox.graham_model_output)
dcf_dialog.outputs_groupbox.graham_model_output.graham_growth_estimate_label.setText("Growth rate implied by stock price:")
dcf_dialog.outputs_groupbox.graham_model_output.graham_growth_estimate_label.setGeometry(10, 80, 200, 50)

dcf_dialog.outputs_groupbox.graham_model_output.graham_growth_estimate = QLabel(dcf_dialog.outputs_groupbox.graham_model_output)
dcf_dialog.outputs_groupbox.graham_model_output.graham_growth_estimate.setGeometry(490, 80, 100, 50)

###################
# settings dialog #
###################

# create lists of colors for up and down candles and chart styles
up_colors = ['Green', 'Red', 'Cyan', 'Purple']
down_colors = ['Green', 'Red', 'Cyan', 'Purple']
chart_styles = ['binance','blueskies', 'brasil', 'charles', 'checkers', 'classic', 'default', 'ibd', 'kenan', 'mike', 'nightclouds', 'sas', 'starsandstripes', 'yahoo']

# ensure that the currently selected setting appears at the top of the dropdown menus
up_colors.remove(up_color[0].text.capitalize())
up_colors.insert(0, up_color[0].text.capitalize())

down_colors.remove(down_color[0].text.capitalize())
down_colors.insert(0, down_color[0].text.capitalize())

chart_styles.remove(base_style[0].text)
chart_styles.insert(0, base_style[0].text)

# label and dropdown menu to set the color of up candles 
settings_dialog = QDialog()
settings_dialog.setStyleSheet('background-color: deepskyblue;')
settings_dialog.up_color_combobox = QComboBox(settings_dialog)
settings_dialog.up_color_label = QLabel(settings_dialog)
settings_dialog.up_color_label.setText("Up Candle Color:")
settings_dialog.up_color_label.setGeometry(10, 10, 200, 40)
settings_dialog.up_color_combobox.addItems(up_colors)
settings_dialog.up_color_combobox.setGeometry(10, 50, 200, 40)

# label and dropdown menu to set the color of down candles 
settings_dialog.down_color_combobox = QComboBox(settings_dialog)
settings_dialog.down_color_label = QLabel(settings_dialog)
settings_dialog.down_color_label.setText("Down Candle Color:")
settings_dialog.down_color_label.setGeometry(220, 10, 200, 40)
settings_dialog.down_color_combobox.addItems(down_colors)
settings_dialog.down_color_combobox.setGeometry(220, 50, 200, 40)

# label and dropdown menu to set the chart style
settings_dialog.chart_style_combobox = QComboBox(settings_dialog)
settings_dialog.chart_style_label = QLabel(settings_dialog)
settings_dialog.chart_style_label.setText("Chart Style:")
settings_dialog.chart_style_label.setGeometry(430, 10, 200, 40)
settings_dialog.chart_style_combobox.addItems(chart_styles)
settings_dialog.chart_style_combobox.setGeometry(430, 50, 200, 40)

# button to apply changes
settings_dialog.apply_button = QPushButton(settings_dialog)
settings_dialog.apply_button.setText("Apply")
settings_dialog.apply_button.setGeometry(450, 500, 100, 50)
settings_dialog.apply_button.clicked.connect(lambda: applySettingsChanges())


#################
# wallet dialog #
#################

wallet_dialog = QDialog()
wallet_dialog.setStyleSheet('background-color: goldenrod')

# user's crypto wallet NAV 
wallet_dialog.currentNAV = QGroupBox(wallet_dialog)
wallet_dialog.currentNAV.setTitle("Your NAV")
wallet_dialog.currentNAV.setGeometry(10, 10, 250, 250)
wallet_dialog.currentNAV.setStyleSheet('background-color: black; color: white;')

# net liquidation value labels
wallet_dialog.currentNAV.netLiq = QLabel(wallet_dialog.currentNAV)
wallet_dialog.currentNAV.netLiq.setText("Net Liq: ")
wallet_dialog.currentNAV.netLiq.setGeometry(10, 20, 80, 20)
wallet_dialog.currentNAV.netLiq.setFont(QFont('genius', 10))
wallet_dialog.currentNAV.liq = QLabel(wallet_dialog.currentNAV)
wallet_dialog.currentNAV.liq.setText('${:0,.2f}'.format(float(str(wallet_nav))))
wallet_dialog.currentNAV.liq.setGeometry(10, 40, 160, 40)
wallet_dialog.currentNAV.liq.setFont(QFont('genius', 20))

# positions table settings
wallet_dialog.positions_view_groupbox = QGroupBox(wallet_dialog)

wallet_dialog.positions_view_groupbox.setGeometry(10, 300, 900, 250)
wallet_dialog.positions_view_groupbox.setTitle("Your Portfolio")
wallet_dialog.positions_view_groupbox.setStyleSheet('background-color: black; color: white;')
wallet_dialog.positions_view_groupbox.positions_view = QTableWidget(wallet_dialog.positions_view_groupbox)
wallet_dialog.positions_view_groupbox.positions_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
wallet_dialog.positions_view_groupbox.positions_view.setFont(QFont('arial', 10))
wallet_dialog.positions_view_groupbox.positions_view.setRowCount(len(wallet_amts) - 1)
wallet_dialog.positions_view_groupbox.positions_view.setColumnCount(8)
wallet_dialog.positions_view_groupbox.positions_view.setGeometry(10, 20, 850, 200)


wallet_dialog.positions_view_groupbox.positions_view.setStyleSheet('background-color: black;')

wallet_dialog.positions_view_groupbox.positions_view.horizontalHeader().setStyleSheet("::section{background-color: black; color: white}")
btn = wallet_dialog.positions_view_groupbox.positions_view.cornerWidget()
wallet_dialog.positions_view_groupbox.positions_view.setHorizontalHeaderItem(0, QTableWidgetItem("Ticker"))
wallet_dialog.positions_view_groupbox.positions_view.setHorizontalHeaderItem(1, QTableWidgetItem("Today's Performance"))
wallet_dialog.positions_view_groupbox.positions_view.setHorizontalHeaderItem(2, QTableWidgetItem("Current Price"))
wallet_dialog.positions_view_groupbox.positions_view.setHorizontalHeaderItem(3, QTableWidgetItem("Gain/Loss Per Share"))
wallet_dialog.positions_view_groupbox.positions_view.setHorizontalHeaderItem(4, QTableWidgetItem("Purchase Price"))
wallet_dialog.positions_view_groupbox.positions_view.setHorizontalHeaderItem(5, QTableWidgetItem("# of Shares"))
wallet_dialog.positions_view_groupbox.positions_view.setHorizontalHeaderItem(6, QTableWidgetItem("Total Value"))
wallet_dialog.positions_view_groupbox.positions_view.setHorizontalHeaderItem(7, QTableWidgetItem("Position Gain/Loss"))


for i in range (8):
    wallet_dialog.positions_view_groupbox.positions_view.horizontalHeaderItem(i).setFont(QFont('arial', 10))
    

for i in range (portfolio_dialog.positions_view_groupbox.positions_view.rowCount()):
    wallet_dialog.positions_view_groupbox.positions_view.setVerticalHeaderItem(0, QTableWidgetItem("1"))
    wallet_dialog.positions_view_groupbox.positions_view.verticalHeaderItem(i).setFont(QFont('arial', 10))
    
update_wallet_table()

# cash labels
wallet_dialog.currentNAV.cashLabel = QLabel(wallet_dialog.currentNAV)
wallet_dialog.currentNAV.cashLabel.setText("Cash: ")
wallet_dialog.currentNAV.cashLabel.setGeometry(10, 90, 80, 20)
wallet_dialog.currentNAV.cash = QLabel(wallet_dialog.currentNAV)
wallet_dialog.currentNAV.cash.setText('${:0,.2f}'.format(wallet_cash))
wallet_dialog.currentNAV.cash.setGeometry(100, 90, 80, 20)

# buying power labels
wallet_dialog.currentNAV.buyingPowerLabel = QLabel(wallet_dialog.currentNAV)
wallet_dialog.currentNAV.buyingPowerLabel.setText("Buying Power: ")
wallet_dialog.currentNAV.buyingPowerLabel.setGeometry(10, 110, 80, 20)
wallet_dialog.currentNAV.buyingPower = QLabel(wallet_dialog.currentNAV)
wallet_dialog.currentNAV.buyingPower.setText('${:0,.2f}'.format(get_wallet_bp()))
wallet_dialog.currentNAV.buyingPower.setGeometry(100, 110, 80, 20)

# assets labels
wallet_dialog.currentNAV.assetsLabel = QLabel(wallet_dialog.currentNAV)
wallet_dialog.currentNAV.assetsLabel.setText("Long Assets: ")
wallet_dialog.currentNAV.assetsLabel.setGeometry(10, 130, 80, 20)
wallet_dialog.currentNAV.assets = QLabel(wallet_dialog.currentNAV)
total_long = 0
for i in range (1, len(wallet_amts)):
    price = atof(wallet_dialog.positions_view_groupbox.positions_view.item(i - 1, 2).text()[1:])
    if float(wallet_amts[i].text) > 0:
        total_long += float(price) * float(wallet_amts[i].text)

wallet_dialog.currentNAV.assets.setText('${:0,.2f}'.format(total_long))
wallet_dialog.currentNAV.assets.setGeometry(100, 130, 80, 20)

# liabilities labels
wallet_dialog.currentNAV.liabilitiesLabel = QLabel(wallet_dialog.currentNAV)
wallet_dialog.currentNAV.liabilitiesLabel.setText("Short Assets: ")
wallet_dialog.currentNAV.liabilitiesLabel.setGeometry(10, 150, 80, 20)
wallet_dialog.currentNAV.liabilities = QLabel(wallet_dialog.currentNAV)
total_short = 0
for i in range (1, len(wallet_amts)):
    price = atof(wallet_dialog.positions_view_groupbox.positions_view.item(i - 1, 2).text()[1:])
    if float(wallet_amts[i].text) < 0:
        total_short -= float(price) * float(wallet_amts[i].text)

wallet_dialog.currentNAV.liabilities.setText('${:0,.2f}'.format(total_short))
wallet_dialog.currentNAV.liabilities.setGeometry(100, 150, 80, 20)

# return since inception labels
wallet_dialog.currentNAV.returnSinceInceptionLabel = QLabel(wallet_dialog.currentNAV)
wallet_dialog.currentNAV.returnSinceInceptionLabel.setText("Return Since Inception: ")
wallet_dialog.currentNAV.returnSinceInceptionLabel.setGeometry(10, 170, 120, 20)
wallet_dialog.currentNAV.returnSinceInception = QLabel(wallet_dialog.currentNAV)
wallet_dialog.currentNAV.returnSinceInception.setFont(QFont('genius', 20))
wallet_dialog.currentNAV.returnSinceInception.setText('{:0.2f}'.format((wallet_nav / 10000 - 1) * 100) + "%")
wallet_dialog.currentNAV.returnSinceInception.setGeometry(10, 190, 120, 30)

wallet_dialog.positions_view_groupbox.positions_view.resizeColumnsToContents()


######################
# end of dialog init #
######################

# adding tabs to main window
widget.addTab(portfolio_dialog, "Your Portfolio")
widget.addTab(chart_dialog, "Chart Stocks")
widget.addTab(trade_dialog, "Trade Stocks")
widget.addTab(stockinfo_dialog, "Get Stock Info")
widget.addTab(dcf_dialog, "DCF Modelling")
widget.addTab(wallet_dialog, "Your Crypto Wallet")
widget.addTab(settings_dialog, "Settings")


widget.resize(1300, 700)
widget.show()

splash.close()

# instantiate thread which runs the updateNav function in an infinite loop

t2 = Thread(target=update_ui, daemon=True)
t2.start()

sys.exit(app.exec())