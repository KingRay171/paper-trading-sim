# Started by Ray Ikome on 11/16/22

from PySide6.QtCharts import QChart, QChartView, QPieSlice, QPieSeries
from PySide6.QtWidgets import (QWidget, QTabWidget, QGroupBox, QLabel, QTableWidget, QTableWidgetItem, QAbstractItemView,
                                QSplashScreen, QPushButton, QDialog, QLineEdit, QComboBox, QRadioButton, QCalendarWidget, QCheckBox
                                , QApplication, QProgressBar, QVBoxLayout, QHeaderView, QTableView, QAbstractButton )
from PySide6.QtGui import QFont, QFontDatabase, QPixmap, QIcon 
from PySide6.QtCore import QRect, QCoreApplication, QStringListModel, QAbstractItemModel
from locale import atof, setlocale, LC_NUMERIC
import yfinance as yf
import sys
import mplfinance as mpf
from threading import Thread, Event
import time
from bs4 import BeautifulSoup
import xml.etree.ElementTree as et
import pandas as pd
import autocomplete as ac
from enum import Enum



download_is_used = Event()
download_is_used.clear()

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
    if the user is on the portfolio dialog. Runs as 
    long as the program is running
    """
    while True:
        if widget.currentWidget() == portfolio_dialog:
            update_portfolio_table()
            update_watchlist_tickers()
            update_portfolio_nav()
            update_piechart()
        elif widget.currentWidget() == wallet_dialog:
            update_wallet_table()
            time.sleep(5)
        
        
def update_piechart():
    """
    Updates the asset class piechart on the portfolio dialog
    """
    cash_amount = 0
    etf_amount = 0
    stock_amount = 0
    option_amount = 0
    futures_amount = 0

    for i in range(len(portfolio_amts)):
        if(portfolio_asset_types[i].text == "ETF"):
            etf_amount += int(portfolio_amts[i].text) * float(portfolio_dialog.positions_view_groupbox.positions_view.item(i - 1, 2).text()[1:])
        elif(portfolio_asset_types[i].text == "Liquidity"):
            cash_amount += float(portfolio_amts[i].text)
        elif(portfolio_asset_types[i].text == "Stock"):
            stock_amount += int(portfolio_amts[i].text) * float(portfolio_dialog.positions_view_groupbox.positions_view.item(i - 1, 2).text()[1:])
        elif(portfolio_asset_types[i].text == "Futures"):
            futures_amount += int(portfolio_amts[i].text) * float(portfolio_dialog.positions_view_groupbox.positions_view.item(i - 1, 2).text()[1:])
        elif(portfolio_asset_types[i].text == "Option"):
            option_amount += int(portfolio_amts[i].text) * float(portfolio_dialog.positions_view_groupbox.positions_view.item(i - 1, 2).text()[1:])

    asset_class_chart.slices()[0].setValue(round(etf_amount / portfolio_nav * 100, 2))
    if(etf_amount != 0):
        asset_class_chart.slices()[0].setLabel(f"ETFs: {round(etf_amount / portfolio_nav * 100, 2)}%")
        asset_class_chart.slices()[0].setLabelVisible(True)
    
    asset_class_chart.slices()[1].setValue(round(stock_amount / portfolio_nav * 100, 2))
    if(stock_amount != 0):
        asset_class_chart.slices()[1].setLabel(f"Stocks: {round(stock_amount / portfolio_nav * 100, 2)}%")

    asset_class_chart.slices()[2].setValue(option_amount / portfolio_nav * 100)
    if(option_amount != 0):
        asset_class_chart.slices()[2].setLabel(f"Options: {round(option_amount / portfolio_nav * 100, 2)}%")

    asset_class_chart.slices()[3].setValue(futures_amount / portfolio_nav * 100)
    if(futures_amount != 0):
        asset_class_chart.slices()[3].setLabel(f"Futures: {round(futures_amount / portfolio_nav * 100, 2)}%")

    asset_class_chart.slices()[4].setValue(cash_amount / portfolio_nav * 100)
    if(cash_amount != 0):
        asset_class_chart.slices()[4].setLabel(f"Cash: {round(cash_amount / portfolio_nav * 100, 2)}%")
        asset_class_chart.slices()[4].setLabelVisible(True)
    

def update_wallet_table():
    for i in range(1, len(wallet_tickers)):

            # get the current price and the price it last closed at
            ticker = yf.download(tickers=wallet_tickers[i].text, period='5d')
            ticker_current = ticker.iloc[4][3]
            ticker_last_close = ticker.iloc[3][3]

            # calculate the return since the position was opened in dollar and percent terms
            total_return = (ticker_current - float(wallet_costbases[i - 1].text)) * float(wallet_amts[i].text)
            percent_change = round(total_return / (float(wallet_costbases[i - 1].text) * float(wallet_amts[i].text)) * 100, 2)
            # update the table with the new information
            wallet_dialog.positions_view_groupbox.positions_view.setItem(i - 1, 0, QTableWidgetItem(wallet_tickers[i].text.upper()))
            wallet_dialog.positions_view_groupbox.positions_view.setItem(i - 1, 1, updateTickerIcon(ticker))
            wallet_dialog.positions_view_groupbox.positions_view.setItem(i - 1, 2, QTableWidgetItem('${:0,.2f}'.format(ticker_current)))
            wallet_dialog.positions_view_groupbox.positions_view.setItem(i - 1, 3, QTableWidgetItem('${:0,.2f}'.format(ticker_current - ticker_last_close) + " (" + str(round(((ticker_current - ticker_last_close) / ticker_last_close * 100), 2)) + "%)"))
            wallet_dialog.positions_view_groupbox.positions_view.setItem(i - 1, 4, QTableWidgetItem('${:0,.2f}'.format(float(wallet_costbases[i - 1].text))))
            wallet_dialog.positions_view_groupbox.positions_view.setItem(i - 1, 5, QTableWidgetItem(portfolio_amts[i].text))
            wallet_dialog.positions_view_groupbox.positions_view.setItem(i - 1, 6, QTableWidgetItem('${:0,.2f}'.format(ticker_current * float(wallet_amts[i].text))))
            wallet_dialog.positions_view_groupbox.positions_view.setItem(i - 1, 7, QTableWidgetItem('${:0,.2f}'.format(((ticker_current - float(wallet_costbases[i - 1].text)) * float(wallet_amts[i].text)))))
            wallet_dialog.positions_view_groupbox.positions_view.setItem(i - 1, 7, QTableWidgetItem('${:0,.2f}'.format(total_return) + " (" + str(percent_change) + "%)"))
        
    
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
    for i in range(len(watchlist_tickers)):
        
        
        ticker = yf.download(tickers=watchlist_tickers[i].text, period='5d')
        ticker_current = ticker.iloc[4][3]
        ticker_last_close = ticker.iloc[3][3]

        portfolio_dialog.watchlist_groupbox.watchlist_view.setItem(i, 0, QTableWidgetItem(watchlist_tickers[i].text.upper()))
        portfolio_dialog.watchlist_groupbox.watchlist_view.setItem(i, 1, updateTickerIcon(ticker))
        portfolio_dialog.watchlist_groupbox.watchlist_view.setItem(i, 2, QTableWidgetItem('${:0,.2f}'.format(ticker_current)))
        
        portfolio_dialog.watchlist_groupbox.watchlist_view.setItem(i, 3, QTableWidgetItem('${:0,.2f}'.format(ticker_current - ticker_last_close) + " (" + str(round(((ticker_current - ticker_last_close) / ticker_last_close * 100), 2)) + "%)"))


def daterange_radiobutton_clicked():
    chart_dialog.settings_groupbox.start_date.setEnabled(True)
    chart_dialog.settings_groupbox.end_date.setEnabled(True)
    chart_dialog.settings_groupbox.data_period_combobox.setEnabled(False)


def period_radiobutton_clicked():
    chart_dialog.settings_groupbox.start_date.setEnabled(False)
    chart_dialog.settings_groupbox.end_date.setEnabled(False)
    chart_dialog.settings_groupbox.data_period_combobox.setEnabled(True)


def searchTextChanged(txt: str):
    """
    Executed when text is typed into the search bar on the "Chart Stocks" tab.
    The function takes the entered text and appends it to the search bar
    """
    chart_dialog.search_bar_groupbox.searchBar.setText(txt.upper())


def searchButtonClicked():
    """
    Shows graph for the selected ticker when the search button is pressed.
    """
    # gets the stock ticker from the search bar
    ticker = ''
    i = 0
    while chart_dialog.search_bar_groupbox.searchBar.text()[i] != ' ':
        ticker += chart_dialog.search_bar_groupbox.searchBar.text()[i]
        i += 1

    period = chart_dialog.settings_groupbox.data_period_combobox.currentText()
    interval = chart_dialog.settings_groupbox.data_timeframe_combobox.currentText()

    include_prepost = False
    if(chart_dialog.settings_groupbox.prepost_checkbox.isChecked()):
        include_prepost = True

    adjust_ohlc = False
    if(chart_dialog.settings_groupbox.adjust_ohlc_checkbox.isChecked()):
        adjust_ohlc = True
    # shows the requested ticker's chart
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

        show_graph(yf.download(tickers=ticker,
                              period=period,
                              interval=interval,
                              prepost=include_prepost,
                              auto_adjust=adjust_ohlc,
                              actions=split_dividend
                              ), ticker, include_volume, non_trading)
                              

def updateTickerIcon(ticker) -> QTableWidgetItem:
    """Updates the performance icon for the given stock"""
    # initializes new table widget item and gets the ticker's open, last close, and current prices
    w = QTableWidgetItem()
    ticker_open = ticker.iloc[4][0]
    ticker_current = ticker.iloc[4][3]
    ticker_last_close = ticker.iloc[3][3]

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

    if open_pos == "UP":
        if close_pos == "UP":
            w.setIcon(QIcon('greenarrowgreenbox.png'))
        elif close_pos == "FLAT":
            w.setIcon(QIcon('greenarrowflatbox.png'))
        elif close_pos == "DOWN":
            w.setIcon(QIcon('greenarrowredbox.png'))
    elif open_pos == "FLAT":
        if close_pos == "UP":
            w.setIcon(QIcon('flatarrowgreenbox.png'))
        elif close_pos == "FLAT":
            w.setIcon(QIcon('flatarrowflatbox.png'))
        elif close_pos == "DOWN":
            w.setIcon(QIcon('flatarrowredbox.png'))
    elif open_pos == "DOWN":
        if close_pos == "UP":
            w.setIcon(QIcon('redarrowgreenbox.png'))
        elif close_pos == "FLAT":
            w.setIcon(QIcon('redarrowflatbox.png'))
        elif close_pos == "DOWN":
            w.setIcon(QIcon('redarrowredbox.png'))
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
    # retrieves user's chart style preferences from settings.xml
    up_color = getXMLData('settings.xml', 'upcolor')
    down_color = getXMLData('settings.xml', 'downcolor')
    base_style = getXMLData('settings.xml', 'basestyle')

    # creates a chart style based on the user's settings
    mc = mpf.make_marketcolors(up=up_color[0].text.lower(), down=down_color[0].text.lower(),inherit=True)
    s  = mpf.make_mpf_style(base_mpf_style=base_style[0].text,marketcolors=mc)
    # plots chart

    mpf.plot(ticker, 
             show_nontrading = non_trading,
             type='candle', 
             style = s, 
             title = title, 
             volume = volume, 
             tight_layout = True
             )


def retranslateChartDialogUi(self):
    """required retranslation function for chart dialog"""
    _translate = QCoreApplication.translate
    self.setWindowTitle(_translate("Dialog", "Dialog"))
    self.broad_market_groupbox.spyButton.setText(_translate("Dialog", "Chart SPY"))
    self.broad_market_groupbox.qqqButton.setText(_translate("Dialog", "Chart QQQ"))
    self.broad_market_groupbox.diaButton.setText(_translate("Dialog", "Chart DIA"))
    self.broad_market_groupbox.vixButton.setText(_translate("Dialog", "Chart VIX"))


def retranslatePortfolioDialogUi(self):
    """required retranslation function for portfolio dialog"""
    _translate = QCoreApplication.translate
    self.setWindowTitle(_translate("Dialog", "Dialog"))
        

def update_portfolio_nav():
    """Updates the user's NAV tab. Calculated as cash + (.5 * value of all long positions) - 
    (1.5 * value of all short positions)."""
    
    # sets buying power to user's cash
    newVal = float(portfolio_amts[0].text)
    liabilities = 0
    assets = 0
    for i in range(1, len(portfolio_tickers)):
        price = float(portfolio_dialog.positions_view_groupbox.positions_view.item(i - 1, 2).text()[1:])
        if int(portfolio_amts[i].text) > 0:
            newVal += float(price) * int(portfolio_amts[i].text)
            assets += float(price) * float(portfolio_amts[i].text)
        elif int(portfolio_amts[i].text) < 0:
            newVal -= float(price) * int(portfolio_amts[i].text)
            liabilites += float(price) * float(portfolio_amts[i].text)

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
    for i in range(1, len(wallet_tickers)):
        price = float(wallet_dialog.positions_view_groupbox.positions_view.item(i - 1, 2).text()[1:])
        if float(wallet_amts[i].text) > 0:
            newVal += float(price) * float(wallet_amts[i].text)
            assets += float(price) * float(wallet_amts[i].text)
        elif float(wallet_amts[i].text) < 0:
            newVal -= float(price) * float(wallet_amts[i].text)
            liabilites += float(price) * float(wallet_amts[i].text)

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
    return BeautifulSoup(open(file, 'r').read(), "xml").find_all(keyword)


def applySettingsChanges():
    """Updates settings.xml with the currently selected settings in the GUI"""
    # gets currently selected settings
    up = settings_dialog.up_color_combobox.currentText()
    down = settings_dialog.down_color_combobox.currentText()
    style = settings_dialog.chart_style_combobox.currentText()

    # parses XML file into an ElementTree
    tree = et.parse('settings.xml')

    # replaces old data in the file with the current data
    for upcolor in tree.getroot().iter('upcolor'):
        upcolor.text = up

    for downcolor in tree.getroot().iter('downcolor'):
        downcolor.text = down

    for basestyle in tree.getroot().iter('basestyle'):
        basestyle.text = style

    tree.write('settings.xml')


def stockinfo_searchbar_click(dialog: QDialog):
    ticker = ''
    i = 0
    while stockinfo_dialog.search_bar_groupbox.searchBar.text()[i] != ' ':
        ticker += stockinfo_dialog.search_bar_groupbox.searchBar.text()[i]
        i += 1
    
    ticker_info = yf.Ticker(ticker).info
    if(ticker_info['quoteType'] == 'ETF'):
        setup_etf_info(ticker_info)


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


def setup_etf_info(ticker_info: dict):
    stockinfo_dialog.about_groupbox.setVisible(True)
    stockinfo_dialog.asset_info_groupbox.setVisible(True)
    stockinfo_dialog.weights_holdings_groupbox.setVisible(True)

    etf_weights = get_etf_weights(ticker_info)


    full_name_label = QLabel(f"Full Name: {ticker_info['longName']}", stockinfo_dialog.about_groupbox)
    
    category_label = QLabel(f"Category: {ticker_info['category']}", stockinfo_dialog.about_groupbox)

    exchange_label = QLabel(f"Exchange: {ticker_info['exchange']}", stockinfo_dialog.about_groupbox)
    
    market_label = QLabel(f"Market: {ticker_info['market']}", stockinfo_dialog.about_groupbox)

    total_assets_label = QLabel(f"Total Assets: {ticker_info['totalAssets']}")

    description_label = QLabel(f"Description: " + ticker_info['longBusinessSummary'], stockinfo_dialog.about_groupbox)
    description_label.adjustSize()
    description_label.setWordWrap(True)

    date_inception = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ticker_info['fundInceptionDate']))
    inception_label = QLabel(f"Date of Inception: " + date_inception, stockinfo_dialog.about_groupbox)

    weights_piechart = QPieSeries()
    
    for i in range(len(etf_weights)):
        weights_piechart.append(etf_weights[i][0], i + 1)
        weights_piechart.slices()[i].setValue(etf_weights[i][1] * 100)
        weights_piechart.slices()[i].setLabelVisible(True)

    weights_chart = QChart()
    weights_chart.addSeries(weights_piechart)
    weights_chart.setTitle(f"{ticker_info['symbol']} Holdings by Sector")
    weights_chart.setVisible(True)

    current_price_label = QLabel(f"Current Price: {ticker_info['regularMarketPrice']}", stockinfo_dialog.asset_info_groupbox)
    open_price_label = QLabel(f"\tOpen: {ticker_info['open']}", stockinfo_dialog.asset_info_groupbox)
    high_price_label = QLabel(f"\tHigh: {ticker_info['dayHigh']}", stockinfo_dialog.asset_info_groupbox)
    low_price_label = QLabel(f"\tLow: {ticker_info['dayLow']}", stockinfo_dialog.asset_info_groupbox)
    close_price_label = QLabel(f"\tLast Close: {ticker_info['previousClose']}", stockinfo_dialog.asset_info_groupbox)
    nav_price_label = QLabel(f"NAV Price: {ticker_info['navPrice']}", stockinfo_dialog.asset_info_groupbox)
    
    bid_label = QLabel(f"Bid: {ticker_info['bid']} ({ticker_info['bidSize']})", stockinfo_dialog.asset_info_groupbox)
    ask_label = QLabel(f"Ask: {ticker_info['ask']} ({ticker_info['askSize']})", stockinfo_dialog.asset_info_groupbox)

    volume_label = QLabel(f"Volume: {ticker_info['volume']}", stockinfo_dialog.asset_info_groupbox)
    avg_volume_label = QLabel(f"Average Volume (10d): {ticker_info['averageVolume10days']}", stockinfo_dialog.asset_info_groupbox)
    long_avg_volume_label = QLabel(f"Average Volume (1y): {ticker_info['averageVolume']} ", stockinfo_dialog.asset_info_groupbox)


    year_high_label = QLabel(f"52 Week High: {ticker_info['fiftyTwoWeekHigh']}", stockinfo_dialog.asset_info_groupbox)
    year_low_label = QLabel(f"52 Week Low: {ticker_info['fiftyTwoWeekLow']}", stockinfo_dialog.asset_info_groupbox)

    averages_label = QLabel("Price Averages: ", stockinfo_dialog.asset_info_groupbox)
    fifty_avg_label = QLabel(f"\t50d MA: {ticker_info['fiftyDayAverage']}", stockinfo_dialog.asset_info_groupbox)
    twohundred_avg_label = QLabel(f"\t200d MA: {ticker_info['twoHundredDayAverage']}", stockinfo_dialog.asset_info_groupbox)

    threeyear_return_label = QLabel(f"Three-Year CAGR: {ticker_info['threeYearAverageReturn'] * 100}% per annum", stockinfo_dialog.asset_info_groupbox)
    fiveyear_return_label = QLabel(f"Five-Year CAGR: {ticker_info['fiveYearAverageReturn'] * 100}% per annum", stockinfo_dialog.asset_info_groupbox)
    dividend_label = QLabel(f"Trailing Annual Dividend Yield: {ticker_info['trailingAnnualDividendYield'] * 100}% per annum", stockinfo_dialog.asset_info_groupbox)
    dividend_rate_label = QLabel(f"Trailing Annual Dividend Rate: ${ticker_info['trailingAnnualDividendRate']}", stockinfo_dialog.asset_info_groupbox)
    current_div_label = QLabel(f"Current Dividend Yield: {ticker_info['yield']}", stockinfo_dialog.asset_info_groupbox)

    beta_3y_label = QLabel(f"3-Year Beta (Relative to SPY): {ticker_info['beta3Year']}", stockinfo_dialog.asset_info_groupbox)

    stockinfo_dialog.about_groupbox.layout().addWidget(full_name_label)
    stockinfo_dialog.about_groupbox.layout().addWidget(category_label)
    stockinfo_dialog.about_groupbox.layout().addWidget(exchange_label)
    stockinfo_dialog.about_groupbox.layout().addWidget(market_label)
    stockinfo_dialog.about_groupbox.layout().addWidget(total_assets_label)
    stockinfo_dialog.about_groupbox.layout().addWidget(inception_label)
    stockinfo_dialog.about_groupbox.layout().addWidget(description_label)
    stockinfo_dialog.about_groupbox.layout().addWidget(QChartView(weights_chart))

    stockinfo_dialog.asset_info_groupbox.layout().addWidget(current_price_label)
    stockinfo_dialog.asset_info_groupbox.layout().addWidget(open_price_label)
    stockinfo_dialog.asset_info_groupbox.layout().addWidget(high_price_label)
    stockinfo_dialog.asset_info_groupbox.layout().addWidget(low_price_label)
    stockinfo_dialog.asset_info_groupbox.layout().addWidget(close_price_label)
    stockinfo_dialog.asset_info_groupbox.layout().addWidget(nav_price_label)
    stockinfo_dialog.asset_info_groupbox.layout().addWidget(bid_label)
    stockinfo_dialog.asset_info_groupbox.layout().addWidget(ask_label)
    stockinfo_dialog.asset_info_groupbox.layout().addWidget(volume_label)
    stockinfo_dialog.asset_info_groupbox.layout().addWidget(avg_volume_label)
    stockinfo_dialog.asset_info_groupbox.layout().addWidget(long_avg_volume_label)
    stockinfo_dialog.asset_info_groupbox.layout().addWidget(year_high_label)
    stockinfo_dialog.asset_info_groupbox.layout().addWidget(year_low_label)
    stockinfo_dialog.asset_info_groupbox.layout().addWidget(averages_label)
    stockinfo_dialog.asset_info_groupbox.layout().addWidget(fifty_avg_label)
    stockinfo_dialog.asset_info_groupbox.layout().addWidget(twohundred_avg_label)
    stockinfo_dialog.asset_info_groupbox.layout().addWidget(threeyear_return_label)
    stockinfo_dialog.asset_info_groupbox.layout().addWidget(fiveyear_return_label)
    stockinfo_dialog.asset_info_groupbox.layout().addWidget(dividend_label)
    stockinfo_dialog.asset_info_groupbox.layout().addWidget(dividend_rate_label)
    stockinfo_dialog.asset_info_groupbox.layout().addWidget(current_div_label)
    stockinfo_dialog.asset_info_groupbox.layout().addWidget(beta_3y_label)
    
    
def close_event(event):
    """Function that is called when the user exits the game. WIP"""
    print("closed")


app = QApplication(sys.argv)
widget = QTabWidget()
widget.setWindowTitle("Ray's Paper Trading Game")

splash = QSplashScreen(QPixmap('splash.png'))
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

up_color = getXMLData('settings.xml', 'upcolor')
down_color = getXMLData('settings.xml', 'downcolor')
base_style = getXMLData('settings.xml', 'basestyle')

portfolio_tickers = getXMLData('portfolio.xml', 'name')
portfolio_asset_types = getXMLData('portfolio.xml', 'type')
portfolio_amts = getXMLData('portfolio.xml', 'amount')
purchase_prices = getXMLData('portfolio.xml', 'costbasis')

wallet_tickers = getXMLData('wallet.xml', 'name')
wallet_amts = getXMLData('wallet.xml', 'amount')
wallet_costbases = getXMLData('wallet.xml', 'costbasis')

watchlist_tickers = getXMLData('watchlist.xml', 'name')


all_tickers_list = pd.read_csv("stock_list.csv")['Symbol'].tolist()
all_names_list = pd.read_csv("stock_list.csv")['Name'].tolist()
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
    price = yf.download(tickers=wallet_tickers[i].text, period='5d').iloc[4][3]
    wallet_nav += float(price) * float(wallet_amts[i].text)



# add genius font to database
QFontDatabase.addApplicationFont('genius.ttf')

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
cash_amount = 0
etf_amount = 0
stock_amount = 0
option_amount = 0
futures_amount = 0

for i in range(len(portfolio_amts)):
    if(portfolio_asset_types[i].text == "ETF"):
        etf_amount += int(portfolio_amts[i].text) * float(portfolio_dialog.positions_view_groupbox.positions_view.item(i - 1, 2).text()[1:])
    elif(portfolio_asset_types[i].text == "Liquidity"):
        cash_amount += float(portfolio_amts[i].text)
    elif(portfolio_asset_types[i].text == "Stock"):
        stock_amount += int(portfolio_amts[i].text) * float(portfolio_dialog.positions_view_groupbox.positions_view.item(i - 1, 2).text()[1:])
    elif(portfolio_asset_types[i].text == "Futures"):
        futures_amount += int(portfolio_amts[i].text) * float(portfolio_dialog.positions_view_groupbox.positions_view.item(i - 1, 2).text()[1:])
    elif(portfolio_asset_types[i].text == "Option"):
        option_amount += int(portfolio_amts[i].text) * float(portfolio_dialog.positions_view_groupbox.positions_view.item(i - 1, 2).text()[1:])
        
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


etf_slice = asset_class_chart.slices()[0]
etf_slice.setValue(etf_amount / portfolio_nav * 100)
if(etf_amount != 0):
    asset_class_chart.slices()[0].setLabel(f"ETFs: {etf_amount * 100}%")

stock_slice = asset_class_chart.slices()[1]
stock_slice.setValue(stock_amount / portfolio_nav * 100)
if(stock_amount != 0):
    asset_class_chart.slices()[1].setLabel(f"Stocks: {stock_amount * 100}%")

options_slice = asset_class_chart.slices()[2]
options_slice.setValue(option_amount / portfolio_nav * 100)
if(option_amount != 0):
    asset_class_chart.slices()[2].setLabel(f"Options: {option_amount * 100}%")

futures_slice = asset_class_chart.slices()[3]
futures_slice.setValue(futures_amount / portfolio_nav * 100)
if(futures_amount != 0):
    asset_class_chart.slices()[3].setLabel(f"Futures: {etf_amount * 100}%")

cash_slice = asset_class_chart.slices()[4]
cash_slice.setValue(cash_amount / portfolio_nav * 100)
if(cash_amount != 0):
    asset_class_chart.slices()[4].setLabel(f"Cash: {cash_amount * 100}%")

portfolio_dialog.chart_view = QChartView(chart)
portfolio_dialog.chart_view.setParent(portfolio_dialog)
portfolio_dialog.chart_view.setGeometry(800, 5, 400, 250)
portfolio_dialog.chart_view.setVisible(True)

retranslatePortfolioDialogUi(portfolio_dialog)

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

chart_dialog.broad_market_groupbox.spyButton = QPushButton(chart_dialog.broad_market_groupbox)
chart_dialog.broad_market_groupbox.spyButton.setGeometry(QRect(10, 20, 150, 20))
chart_dialog.broad_market_groupbox.spyButton.setObjectName("spyButton")
chart_dialog.broad_market_groupbox.spyButton.clicked.connect(spy_button_clicked)

chart_dialog.broad_market_groupbox.qqqButton = QPushButton(chart_dialog.broad_market_groupbox)
chart_dialog.broad_market_groupbox.qqqButton.setGeometry(QRect(170, 20, 150, 20))
chart_dialog.broad_market_groupbox.qqqButton.setObjectName("qqqButton")
chart_dialog.broad_market_groupbox.qqqButton.clicked.connect(qqq_button_clicked)

chart_dialog.broad_market_groupbox.diaButton = QPushButton(chart_dialog.broad_market_groupbox)
chart_dialog.broad_market_groupbox.diaButton.setGeometry(QRect(330, 20, 150, 20))
chart_dialog.broad_market_groupbox.diaButton.setObjectName("diaButton")
chart_dialog.broad_market_groupbox.diaButton.clicked.connect(dia_button_clicked)

chart_dialog.broad_market_groupbox.vixButton = QPushButton(chart_dialog.broad_market_groupbox)
chart_dialog.broad_market_groupbox.vixButton.setGeometry(QRect(490, 20, 150, 20))
chart_dialog.broad_market_groupbox.vixButton.setObjectName("vixButton")
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


retranslateChartDialogUi(chart_dialog)

################
# trade dialog #
################

trade_dialog = QDialog()
trade_dialog.setStyleSheet('background-color: deepskyblue;')


#####################
# stock info dialog #
#####################

stockinfo_dialog = QDialog()
stockinfo_dialog.setStyleSheet('background-color: deepskyblue;')

stockinfo_dialog.search_bar_groupbox = QGroupBox(stockinfo_dialog)
stockinfo_dialog.search_bar_groupbox.setStyleSheet('background-color: white;')
stockinfo_dialog.search_bar_groupbox.setTitle("Find a Stock")
stockinfo_dialog.search_bar_groupbox.setGeometry(10, 10, 960, 70)

stockinfo_dialog.search_bar_groupbox.searchBar = QLineEdit(stockinfo_dialog.search_bar_groupbox)
stockinfo_dialog.search_bar_groupbox.searchBar.setGeometry(10, 20, 850, 40)
stockinfo_dialog.search_bar_groupbox.searchBar.textChanged.connect(lambda txt: searchTextChanged(txt))
stockinfo_dialog.search_bar_groupbox.searchBar.setFont(QFont('arial', 10))
stockinfo_dialog.search_bar_groupbox.searchBar.setCompleter(completer)

stockinfo_dialog.search_bar_groupbox.search_button = QPushButton(stockinfo_dialog.search_bar_groupbox)
stockinfo_dialog.search_bar_groupbox.search_button.setGeometry(870, 20, 80, 40)
stockinfo_dialog.search_bar_groupbox.search_button.setText("Show Info")
stockinfo_dialog.search_bar_groupbox.search_button.clicked.connect(lambda: stockinfo_searchbar_click(stockinfo_dialog))

stockinfo_dialog.asset_info_groupbox = QGroupBox(stockinfo_dialog)
stockinfo_dialog.asset_info_groupbox.setStyleSheet('background-color: white')
stockinfo_dialog.asset_info_groupbox.setTitle("Asset Profile")
stockinfo_dialog.asset_info_groupbox.setGeometry(10, 90, 400, 550)
stockinfo_dialog.asset_info_groupbox.setVisible(False)
stockinfo_dialog.asset_info_groupbox.setLayout(QVBoxLayout())

stockinfo_dialog.about_groupbox = QGroupBox(stockinfo_dialog)
stockinfo_dialog.about_groupbox.setStyleSheet('background-color: white')
stockinfo_dialog.about_groupbox.setTitle("About the Asset")
stockinfo_dialog.about_groupbox.setGeometry(420, 90, 400, 550)
stockinfo_dialog.about_groupbox.setVisible(False)
stockinfo_dialog.about_groupbox.setLayout(QVBoxLayout())

stockinfo_dialog.weights_holdings_groupbox = QGroupBox(stockinfo_dialog)
stockinfo_dialog.weights_holdings_groupbox.setStyleSheet('background-color: white')
stockinfo_dialog.weights_holdings_groupbox.setTitle("ETF Weights and Holdings")
stockinfo_dialog.weights_holdings_groupbox.setGeometry(830, 90, 400, 550)
stockinfo_dialog.weights_holdings_groupbox.setVisible(False)
stockinfo_dialog.weights_holdings_groupbox.setLayout(QVBoxLayout())


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
widget.addTab(wallet_dialog, "Your Crypto Wallet")
widget.addTab(settings_dialog, "Settings")


widget.resize(1300, 700)
widget.show()

splash.close()

# instantiate thread which runs the updateNav function in an infinite loop

t2 = Thread(target=update_ui, daemon=True)
t2.start()

sys.exit(app.exec())

