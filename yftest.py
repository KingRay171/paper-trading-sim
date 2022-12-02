# Started by Ray Ikome on 11/16/22

from PyQt6.QtWidgets import (QGroupBox, QApplication, QLabel, QProgressBar,
                             QTableWidget, QTableWidgetItem, QTabWidget,
                             QSplashScreen, QPushButton, QDialog, QLineEdit,
                             QComboBox, QWidget)
from PyQt6.QtGui import QFontDatabase, QFont, QPixmap, QIcon
from PyQt6.QtCore import QRect, QCoreApplication
import yfinance as yf
import sys
import mplfinance as mpf
from threading import Thread
import time
from bs4 import BeautifulSoup
import xml.etree.ElementTree as et
from enum import Enum


def showGraph(ticker):

    """Plots a ticker from yfinance in a separate matplotfinance window."""
    # retrieves user's chart style preferences from settings.xml
    mc = mpf.make_marketcolors(up=up_color[0].text.lower(), down=down_color[0].text.lower(),inherit=True)
    s  = mpf.make_mpf_style(base_mpf_style=base_style[0].text,marketcolors=mc)

    # plots chart
    mpf.plot(ticker['2022-01-01':], 
             type='candle', 
             style = s, 
             title = 'Stock Price', 
             volume = True, 
             tight_layout = True)


def retranslateChartDialogUi(self):
    """required retranslation function for chart dialog"""
    _translate = QCoreApplication.translate
    self.setWindowTitle(_translate("Dialog", "Dialog"))
    self.spyButton.setText(_translate("Dialog", "Chart SPY"))
    self.qqqButton.setText(_translate("Dialog", "Chart QQQ"))
    self.diaButton.setText(_translate("Dialog", "Chart DIA"))
    self.vixButton.setText(_translate("Dialog", "Chart VIX"))


def retranslatePortfolioDialogUi(self):
    """required retranslation function for portfolio dialog"""
    _translate = QCoreApplication.translate
    self.setWindowTitle(_translate("Dialog", "Dialog"))


def updateWatchlist():
    """Updates the user's watchlist"""
    while True:
        for i in range(len(portfolio_tickers)):
            # sets the value of the current row in the price tab to reflect
            # the live price of the stock
            ticker_current = yf.Ticker(watchlist_tickers[i].text).info['regularMarketPrice']
            column_one_widget_item = QTableWidgetItem('${:0,.2f}'.format(ticker_current))
            portfolio_dialog.watchlistGroupBox.watchlist_view.setItem(i, 1, column_one_widget_item)
            new_icon = QTableWidgetItem()

            ####################################################################
            # code to set the stock's icon to reflect its movement for the day #
            ####################################################################

            # gets the stock's open price and last close price
            ticker_open = yf.Ticker(watchlist_tickers[i].text).info['open']
            ticker_last_close = yf.Ticker(watchlist_tickers[i].text).history(period='5d', interval='1d')['Close'][4]

            # calculates the stock's percent change from open and from last close
            open_change = (ticker_current - ticker_open) / ticker_open * 100
            close_change = (ticker_current - ticker_last_close) / ticker_last_close * 100

            # determines if the stock was up, down, or flat from open and from last close
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

            # determines icon for the stock based on its performance relative to open and last close
            if open_pos == "UP":
                if close_pos == "UP":
                    new_icon.setIcon(QIcon('greenarrowgreenbox.png'))
                elif close_pos == "FLAT":
                    new_icon.setIcon(QIcon('greenarrowflatbox.png'))
                elif close_pos == "DOWN":
                    new_icon.setIcon(QIcon('greenarrowredbox.png'))
            elif open_pos == "FLAT":
                if close_pos == "UP":
                    new_icon.setIcon(QIcon('flatarrowgreenbox.png'))
                elif close_pos == "FLAT":
                    new_icon.setIcon(QIcon('flatarrowflatbox.png'))
                elif close_pos == "DOWN":
                    new_icon.setIcon(QIcon('flatarrowredbox.png'))
            elif open_pos == "DOWN":
                if close_pos == "UP":
                    new_icon.setIcon(QIcon('redarrowgreenbox.png'))
                elif close_pos == "FLAT":
                    new_icon.setIcon(QIcon('redarrowflatbox.png'))
                elif close_pos == "DOWN":
                    new_icon.setIcon(QIcon('redarrowredbox.png'))

            # displays new icon
            portfolio_dialog.watchlistGroupBox.watchlist_view.setItem(i, 2, new_icon)

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
            stock = yf.Ticker(portfolio_tickers[i].text)
            price = stock.info['regularMarketPrice']
            portfolio_dialog.positions_view.setItem(i - 1, 0, QTableWidgetItem(portfolio_tickers[i].text.upper()))
            portfolio_dialog.positions_view.setItem(i - 1, 1, QTableWidgetItem('${:0,.2f}'.format(price)))
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
    up_color = settings_dialog.up_color_combobox.currentText()[0]
    down_color = settings_dialog.down_color_combobox.currentText()[0]
    base_style = settings_dialog.chart_style_combobox.currentText()[0]

    # parses XML file into an ElementTree
    tree = et.parse('settings.xml')

    # replaces old data in the file with the current data
    for upcolor in tree.getroot().iter('upcolor'):
        upcolor.text = up_color

    for downcolor in tree.getroot().iter('downcolor'):
        downcolor.text = down_color

    for basestyle in tree.getroot().iter('basestyle'):
        basestyle.text = base_style

    tree.write('settings.xml')

    # updates global settings variables
    up_color = getXMLData('settings.xml', 'upcolor')
    down_color = getXMLData('settings.xml', 'downcolor')
    base_style = getXMLData('settings.xml', 'basestyle')


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

# set user's NAV equal to cash first, then iterate through stocks,
# find their current price, and add their values to user's NAV
nav = float(amts[0].text)
cash = nav


for i in range(1, len(amts)):
    price = yf.Ticker(portfolio_tickers[i].text).info['regularMarketPrice']
    nav += float(price) * int(amts[i].text)

# add genius font to database
QFontDatabase.addApplicationFont('genius.ttf')

position = Enum('position', ['UP', 'FLAT', 'DOWN'])


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
portfolio_dialog.positions_view = QTableWidget(portfolio_dialog)
portfolio_dialog.positions_view.setRowCount(len(amts) - 1)
portfolio_dialog.positions_view.setColumnCount(10)
portfolio_dialog.positions_view.setGeometry(10, 300, 900, 200)
portfolio_dialog.positions_view.setStyleSheet('background-color: white;')
portfolio_dialog.positions_view.setHorizontalHeaderItem(0, QTableWidgetItem("Ticker"))
portfolio_dialog.positions_view.setHorizontalHeaderItem(1, QTableWidgetItem("Current Price"))
portfolio_dialog.positions_view.setHorizontalHeaderItem(2, QTableWidgetItem("Purchase Price"))
portfolio_dialog.positions_view.setHorizontalHeaderItem(3, QTableWidgetItem("Gain/Loss Per Share"))
portfolio_dialog.positions_view.setHorizontalHeaderItem(3, QTableWidgetItem("# of Shares"))
portfolio_dialog.positions_view.setHorizontalHeaderItem(3, QTableWidgetItem("Gain/Loss"))
portfolio_dialog.positions_view.setHorizontalHeaderItem(3, QTableWidgetItem("Gain/Loss Per Share"))

for i in range(1, len(portfolio_tickers)):
    # for each stock in the user's portfolio, populate its row with its ticker, current price, and purchase price
    stock = yf.Ticker(portfolio_tickers[i].text)
    price = stock.info['regularMarketPrice']
    portfolio_dialog.positions_view.setItem(i - 1, 0, QTableWidgetItem(portfolio_tickers[i].text.upper()))
    portfolio_dialog.positions_view.setItem(i - 1, 1, QTableWidgetItem('${:0,.2f}'.format(price)))
    portfolio_dialog.positions_view.setItem(i - 1, 2, QTableWidgetItem('${:0,.2f}'.format(float(purchase_prices[i - 1].text))))

progressBar.setValue(80)

# watchlist table settings
portfolio_dialog.watchlistGroupBox = QGroupBox(portfolio_dialog)
portfolio_dialog.watchlistGroupBox.setTitle("Your Watchlist")
portfolio_dialog.watchlistGroupBox.setGeometry(350, 10, 500, 250)
portfolio_dialog.watchlistGroupBox.setStyleSheet('background-color: white;')

portfolio_dialog.watchlistGroupBox.watchlist_view = QTableWidget(portfolio_dialog.watchlistGroupBox)
portfolio_dialog.watchlistGroupBox.watchlist_view.setRowCount(len(watchlist_tickers))
portfolio_dialog.watchlistGroupBox.watchlist_view.setColumnCount(3)
portfolio_dialog.watchlistGroupBox.watchlist_view.setColumnWidth(2, 50)
portfolio_dialog.watchlistGroupBox.watchlist_view.setGeometry(10, 20, 400, 200)

for i in range(len(watchlist_tickers)):
    # for each stock in the watchlist, populate its row with its ticker, its current price,
    # and its performance for the day
    portfolio_dialog.watchlistGroupBox.watchlist_view.setRowHeight(i, 50)
    
    portfolio_dialog.watchlistGroupBox.watchlist_view.setItem(i, 0, QTableWidgetItem(watchlist_tickers[i].text.upper()))
    portfolio_dialog.watchlistGroupBox.watchlist_view.setItem(i, 1, QTableWidgetItem('${:0,.2f}'.format(yf.Ticker(watchlist_tickers[i].text.upper()).info['regularMarketPrice'])))
    w = QTableWidgetItem()
    ticker_open = yf.Ticker(watchlist_tickers[i].text).info['open']
    ticker_current = yf.Ticker(watchlist_tickers[i].text).info['regularMarketPrice']
    ticker_last_close = yf.Ticker(watchlist_tickers[i].text).history(period='5d',
                                                                     interval='1d')['Close'][4]

            
    open_change = (ticker_current - ticker_open) / ticker_open * 100
    close_change = (ticker_current - ticker_last_close) / ticker_last_close * 100

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

    portfolio_dialog.watchlistGroupBox.watchlist_view.setItem(i, 2, w)

retranslatePortfolioDialogUi(portfolio_dialog)


################
# chart dialog #
################

progressBar.setValue(90)
chart_dialog = QDialog()
chart_dialog.setObjectName("Dialog")
chart_dialog.resize(1000, 600)

# button for charting SPY
chart_dialog.spyButton = QPushButton(chart_dialog)
chart_dialog.spyButton.setGeometry(QRect(10, 10, 150, 20))
chart_dialog.spyButton.setObjectName("spyButton")
chart_dialog.spyButton.clicked.connect(lambda: showGraph(spy))

# button for charting QQQ
chart_dialog.qqqButton = QPushButton(chart_dialog)
chart_dialog.qqqButton.setGeometry(QRect(170, 10, 150, 20))
chart_dialog.qqqButton.setObjectName("qqqButton")
chart_dialog.qqqButton.clicked.connect(lambda: showGraph(qqq))

# button for charting DIA
chart_dialog.diaButton = QPushButton(chart_dialog)
chart_dialog.diaButton.setGeometry(QRect(330, 10, 150, 20))
chart_dialog.diaButton.setObjectName("diaButton")
chart_dialog.diaButton.clicked.connect(lambda: showGraph(dia))

# button for charting VIX
chart_dialog.vixButton = QPushButton(chart_dialog)
chart_dialog.vixButton.setGeometry(QRect(490, 10, 150, 20))
chart_dialog.vixButton.setObjectName("vixButton")
chart_dialog.vixButton.clicked.connect(lambda: showGraph(vix))

# search bar for searching for a stock to chart
chart_dialog.searchBar = QLineEdit(chart_dialog)
chart_dialog.searchBar.setGeometry(100, 200, 400, 40)
retranslateChartDialogUi(chart_dialog)

# trade dialog

trade_dialog = QDialog()


#####################
# stock info dialog #
#####################
stockinfo_dialog = QDialog()


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
settings_dialog.chart_style_label.setText("Down Candle Color:")
settings_dialog.chart_style_label.setGeometry(430, 10, 200, 40)
settings_dialog.chart_style_combobox.addItems(down_colors)
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
