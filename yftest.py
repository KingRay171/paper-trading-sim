# Started by Ray Ikome on 11/16/22

from PyQt6.QtWidgets import (QGroupBox, QApplication, QLabel, QProgressBar,
                             QTableWidget, QTableWidgetItem, QTabWidget,
                             QSplashScreen, QPushButton, QDialog, QLineEdit,
                             QComboBox, QButtonGroup, QRadioButton)
from PyQt6.QtGui import QFontDatabase, QFont, QPixmap, QIcon
from PyQt6.QtCore import QRect, QCoreApplication, QStringListModel
from PyQt6 import QtCore 
import yfinance as yf
import sys
import mplfinance as mpf
from threading import Thread
import time
from bs4 import BeautifulSoup
import xml.etree.ElementTree as et
import pandas as pd
import autocomplete as ac
from enum import Enum

def searchTextChanged(txt):
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
    if(chart_dialog.settings_groupbox.prepost_radiobutton.isChecked()):
        include_prepost = True

    adjust_ohlc = False
    if(chart_dialog.settings_groupbox.adjust_ohlc_radiobutton.isChecked()):
        adjust_ohlc = True
    # shows the requested ticker's chart
    split_dividend = False
    if(chart_dialog.settings_groupbox.split_dividend_radiobutton.isChecked()):
        split_dividend = True
    
    include_volume = False
    if(chart_dialog.settings_groupbox.volume_radiobutton.isChecked()):
        include_volume = True
    
    non_trading = False
    if(chart_dialog.settings_groupbox.nontrading_radiobutton.isChecked()):
        non_trading = True

    showGraph(yf.download(tickers=ticker,
                          period=period, 
                          interval=interval,
                          prepost=include_prepost,
                          auto_adjust=adjust_ohlc,
                          actions=split_dividend
                          ),  ticker, include_volume, non_trading)


def updateTickerIcon(ticker):
    """Updates the performance icon for the given stock"""
    # initializes new table widget item and gets the ticker's open, last close, and current prices
    w = QTableWidgetItem()
    ticker_open = yf.Ticker(ticker).info['open']
    ticker_current = yf.Ticker(ticker).info['regularMarketPrice']
    ticker_last_close = yf.Ticker(ticker).history(period='5d', interval='1d')['Close'][3]

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
    elif close_change > -.1 and open_change < .1:
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


def showGraph(ticker, title, volume, non_trading):
    """Plots a ticker from yfinance in a separate matplotfinance window."""
    # retrieves user's chart style preferences from settings.xml
    up_color = getXMLData('settings.xml', 'upcolor')
    down_color = getXMLData('settings.xml', 'downcolor')
    base_style = getXMLData('settings.xml', 'basestyle')

    # creates a chart style based on the user's settings
    mc = mpf.make_marketcolors(up=up_color[0].text.lower(), down=down_color[0].text.lower(),inherit=True)
    s  = mpf.make_mpf_style(base_mpf_style=base_style[0].text,marketcolors=mc)
    # plots chart

    mpf.plot(ticker['2022-01-01':], 
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


def updateWatchlist():
    """Updates the user's watchlist"""
    while True:
        for i in range(len(watchlist_tickers)):
            # sets the value of the current row in the price tab to reflect
            # the live price of the stock
            portfolio_dialog.watchlist_groupbox.watchlist_view.setItem(i, 0, QTableWidgetItem(watchlist_tickers[i].text.upper()))
            portfolio_dialog.watchlist_groupbox.watchlist_view.setItem(i, 1, updateTickerIcon(watchlist_tickers[i].text))
            portfolio_dialog.watchlist_groupbox.watchlist_view.setItem(i, 2, QTableWidgetItem('${:0,.2f}'.format(yf.Ticker(watchlist_tickers[i].text.upper()).info['regularMarketPrice'])))
            ticker_current = yf.Ticker(watchlist_tickers[i].text).info['regularMarketPrice']
            ticker_last_close = yf.Ticker(watchlist_tickers[i].text).history(period='5d', interval='1d')['Close'][3]

            portfolio_dialog.watchlist_groupbox.watchlist_view.setItem(i, 3, QTableWidgetItem('${:0,.2f}'.format(ticker_current - ticker_last_close) + " (" + str(round(((ticker_current - ticker_last_close) / ticker_last_close * 100), 2)) + "%)"))

            time.sleep(1)


def updateNav():
    """Updates the user's NAV tab. Calculated as cash + (.5 * value of all long positions) - 
    (1.5 * value of all short positions)."""
    while True:

        # sets buying power to user's cash
        newVal = float(amts[0].text)
        buying_power = cash
        total_long = 0
        total_short = 0

        # iterates through all the user's positions and adds (or subtracts) their impact on BP
        # from the running count
        for i in range(1, len(portfolio_tickers)):

            # gets ticker's current price and last close
            price = yf.Ticker(portfolio_tickers[i].text).info['regularMarketPrice']
            ticker_last_close = yf.Ticker(portfolio_tickers[i].text).history(period='5d', interval='1d')['Close'][3]

            # calculates the total return on the position since it was opened
            total_return = (price - float(purchase_prices[i - 1].text)) * int(amts[i].text)
            percent_change = round(total_return / (float(purchase_prices[i - 1].text) * float(amts[i].text)) * 100, 2)

            # column 1 holds the stock's ticker
            portfolio_dialog.positions_view_groupbox.positions_view.setItem(i - 1, 0, QTableWidgetItem(portfolio_tickers[i].text.upper()))

            # column 2 holds the stock's performance icon
            portfolio_dialog.positions_view_groupbox.positions_view.setItem(i - 1, 1, updateTickerIcon(portfolio_tickers[i].text))

            # column 3 holds the stock's current price
            portfolio_dialog.positions_view_groupbox.positions_view.setItem(i - 1, 2, QTableWidgetItem('${:0,.2f}'.format(price)))

            # column 4 holds the stock's return for the day
            portfolio_dialog.positions_view_groupbox.positions_view.setItem(i - 1, 3, QTableWidgetItem('${:0,.2f}'.format(price - ticker_last_close) + " (" + str(round(((price - ticker_last_close) / ticker_last_close * 100), 2)) + "%)"))

            # column 5 holds the user's cost basis for the stock
            portfolio_dialog.positions_view_groupbox.positions_view.setItem(i - 1, 4, QTableWidgetItem('${:0,.2f}'.format(float(purchase_prices[i - 1].text))))
            
            # column 6 holds the # of shares the user has. Negative should indicate user being short
            portfolio_dialog.positions_view_groupbox.positions_view.setItem(i - 1, 5, QTableWidgetItem(amts[i].text))

            # column 7 holds the total market value of all the user's shares (or the total size of the liability if the user is short)
            portfolio_dialog.positions_view_groupbox.positions_view.setItem(i - 1, 6, QTableWidgetItem('${:0,.2f}'.format(price * int(amts[i].text))))
            
            # column 8 holds the user's total return on the position since it was opened
            portfolio_dialog.positions_view_groupbox.positions_view.setItem(i - 1, 7, QTableWidgetItem('${:0,.2f}'.format(total_return) + " (" + str(percent_change) + "%)"))
            
            # if user is long, add the position's value to the tabulation of market value held long
            # if user is short, add the position's value to the tabulation of market value held short
            if int(amts[i].text) > 0:
                total_long += float(price) * int(amts[i].text)
            elif int(amts[i].text) < 0:
                total_short += float(price) * int(amts[i].text)
            newVal += float(price) * int(amts[i].text)

        # calculates buying power and updates GUI
        buying_power += .5 * total_long
        buying_power -= 1.5 * total_short
        portfolio_dialog.currentNAV.liq.setText('${:0,.2f}'.format(float(str(newVal))))
        portfolio_dialog.currentNAV.buyingPower.setText('${:0,.2f}'.format(buying_power))
        portfolio_dialog.currentNAV.returnSinceInception.setText('{:0.2f}'.format((newVal / 10000 - 1) * 100) + "%")
        

        time.sleep(1)


def calculateBuyingPower():
    buying_power = cash
    total_long = 0
    total_short = 0

    for i in range (1, len(amts)):
        stock = yf.Ticker(portfolio_tickers[i].text)
        price = stock.info['regularMarketPrice']
        if int(amts[i].text) > 0:
            total_long += float(price) * int(amts[i].text)
        elif int(amts[i].text) < 0:
            total_short += float(price) * int(amts[i].text)
    
    buying_power += .5 * total_long
    buying_power -= 1.5 * total_short
    return buying_power


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


def close_event(event):
    """Function that is called when the user exits the game. WIP"""
    print("closed")


app = QApplication(sys.argv)
widget = QTabWidget()
widget.setWindowTitle("Ray's Stock Market Trading Simulator")

splash = QSplashScreen(QPixmap('splash.png'))
progressBar = QProgressBar(splash)
progressBar.setGeometry(420, 500, 400, 50)

splash.show()

start = "2022-01-01"
end = "2022-11-27"

spy = yf.download('SPY', start, end)
spy.head()
progressBar.setValue(10)

qqq = yf.download('QQQ', start, end)
qqq.head()
progressBar.setValue(20)

dia = yf.download('DIA', start, end)
dia.head()
progressBar.setValue(30)
vix = yf.download('^VIX', start, end)


#####################################################
# parse XML file data relating to user's portfolio, #
# watchlist, and settings                           #
#####################################################

portfolio_tickers = getXMLData('portfolio.xml', 'name')
watchlist_tickers = getXMLData('watchlist.xml', 'name')
up_color = getXMLData('settings.xml', 'upcolor')

progressBar.setValue(40)

down_color = getXMLData('settings.xml', 'downcolor')
base_style = getXMLData('settings.xml', 'basestyle')
amts = getXMLData('portfolio.xml', 'amount')
purchase_prices = getXMLData('portfolio.xml', 'costbasis')

all_tickers_list = pd.read_csv("stock_list.csv")['Symbol'].tolist()
all_names_list = pd.read_csv("stock_list.csv")['Name'].tolist()
all_tickers_list[5023] = 'NAN'

for i in range(len(all_tickers_list)):
    all_tickers_list[i] += ' - ' + all_names_list[i]
# set user's NAV equal to cash first, then iterate through stocks,
# find their current price, and add their values to user's NAV
nav = float(amts[0].text)
cash = nav

for i in range(1, len(amts)):
    price = yf.Ticker(portfolio_tickers[i].text).info['regularMarketPrice']
    nav += float(price) * int(amts[i].text)

# add genius font to database
QFontDatabase.addApplicationFont('genius.ttf')

progressBar.setValue(50)

####################
# portfolio dialog #
####################

# dialog settings
portfolio_dialog = QDialog()
portfolio_dialog.setObjectName("Dialog")
portfolio_dialog.resize(1000, 600)
portfolio_dialog.setAutoFillBackground(True)
portfolio_dialog.setStyleSheet('background-color: deepskyblue;')

# user's nav settings
portfolio_dialog.currentNAV = QGroupBox(portfolio_dialog)
portfolio_dialog.currentNAV.setTitle("Your NAV")
portfolio_dialog.currentNAV.setGeometry(10, 10, 300, 200)
portfolio_dialog.currentNAV.setStyleSheet('background-color: white;')

# net liquidation value labels
portfolio_dialog.currentNAV.netLiq = QLabel(portfolio_dialog.currentNAV)
portfolio_dialog.currentNAV.netLiq.setText("Net Liq: ")
portfolio_dialog.currentNAV.netLiq.setGeometry(10, 20, 80, 20)
portfolio_dialog.currentNAV.netLiq.setFont(QFont('genius', 10))
portfolio_dialog.currentNAV.liq = QLabel(portfolio_dialog.currentNAV)
portfolio_dialog.currentNAV.liq.setText('${:0,.2f}'.format(float(str(nav))))
portfolio_dialog.currentNAV.liq.setGeometry(10, 40, 160, 40)
portfolio_dialog.currentNAV.liq.setFont(QFont('genius', 20))

# cash value labels
portfolio_dialog.currentNAV.cashLabel = QLabel(portfolio_dialog.currentNAV)
portfolio_dialog.currentNAV.cashLabel.setText("Cash: ")
portfolio_dialog.currentNAV.cashLabel.setGeometry(10, 90, 80, 20)
portfolio_dialog.currentNAV.cash = QLabel(portfolio_dialog.currentNAV)
portfolio_dialog.currentNAV.cash.setText('${:0,.2f}'.format(cash))
portfolio_dialog.currentNAV.cash.setGeometry(100, 90, 80, 20)

progressBar.setValue(60)

# buying power labels
portfolio_dialog.currentNAV.buyingPowerLabel = QLabel(portfolio_dialog.currentNAV)
portfolio_dialog.currentNAV.buyingPowerLabel.setText("Buying Power: ")
portfolio_dialog.currentNAV.buyingPowerLabel.setGeometry(10, 110, 80, 20)
portfolio_dialog.currentNAV.buyingPower = QLabel(portfolio_dialog.currentNAV)
portfolio_dialog.currentNAV.buyingPower.setText('${:0,.2f}'.format(calculateBuyingPower()))
portfolio_dialog.currentNAV.buyingPower.setGeometry(100, 110, 80, 20)

# return since inception labels
portfolio_dialog.currentNAV.returnSinceInceptionLabel = QLabel(portfolio_dialog.currentNAV)
portfolio_dialog.currentNAV.returnSinceInceptionLabel.setText("Return Since Inception: ")
portfolio_dialog.currentNAV.returnSinceInceptionLabel.setGeometry(10, 130, 120, 20)
portfolio_dialog.currentNAV.returnSinceInception = QLabel(portfolio_dialog.currentNAV)
portfolio_dialog.currentNAV.returnSinceInception.setFont(QFont('genius', 20))
portfolio_dialog.currentNAV.returnSinceInception.setText('{:0.2f}'.format((nav / 10000 - 1) * 100) + "%")
portfolio_dialog.currentNAV.returnSinceInception.setGeometry(10, 160, 120, 30)
progressBar.setValue(70)

# positions table settings
portfolio_dialog.positions_view_groupbox = QGroupBox(portfolio_dialog)
portfolio_dialog.positions_view_groupbox.setGeometry(10, 300, 950, 250)
portfolio_dialog.positions_view_groupbox.setTitle("Your Portfolio")
portfolio_dialog.positions_view_groupbox.setStyleSheet('background-color: white;')

portfolio_dialog.positions_view_groupbox.positions_view = QTableWidget(portfolio_dialog.positions_view_groupbox)
portfolio_dialog.positions_view_groupbox.positions_view.setFont(QFont('arial', 10))
portfolio_dialog.positions_view_groupbox.positions_view.setRowCount(len(amts) - 1)
portfolio_dialog.positions_view_groupbox.positions_view.setColumnCount(8)
portfolio_dialog.positions_view_groupbox.positions_view.setGeometry(10, 20, 900, 200)
portfolio_dialog.positions_view_groupbox.positions_view.setStyleSheet('background-color: white;')
portfolio_dialog.positions_view_groupbox.positions_view.setHorizontalHeaderItem(0, QTableWidgetItem("Ticker"))
portfolio_dialog.positions_view_groupbox.positions_view.setHorizontalHeaderItem(1, QTableWidgetItem("Today's Performance"))
portfolio_dialog.positions_view_groupbox.positions_view.setHorizontalHeaderItem(2, QTableWidgetItem("Current Price"))
portfolio_dialog.positions_view_groupbox.positions_view.setHorizontalHeaderItem(3, QTableWidgetItem("Gain/Loss Per Share"))
portfolio_dialog.positions_view_groupbox.positions_view.setHorizontalHeaderItem(4, QTableWidgetItem("Purchase Price"))
portfolio_dialog.positions_view_groupbox.positions_view.setHorizontalHeaderItem(5, QTableWidgetItem("# of Shares"))
portfolio_dialog.positions_view_groupbox.positions_view.setHorizontalHeaderItem(6, QTableWidgetItem("Total Value"))
portfolio_dialog.positions_view_groupbox.positions_view.setHorizontalHeaderItem(7, QTableWidgetItem("Gain/Loss"))


for i in range (8):
    portfolio_dialog.positions_view_groupbox.positions_view.horizontalHeaderItem(i).setFont(QFont('arial', 10))
for i in range (portfolio_dialog.positions_view_groupbox.positions_view.rowCount()):
    portfolio_dialog.positions_view_groupbox.positions_view.setVerticalHeaderItem(0, QTableWidgetItem("1"))
    portfolio_dialog.positions_view_groupbox.positions_view.verticalHeaderItem(i).setFont(QFont('arial', 10))

for i in range(1, len(portfolio_tickers)):
    # for each stock in the user's portfolio, populate its row with its ticker, current price, and purchase price
    portfolio_dialog.positions_view_groupbox.positions_view.setItem(i - 1, 0, QTableWidgetItem(portfolio_tickers[i].text.upper()))
    portfolio_dialog.positions_view_groupbox.positions_view.setItem(i - 1, 1, updateTickerIcon(portfolio_tickers[i].text))
    portfolio_dialog.positions_view_groupbox.positions_view.setItem(i - 1, 2, QTableWidgetItem('${:0,.2f}'.format(price)))

    ticker_current = yf.Ticker(portfolio_tickers[i].text).info['regularMarketPrice']
    ticker_last_close = yf.Ticker(portfolio_tickers[i].text).history(period='5d', interval='1d')['Close'][3]

    portfolio_dialog.positions_view_groupbox.positions_view.setItem(i - 1, 3, QTableWidgetItem('${:0,.2f}'.format(ticker_current - ticker_last_close) + " (" + str(round(((ticker_current - ticker_last_close) / ticker_last_close * 100), 2)) + "%)"))
    portfolio_dialog.positions_view_groupbox.positions_view.setItem(i - 1, 4, QTableWidgetItem('${:0,.2f}'.format(float(purchase_prices[i - 1].text))))
    portfolio_dialog.positions_view_groupbox.positions_view.setItem(i - 1, 5, QTableWidgetItem(amts[i].text))
    portfolio_dialog.positions_view_groupbox.positions_view.setItem(i - 1, 6, QTableWidgetItem('${:0,.2f}'.format(ticker_current * int(amts[i].text))))
    portfolio_dialog.positions_view_groupbox.positions_view.setItem(i - 1, 7, QTableWidgetItem('${:0,.2f}'.format(((ticker_current - float(purchase_prices[i - 1].text)) * int(amts[i].text)))))
    total_return = (ticker_current - float(purchase_prices[i - 1].text)) * int(amts[i].text)
    percent_change = round(total_return / (float(purchase_prices[i - 1].text) * float(amts[i].text)) * 100, 2)
    portfolio_dialog.positions_view_groupbox.positions_view.setItem(i - 1, 7, QTableWidgetItem('${:0,.2f}'.format(total_return) + " (" + str(percent_change) + "%)"))
    
    

portfolio_dialog.positions_view_groupbox.positions_view.resizeColumnsToContents()
progressBar.setValue(80)

# watchlist table settings
portfolio_dialog.watchlist_groupbox = QGroupBox(portfolio_dialog)
portfolio_dialog.watchlist_groupbox.setTitle("Your Watchlist")
portfolio_dialog.watchlist_groupbox.setGeometry(350, 10, 500, 250)
portfolio_dialog.watchlist_groupbox.setStyleSheet('background-color: white;')

portfolio_dialog.watchlist_groupbox.watchlist_view = QTableWidget(portfolio_dialog.watchlist_groupbox)

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


for i in range(len(watchlist_tickers)):
    # for each stock in the watchlist, populate its row with its ticker, its current price,
    # and its performance for the day
    portfolio_dialog.watchlist_groupbox.watchlist_view.setRowHeight(i, 50)
    
    portfolio_dialog.watchlist_groupbox.watchlist_view.setItem(i, 0, QTableWidgetItem(watchlist_tickers[i].text.upper()))
    portfolio_dialog.watchlist_groupbox.watchlist_view.setItem(i, 1, updateTickerIcon(watchlist_tickers[i].text))
    portfolio_dialog.watchlist_groupbox.watchlist_view.setItem(i, 2, QTableWidgetItem('${:0,.2f}'.format(yf.Ticker(watchlist_tickers[i].text.upper()).info['regularMarketPrice'])))
    ticker_current = yf.Ticker(watchlist_tickers[i].text).info['regularMarketPrice']
    ticker_last_close = yf.Ticker(watchlist_tickers[i].text).history(period='5d', interval='1d')['Close'][3]

    portfolio_dialog.watchlist_groupbox.watchlist_view.setItem(i, 3, QTableWidgetItem('${:0,.2f}'.format(ticker_current - ticker_last_close) + " (" + str(round(((ticker_current - ticker_last_close) / ticker_last_close * 100), 2)) + "%)"))
    
portfolio_dialog.watchlist_groupbox.watchlist_view.resizeColumnsToContents()

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
chart_dialog.broad_market_groupbox.spyButton.clicked.connect(lambda: showGraph(spy, 'SPY'))

chart_dialog.broad_market_groupbox.qqqButton = QPushButton(chart_dialog.broad_market_groupbox)
chart_dialog.broad_market_groupbox.qqqButton.setGeometry(QRect(170, 20, 150, 20))
chart_dialog.broad_market_groupbox.qqqButton.setObjectName("qqqButton")
chart_dialog.broad_market_groupbox.qqqButton.clicked.connect(lambda: showGraph(qqq, 'QQQ'))

chart_dialog.broad_market_groupbox.diaButton = QPushButton(chart_dialog.broad_market_groupbox)
chart_dialog.broad_market_groupbox.diaButton.setGeometry(QRect(330, 20, 150, 20))
chart_dialog.broad_market_groupbox.diaButton.setObjectName("diaButton")
chart_dialog.broad_market_groupbox.diaButton.clicked.connect(lambda: showGraph(dia, 'DIA'))

chart_dialog.broad_market_groupbox.vixButton = QPushButton(chart_dialog.broad_market_groupbox)
chart_dialog.broad_market_groupbox.vixButton.setGeometry(QRect(490, 20, 150, 20))
chart_dialog.broad_market_groupbox.vixButton.setObjectName("vixButton")
chart_dialog.broad_market_groupbox.vixButton.clicked.connect(lambda: showGraph(vix, 'VIX'))

# search bar for searching for a stock to chart
chart_dialog.search_bar_groupbox = QGroupBox(chart_dialog)
chart_dialog.search_bar_groupbox.setStyleSheet('background-color: white;')
chart_dialog.search_bar_groupbox.setTitle("Find a Stock")
chart_dialog.search_bar_groupbox.setGeometry(10, 70, 850, 70)

chart_dialog.search_bar_groupbox.searchBar = QLineEdit(chart_dialog.search_bar_groupbox)
chart_dialog.search_bar_groupbox.searchBar.setGeometry(10, 20, 700, 40)
chart_dialog.search_bar_groupbox.searchBar.textChanged.connect(lambda txt: searchTextChanged(txt))
chart_dialog.search_bar_groupbox.searchBar.setFont(QFont('arial', 10))

chart_dialog.settings_groupbox = QGroupBox(chart_dialog)
chart_dialog.settings_groupbox.setStyleSheet('background-color: white;')
chart_dialog.settings_groupbox.setGeometry(10, 150, 850, 100)
chart_dialog.settings_groupbox.setTitle("Chart Settings")

chart_dialog.settings_groupbox.data_period_combobox = QComboBox(chart_dialog.settings_groupbox)
periods = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]
timeframes = ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"]

chart_dialog.settings_groupbox.data_period_combobox.addItems(periods)
chart_dialog.settings_groupbox.data_period_combobox.setGeometry(10, 50, 50, 30)


chart_dialog.settings_groupbox.data_timeframe_combobox = QComboBox(chart_dialog.settings_groupbox)
chart_dialog.settings_groupbox.data_timeframe_combobox.addItems(timeframes)
chart_dialog.settings_groupbox.data_timeframe_combobox.setGeometry(70, 50, 50, 30)




chart_dialog.settings_groupbox.prepost_radiobutton = QRadioButton(chart_dialog.settings_groupbox)
chart_dialog.settings_groupbox.prepost_radiobutton.setText("Include Pre/Post Market Data")
chart_dialog.settings_groupbox.prepost_radiobutton.setGeometry(130, 50, 100, 30)
chart_dialog.settings_groupbox.prepost_buttongroup = QButtonGroup(chart_dialog.settings_groupbox)
chart_dialog.settings_groupbox.prepost_buttongroup.addButton(chart_dialog.settings_groupbox.prepost_radiobutton)

chart_dialog.settings_groupbox.split_dividend_radiobutton = QRadioButton(chart_dialog.settings_groupbox)
chart_dialog.settings_groupbox.split_dividend_radiobutton.setText("Show Split and Dividend Actions")
chart_dialog.settings_groupbox.split_dividend_radiobutton.setGeometry(240, 50, 100, 30)
chart_dialog.settings_groupbox.split_dividend_buttongroup = QButtonGroup(chart_dialog.settings_groupbox)
chart_dialog.settings_groupbox.split_dividend_buttongroup.addButton(chart_dialog.settings_groupbox.split_dividend_radiobutton)

chart_dialog.settings_groupbox.adjust_ohlc_radiobutton = QRadioButton(chart_dialog.settings_groupbox)
chart_dialog.settings_groupbox.adjust_ohlc_radiobutton.setText("Adjust OHLC")
chart_dialog.settings_groupbox.adjust_ohlc_radiobutton.setGeometry(350, 50, 100, 30)
chart_dialog.settings_groupbox.adjust_ohlc_buttongroup = QButtonGroup(chart_dialog.settings_groupbox)
chart_dialog.settings_groupbox.adjust_ohlc_buttongroup.addButton(chart_dialog.settings_groupbox.adjust_ohlc_radiobutton)

chart_dialog.settings_groupbox.volume_radiobutton = QRadioButton(chart_dialog.settings_groupbox)
chart_dialog.settings_groupbox.volume_radiobutton.setText("Include Volume Bars")
chart_dialog.settings_groupbox.volume_radiobutton.setGeometry(460, 50, 140, 30)
chart_dialog.settings_groupbox.volume_buttongroup = QButtonGroup(chart_dialog.settings_groupbox)
chart_dialog.settings_groupbox.volume_buttongroup.addButton(chart_dialog.settings_groupbox.volume_radiobutton)

chart_dialog.settings_groupbox.nontrading_radiobutton = QRadioButton(chart_dialog.settings_groupbox)
chart_dialog.settings_groupbox.nontrading_radiobutton.setText("Include Non-Trading Days")
chart_dialog.settings_groupbox.nontrading_radiobutton.setGeometry(610, 50, 160, 30)
chart_dialog.settings_groupbox.nontrading_buttongroup = QButtonGroup(chart_dialog.settings_groupbox)
chart_dialog.settings_groupbox.nontrading_buttongroup.addButton(chart_dialog.settings_groupbox.nontrading_radiobutton)

model = QStringListModel()
model.setStringList(all_tickers_list)

completer = ac.CustomQCompleter()
completer.setModel(model)
chart_dialog.search_bar_groupbox.searchBar.setCompleter(completer)
completer.activated.connect(lambda: chart_dialog.search_bar_groupbox.search_button.setEnabled(True))
completer.setMaxVisibleItems(5)

chart_dialog.search_bar_groupbox.search_button = QPushButton(chart_dialog.search_bar_groupbox)
chart_dialog.search_bar_groupbox.search_button.setGeometry(710, 20, 80, 40)
chart_dialog.search_bar_groupbox.search_button.setText("Chart")
chart_dialog.search_bar_groupbox.search_button.setEnabled(False)
chart_dialog.search_bar_groupbox.search_button.clicked.connect(searchButtonClicked)
retranslateChartDialogUi(chart_dialog)

################
# trade dialog #
################

trade_dialog = QDialog()


#####################
# stock info dialog #
#####################

stockinfo_dialog = QDialog()
stockinfo_dialog.setStyleSheet('background-color: deepskyblue;')



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

# adding tabs to main window
widget.addTab(portfolio_dialog, "Your Portfolio")
widget.addTab(chart_dialog, "Chart Stocks")
widget.addTab(trade_dialog, "Trade Stocks")
widget.addTab(stockinfo_dialog, "Get Stock Info")
widget.addTab(settings_dialog, "Settings")

widget.resize(1000, 600)
widget.show()

splash.close()

# instantiate thread which runs the updateNav function in an infinite loop
portfolio_background_thread = Thread(target=updateNav, daemon=True)
portfolio_background_thread.start()

watchlist_background_thread = Thread(target=updateWatchlist, daemon=True)
watchlist_background_thread.start()

sys.exit(app.exec())
