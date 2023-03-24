# Started by Ray Ikome on 11/16/22
import sys
import os
from locale import atof, setlocale, LC_NUMERIC
from threading import Thread
import time
import xml.etree.ElementTree as et
from datetime import datetime

import pandas as pd
# pylint: disable-msg=E0611
# pylint: disable-msg=W0603
# pylint: disable-msg=C0103
from PySide6.QtCharts import (QChart, QChartView, QPieSeries, QLineSeries,
                              QDateTimeAxis, QValueAxis, QBarSeries, QBarSet)
from PySide6.QtWidgets import (QWidget, QTabWidget, QGroupBox, QLabel, QTableWidget,
                               QTableWidgetItem, QAbstractItemView, QHBoxLayout,
                               QSplashScreen, QPushButton, QDialog, QLineEdit, QComboBox,
                               QRadioButton, QCalendarWidget, QCheckBox, QApplication,
                               QProgressBar, QVBoxLayout, QScrollArea, QButtonGroup,
                               QSlider, QSpinBox, QDoubleSpinBox, QSizePolicy, QGridLayout)
from PySide6.QtGui import QFont, QFontDatabase, QPixmap, QIcon, QColor, QEnterEvent
from PySide6.QtCore import QStringListModel, QDateTime, Qt, SIGNAL, QPropertyAnimation, QSize
import yahooquery as yq

from dependencies import autocomplete as ac
from dependencies import IsMarketOpen as mktopen
from dependencies import dcfmodel as dcf
from dependencies import numberformat as nf
from dependencies import finviznews as fn
from dependencies import readassets as ra
from dependencies import savetrades as st
from dependencies import saveport as sp
from dependencies import scanner as sc
from dependencies import unconventional_stragegies as us
app = QApplication(sys.argv)

CWD = os.getcwd() + '\\'

QPropertyAnimation()

CURRENT_TICKER = ''

selected_ta = []

OPEN_ORDERS = []

TOKEN_OBJECTS = []

PORTFOLIO_OBJECTS = []

WATCHLIST_OBJECTS = []

ARIAL_10 = QFont('arial', 10)

GEAR_ICON = QIcon('icons/gear.jpg')

SETTINGS_DIALOG_BTN_STYLESHEET = "QPushButton::hover{background-color: deepskyblue; color: white;}"

SCROLLBAR_ALWAYSON = Qt.ScrollBarPolicy.ScrollBarAlwaysOn

CURRENT_TRADE_STOCK = None

# performance icons
GREENARROW_GREENBOX = QIcon(f"{CWD}icons/greenarrowgreenbox.png")
GREENARROW_FLATBOX = QIcon(f"{CWD}icons/greenarrowflatbox.png")
GREENARROW_REDBOX = QIcon(f"{CWD}icons/greenarrowredbox.png")
FLATARROW_GREENBOX = QIcon(f"{CWD}icons/flatarrowgreenbox.png")
FLATARROW_FLATBOX = QIcon(f"{CWD}icons/flatarrowflatbox.png")
FLATARROW_REDBOX = QIcon(f"{CWD}icons/flatarrowredbox.png")
REDARROW_GREENBOX = QIcon(f"{CWD}icons/redarrowgreenbox.png")
REDARROW_FLATBOX = QIcon(f"{CWD}icons/redarrowflatbox.png")
REDARROW_REDBOX = QIcon(f"{CWD}icons/redarrowredbox.png")


def spy_button_clicked():
    """
    Is called when the "Chart SPY" button is clicked.
    Charts SPY with the current user settings
    """
    chart_configs.searchbar_gb.searchBar.setText("SPY - SPDR S&P 500 ETF Trust")
    search_button_clicked()


def qqq_button_clicked():
    """
    Is called when the "Chart QQQ" button is clicked.
    Charts QQQ with the current user settings
    """
    chart_configs.searchbar_gb.searchBar.setText("QQQ - Invesco QQQ Trust")
    search_button_clicked()


def dia_button_clicked():
    """
    Is called when the "Chart DIA" button is clicked.
    Charts DIA with the current user settings
    """
    chart_configs.searchbar_gb.searchBar.setText(
        "DIA - SPDR Dow Jones Industrial Average ETF Trust"
    )
    search_button_clicked()


def vix_button_clicked():
    """
    Is called when the "Chart VIX" button is clicked.
    Charts VIX with the current user settings
    """
    chart_configs.searchbar_gb.searchBar.setText("^VIX ")
    search_button_clicked()


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
        if widget.currentWidget() == wallet_dialog:
            update_wallet_nav()
            update_wallet_table()
            time.sleep(5)
        if widget.currentWidget() == trade_dialog and CURRENT_TRADE_STOCK is not None:
            update_trade_dialog()
        if mktopen.isMarketOpen():
            if widget.currentWidget() == port_dialog:
                update_portfolio_table()
                update_watchlist_tickers()
                update_portfolio_nav()
                update_portfolio_piechart()
            update_trades()
        else:
            time.sleep(1)




def update_trades():

    for order in OPEN_ORDERS:

        cash = float(portfolio_amts[0])
        ticker = yq.Ticker(order[0])
        asset_type = ""
        match ticker.quote_type[order[0]]['quoteType']:
            case 'EQUITY':
                asset_type = 'Stock'
            case 'ETF':
                asset_type = 'ETF'

        if order[2] == 'Market' and order[1] == 'Buy':
            execute_buy(order, ticker, asset_type, cash)

        elif order[2] == 'Market' and order[1] == 'Sell':
            execute_sell(order, ticker, asset_type, cash)

        elif order[2] == 'Limit' and order[1] == 'Buy':
            if yq.Ticker(order[0]).summary_detail[order[0]]['ask'] < float(order[3]):
                execute_buy(order, ticker, asset_type, cash)

        elif order[2] == 'Limit' and order[1] == 'Sell':
            if yq.Ticker(order[0]).summary_detail[order[0]]['bid'] > float(order[3]):
                execute_sell(order, ticker, asset_type, cash)

        elif order[2] == 'Stop' and order[1] == 'Buy':
            if yq.Ticker(order[0]).summary_detail[order[0]]['ask'] > float(order[3]):
                execute_buy(order, ticker, asset_type, cash)

        elif order[2] == 'Stop' and order[1] == 'Sell':
            if yq.Ticker(order[0]).summary_detail[order[0]]['bid'] < float(order[3]):
                execute_sell(order, ticker, asset_type, cash)




def execute_buy(order: list, ticker: yq.Ticker, asset_type: str, cash: float, trade_price=None):
    global portfolio_cash
    if trade_price is None:
        trade_price = ticker.summary_detail[order[0]]['ask']

    cash -= float(order[4]) * float(trade_price)
    portfolio_amts[0] = str(cash)
    portfolio_cash = cash

    if order[0] in portfolio_tickers:
        idx = portfolio_tickers.index(order[0])

        if -1 * int(order[4]) == int(portfolio_amts[idx]):
            portfolio_tickers.remove(order[0])
            portfolio_amts.remove(str(-1 * int(order[4])))
            purchase_prices.remove(purchase_prices[idx - 1])
            portfolio_asset_types.remove(portfolio_asset_types[idx])
            PORTFOLIO_OBJECTS.remove(ticker)
            try:
                port_dialog.pos_view_gb.pos_view.setRowCount(
                    len(portfolio_amts) - 1
                )

            except Exception:
                pass

        elif int(order[4]) < int(portfolio_amts[idx]):


            stock_amt = int(portfolio_amts[idx])
            stock_amt += int(order[4])
            portfolio_amts[idx] = str(stock_amt)

            purchase_price = float(purchase_prices[idx - 1])
            new_cb = round(
                (purchase_price * (int(portfolio_amts[idx]) - int(order[4])) + trade_price * int(order[4])) / int(portfolio_amts[idx]), 2
            )
            purchase_prices[idx - 1] = str(new_cb)
        elif int(order[4]) > int(portfolio_amts[idx]):
            stock_amt = int(portfolio_amts[idx])
            stock_amt += int(order[4])
            portfolio_amts[idx] = str(stock_amt)

            purchase_prices[idx - 1] = str(trade_price)

    else:
        portfolio_tickers.append(order[0])
        portfolio_amts.append(order[4])
        portfolio_asset_types.append(asset_type)
        purchase_prices.append(str(trade_price))
        PORTFOLIO_OBJECTS.append(ticker)
        try:
            port_dialog.pos_view_gb.pos_view.setRowCount(
                len(portfolio_amts) - 1
            )
            column_count = port_dialog.pos_view_gb.pos_view.columnCount()
            for k in range(column_count):
                port_dialog.pos_view_gb.pos_view.setItem(column_count - 1, k, QTableWidgetItem())

        except Exception:
            pass
    OPEN_ORDERS.remove(order)



def execute_sell(order: list, ticker: yq.Ticker, asset_type: str, cash: float, trade_price=None):
    global portfolio_cash
    if trade_price is None:
        trade_price = ticker.summary_detail[order[0]]['bid']
    cash += float(order[4]) * float(trade_price)
    portfolio_amts[0] = str(cash)
    portfolio_cash = cash

    if order[0] in portfolio_tickers:
        idx = portfolio_tickers.index(order[0])

        if int(order[4]) < int(portfolio_amts[idx]):
            stock_amt = int(portfolio_amts[idx])
            stock_amt -= int(order[4])
            portfolio_amts[idx] = str(stock_amt)


        elif int(order[4]) == int(portfolio_amts[idx]):
            portfolio_tickers.remove(order[0])
            portfolio_amts.remove(order[4])
            purchase_prices.remove(purchase_prices[idx - 1])
            portfolio_asset_types.remove(portfolio_asset_types[idx])
            PORTFOLIO_OBJECTS.remove(ticker)
            try:
                port_dialog.pos_view_gb.pos_view.setRowCount(
                    len(portfolio_amts) - 1
                )
            except TypeError:
                pass
        else:
            stock_amt = int(portfolio_amts[idx])
            stock_amt -= int(order[4])
            portfolio_amts[idx] = str(stock_amt)
            purchase_prices[idx - 1] = str(trade_price)

            purchase_price = float(purchase_prices[idx - 1])
            new_cb = round(
                (purchase_price * (int(portfolio_amts[idx]) - int(order[4])) + trade_price * int(order[4])) / int(portfolio_amts[idx]), 2
            )
            purchase_prices[idx - 1] = str(new_cb)


    else:
        portfolio_tickers.append(order[0])
        portfolio_amts.append(str(-1 * int(order[4])))
        portfolio_asset_types.append(asset_type)
        purchase_prices.append(str(trade_price))
        PORTFOLIO_OBJECTS.append(ticker)
        try:
            port_dialog.pos_view_gb.pos_view.setRowCount(
                len(portfolio_amts) - 1
            )
            column_count = port_dialog.pos_view_gb.pos_view.columnCount()
            for j in range(column_count):
                port_dialog.pos_view_gb.pos_view.setItem(column_count - 1, j, QTableWidgetItem())
        except TypeError:
            pass
    OPEN_ORDERS.remove(order)



def update_portfolio_piechart():
    """
    Updates the asset class piechart on the portfolio dialog
    """

    # gets the present value of the portfolio broken down by asset type
    long_etfs = 0
    short_etfs = 0
    long_stocks = 0
    short_stocks = 0
    long_options = 0
    short_options = 0
    cash_amount = 0

    for idx, amount in enumerate(portfolio_amts):
        if portfolio_asset_types[idx] != 'Liquidity':
            asset_price = float(port_dialog.pos_view_gb.pos_view.item(idx - 1, 2).text()[1:])

        match portfolio_asset_types[idx]:
            case "ETF":
                if int(amount) > 0:
                    long_etfs += int(amount) * asset_price
                else:
                    short_etfs -= int(amount) * asset_price
            case "Liquidity":
                cash_amount += float(amount)
            case "Stock":
                if int(amount) > 0:
                    long_stocks += int(amount) * asset_price
                else:
                    short_stocks -= int(amount) * asset_price
            case "Option":
                if int(amount) > 0:
                    long_options += int(amount) * asset_price
                else:
                    short_options -= int(amount) * asset_price

    cash_amount -= 2 * float(port_dialog.nav_gb.liabilities.text()[2:].replace(",", ""))
    # loads values into pie chart and displays them

    asset_class_chart.slices()[0].setValue(round(long_etfs / portfolio_nav * 100, 2))
    if long_etfs != 0:
        asset_class_chart.slices()[0].setLabel(
            f"Long ETFs: {round(long_etfs / portfolio_nav * 100, 2)}%"
        )
        asset_class_chart.slices()[0].setLabelVisible(True)

    asset_class_chart.slices()[1].setValue(round(short_etfs / portfolio_nav * 100, 2))
    if short_etfs != 0:
        asset_class_chart.slices()[1].setLabel(
            f"Short ETFs: {round(short_etfs / portfolio_nav * 100, 2)}%"
        )
        asset_class_chart.slices()[1].setLabelVisible(True)

    asset_class_chart.slices()[2].setValue(round(long_stocks / portfolio_nav * 100, 2))
    if long_stocks != 0:
        asset_class_chart.slices()[2].setLabel(
            f"Long Stocks: {round(long_stocks / portfolio_nav * 100, 2)}%"
        )
        asset_class_chart.slices()[2].setLabelVisible(True)

    asset_class_chart.slices()[3].setValue(round(short_stocks / portfolio_nav * 100, 2))
    if short_stocks != 0:
        asset_class_chart.slices()[3].setLabel(
            f"Short Stocks: {round(short_stocks / portfolio_nav * 100, 2)}%"
        )
        asset_class_chart.slices()[3].setLabelVisible(True)

    asset_class_chart.slices()[4].setValue(long_options / portfolio_nav * 100)
    if long_options != 0:
        asset_class_chart.slices()[4].setLabel(
            f"Long Options: {round(long_options / portfolio_nav * 100, 2)}%"
        )
        asset_class_chart.slices()[4].setLabelVisible(True)

    asset_class_chart.slices()[5].setValue(short_options / portfolio_nav * 100)
    if short_options != 0:
        asset_class_chart.slices()[5].setLabel(
            f"Short Options: {round(short_options / portfolio_nav * 100, 2)}%"
        )
        asset_class_chart.slices()[5].setLabelVisible(True)

    asset_class_chart.slices()[6].setValue(cash_amount / portfolio_nav * 100)
    if cash_amount != 0:
        asset_class_chart.slices()[6].setLabel(
            f"Cash: {round(cash_amount / portfolio_nav * 100, 2)}%"
        )
        asset_class_chart.slices()[6].setLabelVisible(True)


def update_wallet_table():
    """
    Updates the positions table on the crypto wallet dialog.
    """
    wallet_zip = zip(wallet_tickers[1:], TOKEN_OBJECTS, wallet_costbases, wallet_amts[1:])
    for idx, (ticker, obj, basis, amt) in enumerate(wallet_zip):

        # get the current price and the price it last closed at
        ticker_data = obj.history('1wk')
        current_price = ticker_data.iloc[-1][5]
        last_close_price = ticker_data.iloc[-2][5]

        # calculate the return since the position was opened in dollar and percent terms
        total_return = (current_price - float(basis)) * float(amt)
        percent_change = round(total_return / (float(basis) * float(amt)) * 100, 2)

        # update the table with the new information

        # first cell in the row is the coin symbol
        wallet_dialog.pos_view_gb.pos_view.item(idx, 0).setText(ticker)

        # second cell is the coin's performance icon
        wallet_dialog.pos_view_gb.pos_view.item(idx, 1).setIcon(update_ticker_icon(ticker_data))

        # third cell is the coin's current price
        wallet_dialog.pos_view_gb.pos_view.item(idx, 2).setText(f'${current_price:0,.2f}')


        # fourth cell is the change in the coin's price from it's last close,
        # in dollar and percent terms
        last_close_change = current_price - last_close_price
        wallet_dialog.pos_view_gb.pos_view.item(idx, 3).setText(
            f'${last_close_change:0,.2f} ({round(last_close_change / last_close_price * 100, 2)}%)'
        )


        # fifth cell is the user's costbasis for the token
        wallet_dialog.pos_view_gb.pos_view.item(idx, 4).setText(f'${float(basis):0,.2f}')


        # sixth cell is the amount of the coin the user has (or is short)
        wallet_dialog.pos_view_gb.pos_view.item(idx, 5).setText(amt)


        # seventh cell is the NLV the user has in the coin
        wallet_dialog.pos_view_gb.pos_view.item(idx, 6).setText(
            f'${(current_price * float(amt)):0,.2f}')


        # eighth cell is the user's net P/L on the position from when it was opened
        wallet_dialog.pos_view_gb.pos_view.item(idx, 7).setText(
            f'${total_return:0,.2f} ({percent_change}%)'
        )


def update_portfolio_table():
    """
    Updates the table with all the user's positions in the portfolio dialog
    """
    # for each asset in the portfolio
    port_zip = zip(portfolio_tickers[1:], PORTFOLIO_OBJECTS, purchase_prices, portfolio_amts[1:])
    for idx, (ticker, obj, basis, amt) in enumerate(port_zip):
        int_amt = int(amt)
        basis = float(basis)
        # get the current price and the price it last closed at

        ticker_data = obj.history(period='5d')
        current_price = ticker_data.iloc[-1][5]
        last_close = ticker_data.iloc[-2][5]
        # calculate the return since the position was opened in dollar and percent terms
        total_return = (current_price - basis) * int_amt
        percent_change = round(total_return / (basis * int_amt) * 100, 2)
        # update the table with the new information

        if port_dialog.pos_view_gb.pos_view.item(idx, 0) is None:
            column_count = port_dialog.pos_view_gb.pos_view.columnCount()
            for k in range(column_count):
                port_dialog.pos_view_gb.pos_view.setItem(idx, k, QTableWidgetItem())


        port_dialog.pos_view_gb.pos_view.item(idx, 0).setText(ticker)

        port_dialog.pos_view_gb.pos_view.item(idx, 1).setIcon(update_ticker_icon(ticker_data))

        port_dialog.pos_view_gb.pos_view.item(idx, 2).setText(f'${current_price:0,.2f}')

        last_close_change = current_price - last_close
        port_dialog.pos_view_gb.pos_view.item(idx, 3).setText(
            f'${last_close_change:0,.2f} ({round(last_close_change / last_close * 100, 2)}%)'
        )

        port_dialog.pos_view_gb.pos_view.item(idx, 4).setText(f'${basis:0,.2f}')

        port_dialog.pos_view_gb.pos_view.item(idx, 5).setText(amt)

        port_dialog.pos_view_gb.pos_view.item(idx, 6).setText(f'${(current_price * int_amt):0,.2f}')

        port_dialog.pos_view_gb.pos_view.item(idx, 7).setText(
            f'${total_return:0,.2f} ({percent_change}%)')


def update_watchlist_tickers():
    """
    Updates the table with all the tickers in the user's watchlist in the portfolio dialog
    """

    # for each ticker in the watchlist
    watchlist_zip = zip(watchlist_tickers, WATCHLIST_OBJECTS)
    for idx, (item, obj) in enumerate(watchlist_zip):

        ticker = obj.history(period='5d')
        ticker_current = ticker.iloc[-1][5]
        last_close = ticker.iloc[-2][5]

        port_dialog.watchlist_gb.watchlist.item(idx, 0).setText(item)

        port_dialog.watchlist_gb.watchlist.item(idx, 1).setIcon(update_ticker_icon(ticker))

        port_dialog.watchlist_gb.watchlist.item(idx, 2).setText(f'${ticker_current:0,.2f}')

        last_close_change = ticker_current - last_close
        port_dialog.watchlist_gb.watchlist.item(idx, 3).setText(
            f'${last_close_change:0,.2f} ({round(last_close_change / last_close * 100, 2)}%)'

        )


def daterange_radiobutton_clicked():
    """
    Should run only when the player clicks the "Chart by Date Range" radiobutton on the
    "Chart Stocks" dialog. Disables the combobox that lets the user select a period to
    chart over and enables the calendars so that the user can pick a start and end date
    for the chart.
    """
    chart_configs.settings_gb.start_date.setEnabled(True)
    chart_configs.settings_gb.end_date.setEnabled(True)
    chart_configs.settings_gb.data_period_combobox.setEnabled(
        False)


def period_radiobutton_clicked():
    """
    Should run only when the player clicks the "Chart by Period" radiobutton on the
    "Chart Stocks" dialog. Disables the calendars that let the user select a start
    and end date for the chart and enables the period
    combobox so that the user can pick a start and end date for the chart.
    """
    chart_configs.settings_gb.start_date.setEnabled(False)
    chart_configs.settings_gb.end_date.setEnabled(False)
    chart_configs.settings_gb.data_period_combobox.setEnabled(
        True)


def search_text_changed(txt: str):
    """
    Executed when text is typed into the search bar on the "Chart Stocks" tab.
    The function takes the entered text and appends it to the search bar.
    """
    chart_configs.searchbar_gb.searchBar.setText(txt.upper())


def search_button_clicked():
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
    # gets the stock ticker from the search bar
    ticker = chart_configs.searchbar_gb.searchBar.text().split(' ')[0]

    # get the interval the user selected
    interval = chart_configs.settings_gb.data_timeframe_combobox.currentText()

    # get all chart settings the user selected on the chart menu
    include_prepost = chart_configs.settings_gb.prepost_checkbox.isChecked()

    adjust_ohlc = chart_configs.settings_gb.adjust_ohlc_checkbox.isChecked()

    split_dividend = chart_configs.settings_gb.split_dividend_checkbox.isChecked()

    include_volume = chart_configs.settings_gb.volume_checkbox.isChecked()

   # shows the requested ticker's chart
    if chart_configs.settings_gb.daterange_radiobutton.isChecked():

        chart_by_dates(
            ticker, interval, include_prepost, adjust_ohlc, split_dividend, include_volume
        )
    else:
        # only get period if user chose to chart by period
        chart_by_period(
            ticker, interval, include_prepost, adjust_ohlc, split_dividend, include_volume
        )


def chart_by_dates(ticker: str, interval: str, prepost: str, ohlc: str, split_div: str, vol: str):
    """
    Starts chart UI, passes start date and end date as command line arguments
    """
    def thread_worker(title, start, end, interval):
        cla = f'{title} {interval} "{selected_ta}" {start} {end} {prepost} {ohlc} {split_div} {vol}'
        os.system(rf"python3 {CWD}dependencies\stockchart.py {cla}")

    start = chart_configs.settings_gb.start_date.selectedDate().toString("yyyy-MM-dd")
    end = chart_configs.settings_gb.end_date.selectedDate().toString("yyyy-MM-dd")

    Thread(daemon=True, target=thread_worker, args=(ticker, start, end, interval)).start()


def chart_by_period(ticker: str, interval: str, prepost: str, ohlc: str, split_div: str, vol: str):
    """
    Starts chart UI, passes a period as a command line argument
    """
    def thread_worker(title, period, interval):
        cla = f'{title} {interval} "{selected_ta}" {period} {prepost} {ohlc} {split_div} {vol}'
        os.system(rf"python3 {CWD}dependencies\stockchart.py {cla}")

    period = chart_configs.settings_gb.data_period_combobox.currentText()

    Thread(daemon=True, target=thread_worker, args=(ticker, period, interval)).start()


def update_ticker_icon(ticker) -> QIcon:
    """
    Updates the performance icon for the given stock

        ticker : pandas.DataFrame
            A Pandas dataframe representing a ticker's price history.
            Obtained through a call to yf.download
        Returns a QTableWidgetItem with the new performance icon
    """
    # initializes new table widget item and gets the ticker's open, last close, and current prices

    ticker_open = ticker.iloc[-1][0]
    ticker_current = ticker.iloc[-1][5]
    last_close = ticker.iloc[-2][5]

    # calculates the percent change in price from open and from yesterday's close
    open_change = (ticker_current - ticker_open) / ticker_open * 100
    close_change = (ticker_current - last_close) / last_close * 100

    # decides if the stock is up, down, or flat compared to open and yesterday's close
    open_pos = "UP"
    close_pos = "UP"
    if open_change < -.1:
        open_pos = "DOWN"

    elif -.1 < open_change < .1:
        open_pos = "FLAT"

    if close_change < -.1:
        close_pos = "DOWN"
    elif -.1 < close_change < .1:
        close_pos = "FLAT"

    match open_pos:
        case "UP":
            match close_pos:
                case "UP":
                    return GREENARROW_GREENBOX
                case "FLAT":
                    return GREENARROW_FLATBOX
                case "DOWN":
                    return GREENARROW_REDBOX

        case "FLAT":
            match close_pos:
                case "UP":
                    return FLATARROW_GREENBOX
                case "FLAT":
                    return FLATARROW_FLATBOX
                case "DOWN":
                    return FLATARROW_REDBOX

        case "DOWN":
            match close_pos:
                case "UP":
                    return REDARROW_GREENBOX
                case "FLAT":
                    return REDARROW_FLATBOX
                case "DOWN":
                    return REDARROW_REDBOX

    # returns a tablewidgetitem containing the new icon


def update_portfolio_nav():
    """
    Updates the user's NAV tab. Buying power is calculated as
    cash + (.5 * value of all long positions) -
    (1.5 * value of all short positions).
    """

    # sets buying power to user's cash
    new_val = float(portfolio_amts[0])
    liabilities = 0
    assets = 0

    # for each stock in the portfolio, get its price and check if it's held long or sold short
    for idx, amt in enumerate(portfolio_amts[1:]):
        # slice returns only the dollar value without the '$'
        cur_val = float(port_dialog.pos_view_gb.pos_view.item(idx, 2).text()[1:])
        amt = int(amt)

        if amt > 0:
            # if it's long, add its value to the new value and to the assets tally
            new_val += cur_val * amt
            assets += cur_val * amt
        elif amt < 0:
            # if it's short, subtract its value from the new value and add to the liabilities tally
            new_val += cur_val * amt
            liabilities += cur_val * amt

    port_dialog.nav_gb.liq.setText(f'${new_val:0,.2f}')

    port_dialog.nav_gb.bp.setText(f'${get_portfolio_bp():0,.2f}')

    port_dialog.nav_gb.cash.setText(f'${portfolio_cash:0,.2f}')

    port_dialog.nav_gb.assets.setText(f'${assets:0,.2f}')

    port_dialog.nav_gb.liabilities.setText(f'${liabilities:0,.2f}')

    port_dialog.nav_gb.returnSinceInception.setText(f'{((new_val / 10000 - 1) * 100):0,.2f}%')


def update_wallet_nav():
    """Updates the user's NAV tab. Calculated as cash + (.5 * value of all long positions) -
    (1.5 * value of all short positions)."""

    # sets buying power to user's cash
    new_val = float(wallet_amts[0])
    liabilities = 0
    assets = 0
    for idx, amt in enumerate(wallet_amts[1:]):
        cur_val = atof(wallet_dialog.pos_view_gb.pos_view.item(idx, 2).text()[1:])
        amt = float(amt)
        if amt > 0:
            new_val += cur_val * amt
            assets += cur_val * amt
        elif amt < 0:
            new_val -= cur_val * amt
            liabilites += cur_val * amt

    buying_power = get_wallet_bp()
    wallet_dialog.nav_gb.liq.setText(f'${new_val:0,.2f}')

    wallet_dialog.nav_gb.bp.setText(f'${buying_power:0,.2f}')

    wallet_dialog.nav_gb.cash.setText(f'${wallet_cash:0,.2f}')

    wallet_dialog.nav_gb.assets.setText(f'${assets:0,.2f}')

    wallet_dialog.nav_gb.liabilities.setText(f'${liabilities:0,.2f}')

    wallet_dialog.nav_gb.returnSinceInception.setText(f'{((new_val / 10000 - 1) * 100):0,.2f}%')


def get_portfolio_bp() -> float:
    """
    Returns the user's portfolio buying power.
    Calculated as cash + (long assets * 0.5) - (short assets * 1.5)
    """
    buying_power = portfolio_cash
    total_long = 0
    total_short = 0

    for idx, amt in enumerate(portfolio_amts[1:]):
        cur_val = float(port_dialog.pos_view_gb.pos_view.item(idx, 2).text()[1:])
        amt = int(amt)
        if amt > 0:
            total_long += cur_val * amt
        elif amt < 0:
            total_short += cur_val * amt

    buying_power += .5 * total_long
    buying_power += 1.5 * total_short
    return buying_power


def get_wallet_bp() -> float:
    """
    Returns the user's wallet buying power.
    Calculated as cash * 10
    """
    return wallet_cash * 10


def apply_settings_changes():
    """Updates assets/settings.xml with the currently selected settings in the GUI"""
    # gets currently selected settings
    color_up = settings_dialog.up_color_combobox.currentText()
    color_down = settings_dialog.down_color_combobox.currentText()
    style = settings_dialog.chart_style_combobox.currentText()

    # parses XML file into an ElementTree
    tree = et.parse('assets/settings.xml')


    # replaces old data in the file with the current data
    for color in tree.getroot().iter('upcolor'):
        color.text = color_up

    for color in tree.getroot().iter('downcolor'):
        color.text = color_down

    for chart_style in tree.getroot().iter('basestyle'):
        chart_style.text = style

    tree.write('assets/settings.xml')


def stockinfo_searchbar_click():
    """
    Initiates the retrieval and display of stock information when the searchbar button
    is pressed
    """
    global TAB2_ISLOADED
    global TAB3_ISLOADED
    TAB2_ISLOADED = False
    TAB3_ISLOADED = False

    ticker = stockinfo_main.searchbar_gb.searchBar.text().split(' ')[0]
    yq_ticker = yq.Ticker(ticker)

    if yq_ticker.quote_type[ticker]['quoteType'] == 'ETF':
        stockinfo_dialog.setTabEnabled(1, False)
        stockinfo_dialog.setTabEnabled(2, False)
        stockinfo_dialog.setTabEnabled(3, False)
        setup_etf_info(yq_ticker, ticker)
    elif yq_ticker.quote_type[ticker]['quoteType'] == 'EQUITY':
        stockinfo_dialog.setTabEnabled(1, True)
        stockinfo_dialog.setTabEnabled(2, True)
        stockinfo_dialog.setTabEnabled(3, True)
        setup_stock_info(yq_ticker, ticker)


def get_etf_weights(ticker_info: pd.DataFrame) -> dict:
    """
    Creates a dictionary with sector names as keys and sector
    weights as values from the given ticker information dataframe,
    obtained from a call to yq.Ticker('name').fund_sector_weightings
    """

    return {
        "Real Estate" : ticker_info.iloc[0],
        "Consumer Cyclicals" : ticker_info.iloc[1],
        "Basic Materials" : ticker_info.iloc[2],
        "Consumer Defensives" : ticker_info.iloc[3],
        "Technology" : ticker_info.iloc[4],
        "Communication Services" : ticker_info.iloc[5],
        "Financial Services" : ticker_info.iloc[6],
        "Utilities" : ticker_info.iloc[7],
        "Industrials" : ticker_info.iloc[8],
        "Energy" : ticker_info.iloc[9],
        "Healthcare" : ticker_info.iloc[10]
    }


def clear_layout(layout: QVBoxLayout):
    """
    Removes all child widgets from the given layout
    """
    for idx in reversed(range(layout.count())):
        layout.itemAt(idx).widget().setParent(None)


def setup_etf_info(ticker: yq.Ticker, name: str):
    """
    Populates the stock information dialog with the given ETF's info
    """
    ticker_data = ticker.all_modules

    price_data = ticker_data[name]['price']
    fund_profile = ticker_data[name]['fundProfile']
    quote_type = ticker_data[name]['quoteType']
    summary_detail = ticker_data[name]['summaryDetail']
    asset_profile = ticker_data[name]['assetProfile']
    key_stats = ticker_data[name]['defaultKeyStatistics']
    fund_performance = ticker.fund_performance[name]['trailingReturns']
    etf_weights = get_etf_weights(ticker.fund_sector_weightings)
    ticker_news = fn.get_finviz_news(name)


    stockinfo_main.about_groupbox.setVisible(True)
    stockinfo_main.asset_info_gb.setVisible(True)
    stockinfo_main.news_groupbox.setVisible(True)


    full_name_label = QLabel(f"Full Name: {price_data['longName']}")

    category_label = QLabel(f"Category: {fund_profile['categoryName']}")

    exchange_label = QLabel(f"Exchange: {quote_type['exchange']}")

    total_assets_label = QLabel(f"Total Assets: {summary_detail['totalAssets']}")


    description_label = QLabel("Description: " + asset_profile['longBusinessSummary'])
    description_label.setWordWrap(True)

    inception_label = QLabel(f"Date of Inception: {key_stats['fundInceptionDate']}")

    more_info_label = QLabel("Hover over a slice of the pie chart for more information")
    more_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)


    weights_piechart = QPieSeries()

    for index, (sector, weight) in enumerate(etf_weights.items()):
        weights_piechart.append(sector, index + 1)
        weights_piechart.slices()[index].setValue(weight * 100)
        weights_piechart.slices()[index].setLabelVisible(True)
        weights_piechart.slices()[index].setLabelFont(QFont('arial', 8))

    def on_slice_hover(idx, state):
        _slice = weights_piechart.slices()[idx]
        _slice.setExploded(state)
        border_width = 2 if state else 0
        _slice.setBorderWidth(border_width)
        _slice.setBorderColor(QColor('black'))
        more_info_label.setText(f'{_slice.label()} - {_slice.value()}%')

    weights_chart = QChart()
    weights_chart.addSeries(weights_piechart)
    weights_chart.setTitle(f"{name} Holdings by Sector")
    weights_chart.setVisible(True)

    weights_chartview = QChartView(weights_chart)
    weights_piechart.slices()[0].hovered.connect(lambda state: on_slice_hover(0, state))
    weights_piechart.slices()[1].hovered.connect(lambda state: on_slice_hover(1, state))
    weights_piechart.slices()[2].hovered.connect(lambda state: on_slice_hover(2, state))
    weights_piechart.slices()[3].hovered.connect(lambda state: on_slice_hover(3, state))
    weights_piechart.slices()[4].hovered.connect(lambda state: on_slice_hover(4, state))
    weights_piechart.slices()[5].hovered.connect(lambda state: on_slice_hover(5, state))
    weights_piechart.slices()[6].hovered.connect(lambda state: on_slice_hover(6, state))
    weights_piechart.slices()[7].hovered.connect(lambda state: on_slice_hover(7, state))
    weights_piechart.slices()[8].hovered.connect(lambda state: on_slice_hover(8, state))
    weights_piechart.slices()[9].hovered.connect(lambda state: on_slice_hover(9, state))
    weights_piechart.slices()[10].hovered.connect(lambda state: on_slice_hover(10, state))


    current_price_label = QLabel(f"Current Price: {price_data['regularMarketPrice']}")
    open_price_label = QLabel(f"\tOpen: {price_data['regularMarketOpen']}")
    high_price_label = QLabel(f"\tHigh: {price_data['regularMarketDayHigh']}")
    low_price_label = QLabel(f"\tLow: {price_data['regularMarketDayLow']}")
    close_price_label = QLabel(f"\tLast Close: {summary_detail['regularMarketPreviousClose']}")
    nav_price_label = QLabel(f"NAV Price: {summary_detail['navPrice']}")

    bid_label = QLabel(f"Bid: {summary_detail['bid']} ({summary_detail['bidSize']})")
    ask_label = QLabel(f"Ask: {summary_detail['ask']} ({summary_detail['askSize']})")

    volume_label = QLabel(f"Volume: {summary_detail['regularMarketVolume']}")
    avg_volume_label = QLabel(f"Average Volume (10d): {summary_detail['averageVolume10days']}")
    long_avg_volume_label = QLabel(f"Average Volume (1M): {summary_detail['averageVolume']} ")

    year_high_label = QLabel(f"52 Week High: {summary_detail['fiftyTwoWeekHigh']}")
    year_low_label = QLabel(f"52 Week Low: {summary_detail['fiftyTwoWeekLow']}")

    averages_label = QLabel("Price Averages: ")
    fifty_avg_label = QLabel(f"\t50d MA: {summary_detail['fiftyDayAverage']}")
    twohundred_avg_label = QLabel(f"\t200d MA: {summary_detail['twoHundredDayAverage']}")

    threeyr_cagr_label = QLabel(
        f"Three-Year CAGR: {fund_performance['threeYear'] * 100}% per annum")
    fiveyr_cagr_label = QLabel(f"Five-Year CAGR: {fund_performance['fiveYear'] * 100}% per annum")

    try:
        dividend_label = QLabel(
            f"Trailing Dividend Yield: {summary_detail['trailingAnnualDividendYield'] * 100}%"
        )
    except KeyError:  # ETF does not pay a dividend
        dividend_label = QLabel("Trailing Annual Dividend Yield: 0% per annum")

    try:
        dividend_rate_label = QLabel(
            f"Trailing Dividend Rate: ${summary_detail['trailingAnnualDividendRate']}"
        )
    except KeyError:
        dividend_rate_label = QLabel("Trailing Annual Dividend Rate: $0.00")

    beta_3y_label = QLabel(f"3-Year Beta (Relative to SPY): {key_stats['beta3Year']}")


    clear_layout(about_scrollarea_widget.layout())
    clear_layout(assetinfo_scrollarea_widget.layout())
    clear_layout(stockinfo_main.news_groupbox.layout())

    for news_item in ticker_news:
        news_label = QLabel(f"""
            <a href=\"{news_item['link']}\">
                <font face=verdana size=1 color=black> {news_item['title']}</font>
            </a>
            <br>
            <a>{news_item['source']}
            <br> {news_item['dateTime']}
            </a>
        """)
        news_label.setOpenExternalLinks(True)
        news_label.setStyleSheet("""QToolTip {
                           font-size: 12px
                           }""")
        news_label.setToolTip(news_item['link'])
        stockinfo_main.news_groupbox.layout().addWidget(news_label)

    about_scrollarea_widget.layout().addWidget(full_name_label)
    about_scrollarea_widget.layout().addWidget(category_label)
    about_scrollarea_widget.layout().addWidget(exchange_label)
    about_scrollarea_widget.layout().addWidget(total_assets_label)
    about_scrollarea_widget.layout().addWidget(inception_label)
    about_scrollarea_widget.layout().addWidget(description_label)
    about_scrollarea_widget.layout().addWidget(weights_chartview)
    about_scrollarea_widget.layout().addWidget(more_info_label)

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
    assetinfo_scrollarea_widget.layout().addWidget(threeyr_cagr_label)
    assetinfo_scrollarea_widget.layout().addWidget(fiveyr_cagr_label)
    assetinfo_scrollarea_widget.layout().addWidget(dividend_label)
    assetinfo_scrollarea_widget.layout().addWidget(dividend_rate_label)
    assetinfo_scrollarea_widget.layout().addWidget(beta_3y_label)


def setup_stock_info(ticker: yq.Ticker, name: str):
    """
    Populates the stock information dialog with the given stock's info
    """
    ticker_data = ticker.all_modules
    ticker_news = fn.get_finviz_news(name)

    price_data = ticker_data[name]['price']
    asset_profile = ticker_data[name]['assetProfile']
    summary_detail = ticker_data[name]['summaryDetail']

    stockinfo_main.about_groupbox.setVisible(True)
    stockinfo_main.asset_info_gb.setVisible(True)
    stockinfo_main.news_groupbox.setVisible(True)
    stockinfo_recs.analyst_rec_groupbox.setVisible(True)
    stockinfo_recs.iandi_groupbox.setVisible(True)
    stockinfo_recs.mutfund_groupbox.setVisible(True)

    full_name_label = QLabel(f"Full Name: {price_data['longName']}")

    sector_label = QLabel(f"Sector: {asset_profile['sector']}: {asset_profile['industry']}")

    country_label = QLabel(f"Country: {asset_profile['country']}")

    description_label = QLabel("Description: " + asset_profile['longBusinessSummary'])

    description_label.setWordWrap(True)

    location_label = QLabel(f"Location: {asset_profile['city']}, {asset_profile['state']}")

    website_label = QLabel(
        f"Website: <a href=\"{asset_profile['website']}\"> {asset_profile['website']} </a>")

    current_price_label = QLabel(f"Current Price: {price_data['regularMarketPrice']}")
    open_price_label = QLabel(f"\tOpen: {price_data['regularMarketOpen']}")
    high_price_label = QLabel(f"\tHigh: {price_data['regularMarketDayHigh']}")
    low_price_label = QLabel(f"\tLow: {price_data['regularMarketDayLow']}")
    close_price_label = QLabel(f"\tLast Close: {price_data['regularMarketPreviousClose']}")

    bid_label = QLabel(f"Bid: {summary_detail['bid']} ({summary_detail['bidSize']})")
    ask_label = QLabel(f"Ask: {summary_detail['ask']} ({summary_detail['askSize']})")

    volume_label = QLabel(f"Volume: {price_data['regularMarketVolume']}")
    avg_volume_label = QLabel(f"Average Volume (10d): {summary_detail['averageVolume10days']}")
    long_avg_volume_label = QLabel(f"Average Volume (3M): {summary_detail['averageVolume']} ")

    year_high_label = QLabel(f"52 Week High: {summary_detail['fiftyTwoWeekHigh']}")
    year_low_label = QLabel(f"52 Week Low: {summary_detail['fiftyTwoWeekLow']}")

    averages_label = QLabel("Price Averages: ")
    fifty_avg_label = QLabel(f"\t50d MA: {summary_detail['fiftyDayAverage']}")
    twohundred_avg_label = QLabel(f"\t200d MA: {summary_detail['twoHundredDayAverage']}")


    clear_layout(about_scrollarea_widget.layout())
    clear_layout(assetinfo_scrollarea_widget.layout())
    clear_layout(stockinfo_main.news_groupbox.layout())
    clear_layout(stockinfo_recs.analyst_rec_groupbox.layout())
    clear_layout(stockinfo_recs.iandi_groupbox.layout())
    clear_layout(stockinfo_recs.mutfund_groupbox.layout())

    for news_item in ticker_news:
        news_label = QLabel(f"""
            <a href=\"{news_item['link']}\">
                <font face=verdana size=1 color=black> {news_item['title']}</font>
            </a>
            <br>
            <a>{news_item['source']}
            <br> {news_item['dateTime']}
            </a>
        """)
        news_label.setOpenExternalLinks(True)
        news_label.setStyleSheet("""QToolTip {
                           font-size: 12px
                           }""")
        news_label.setToolTip(news_item['link'])
        stockinfo_main.news_groupbox.layout().addWidget(news_label)



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
    """
    Populates each tab in the stock information dialog when the user clicks on it
    """

    name = stockinfo_main.searchbar_gb.searchBar.text().split(' ')[0]
    ticker = yq.Ticker(name)
    ticker_data = ticker.all_modules
    global TAB2_ISLOADED
    global TAB3_ISLOADED
    global TAB4_ISLOADED

    if (tab_id == 1 and not TAB2_ISLOADED):
        ticker_recommendations = ticker_data[name]['upgradeDowngradeHistory']['history'][:9]
        ticker_instholders = ticker_data[name]['institutionOwnership']['ownershipList'][:9]
        ticker_mutfundholders = ticker_data[name]['fundOwnership']['ownershipList'][:9]

        for recommendation in ticker_recommendations:
            txt = f"""
            {recommendation['firm']}: {recommendation['toGrade']} <br>
            {recommendation['epochGradeDate']}
            """
            stockinfo_recs.analyst_rec_groupbox.layout().addWidget(QLabel(txt))

        for instholder in ticker_instholders:
            txt = f"""
            {instholder['organization']}: {instholder['position']} shares ({instholder['pctHeld'] * 100}%) <br>
            {instholder['reportDate']}
            """
            stockinfo_recs.iandi_groupbox.layout().addWidget(QLabel(txt))

        for mutfund in ticker_mutfundholders:
            txt = f"""
            {mutfund['organization']}: {mutfund['position']} shares ({mutfund['pctHeld'] * 100}%) <br>
            {mutfund['reportDate']}
            """
            stockinfo_recs.mutfund_groupbox.layout().addWidget(QLabel(txt))

        TAB2_ISLOADED = True

    elif (tab_id == 2 and not TAB3_ISLOADED):
        ticker_pts = ticker_data[name]['financialData']
        ticker_hist = ticker.history(period="2y", interval="1wk")
        ticker_qtr_earnings = ticker_data[name]['earningsHistory']['history']
        ticker_qtr_rev = ticker_data[name]['earnings']['financialsChart']['quarterly']
        ticker_yr_earnings_rev = ticker_data[name]['earnings']['financialsChart']['yearly']

        ptchart.removeAxis(ptchart.axes(Qt.Orientation.Horizontal)[0])
        ptchart.removeAxis(ptchart.axes(Qt.Orientation.Vertical)[0])

        ptchart.removeAllSeries()

        series = QLineSeries()

        series2 = QLineSeries()

        series3 = QLineSeries()

        series4 = QLineSeries()

        current_dt = float(QDateTime().currentDateTime().toMSecsSinceEpoch())
        prediction_date = QDateTime().currentDateTime().addYears(1).toMSecsSinceEpoch()
        date_format = "yyyy-MM-dd hh:mm:ss"
        for idx, close in enumerate(ticker_hist.loc[:, 'adjclose']):
            price_dt = QDateTime().fromString(str(ticker_hist.index[idx][1])[0:19], date_format)

            series.append(float(price_dt.toMSecsSinceEpoch()), close)

        series.append(float(prediction_date), ticker_pts['currentPrice'])
        series.setName("Current Price")
        series.setColor(QColor("blue"))

        series2.setName("Worst Case")
        series2.setColor(QColor("red"))

        series3.setName("Mean Target Price")
        series3.setColor(QColor("black"))

        series4.setName("Best Case")
        series4.setColor(QColor("green"))

        series2.append(current_dt, ticker_hist.iloc[ticker_hist.count().iloc[0] - 1][3])
        series2.append(float(prediction_date), ticker_pts['targetLowPrice'])

        series3.append(current_dt, ticker_hist.iloc[ticker_hist.count().iloc[0] - 1][3])
        series3.append(float(prediction_date), ticker_pts['targetMeanPrice'])

        series4.append(current_dt, ticker_hist.iloc[ticker_hist.count().iloc[0] - 1][3])
        series4.append(float(prediction_date), ticker_pts['targetHighPrice'])

        ptchart.addSeries(series)
        ptchart.addSeries(series2)
        ptchart.addSeries(series3)
        ptchart.addSeries(series4)

        ptchart.createDefaultAxes()
        ptchart.axes(Qt.Orientation.Horizontal)[0].hide()

        ptchart_x_axis = QDateTimeAxis()
        ptchart_x_axis.setTickCount(7)
        ptchart_x_axis.setFormat("MM-dd-yyyy")
        ptchart_x_axis.setTitleText("Date")
        ptchart_x_axis.setVisible(True)

        ptchart.addAxis(ptchart_x_axis, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(ptchart_x_axis)

        clear_layout(pt_label_container.layout())
        pt_label_container.layout().addWidget(
            QLabel(f"Current Price: {ticker_pts['currentPrice']}")
        )
        pt_label_container.layout().addWidget(
            QLabel(f"Target Low Price: {ticker_pts['targetLowPrice']}")
        )
        pt_label_container.layout().addWidget(
            QLabel(f"Target Mean Price: {ticker_pts['targetMeanPrice']}")
        )
        pt_label_container.layout().addWidget(
            QLabel(f"Target High Price: {ticker_pts['targetHighPrice']}")
        )
        pt_label_container.layout().addWidget(
            QLabel(f"Number of Analyst Opinions: {ticker_pts['numberOfAnalystOpinions']}")
        )


        qtr_earnings_chart.removeAllSeries()
        series = QBarSeries()

        actual_qtr_earnings_set = QBarSet("Actual")
        estimate_qtr_earnings_set = QBarSet("Estimate")
        earnings_trend_max = 0
        earnings_trend_min = 0

        qtr_earnings_table.setRowCount(5)
        qtr_earnings_table.setColumnCount(3)
        qtr_earnings_table.setHorizontalHeaderItem(0, QTableWidgetItem("Actual"))
        qtr_earnings_table.setHorizontalHeaderItem(1, QTableWidgetItem("Expected"))
        qtr_earnings_table.setHorizontalHeaderItem(2, QTableWidgetItem("Surprise"))
        for idx in range(qtr_earnings_table.columnCount()):
            qtr_earnings_table.horizontalHeaderItem(idx).setFont(ARIAL_10)

        for idx in range(qtr_earnings_table.rowCount()):
            qtr_earnings_table.setVerticalHeaderItem(idx, QTableWidgetItem(str(idx + 1)))
            qtr_earnings_table.verticalHeaderItem(idx).setFont(ARIAL_10)

        for idx, report in enumerate(ticker_qtr_earnings):
            reported = report['epsActual']
            actual_qtr_earnings_set.append(reported)
            if reported > earnings_trend_max:
                earnings_trend_max = reported
            if reported < earnings_trend_min:
                earnings_trend_min = reported

            estimate = report['epsEstimate']
            if estimate > earnings_trend_max:
                earnings_trend_max = estimate
            if estimate < earnings_trend_min:
                earnings_trend_min = estimate
            estimate_qtr_earnings_set.append(estimate)

            qtr_earnings_table.setItem(idx, 0, QTableWidgetItem(str(reported)))
            qtr_earnings_table.setItem(idx, 1, QTableWidgetItem(str(estimate)))
            qtr_earnings_table.setItem(idx, 2, QTableWidgetItem(str(reported - estimate)))

        series.append(actual_qtr_earnings_set)
        series.append(estimate_qtr_earnings_set)
        qtr_earnings_chart.addSeries(series)
        qtr_earnings_chart.createDefaultAxes()
        qtr_earnings_chart.axes(Qt.Orientation.Vertical)[0].setRange(
            earnings_trend_min * 1.1, earnings_trend_max * 1.1)

        qtr_revtrend_chart.removeAllSeries()
        qtr_rev_barseries = QBarSeries()
        qtr_rev_barset = QBarSet("Revenue")
        qtr_revtrend_max = 0
        qtr_revtrend_min = 0
        for rev in ticker_qtr_rev:
            revenue = rev['revenue']
            qtr_rev_barset.append(float(revenue))
            if revenue > qtr_revtrend_max:
                qtr_revtrend_max = revenue
            if revenue < qtr_revtrend_min:
                qtr_revtrend_min = revenue
            qtr_revtrend_label_container.layout().addWidget(QLabel(f"{rev['date']}: {revenue}"))

        qtr_rev_barseries.append(qtr_rev_barset)

        qtr_revtrend_chart.addSeries(qtr_rev_barseries)
        qtr_revtrend_chart.createDefaultAxes()
        qtr_revtrend_chart.axes(Qt.Orientation.Vertical)[0].setRange(
            qtr_revtrend_min * 1.1, qtr_revtrend_max * 1.1)

        yr_earnings_chart.removeAllSeries()
        clear_layout(yr_earnings_label_container.layout())
        yr_er_barseries = QBarSeries()
        yr_er_barset = QBarSet("Earnings")
        yr_eps_max = 0
        yr_eps_min = 0

        for report in ticker_yr_earnings_rev:
            earnings = float(report['earnings'])
            if earnings > yr_eps_max:
                yr_eps_max = earnings
            if earnings < yr_eps_min:
                yr_eps_min = earnings
            yr_er_barset.append(earnings)
            yr_earnings_label_container.layout().addWidget(
                QLabel(f"{report['date']}: {earnings}"))

        yr_er_barseries.append(yr_er_barset)
        yr_earnings_chart.addSeries(yr_er_barseries)
        yr_earnings_chart.createDefaultAxes()
        yr_earnings_chart.axes(Qt.Orientation.Vertical)[0].setRange(
            yr_eps_min * 1.1, yr_eps_max * 1.1)

        yr_revtrend_chart.removeAllSeries()
        clear_layout(yr_revtrend_label_container.layout())
        year_rev_series = QBarSeries()
        year_rev_set = QBarSet("Revenue")

        yr_revtrend_max = 0
        yr_revtrend_min = 0
        for report in ticker_yr_earnings_rev:
            rev = float(report['revenue'])
            year_rev_set.append(rev)
            yr_revtrend_max = rev if rev > yr_revtrend_max else yr_revtrend_max
            yr_revtrend_min = rev if rev < yr_revtrend_min else yr_revtrend_min
            yr_revtrend_label_container.layout().addWidget(
                QLabel(f"{report['date']}: {rev}"))

        year_rev_set.setPen(QColor("green"))

        year_rev_series.append(year_rev_set)

        yr_revtrend_chart.addSeries(year_rev_series)
        yr_revtrend_chart.createDefaultAxes()
        yr_revtrend_chart.axes(Qt.Orientation.Vertical)[0].setRange(
            yr_revtrend_min * 1.1, yr_revtrend_max * 1.1)

        TAB3_ISLOADED = True

    elif (tab_id == 3 and not TAB4_ISLOADED):
        ticker_financials = ticker.all_financial_data()
        financials_table.setRowCount(ticker_financials.columns.size)
        financials_table.setColumnCount(5)
        for idx in range(4):
            tw_item = QTableWidgetItem(str(ticker_financials.iloc[idx][0])[:10])
            financials_table.setHorizontalHeaderItem(idx, tw_item)
            financials_table.horizontalHeaderItem(idx).setFont(ARIAL_10)

        for idx in range(4):
            for j in range(3, ticker_financials.iloc[0].size):
                current_data = float(ticker_financials.iloc[idx][j])
                if current_data > 1000:
                    formatted_data = nf.simplify(current_data, True)
                    financials_table.setItem(j, idx, QTableWidgetItem(formatted_data))
                elif current_data < -1000:
                    formatted_data = nf.simplify(abs(current_data), True)
                    financials_table.setItem(j, idx, QTableWidgetItem(f"-{formatted_data}"))
                else:
                    financials_table.setItem(j, idx, QTableWidgetItem(str(current_data)))

        checkboxes = QButtonGroup()

        for idx in range(ticker_financials.iloc[0].size):

            checkbox = QCheckBox()
            checkboxes.addButton(checkbox)
            item = QTableWidgetItem(ticker_financials.columns[idx])
            financials_table.setVerticalHeaderItem(idx, item)
            financials_table.verticalHeaderItem(idx).setFont(ARIAL_10)
            checkbox.clicked.connect(on_financials_checkbox_click)

            financials_table.setCellWidget(idx, 4, checkbox)
        TAB4_ISLOADED = True


def on_financials_checkbox_click():
    """
    Adds the financial data from the checkbox's row to the chart in the financials
    tab of the stockinfo dialog when selected
    """

    financials_chart.removeAllSeries()
    series = QBarSeries()
    for outer in range(financials_table.rowCount()):
        box = financials_table.cellWidget(i, 4)
        if box.isChecked():
            financials_set = QBarSet(financials_table.verticalHeaderItem(outer).text())
            for inner in range(4):
                val = financials_table.item(outer, inner).text()
                last_char = val[-1]
                match last_char:
                    case 'k':
                        financials_set.append(float(val[:-1]) * 10**3)
                    case 'M':
                        financials_set.append(float(val[:-1]) * 10**6)
                    case 'B':
                        financials_set.append(float(val[:-1]) * 10**9)
                    case 'T':
                        financials_set.append(float(val[:-1]) * 10**12)
                    case _:
                        financials_set.append(float(val))
            series.append(financials_set)

    financials_chart.addSeries(series)
    financials_chart.createDefaultAxes()


def dcf_findstock_button_click():
    """
    Populates the DCF dialog with default settings for the stock the user
    searched for
    """

    global CURRENT_TICKER
    ticker = dcf_dialog.searchbar_gb.searchBar.text().split(' ')[0]
    CURRENT_TICKER = ticker

    input_info = dcf.parse(ticker)
    dcf_dialog.inputs_gb.setVisible(True)
    dcf_dialog.inputs_gb.company_label.setText(f"Company: {input_info['company_name']}")
    mkt_price = input_info['mp']
    dcf_dialog.inputs_gb.mkt_price.setText(f"${mkt_price:0,.2f}")

    dcf_dialog.inputs_gb.eps.setText(str(input_info['eps']))

    dcf_dialog.inputs_gb.growth.setText(f"{input_info['ge']}")

    dcf_dialog.inputs_gb.growth_slider.setValue(input_info['ge'] * 100)

    dcf_dialog.inputs_gb.discount_rate.setText(
        f"{dcf_dialog.inputs_gb.discount_rate_slider.value() / 100.0}%"
    )


    dcf_dialog.inputs_gb.perpetual_rate.setText(
        f"{dcf_dialog.inputs_gb.perpetual_rate_slider.value() / 100.0}%"
    )

    dcf_dialog.inputs_gb.last_fcf.setText(nf.simplify(input_info['fcf'], True))

    dcf_dialog.inputs_gb.shares.setText(nf.simplify(input_info['shares'], True))


def growth_slider_moved():
    """
    Changes the text on the growth factor label to reflect the new value of the growth
    factor slider when it is moved
    """
    dcf_dialog.inputs_gb.growth.setText(f"{dcf_dialog.inputs_gb.growth_slider.value() / 100.0}%")


def term_slider_moved():
    """
    Changes the text on the term label to reflect the new value of the term slider when
    it is moved
    """
    dcf_dialog.inputs_gb.term.setText(f"{dcf_dialog.inputs_gb.term_slider.value()} years")


def discount_slider_moved():
    """
    Changes the text on the discount rate label to reflect the new value of the discount
    rate slider when it is moved
    """
    dcf_dialog.inputs_gb.discount_rate.setText(
        f"{dcf_dialog.inputs_gb.discount_rate_slider.value() / 100.0}%"
    )


def perpetual_slider_moved():
    """
    Changes the text on the perpetual rate label to reflect the new value of the perpetual
    rate slider when it is moved
    """
    dcf_dialog.inputs_gb.perpetual_rate.setText(
        f"{dcf_dialog.inputs_gb.perpetual_rate_slider.value() / 100.0}%"
    )


def dcf_getanalysis_button_click():
    """
    Populates the right side of the DCF dialog with the report from the DCF module when
    the "Get Analysis" button is pressed.
    """

    discount_rate = dcf_dialog.inputs_gb.discount_rate_slider.value() / 100.0
    perp_rate = dcf_dialog.inputs_gb.perpetual_rate_slider.value() / 100.0
    growth_estimate = dcf_dialog.inputs_gb.growth_slider.value() / 100.0
    term = dcf_dialog.inputs_gb.term_slider.value()
    eps = float(dcf_dialog.inputs_gb.eps.text())
    dcf_analysis = dcf.get_fairval(
        CURRENT_TICKER, discount_rate, perp_rate, growth_estimate, term, eps
    )

    future_cashflows_chartview.setVisible(True)

    future_cashflows_chart.removeAllSeries()
    future_cashflows_series = QLineSeries()
    future_cashflows_series.setName("Forecasted Cash Flows")
    future_cashflows_pv_lineseries = QLineSeries()
    future_cashflows_pv_lineseries.setName(
        "Present Value of Forecasted Cash Flows")
    current_year = QDateTime().currentDateTime().date().year()


    dcf_zip = zip(
        dcf_analysis['forecasted_cash_flows'][:-1], dcf_analysis['cashflow_present_values'][:-1]
    )

    for idx, (fcf, present_val) in enumerate(dcf_zip):
        future_cashflows_series.append(current_year + idx, fcf)
        future_cashflows_pv_lineseries.append(current_year + idx, present_val)

    future_cashflows_chart.addSeries(future_cashflows_series)
    future_cashflows_chart.addSeries(future_cashflows_pv_lineseries)

    future_cashflows_chart.createDefaultAxes()
    future_cashflows_chart.axes(Qt.Orientation.Horizontal)[
        0].setTickCount(term)

    upside = round((dcf_analysis['fair_value'] / dcf_analysis['mp'] - 1) * 100, 2)
    dcf_dialog.outputs_gb.basic_gb.fair_value.setText(
        f"${round(dcf_analysis['fair_value'], 2)} ({upside}%)"
    )

    upside = round(
        (dcf_analysis['graham_expected_value'] / dcf_analysis['mp'] - 1) * 100, 2)
    dcf_dialog.outputs_gb.graham_gb.ev.setText(
        f"${round(dcf_analysis['graham_expected_value'], 2)} ({upside}%)"
    )

    dcf_dialog.outputs_gb.graham_gb.graham_growth_estimate.setText(
        f"{round(dcf_analysis['graham_growth_estimate'], 2)}% per annum"
    )


def change_indicator_panel(indicator_fn: str, value: int, args: list):
    """
    Changes the given indicator's panel (where it appears on the chart). Should
    be called whenever an indicator's panel combobox is changed.
    """
    for indicator in selected_ta:
        if indicator[0] == indicator_fn:
            index = selected_ta.index(indicator)
            new_tup = (indicator_fn, int(value))
            new_tup += (args, )
            selected_ta[index] = new_tup


def get_indicator_index(indicator_fn: str) -> int:
    """
    Takes an indicator as a string and returns its index in the TA list
    """
    for indicator in selected_ta:
        if indicator[0] == indicator_fn:
            return selected_ta.index(indicator)
    raise ValueError(f"Indicator '{str}' is not in the list of TA")


def close_event():
    """
    Saves currently open trades and the state of the portfolio to trades.xml and portfolio.xml
    """
    st.save(OPEN_ORDERS)
    sp.save_port(portfolio_asset_types, portfolio_tickers, portfolio_amts, purchase_prices)


app.aboutToQuit.connect(close_event)
widget = QTabWidget()
widget.setWindowTitle("Paper Trading Game")
splash = QSplashScreen(QPixmap(f"{CWD}splashscreen-images/splash.png"))
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

up_color = ra.get_xml_data(r'assets\settings.xml', 'upcolor')
down_color = ra.get_xml_data(r'assets\settings.xml', 'downcolor')
base_style = ra.get_xml_data(r'assets\settings.xml', 'basestyle')
portfolio_tickers = [ticker.text for ticker in ra.get_xml_data(r'assets\portfolio.xml', 'name')]
portfolio_asset_types = [type.text for type in ra.get_xml_data(r'assets\portfolio.xml', 'type')]
portfolio_amts = [amt.text for amt in ra.get_xml_data(r'assets\portfolio.xml', 'amount')]
purchase_prices = [price.text for price in ra.get_xml_data(r'assets\portfolio.xml', 'costbasis')]
wallet_tickers = [ticker.text for ticker in ra.get_xml_data(r'assets\wallet.xml', 'name')]
wallet_amts = [amt.text for amt in ra.get_xml_data(r'assets\wallet.xml', 'amount')]
wallet_costbases = [basis.text for basis in ra.get_xml_data(r'assets\wallet.xml', 'costbasis')]
watchlist_tickers = [ticker.text for ticker in ra.get_xml_data(r'assets\watchlist.xml', 'name')]

TOKEN_OBJECTS = [yq.Ticker(symbol) for symbol in wallet_tickers[1:]]
PORTFOLIO_OBJECTS = [yq.Ticker(symbol) for symbol in portfolio_tickers[1:]]
WATCHLIST_OBJECTS = [yq.Ticker(symbol) for symbol in watchlist_tickers]

trades = ra.get_xml_data(r'assets\trades.xml', 'trade')

for trade in trades:
    trade_list_item = [trade.contents[1].text, trade.contents[3].text, trade.contents[5].text,
                       trade.contents[7].text, trade.contents[9].text]

    OPEN_ORDERS.append(trade_list_item)

    ticker_obj = yq.Ticker(trade.contents[1].text)
    prices_frame = ticker_obj.history(
        interval='1m',
        start=datetime.strptime(trade.contents[11].text, '%Y-%m-%d %H:%M:%S.%f'),
        end=datetime.now()
    )
    cash = float(portfolio_amts[0])


    asset_class = ""
    match ticker_obj.quote_type[trade.contents[1].text]['quoteType']:
        case 'EQUITY':
            asset_class = 'Stock'
        case 'ETF':
            asset_class = 'ETF'

    trade_price = float(trade.contents[7].text)
    if trade.contents[3].text == 'Buy' and trade.contents[5].text == 'Limit':
        for row in prices_frame.iterrows():
            if row[1].iloc[3] < trade_price:
                execute_buy(trade_list_item, ticker_obj, asset_class, cash, trade_price)
                break
    elif trade.contents[3].text == 'Sell' and trade.contents[5].text == 'Limit':
        for row in prices_frame.iterrows():
            if row[1].iloc[2] > trade_price:
                execute_sell(trade_list_item, ticker_obj, asset_class, cash, trade_price)
                break
    elif trade.contents[3].text == 'Buy' and trade.contents[5].text == 'Stop':
        for row in prices_frame.iterrows():
            if row[1].iloc[2] > trade_price:
                execute_buy(trade_list_item, ticker_obj, asset_class, cash, trade_price)
                break
    elif trade.contents[3].text == 'Sell' and trade.contents[5].text == 'Stop':
        for row in prices_frame.iterrows():
            if row[1].iloc[3] < trade_price:
                execute_sell(trade_list_item, ticker_obj, asset_class, cash, trade_price)
                break
    elif trade.contents[3].text == 'Buy' and trade.contents[5].text == 'Market':
        if prices_frame.size > 1:
            execute_buy(trade_list_item, ticker_obj, asset_class, cash, trade_price)
            break
    elif trade.contents[3].text == 'Sell' and trade.contents[5].text == 'Market':
        if prices_frame.size > 1:
            execute_sell(trade_list_item, ticker_obj, asset_class, cash, trade_price)
            break



TAB2_ISLOADED = False
TAB3_ISLOADED = False
TAB4_ISLOADED = False

all_tickers_list = pd.read_csv(CWD + r"assets\stock_list.csv")['Symbol'].tolist()
all_names_list = pd.read_csv(CWD + r"assets\stock_list.csv")['Name'].tolist()

all_tickers_list[5023] = 'NAN'

tickers_names_zip = zip(all_tickers_list, all_names_list)
all_tickers_list = [f"{ticker} - {name}" for (ticker, name) in tickers_names_zip]

# set user's NAV equal to cash first, then iterate through stocks,
# find their current price, and add their values to user's NAV
portfolio_nav = float(portfolio_amts[0])
portfolio_cash = float(portfolio_amts[0])

for port_ticker, port_amt in zip(portfolio_tickers[1:], portfolio_amts[1:]):
    price = yq.Ticker(port_ticker).history(period='5d').iloc[4][3]
    portfolio_nav += float(price) * int(port_amt)

wallet_nav = float(wallet_amts[0])
wallet_cash = float(wallet_amts[0])
for wallet_ticker, wallet_amt in zip(wallet_tickers[1:], wallet_amts[1:]):
    price = yq.Ticker(wallet_ticker).history('5d').iloc[-1][5]
    wallet_nav += float(price) * float(wallet_amt)

# add genius font to database
QFontDatabase.addApplicationFont('fonts/genius.ttf')
progressBar.setValue(50)


####################
# portfolio dialog #
####################

# dialog settings
port_dialog = QWidget()
port_dialog.setObjectName("Dialog")
port_dialog.resize(1000, 600)
port_dialog.setAutoFillBackground(True)
port_dialog.setStyleSheet('background-color: deepskyblue;')

# positions table settings
port_dialog.pos_view_gb = QGroupBox(port_dialog)
port_dialog.pos_view_gb.setGeometry(10, 300, 900, 250)
port_dialog.pos_view_gb.setTitle("Your Portfolio")
port_dialog.pos_view_gb.setStyleSheet('background-color: white;')

port_dialog.pos_view_gb.pos_view = QTableWidget(port_dialog.pos_view_gb)
port_dialog.pos_view_gb.pos_view.setEditTriggers(
    QAbstractItemView.EditTrigger.NoEditTriggers)
port_dialog.pos_view_gb.pos_view.setFont(ARIAL_10)
port_dialog.pos_view_gb.pos_view.setRowCount(len(portfolio_amts) - 1)
port_dialog.pos_view_gb.pos_view.setColumnCount(8)
port_dialog.pos_view_gb.pos_view.setGeometry(10, 20, 850, 200)
port_dialog.pos_view_gb.pos_view.setStyleSheet('background-color: white;')
port_dialog.pos_view_gb.pos_view.setHorizontalHeaderItem(0, QTableWidgetItem("Ticker"))
port_dialog.pos_view_gb.pos_view.setHorizontalHeaderItem(1, QTableWidgetItem("Today's Performance"))
port_dialog.pos_view_gb.pos_view.setHorizontalHeaderItem(2, QTableWidgetItem("Current Price"))
port_dialog.pos_view_gb.pos_view.setHorizontalHeaderItem(3, QTableWidgetItem("Gain/Loss Per Share"))
port_dialog.pos_view_gb.pos_view.setHorizontalHeaderItem(4, QTableWidgetItem("Purchase Price"))
port_dialog.pos_view_gb.pos_view.setHorizontalHeaderItem(5, QTableWidgetItem("# of Shares"))
port_dialog.pos_view_gb.pos_view.setHorizontalHeaderItem(6, QTableWidgetItem("Total Value"))
port_dialog.pos_view_gb.pos_view.setHorizontalHeaderItem(7, QTableWidgetItem("Position Gain/Loss"))
for i in range(8):
    port_dialog.pos_view_gb.pos_view.horizontalHeaderItem(i).setFont(ARIAL_10)
for i in range(port_dialog.pos_view_gb.pos_view.rowCount()):
    port_dialog.pos_view_gb.pos_view.setVerticalHeaderItem(i, QTableWidgetItem("1"))
    port_dialog.pos_view_gb.pos_view.verticalHeaderItem(i).setFont(ARIAL_10)
    for j in range(port_dialog.pos_view_gb.pos_view.columnCount()):
        port_dialog.pos_view_gb.pos_view.setItem(i, j, QTableWidgetItem())
update_portfolio_table()
port_dialog.pos_view_gb.pos_view.resizeColumnsToContents()
progressBar.setValue(60)

# user's nav settings
port_dialog.nav_gb = QGroupBox(port_dialog)
port_dialog.nav_gb.setTitle("Your NAV")
port_dialog.nav_gb.setGeometry(10, 10, 250, 250)
port_dialog.nav_gb.setStyleSheet('background-color: white;')
# net liquidation value labels
port_dialog.nav_gb.netLiq = QLabel(port_dialog.nav_gb)
port_dialog.nav_gb.netLiq.setText("Net Liq: ")
port_dialog.nav_gb.netLiq.setGeometry(10, 20, 80, 20)
port_dialog.nav_gb.netLiq.setFont(QFont('genius', 10))
port_dialog.nav_gb.liq = QLabel(port_dialog.nav_gb)
port_dialog.nav_gb.liq.setGeometry(10, 40, 160, 40)
port_dialog.nav_gb.liq.setFont(QFont('genius', 20))
# cash value labels
port_dialog.nav_gb.cashLabel = QLabel(port_dialog.nav_gb)
port_dialog.nav_gb.cashLabel.setText("Cash: ")
port_dialog.nav_gb.cashLabel.setGeometry(10, 90, 80, 20)
port_dialog.nav_gb.cash = QLabel(port_dialog.nav_gb)
port_dialog.nav_gb.cash.setGeometry(100, 90, 80, 20)
progressBar.setValue(70)
# buying power labels
port_dialog.nav_gb.bp_label = QLabel(port_dialog.nav_gb)
port_dialog.nav_gb.bp_label.setText("Buying Power: ")
port_dialog.nav_gb.bp_label.setGeometry(10, 110, 80, 20)
port_dialog.nav_gb.bp = QLabel(port_dialog.nav_gb)
port_dialog.nav_gb.bp.setGeometry(100, 110, 80, 20)
# assets labels
port_dialog.nav_gb.assetsLabel = QLabel(port_dialog.nav_gb)
port_dialog.nav_gb.assetsLabel.setText("Long Assets: ")
port_dialog.nav_gb.assetsLabel.setGeometry(10, 130, 80, 20)
port_dialog.nav_gb.assets = QLabel(port_dialog.nav_gb)
port_dialog.nav_gb.assets.setGeometry(100, 130, 80, 20)
# liabilities labels
port_dialog.nav_gb.liabilitiesLabel = QLabel(port_dialog.nav_gb)
port_dialog.nav_gb.liabilitiesLabel.setText("Short Assets: ")
port_dialog.nav_gb.liabilitiesLabel.setGeometry(10, 150, 80, 20)
port_dialog.nav_gb.liabilities = QLabel(port_dialog.nav_gb)
port_dialog.nav_gb.liabilities.setGeometry(100, 150, 80, 20)
# return since inception labels
port_dialog.nav_gb.returnSinceInceptionLabel = QLabel(port_dialog.nav_gb)
port_dialog.nav_gb.returnSinceInceptionLabel.setText("Return Since Inception: ")
port_dialog.nav_gb.returnSinceInceptionLabel.setGeometry(10, 170, 120, 20)
port_dialog.nav_gb.returnSinceInception = QLabel(port_dialog.nav_gb)
port_dialog.nav_gb.returnSinceInception.setFont(QFont('genius', 20))
port_dialog.nav_gb.returnSinceInception.setGeometry(10, 190, 120, 30)
update_portfolio_nav()
progressBar.setValue(80)
# watchlist table settings
port_dialog.watchlist_gb = QGroupBox(port_dialog)
port_dialog.watchlist_gb.setTitle("Your Watchlist")
port_dialog.watchlist_gb.setGeometry(270, 10, 500, 250)
port_dialog.watchlist_gb.setStyleSheet('background-color: white;')
port_dialog.watchlist_gb.watchlist = QTableWidget(port_dialog.watchlist_gb)
port_dialog.watchlist_gb.watchlist.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
port_dialog.watchlist_gb.watchlist.setRowCount(len(watchlist_tickers))
port_dialog.watchlist_gb.watchlist.setColumnCount(4)
port_dialog.watchlist_gb.watchlist.setHorizontalHeaderItem(0, QTableWidgetItem("Ticker"))
port_dialog.watchlist_gb.watchlist.setHorizontalHeaderItem(
    1, QTableWidgetItem("Today's Performance"))
port_dialog.watchlist_gb.watchlist.setHorizontalHeaderItem(2, QTableWidgetItem("Current Price"))
port_dialog.watchlist_gb.watchlist.setHorizontalHeaderItem(
    3, QTableWidgetItem("Gain/Loss Per Share"))
for i in range(4):
    port_dialog.watchlist_gb.watchlist.horizontalHeaderItem(i).setFont(ARIAL_10)
for i in range(port_dialog.watchlist_gb.watchlist.rowCount()):
    port_dialog.watchlist_gb.watchlist.setVerticalHeaderItem(i, QTableWidgetItem(str(i + 1)))
    port_dialog.watchlist_gb.watchlist.verticalHeaderItem(i).setFont(ARIAL_10)
    for j in range(port_dialog.watchlist_gb.watchlist.columnCount()):
        port_dialog.watchlist_gb.watchlist.setItem(i, j, QTableWidgetItem())

port_dialog.watchlist_gb.watchlist.setFont(ARIAL_10)
port_dialog.watchlist_gb.watchlist.setGeometry(10, 20, 500, 200)
update_watchlist_tickers()
port_dialog.watchlist_gb.watchlist.resizeColumnsToContents()
# asset class pie chart
asset_class_chart = QPieSeries()
asset_class_chart.append("Long ETFs", 1)
asset_class_chart.append("Short ETFs", 2)
asset_class_chart.append("Long Stocks", 3)
asset_class_chart.append("Short Stocks", 4)
asset_class_chart.append("Long Options", 5)
asset_class_chart.append("Short Options", 6)
asset_class_chart.append("Cash", 7)
chart = QChart()
chart.addSeries(asset_class_chart)
chart.setTitle("Positions by Asset Class")
chart.setVisible(True)
port_dialog.chart_view = QChartView(chart)
port_dialog.chart_view.setParent(port_dialog)
port_dialog.chart_view.setGeometry(780, 2, 500, 270)
port_dialog.chart_view.setVisible(True)
update_portfolio_piechart()


################
# chart dialog #
################
progressBar.setValue(90)
chart_dialog = QTabWidget()
chart_dialog.setObjectName("Dialog")
chart_dialog.resize(1000, 600)
chart_dialog.setStyleSheet('background-color: deepskyblue;')
chart_configs = QDialog()
chart_configs.market_gb = QGroupBox(chart_configs)
chart_configs.market_gb.setTitle("Broad Market Indicies")
chart_configs.market_gb.setStyleSheet('background-color: white;')
chart_configs.market_gb.setGeometry(10, 10, 700, 50)
chart_configs.market_gb.spyButton = QPushButton(text="Chart SPY", parent=chart_configs.market_gb)
chart_configs.market_gb.spyButton.setGeometry(10, 20, 150, 20)
chart_configs.market_gb.spyButton.clicked.connect(spy_button_clicked)
chart_configs.market_gb.qqqButton = QPushButton(text="Chart QQQ", parent=chart_configs.market_gb)
chart_configs.market_gb.qqqButton.setGeometry(170, 20, 150, 20)
chart_configs.market_gb.qqqButton.clicked.connect(qqq_button_clicked)
chart_configs.market_gb.diaButton = QPushButton(text="Chart DIA", parent=chart_configs.market_gb)
chart_configs.market_gb.diaButton.setGeometry(330, 20, 150, 20)
chart_configs.market_gb.diaButton.clicked.connect(dia_button_clicked)
chart_configs.market_gb.vixButton = QPushButton(text="Chart VIX", parent=chart_configs.market_gb)
chart_configs.market_gb.vixButton.setGeometry(490, 20, 150, 20)
chart_configs.market_gb.vixButton.clicked.connect(vix_button_clicked)

# search bar for searching for a stock to chart
chart_configs.searchbar_gb = QGroupBox(chart_configs)
chart_configs.searchbar_gb.setStyleSheet('background-color: white;')
chart_configs.searchbar_gb.setTitle("Find a Stock")
chart_configs.searchbar_gb.setGeometry(10, 70, 960, 70)
chart_configs.searchbar_gb.searchBar = QLineEdit(chart_configs.searchbar_gb)
chart_configs.searchbar_gb.searchBar.setGeometry(10, 20, 850, 40)
chart_configs.searchbar_gb.searchBar.textChanged.connect(search_text_changed)
chart_configs.searchbar_gb.searchBar.setFont(ARIAL_10)
chart_configs.searchbar_gb.search_button = QPushButton(chart_configs.searchbar_gb)
chart_configs.searchbar_gb.search_button.setGeometry(870, 20, 80, 40)
chart_configs.searchbar_gb.search_button.setText("Chart")
chart_configs.searchbar_gb.search_button.setEnabled(False)
chart_configs.searchbar_gb.search_button.clicked.connect(search_button_clicked)
chart_configs.settings_gb = QGroupBox(chart_configs)
chart_configs.settings_gb.setStyleSheet('background-color: white;')
chart_configs.settings_gb.setGeometry(10, 150, 1280, 600)
chart_configs.settings_gb.setTitle("Chart Settings")
periods = ["1d", "5d", "1mo", "3mo", "6mo","1y", "2y", "5y", "10y", "ytd", "max"]
timeframes = ["1m", "2m", "5m", "15m", "30m", "60m","90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"]
chart_configs.settings_gb.period_radiobutton = QRadioButton(chart_configs.settings_gb)
chart_configs.settings_gb.period_radiobutton.setText("Chart by Period")
chart_configs.settings_gb.period_radiobutton.setGeometry(10, 50, 100, 30)
chart_configs.settings_gb.period_radiobutton.setChecked(True)
chart_configs.settings_gb.period_radiobutton.clicked.connect(period_radiobutton_clicked)
chart_configs.settings_gb.daterange_radiobutton = QRadioButton(chart_configs.settings_gb)
chart_configs.settings_gb.daterange_radiobutton.setText("Chart by Date Range")
chart_configs.settings_gb.daterange_radiobutton.setGeometry(10, 100, 170, 30)
chart_configs.settings_gb.daterange_radiobutton.clicked.connect(daterange_radiobutton_clicked)
chart_configs.settings_gb.data_period_combobox = QComboBox(chart_configs.settings_gb)
chart_configs.settings_gb.data_period_combobox.addItems(periods)
chart_configs.settings_gb.data_period_combobox.setGeometry(120, 60, 50, 20)
chart_configs.settings_gb.data_timeframe_combobox = QComboBox(chart_configs.settings_gb)
chart_configs.settings_gb.data_timeframe_combobox.addItems(timeframes)
chart_configs.settings_gb.data_timeframe_combobox.setGeometry(850, 50, 50, 30)
chart_configs.settings_gb.prepost_checkbox = QCheckBox(chart_configs.settings_gb)
chart_configs.settings_gb.prepost_checkbox.setText("Include Pre/Post Market Data")
chart_configs.settings_gb.prepost_checkbox.setGeometry(10, 20, 180, 30)
chart_configs.settings_gb.split_dividend_checkbox = QCheckBox(chart_configs.settings_gb)
chart_configs.settings_gb.split_dividend_checkbox.setText("Show Split and Dividend Actions")
chart_configs.settings_gb.split_dividend_checkbox.setGeometry(200, 20, 190, 30)
chart_configs.settings_gb.adjust_ohlc_checkbox = QCheckBox(chart_configs.settings_gb)
chart_configs.settings_gb.adjust_ohlc_checkbox.setText("Adjust OHLC")
chart_configs.settings_gb.adjust_ohlc_checkbox.setGeometry(400, 20, 100, 30)
chart_configs.settings_gb.volume_checkbox = QCheckBox(chart_configs.settings_gb)
chart_configs.settings_gb.volume_checkbox.setText("Include Volume Bars")
chart_configs.settings_gb.volume_checkbox.setGeometry(500, 20, 140, 30)
chart_configs.settings_gb.timeframe_label = QLabel(chart_configs.settings_gb)
chart_configs.settings_gb.timeframe_label.setText("Chart Timeframe:")
chart_configs.settings_gb.timeframe_label.setGeometry(820, 20, 100, 30)
chart_configs.settings_gb.start_date = QCalendarWidget(chart_configs.settings_gb)
chart_configs.settings_gb.start_date.setGeometry(10, 130, 600, 370)
chart_configs.settings_gb.start_date.setStyleSheet(
    'background-color: deepskyblue; border: 3px solid black;'
)
chart_configs.settings_gb.start_date.setEnabled(False)
chart_configs.settings_gb.end_date = QCalendarWidget(chart_configs.settings_gb)
chart_configs.settings_gb.end_date.setGeometry(620, 130, 600, 370)
chart_configs.settings_gb.end_date.setStyleSheet(
    'background-color: deepskyblue; border: 3px solid black;'
)
chart_configs.settings_gb.end_date.setEnabled(False)
model = QStringListModel()
model.setStringList(all_tickers_list)
completer = ac.CustomQCompleter()
completer.setModel(model)
chart_configs.searchbar_gb.searchBar.setCompleter(completer)
completer.activated.connect(lambda: chart_configs.searchbar_gb.search_button.setEnabled(True))
completer.setMaxVisibleItems(5)
indicators_dialog = QDialog()
indicators_dialog.momentum_gb = QGroupBox(indicators_dialog)
indicators_dialog.momentum_gb.setTitle("Momentum Indicators")
indicators_dialog.momentum_gb.setGeometry(10, 10, 300, 620)
indicators_dialog.momentum_gb.setStyleSheet('background-color: white')
ta_combobox_items = [str(i) for i in range(0, 16)]


def on_enter(_, indicator_widget, widget_button):
    """
    Sets the background color of the technical indicator widget to gray when it is hovered over
    """
    widget_button.setVisible(True)
    indicator_widget.setStyleSheet("background-color : #E3E3E3;")
    for child in indicator_widget.children()[1:]:
        child.setStyleSheet("background-color : #E3E3E3;")


def on_exit(_, indicator_widget, widget_button):
    """
    Sets the background color of the technical indicator indicator_widge to white when it is
    no longer being hovered over
    """
    widget_button.setVisible(False)
    indicator_widget.setStyleSheet("background-color : white;")
    for child in indicator_widget.children()[1:]:
        child.setStyleSheet("background-color : white;")


indicators_dialog.momentum_gb.momentum_scrollarea = QScrollArea(indicators_dialog.momentum_gb)
indicators_dialog.momentum_gb.momentum_scrollarea.setGeometry(10, 20, 280, 600)
momentum_widget = QWidget()
momentum_widget.resize(280, 1500)
momentum_widget.setLayout(QVBoxLayout())
indicators_dialog.momentum_gb.momentum_scrollarea.setWidget(momentum_widget)
indicators_dialog.momentum_gb.momentum_scrollarea.setVerticalScrollBarPolicy(SCROLLBAR_ALWAYSON)

# add average directional index indicator to momentum indicator scrollable
adx_widget = QWidget()
adx_widget.setLayout(QHBoxLayout())
adx_widget.layout().addWidget(QLabel("Average Directional Movement"))
adx_panel_cb = QComboBox()
adx_panel_cb.addItems(ta_combobox_items)
adx_panel_cb.currentTextChanged.connect(
    lambda state: change_indicator_panel(
        "talib.ADX", state, selected_ta[get_indicator_index("talib.ADX")][2]
    )
    if adx_checkbox.isChecked()
    else None
)
adx_widget.layout().addWidget(adx_panel_cb)
adx_settings_button = QPushButton()
adx_settings_button.setVisible(False)
size_retain = adx_settings_button.sizePolicy()
size_retain.setRetainSizeWhenHidden(True)
adx_settings_button.setSizePolicy(size_retain)
adx_settings_button.setIcon(GEAR_ICON)
adx_widget.enterEvent = lambda event: on_enter(event, adx_widget, adx_settings_button)
adx_widget.leaveEvent = lambda event: on_exit(event, adx_widget, adx_settings_button)
def adx_button_clicked():
    """
    Displays a separate window with adjustable settings for the adx indicator
    """
    wnd = QDialog(widget)
    wnd.setWindowTitle("Average Directional Movement")
    wnd.setLayout(QVBoxLayout())
    period_widget = QWidget()
    period_widget.setLayout(QHBoxLayout())
    period_spinbox = QSpinBox()
    period_spinbox.setValue(selected_ta[get_indicator_index(
        "talib.ADX")][2][0] if adx_checkbox.isChecked() else 14)
    period_widget.layout().addWidget(QLabel("Period"))
    period_widget.layout().addWidget(period_spinbox)
    wnd.layout().addWidget(period_widget)

    defaults_button = QPushButton("Reset to Defaults")
    defaults_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    defaults_button.clicked.connect(lambda: period_spinbox.setValue(10))
    cancel_button = QPushButton("Cancel")
    cancel_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    cancel_button.clicked.connect(lambda: wnd.done(0))
    ok_button = QPushButton("Save" if adx_checkbox.isChecked() else "Save and Add")
    ok_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    def ok_button_clicked():
        settings_tuple = ("talib.ADX", adx_panel_cb.currentIndex(), [period_spinbox.value()])

        if adx_checkbox.isChecked():
            selected_ta[get_indicator_index("talib.ADX")] = settings_tuple
        else:
            selected_ta.append(settings_tuple)
            adx_checkbox.setChecked(True)

        wnd.done(0)
    ok_button.clicked.connect(ok_button_clicked)
    buttons_widget = QWidget()
    buttons_widget.setLayout(QHBoxLayout())
    buttons_widget.layout().addWidget(defaults_button)
    buttons_widget.layout().addWidget(cancel_button)
    buttons_widget.layout().addWidget(ok_button)
    wnd.layout().addWidget(buttons_widget)
    wnd.exec_()
adx_settings_button.clicked.connect(adx_button_clicked)
adx_widget.layout().addWidget(adx_settings_button)
adx_checkbox = QCheckBox()
adx_checkbox.clicked.connect(
    lambda: indicator_box_clicked(
        adx_checkbox, adx_panel_cb.currentIndex(), "talib.ADX", [14], selected_ta
    )
)
adx_widget.layout().addWidget(adx_checkbox)
momentum_widget.layout().addWidget(adx_widget)

# add ADX rating indicator to momentum indicator scrollable
adxr_widget = QWidget()
adxr_widget.setLayout(QHBoxLayout())
adxr_widget.layout().addWidget(QLabel("ADX Rating"))
adxr_panel_cb = QComboBox()
adxr_panel_cb.addItems(ta_combobox_items)
adxr_panel_cb.currentTextChanged.connect(
    lambda state: change_indicator_panel(
        "talib.ADXR", state, selected_ta[get_indicator_index("talib.ADXR")][2]
    )
    if adxr_checkbox.isChecked()
    else None
)
adxr_widget.layout().addWidget(adxr_panel_cb)
adxr_settings_button = QPushButton()
adxr_settings_button.setVisible(False)
size_retain = adxr_settings_button.sizePolicy()
size_retain.setRetainSizeWhenHidden(True)
adxr_settings_button.setSizePolicy(size_retain)
adxr_settings_button.setIcon(GEAR_ICON)
adxr_widget.enterEvent = lambda event: on_enter(event, adxr_widget, adxr_settings_button)
adxr_widget.leaveEvent = lambda event: on_exit(event, adxr_widget, adxr_settings_button)
def adxr_button_clicked():
    """
    Displays a separate window with adjustable settings for the adxr indicator
    """
    wnd = QDialog(widget)
    wnd.setWindowTitle("ADX Rating")
    wnd.setLayout(QVBoxLayout())
    period_widget = QWidget()
    period_widget.setLayout(QHBoxLayout())
    period_spinbox = QSpinBox()
    period_spinbox.setValue(selected_ta[get_indicator_index(
        "talib.ADXR")][2][0] if adxr_checkbox.isChecked() else 14)
    period_widget.layout().addWidget(QLabel("Period"))
    period_widget.layout().addWidget(period_spinbox)
    wnd.layout().addWidget(period_widget)
    defaults_button = QPushButton("Reset to Defaults")
    defaults_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    defaults_button.clicked.connect(lambda: period_spinbox.setValue(10))
    cancel_button = QPushButton("Cancel")
    cancel_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    cancel_button.clicked.connect(lambda: wnd.done(0))
    ok_button = QPushButton("Save" if adxr_checkbox.isChecked() else "Save and Add")
    ok_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    def ok_button_clicked():
        settings_tuple = ("talib.ADXR", adxr_panel_cb.currentIndex(), [period_spinbox.value()])

        if adxr_checkbox.isChecked():
            selected_ta[get_indicator_index("talib.ADXR")] = settings_tuple
        else:
            selected_ta.append(settings_tuple)
            adxr_checkbox.setChecked(True)

        wnd.done(0)
    ok_button.clicked.connect(ok_button_clicked)
    buttons_widget = QWidget()
    buttons_widget.setLayout(QHBoxLayout())
    buttons_widget.layout().addWidget(defaults_button)
    buttons_widget.layout().addWidget(cancel_button)
    buttons_widget.layout().addWidget(ok_button)
    wnd.layout().addWidget(buttons_widget)
    wnd.exec_()
adxr_settings_button.clicked.connect(adxr_button_clicked)
adxr_widget.layout().addWidget(adxr_settings_button)
adxr_checkbox = QCheckBox()
adxr_checkbox.clicked.connect(
    lambda: indicator_box_clicked(
        adxr_checkbox, adxr_panel_cb.currentIndex(), "talib.ADXR", [14], selected_ta
    )
)
adxr_widget.layout().addWidget(adxr_checkbox)
momentum_widget.layout().addWidget(adxr_widget)

# add abs. price osc. to momentum indicator scrollable
apo_widget = QWidget()
apo_widget.setLayout(QHBoxLayout())
apo_widget.layout().addWidget(QLabel("Absolute Price Oscillator"))
apo_panel_cb = QComboBox()
apo_panel_cb.addItems(ta_combobox_items)
apo_panel_cb.currentTextChanged.connect(
    lambda state: change_indicator_panel(
        "talib.APO", state, selected_ta[get_indicator_index("talib.APO")][2]
    )
    if apo_checkbox.isChecked()
    else None
)
apo_widget.layout().addWidget(apo_panel_cb)
apo_settings_button = QPushButton()
apo_settings_button.setVisible(False)
size_retain = apo_settings_button.sizePolicy()
size_retain.setRetainSizeWhenHidden(True)
apo_settings_button.setSizePolicy(size_retain)
apo_settings_button.setIcon(GEAR_ICON)
apo_widget.enterEvent = lambda event: on_enter(event, apo_widget, apo_settings_button)
apo_widget.leaveEvent = lambda event: on_exit(event, apo_widget, apo_settings_button)
def apo_button_clicked():
    """
    Displays a separate window with adjustable settings for the apo indicator
    """
    wnd = QDialog(widget)
    wnd.setWindowTitle("Absolute Price Oscillator")
    wnd.setLayout(QVBoxLayout())

    fastma_widget = QWidget()
    fastma_widget.setLayout(QHBoxLayout())
    fastma_spinbox = QSpinBox()
    fastma_spinbox.setValue(selected_ta[get_indicator_index(
        "talib.APO")][2][0] if apo_checkbox.isChecked() else 12)
    fastma_widget.layout().addWidget(QLabel("Fast MA Period"))
    fastma_widget.layout().addWidget(fastma_spinbox)
    wnd.layout().addWidget(fastma_widget)

    slowma_widget = QWidget()
    slowma_widget.setLayout(QHBoxLayout())
    slowma_spinbox = QSpinBox()
    slowma_spinbox.setValue(selected_ta[get_indicator_index(
        "talib.APO")][2][1] if apo_checkbox.isChecked() else 26)
    slowma_widget.layout().addWidget(QLabel("Slow MA Period"))
    slowma_widget.layout().addWidget(slowma_spinbox)
    wnd.layout().addWidget(slowma_widget)

    matype_widget = QWidget()
    matype_widget.setLayout(QHBoxLayout())
    matype_spinbox = QSpinBox()
    matype_spinbox.setValue(selected_ta[get_indicator_index(
        "talib.APO")][2][2] if apo_checkbox.isChecked() else 0)
    matype_widget.layout().addWidget(QLabel("MA Type"))
    matype_widget.layout().addWidget(matype_spinbox)
    wnd.layout().addWidget(matype_widget)

    defaults_button = QPushButton("Reset to Defaults")
    defaults_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    def restore_defaults():
        fastma_spinbox.setValue(12)
        slowma_spinbox.setValue(26)
        matype_spinbox.setValue(9)
    defaults_button.clicked.connect(restore_defaults)
    cancel_button = QPushButton("Cancel")
    cancel_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    cancel_button.clicked.connect(lambda: wnd.done(0))
    ok_button = QPushButton("Save" if apo_checkbox.isChecked() else "Save and Add")
    ok_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    def ok_button_clicked():
        new_vals = [fastma_spinbox.value(), slowma_spinbox.value(), matype_spinbox.value()]
        settings_tuple = ("talib.APO", apo_panel_cb.currentIndex(), new_vals)
        if apo_checkbox.isChecked():
            selected_ta[get_indicator_index("talib.APO")] = settings_tuple
        else:
            selected_ta.append(settings_tuple)
            apo_checkbox.setChecked(True)
        wnd.done(0)
    ok_button.clicked.connect(ok_button_clicked)
    buttons_widget = QWidget()
    buttons_widget.setLayout(QHBoxLayout())
    buttons_widget.layout().addWidget(defaults_button)
    buttons_widget.layout().addWidget(cancel_button)
    buttons_widget.layout().addWidget(ok_button)
    wnd.layout().addWidget(buttons_widget)
    wnd.exec_()
apo_settings_button.clicked.connect(apo_button_clicked)
apo_widget.layout().addWidget(apo_settings_button)
apo_checkbox = QCheckBox()
apo_checkbox.clicked.connect(
    lambda: indicator_box_clicked(
        apo_checkbox, apo_panel_cb.currentIndex(), "talib.APO", [12, 26, 0], selected_ta
    )
)
apo_widget.layout().addWidget(apo_checkbox)
momentum_widget.layout().addWidget(apo_widget)

# add aroon indicator to momentum indicator scrollable
aroon_widget = QWidget()
aroon_widget.setLayout(QHBoxLayout())
aroon_widget.layout().addWidget(QLabel("Aroon"))
aroon_panel_cb = QComboBox()
aroon_panel_cb.addItems(ta_combobox_items)
aroon_panel_cb.currentTextChanged.connect(
    lambda state: change_indicator_panel(
        "talib.AROON", state, selected_ta[get_indicator_index("talib.AROON")][2]
    )
    if aroon_checkbox.isChecked()
    else None
)
aroon_widget.layout().addWidget(aroon_panel_cb)
aroon_settings_button = QPushButton()
aroon_settings_button.setVisible(False)
size_retain = aroon_settings_button.sizePolicy()
size_retain.setRetainSizeWhenHidden(True)
aroon_settings_button.setSizePolicy(size_retain)
aroon_settings_button.setIcon(GEAR_ICON)
aroon_widget.enterEvent = lambda event: on_enter(event, aroon_widget, aroon_settings_button)
aroon_widget.leaveEvent = lambda event: on_exit(event, aroon_widget, aroon_settings_button)
def aroon_button_clicked():
    """
    Displays a separate window with adjustable settings for the aroon indicator
    """
    wnd = QDialog(widget)
    wnd.setWindowTitle("Aroon")
    wnd.setLayout(QVBoxLayout())
    period_widget = QWidget()
    period_widget.setLayout(QHBoxLayout())
    period_spinbox = QSpinBox()
    period_spinbox.setValue(selected_ta[get_indicator_index(
        "talib.AROON")][2][0] if aroon_checkbox.isChecked() else 14)
    period_widget.layout().addWidget(QLabel("Period"))
    period_widget.layout().addWidget(period_spinbox)
    wnd.layout().addWidget(period_widget)
    defaults_button = QPushButton("Reset to Defaults")
    defaults_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    defaults_button.clicked.connect(lambda: period_spinbox.setValue(10))
    cancel_button = QPushButton("Cancel")
    cancel_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    cancel_button.clicked.connect(lambda: wnd.done(0))
    ok_button = QPushButton("Save" if aroon_checkbox.isChecked() else "Save and Add")
    ok_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    def ok_button_clicked():
        settings_tuple = ("talib.AROON", aroon_panel_cb.currentIndex(), [period_spinbox.value()])

        if aroon_checkbox.isChecked():
            selected_ta[get_indicator_index("talib.AROON")] = settings_tuple
        else:
            selected_ta.append(settings_tuple)
            aroon_checkbox.setChecked(True)

        wnd.done(0)
    ok_button.clicked.connect(ok_button_clicked)
    buttons_widget = QWidget()
    buttons_widget.setLayout(QHBoxLayout())
    buttons_widget.layout().addWidget(defaults_button)
    buttons_widget.layout().addWidget(cancel_button)
    buttons_widget.layout().addWidget(ok_button)
    wnd.layout().addWidget(buttons_widget)
    wnd.exec_()
aroon_settings_button.clicked.connect(aroon_button_clicked)
aroon_widget.layout().addWidget(aroon_settings_button)
aroon_checkbox = QCheckBox()
aroon_checkbox.clicked.connect(
    lambda: indicator_box_clicked(
        aroon_checkbox, aroon_panel_cb.currentIndex(), "talib.AROON", [14], selected_ta
    )
)
aroon_widget.layout().addWidget(aroon_checkbox)
momentum_widget.layout().addWidget(aroon_widget)

# add aroon oscillator to momentum indicator scrollable
aroonosc_widget = QWidget()
aroonosc_widget.setLayout(QHBoxLayout())
aroonosc_widget.layout().addWidget(QLabel("Aroon Oscillator"))
aroonosc_panel_cb = QComboBox()
aroonosc_panel_cb.addItems(ta_combobox_items)
aroonosc_panel_cb.currentTextChanged.connect(
    lambda state: change_indicator_panel(
        "talib.AROONOSC", state, selected_ta[get_indicator_index("talib.AROONOSC")][2]
    )
    if aroonosc_checkbox.isChecked()
    else None
)
aroonosc_widget.layout().addWidget(aroonosc_panel_cb)
aroonosc_settings_button = QPushButton()
aroonosc_settings_button.setVisible(False)
size_retain = aroonosc_settings_button.sizePolicy()
size_retain.setRetainSizeWhenHidden(True)
aroonosc_settings_button.setSizePolicy(size_retain)
aroonosc_settings_button.setIcon(GEAR_ICON)
aroonosc_widget.enterEvent = lambda e: on_enter(e, aroonosc_widget, aroonosc_settings_button)
aroonosc_widget.leaveEvent = lambda e: on_exit(e, aroonosc_widget, aroonosc_settings_button)
def aroonosc_button_clicked():
    """
    Displays a separate window with adjustable settings for the aroonosc indicator
    """
    wnd = QDialog(widget)
    wnd.setWindowTitle("Aroon Oscillator")
    wnd.setLayout(QVBoxLayout())
    period_widget = QWidget()
    period_widget.setLayout(QHBoxLayout())
    period_spinbox = QSpinBox()
    period_spinbox.setValue(selected_ta[get_indicator_index(
        "talib.AROONOSC")][2][0] if aroonosc_checkbox.isChecked() else 14)
    period_widget.layout().addWidget(QLabel("Period"))
    period_widget.layout().addWidget(period_spinbox)
    wnd.layout().addWidget(period_widget)
    defaults_button = QPushButton("Reset to Defaults")
    defaults_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    defaults_button.clicked.connect(lambda: period_spinbox.setValue(10))
    cancel_button = QPushButton("Cancel")
    cancel_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    cancel_button.clicked.connect(lambda: wnd.done(0))
    ok_button = QPushButton("Save" if aroonosc_checkbox.isChecked() else "Save and Add")
    ok_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    def ok_button_clicked():
        settings_tuple = (
            "talib.AROONOSC", aroonosc_panel_cb.currentIndex(), [period_spinbox.value()]
        )

        if aroonosc_checkbox.isChecked():
            selected_ta[get_indicator_index("talib.AROONOSC")] = settings_tuple
        else:
            selected_ta.append(settings_tuple)
            aroonosc_checkbox.setChecked(True)

        wnd.done(0)
    ok_button.clicked.connect(ok_button_clicked)
    buttons_widget = QWidget()
    buttons_widget.setLayout(QHBoxLayout())
    buttons_widget.layout().addWidget(defaults_button)
    buttons_widget.layout().addWidget(cancel_button)
    buttons_widget.layout().addWidget(ok_button)
    wnd.layout().addWidget(buttons_widget)
    wnd.exec_()
aroonosc_settings_button.clicked.connect(aroonosc_button_clicked)
aroonosc_widget.layout().addWidget(aroonosc_settings_button)
aroonosc_checkbox = QCheckBox()
aroonosc_checkbox.clicked.connect(
    lambda: indicator_box_clicked(
        aroonosc_checkbox, aroonosc_panel_cb.currentIndex(), "talib.AROONOSC", [14], selected_ta
    )
)
aroonosc_widget.layout().addWidget(aroonosc_checkbox)
momentum_widget.layout().addWidget(aroonosc_widget)

# add balance of power to momentum indicator scrollable
bop_widget = QWidget()
bop_widget.setLayout(QHBoxLayout())
bop_widget.layout().addWidget(QLabel("Balance of Power"))
bop_panel_cb = QComboBox()
bop_panel_cb.addItems(ta_combobox_items)
bop_panel_cb.currentTextChanged.connect(
    lambda state: change_indicator_panel(
        "talib.BOP", state, selected_ta[get_indicator_index("talib.BOP")][2]
    )
    if bop_checkbox.isChecked()
    else None
)
bop_widget.layout().addWidget(bop_panel_cb)
bop_settings_button = QPushButton()
bop_settings_button.setVisible(False)
size_retain = bop_settings_button.sizePolicy()
size_retain.setRetainSizeWhenHidden(True)
bop_settings_button.setSizePolicy(size_retain)
bop_settings_button.setIcon(GEAR_ICON)
bop_widget.enterEvent = lambda event: on_enter(event, bop_widget, bop_settings_button)
bop_widget.leaveEvent = lambda event: on_exit(event, bop_widget, bop_settings_button)
def bop_button_clicked():
    """
    Displays a separate window with adjustable settings for the bop indicator
    """
    wnd = QDialog(widget)
    wnd.setWindowTitle("Balance of Power")
    wnd.setLayout(QVBoxLayout())

    defaults_button = QPushButton("Reset to Defaults")
    defaults_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    cancel_button = QPushButton("Cancel")
    cancel_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    cancel_button.clicked.connect(lambda: wnd.done(0))
    ok_button = QPushButton("Save" if bop_checkbox.isChecked() else "Save and Add")
    ok_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    def ok_button_clicked():
        settings_tuple = ("talib.BOP", bop_panel_cb.currentIndex(), [])

        if bop_checkbox.isChecked():
            selected_ta[get_indicator_index("talib.BOP")] = settings_tuple
        else:
            selected_ta.append(settings_tuple)
            bop_checkbox.setChecked(True)

        wnd.done(0)
    ok_button.clicked.connect(ok_button_clicked)
    buttons_widget = QWidget()
    buttons_widget.setLayout(QHBoxLayout())
    buttons_widget.layout().addWidget(defaults_button)
    buttons_widget.layout().addWidget(cancel_button)
    buttons_widget.layout().addWidget(ok_button)
    wnd.layout().addWidget(buttons_widget)
    wnd.exec_()
bop_settings_button.clicked.connect(bop_button_clicked)
bop_widget.layout().addWidget(bop_settings_button)
bop_checkbox = QCheckBox()
bop_checkbox.clicked.connect(
    lambda: indicator_box_clicked(
        bop_checkbox, bop_panel_cb.currentIndex(), "talib.BOP", [], selected_ta
    )
)
bop_widget.layout().addWidget(bop_checkbox)
momentum_widget.layout().addWidget(bop_widget)

# add commodity channel index to momentum indicator scrollable
cci_widget = QWidget()
cci_widget.setLayout(QHBoxLayout())
cci_widget.layout().addWidget(QLabel("Commodity Channel Index"))
cci_panel_cb = QComboBox()
cci_panel_cb.addItems(ta_combobox_items)
cci_panel_cb.currentTextChanged.connect(
    lambda state: change_indicator_panel(
        "talib.CCI", state, selected_ta[get_indicator_index("talib.CCI")][2]
    )
    if cci_checkbox.isChecked()
    else None
)
cci_widget.layout().addWidget(cci_panel_cb)
cci_settings_button = QPushButton()
cci_settings_button.setVisible(False)
size_retain = cci_settings_button.sizePolicy()
size_retain.setRetainSizeWhenHidden(True)
cci_settings_button.setSizePolicy(size_retain)
cci_settings_button.setIcon(GEAR_ICON)
cci_widget.enterEvent = lambda event: on_enter(event, cci_widget, cci_settings_button)
cci_widget.leaveEvent = lambda event: on_exit(event, cci_widget, cci_settings_button)
def cci_button_clicked():
    """
    Displays a separate window with adjustable settings for the cci indicator
    """
    wnd = QDialog(widget)
    wnd.setWindowTitle("Commodity Channel Index")
    wnd.setLayout(QVBoxLayout())
    period_widget = QWidget()
    period_widget.setLayout(QHBoxLayout())
    period_spinbox = QSpinBox()
    period_spinbox.setValue(selected_ta[get_indicator_index(
        "talib.CCI")][2][0] if cci_checkbox.isChecked() else 14)
    period_widget.layout().addWidget(QLabel("Period"))
    period_widget.layout().addWidget(period_spinbox)
    wnd.layout().addWidget(period_widget)
    defaults_button = QPushButton("Reset to Defaults")
    defaults_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    defaults_button.clicked.connect(lambda: period_spinbox.setValue(10))
    cancel_button = QPushButton("Cancel")
    cancel_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    cancel_button.clicked.connect(lambda: wnd.done(0))
    ok_button = QPushButton("Save" if cci_checkbox.isChecked() else "Save and Add")
    ok_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    def ok_button_clicked():
        settings_tuple = ("talib.CCI", cci_panel_cb.currentIndex(), [period_spinbox.value()])

        if cci_checkbox.isChecked():
            selected_ta[get_indicator_index("talib.CCI")] = settings_tuple
        else:
            selected_ta.append(settings_tuple)
            cci_checkbox.setChecked(True)

        wnd.done(0)
    ok_button.clicked.connect(ok_button_clicked)
    buttons_widget = QWidget()
    buttons_widget.setLayout(QHBoxLayout())
    buttons_widget.layout().addWidget(defaults_button)
    buttons_widget.layout().addWidget(cancel_button)
    buttons_widget.layout().addWidget(ok_button)
    wnd.layout().addWidget(buttons_widget)
    wnd.exec_()
cci_settings_button.clicked.connect(cci_button_clicked)
cci_widget.layout().addWidget(cci_settings_button)
cci_checkbox = QCheckBox()
cci_checkbox.clicked.connect(
    lambda: indicator_box_clicked(
        cci_checkbox, cci_panel_cb.currentIndex(), "talib.CCI", [14], selected_ta
    )
)
cci_widget.layout().addWidget(cci_checkbox)
momentum_widget.layout().addWidget(cci_widget)

# add chande momentum oscillator to momentum indicator scrollable
cmo_widget = QWidget()
cmo_widget.setLayout(QHBoxLayout())
cmo_widget.layout().addWidget(QLabel("Chande Momentum Oscillator"))
cmo_panel_cb = QComboBox()
cmo_panel_cb.addItems(ta_combobox_items)
cmo_panel_cb.currentTextChanged.connect(
    lambda state: change_indicator_panel(
        "talib.CMO", state, selected_ta[get_indicator_index("talib.CMO")][2]
    )
    if cmo_checkbox.isChecked()
    else None
)
cmo_widget.layout().addWidget(cmo_panel_cb)
cmo_settings_button = QPushButton()
cmo_settings_button.setVisible(False)
size_retain = cmo_settings_button.sizePolicy()
size_retain.setRetainSizeWhenHidden(True)
cmo_settings_button.setSizePolicy(size_retain)
cmo_settings_button.setIcon(GEAR_ICON)
cmo_widget.enterEvent = lambda event: on_enter(event, cmo_widget, cmo_settings_button)
cmo_widget.leaveEvent = lambda event: on_exit(event, cmo_widget, cmo_settings_button)
def cmo_button_clicked():
    """
    Displays a separate window with adjustable settings for the cmo indicator
    """
    wnd = QDialog(widget)
    wnd.setWindowTitle("Chande Momentum Oscillator")
    wnd.setLayout(QVBoxLayout())
    period_widget = QWidget()
    period_widget.setLayout(QHBoxLayout())
    period_spinbox = QSpinBox()
    period_spinbox.setValue(selected_ta[get_indicator_index(
        "talib.CMO")][2][0] if cmo_checkbox.isChecked() else 14)
    period_widget.layout().addWidget(QLabel("Period"))
    period_widget.layout().addWidget(period_spinbox)
    wnd.layout().addWidget(period_widget)

    defaults_button = QPushButton("Reset to Defaults")
    defaults_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    defaults_button.clicked.connect(lambda: period_spinbox.setValue(10))
    cancel_button = QPushButton("Cancel")
    cancel_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    cancel_button.clicked.connect(lambda: wnd.done(0))
    ok_button = QPushButton("Save" if cmo_checkbox.isChecked() else "Save and Add")
    ok_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    def ok_button_clicked():
        settings_tuple = ("talib.CMO", cmo_panel_cb.currentIndex(), [period_spinbox.value()])

        if cmo_checkbox.isChecked():
            selected_ta[get_indicator_index("talib.CMO")] = settings_tuple
        else:
            selected_ta.append(settings_tuple)
            cmo_checkbox.setChecked(True)

        wnd.done(0)
    ok_button.clicked.connect(ok_button_clicked)
    buttons_widget = QWidget()
    buttons_widget.setLayout(QHBoxLayout())
    buttons_widget.layout().addWidget(defaults_button)
    buttons_widget.layout().addWidget(cancel_button)
    buttons_widget.layout().addWidget(ok_button)
    wnd.layout().addWidget(buttons_widget)
    wnd.exec_()
cmo_settings_button.clicked.connect(cmo_button_clicked)
cmo_widget.layout().addWidget(cmo_settings_button)
cmo_checkbox = QCheckBox()
cmo_checkbox.clicked.connect(
    lambda: indicator_box_clicked(
        cmo_checkbox, cmo_panel_cb.currentIndex(), "talib.CMO", [14], selected_ta
    )
)
cmo_widget.layout().addWidget(cmo_checkbox)
momentum_widget.layout().addWidget(cmo_widget)

# add directional movement index to momentum indicator scrollable
dx_widget = QWidget()
dx_widget.setLayout(QHBoxLayout())
dx_widget.layout().addWidget(QLabel("Directional Movement Index"))
dx_panel_cb = QComboBox()
dx_panel_cb.addItems(ta_combobox_items)
dx_panel_cb.currentTextChanged.connect(
    lambda state: change_indicator_panel(
        "talib.DX", state, selected_ta[get_indicator_index("talib.DX")][2]
    )
    if dx_checkbox.isChecked()
    else None
)
dx_widget.layout().addWidget(dx_panel_cb)
dx_settings_button = QPushButton()
dx_settings_button.setVisible(False)
size_retain = dx_settings_button.sizePolicy()
size_retain.setRetainSizeWhenHidden(True)
dx_settings_button.setSizePolicy(size_retain)
dx_settings_button.setIcon(GEAR_ICON)
dx_widget.enterEvent = lambda event: on_enter(event, dx_widget, dx_settings_button)
dx_widget.leaveEvent = lambda event: on_exit(event, dx_widget, dx_settings_button)
def dx_button_clicked():
    """
    Displays a separate window with adjustable settings for the dx indicator
    """
    wnd = QDialog(widget)
    wnd.setWindowTitle("Directional Movement Index")
    wnd.setLayout(QVBoxLayout())
    period_widget = QWidget()
    period_widget.setLayout(QHBoxLayout())
    period_spinbox = QSpinBox()
    period_spinbox.setValue(selected_ta[get_indicator_index(
        "talib.DX")][2][0] if dx_checkbox.isChecked() else 14)
    period_widget.layout().addWidget(QLabel("Period"))
    period_widget.layout().addWidget(period_spinbox)
    wnd.layout().addWidget(period_widget)

    defaults_button = QPushButton("Reset to Defaults")
    defaults_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    defaults_button.clicked.connect(lambda: period_spinbox.setValue(10))
    cancel_button = QPushButton("Cancel")
    cancel_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    cancel_button.clicked.connect(lambda: wnd.done(0))
    ok_button = QPushButton("Save" if dx_checkbox.isChecked() else "Save and Add")
    ok_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    def ok_button_clicked():
        settings_tuple = ("talib.DX", dx_panel_cb.currentIndex(), [period_spinbox.value()])

        if dx_checkbox.isChecked():
            selected_ta[get_indicator_index("talib.DX")] = settings_tuple
        else:
            selected_ta.append(settings_tuple)
            dx_checkbox.setChecked(True)

        wnd.done(0)
    ok_button.clicked.connect(ok_button_clicked)
    buttons_widget = QWidget()
    buttons_widget.setLayout(QHBoxLayout())
    buttons_widget.layout().addWidget(defaults_button)
    buttons_widget.layout().addWidget(cancel_button)
    buttons_widget.layout().addWidget(ok_button)
    wnd.layout().addWidget(buttons_widget)
    wnd.exec_()
dx_settings_button.clicked.connect(dx_button_clicked)
dx_widget.layout().addWidget(dx_settings_button)
dx_checkbox = QCheckBox()
dx_checkbox.clicked.connect(
    lambda: indicator_box_clicked(
        dx_checkbox, dx_panel_cb.currentIndex(), "talib.DX", [14], selected_ta
    )
)
dx_widget.layout().addWidget(dx_checkbox)
momentum_widget.layout().addWidget(dx_widget)

# add moving average convergence divergence w/controllable MA type to momentum indicator scrollable
macdext_widget = QWidget()
macdext_widget.setLayout(QHBoxLayout())
macdext_widget.layout().addWidget(QLabel("MACD"))
macdext_panel_cb = QComboBox()
macdext_panel_cb.addItems(ta_combobox_items)
macdext_panel_cb.currentTextChanged.connect(
    lambda state: change_indicator_panel(
        "talib.MACDEXT", state, selected_ta[get_indicator_index("talib.MACDEXT")][2]
    )
    if macdext_checkbox.isChecked()
    else None
)
macdext_widget.layout().addWidget(macdext_panel_cb)
macdext_settings_button = QPushButton()
macdext_settings_button.setVisible(False)
size_retain = macdext_settings_button.sizePolicy()
size_retain.setRetainSizeWhenHidden(True)
macdext_settings_button.setSizePolicy(size_retain)
macdext_settings_button.setIcon(GEAR_ICON)
macdext_widget.enterEvent = lambda event: on_enter(event, macdext_widget, macdext_settings_button)
macdext_widget.leaveEvent = lambda event: on_exit(event, macdext_widget, macdext_settings_button)
def macdext_button_clicked():
    """
    Displays a separate window with adjustable settings for the macdext indicator
    """
    wnd = QDialog(widget)
    wnd.setWindowTitle("MACD")
    wnd.setLayout(QVBoxLayout())
    fastpd_widget = QWidget()
    fastpd_widget.setLayout(QHBoxLayout())
    fastpd_spinbox = QSpinBox()
    fastpd_spinbox.setValue(selected_ta[get_indicator_index(
        "talib.MACDEXT")][2][0] if macdext_checkbox.isChecked() else 12)
    fastpd_widget.layout().addWidget(QLabel("Fast Period"))
    fastpd_widget.layout().addWidget(fastpd_spinbox)
    wnd.layout().addWidget(fastpd_widget)

    fastpd_matype_widget = QWidget()
    fastpd_matype_widget.setLayout(QHBoxLayout())
    fastpd_matype_spinbox = QSpinBox()
    fastpd_matype_spinbox.setValue(selected_ta[get_indicator_index(
        "talib.MACDEXT")][2][1] if macdext_checkbox.isChecked() else 0)
    fastpd_matype_widget.layout().addWidget(QLabel("Fast MA Type"))
    fastpd_matype_widget.layout().addWidget(fastpd_matype_spinbox)
    wnd.layout().addWidget(fastpd_matype_widget)

    slowpd_widget = QWidget()
    slowpd_widget.setLayout(QHBoxLayout())
    slowpd_spinbox = QSpinBox()
    slowpd_spinbox.setValue(selected_ta[get_indicator_index(
        "talib.MACDEXT")][2][2] if macdext_checkbox.isChecked() else 26)
    slowpd_widget.layout().addWidget(QLabel("Slow Period"))
    slowpd_widget.layout().addWidget(slowpd_spinbox)
    wnd.layout().addWidget(slowpd_widget)

    slowpd_matype_widget = QWidget()
    slowpd_matype_widget.setLayout(QHBoxLayout())
    slowpd_matype_spinbox = QSpinBox()
    slowpd_matype_spinbox.setValue(selected_ta[get_indicator_index(
        "talib.MACDEXT")][2][3] if macdext_checkbox.isChecked() else 0)
    slowpd_matype_widget.layout().addWidget(QLabel("Slow MA Type"))
    slowpd_matype_widget.layout().addWidget(slowpd_matype_spinbox)
    wnd.layout().addWidget(slowpd_matype_widget)

    signalpd_widget = QWidget()
    signalpd_widget.setLayout(QHBoxLayout())
    signalpd_spinbox = QSpinBox()
    signalpd_spinbox.setValue(selected_ta[get_indicator_index(
        "talib.MACDEXT")][2][4] if macdext_checkbox.isChecked() else 9)
    signalpd_widget.layout().addWidget(QLabel("Signal Period"))
    signalpd_widget.layout().addWidget(signalpd_spinbox)
    wnd.layout().addWidget(signalpd_widget)

    signalpd_matype_widget = QWidget()
    signalpd_matype_widget.setLayout(QHBoxLayout())
    signalpd_matype_spinbox = QSpinBox()
    signalpd_matype_spinbox.setValue(selected_ta[get_indicator_index(
        "talib.MACDEXT")][2][5] if macdext_checkbox.isChecked() else 0)
    signalpd_matype_widget.layout().addWidget(QLabel("Signal MA Type"))
    signalpd_matype_widget.layout().addWidget(signalpd_matype_spinbox)
    wnd.layout().addWidget(signalpd_matype_widget)

    defaults_button = QPushButton("Reset to Defaults")
    defaults_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    def restore_defaults():
        fastpd_spinbox.setValue(12)
        fastpd_matype_spinbox.setValue(0)
        slowpd_spinbox.setValue(26)
        slowpd_matype_spinbox.setValue(0)
        signalpd_spinbox.setValue(9)
        signalpd_matype_spinbox.setValue(0)
    defaults_button.clicked.connect(restore_defaults)
    cancel_button = QPushButton("Cancel")
    cancel_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    cancel_button.clicked.connect(lambda: wnd.done(0))
    ok_button = QPushButton("Save" if macdext_checkbox.isChecked() else "Save and Add")
    ok_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    def ok_button_clicked():
        new_vals = [
                fastpd_spinbox.value(), fastpd_matype_spinbox.value(),
                slowpd_spinbox.value(), slowpd_matype_spinbox.value(),
                signalpd_spinbox.value(), signalpd_matype_spinbox.value(),
        ]
        settings_tuple = ("talib.MACDEXT", macdext_panel_cb.currentIndex(), new_vals)

        if macdext_checkbox.isChecked():
            selected_ta[get_indicator_index("talib.MACDEXT")] = settings_tuple
        else:
            selected_ta.append(settings_tuple)
            macdext_checkbox.setChecked(True)
        wnd.done(0)
    ok_button.clicked.connect(ok_button_clicked)
    buttons_widget = QWidget()
    buttons_widget.setLayout(QHBoxLayout())
    buttons_widget.layout().addWidget(defaults_button)
    buttons_widget.layout().addWidget(cancel_button)
    buttons_widget.layout().addWidget(ok_button)
    wnd.layout().addWidget(buttons_widget)
    wnd.exec_()
macdext_settings_button.clicked.connect(macdext_button_clicked)
macdext_widget.layout().addWidget(macdext_settings_button)
macdext_checkbox = QCheckBox()
macdext_checkbox.clicked.connect(
    lambda: indicator_box_clicked(
        macdext_checkbox,
        macdext_panel_cb.currentIndex(),
        "talib.MACDEXT",
        [12, 0, 26, 0, 9, 0],
        selected_ta
    )
)
macdext_widget.layout().addWidget(macdext_checkbox)
momentum_widget.layout().addWidget(macdext_widget)

# add money flow index to momentum indicator scrollable
mfi_widget = QWidget()
mfi_widget.setLayout(QHBoxLayout())
mfi_widget.layout().addWidget(QLabel("Money Flow Index"))
mfi_panel_cb = QComboBox()
mfi_panel_cb.addItems(ta_combobox_items)
mfi_panel_cb.currentTextChanged.connect(
    lambda state: change_indicator_panel(
        "talib.MFI", state, selected_ta[get_indicator_index("talib.MFI")][2]
    )
    if mfi_checkbox.isChecked()
    else None
)
mfi_widget.layout().addWidget(mfi_panel_cb)
mfi_settings_button = QPushButton()
mfi_settings_button.setVisible(False)
size_retain = mfi_settings_button.sizePolicy()
size_retain.setRetainSizeWhenHidden(True)
mfi_settings_button.setSizePolicy(size_retain)
mfi_settings_button.setIcon(GEAR_ICON)
mfi_widget.enterEvent = lambda event: on_enter(event, mfi_widget, mfi_settings_button)
mfi_widget.leaveEvent = lambda event: on_exit(event, mfi_widget, mfi_settings_button)
def mfi_button_clicked():
    """
    Displays a separate window with adjustable settings for the mfi indicator
    """
    wnd = QDialog(widget)
    wnd.setWindowTitle("Money Flow Index")
    wnd.setLayout(QVBoxLayout())
    period_widget = QWidget()
    period_widget.setLayout(QHBoxLayout())
    period_spinbox = QSpinBox()
    period_spinbox.setValue(selected_ta[get_indicator_index(
        "talib.MFI")][2][0] if mfi_checkbox.isChecked() else 14)
    period_widget.layout().addWidget(QLabel("Period"))
    period_widget.layout().addWidget(period_spinbox)
    wnd.layout().addWidget(period_widget)

    defaults_button = QPushButton("Reset to Defaults")
    defaults_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    defaults_button.clicked.connect(lambda: period_spinbox.setValue(10))
    cancel_button = QPushButton("Cancel")
    cancel_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    cancel_button.clicked.connect(lambda: wnd.done(0))
    ok_button = QPushButton("Save" if mfi_checkbox.isChecked() else "Save and Add")
    ok_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    def ok_button_clicked():
        settings_tuple = ("talib.MFI", mfi_panel_cb.currentIndex(), [period_spinbox.value()])

        if mfi_checkbox.isChecked():
            selected_ta[get_indicator_index("talib.MFI")] = settings_tuple
        else:
            selected_ta.append(settings_tuple)
            mfi_checkbox.setChecked(True)

        wnd.done(0)
    ok_button.clicked.connect(ok_button_clicked)
    buttons_widget = QWidget()
    buttons_widget.setLayout(QHBoxLayout())
    buttons_widget.layout().addWidget(defaults_button)
    buttons_widget.layout().addWidget(cancel_button)
    buttons_widget.layout().addWidget(ok_button)
    wnd.layout().addWidget(buttons_widget)
    wnd.exec_()
mfi_settings_button.clicked.connect(mfi_button_clicked)
mfi_widget.layout().addWidget(mfi_settings_button)
mfi_checkbox = QCheckBox()
mfi_checkbox.clicked.connect(
    lambda: indicator_box_clicked(
        mfi_checkbox, mfi_panel_cb.currentIndex(), "talib.MFI", [14], selected_ta
    )
)
mfi_widget.layout().addWidget(mfi_checkbox)
momentum_widget.layout().addWidget(mfi_widget)

# add minus directional index to momentum indicator scrollable
minusdi_widget = QWidget()
minusdi_widget.setLayout(QHBoxLayout())
minusdi_widget.layout().addWidget(QLabel("Minus Directional Indicator"))
minusdi_panel_cb = QComboBox()
minusdi_panel_cb.addItems(ta_combobox_items)
minusdi_panel_cb.currentTextChanged.connect(
    lambda state: change_indicator_panel(
        "talib.MINUS_DI", state, selected_ta[get_indicator_index("talib.MINUS_DI")][2]
    )
    if minusdi_checkbox.isChecked()
    else None
)
minusdi_widget.layout().addWidget(minusdi_panel_cb)
minusdi_settings_button = QPushButton()
minusdi_settings_button.setVisible(False)
size_retain = minusdi_settings_button.sizePolicy()
size_retain.setRetainSizeWhenHidden(True)
minusdi_settings_button.setSizePolicy(size_retain)
minusdi_settings_button.setIcon(GEAR_ICON)
minusdi_widget.enterEvent = lambda event: on_enter(event, minusdi_widget, minusdi_settings_button)
minusdi_widget.leaveEvent = lambda event: on_exit(event, minusdi_widget, minusdi_settings_button)
def minusdi_button_clicked():
    """
    Displays a separate window with adjustable settings for the minusdi indicator
    """
    wnd = QDialog(widget)
    wnd.setWindowTitle("Minus Directional Indicator")
    wnd.setLayout(QVBoxLayout())
    period_widget = QWidget()
    period_widget.setLayout(QHBoxLayout())
    period_spinbox = QSpinBox()
    period_spinbox.setValue(selected_ta[get_indicator_index(
        "talib.MINUS_DI")][2][0] if minusdi_checkbox.isChecked() else 14)
    period_widget.layout().addWidget(QLabel("Period"))
    period_widget.layout().addWidget(period_spinbox)
    wnd.layout().addWidget(period_widget)

    defaults_button = QPushButton("Reset to Defaults")
    defaults_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    defaults_button.clicked.connect(lambda: period_spinbox.setValue(10))
    cancel_button = QPushButton("Cancel")
    cancel_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    cancel_button.clicked.connect(lambda: wnd.done(0))
    ok_button = QPushButton("Save" if minusdi_checkbox.isChecked() else "Save and Add")
    ok_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    def ok_button_clicked():
        settings_tuple = (
            "talib.MINUS_DI", minusdi_panel_cb.currentIndex(), [period_spinbox.value()]
        )

        if minusdi_checkbox.isChecked():
            selected_ta[get_indicator_index("talib.MINUS_DI")] = settings_tuple
        else:
            selected_ta.append(settings_tuple)
            minusdi_checkbox.setChecked(True)

        wnd.done(0)
    ok_button.clicked.connect(ok_button_clicked)
    buttons_widget = QWidget()
    buttons_widget.setLayout(QHBoxLayout())
    buttons_widget.layout().addWidget(defaults_button)
    buttons_widget.layout().addWidget(cancel_button)
    buttons_widget.layout().addWidget(ok_button)
    wnd.layout().addWidget(buttons_widget)
    wnd.exec_()
minusdi_settings_button.clicked.connect(minusdi_button_clicked)
minusdi_widget.layout().addWidget(minusdi_settings_button)
minusdi_checkbox = QCheckBox()
minusdi_checkbox.clicked.connect(
    lambda: indicator_box_clicked(
        minusdi_checkbox, minusdi_panel_cb.currentIndex(), "talib.MINUS_DI", [14], selected_ta
    )
)
minusdi_widget.layout().addWidget(minusdi_checkbox)
momentum_widget.layout().addWidget(minusdi_widget)

# add minus directional movement to momentum indicator scrollable
minusdm_widget = QWidget()
minusdm_widget.setLayout(QHBoxLayout())
minusdm_widget.layout().addWidget(QLabel("Minus Directional Movement"))
minusdm_panel_cb = QComboBox()
minusdm_panel_cb.addItems(ta_combobox_items)
minusdm_panel_cb.currentTextChanged.connect(
    lambda state: change_indicator_panel(
        "talib.MINUS_DM", state, selected_ta[get_indicator_index("talib.MINUS_DM")][2]
    )
    if minusdm_checkbox.isChecked()
    else None
)
minusdm_widget.layout().addWidget(minusdm_panel_cb)
minusdm_settings_button = QPushButton()
minusdm_settings_button.setVisible(False)
size_retain = minusdm_settings_button.sizePolicy()
size_retain.setRetainSizeWhenHidden(True)
minusdm_settings_button.setSizePolicy(size_retain)
minusdm_settings_button.setIcon(GEAR_ICON)
minusdm_widget.enterEvent = lambda event: on_enter(event, minusdm_widget, minusdm_settings_button)
minusdm_widget.leaveEvent = lambda event: on_exit(event, minusdm_widget, minusdm_settings_button)
def minusdm_button_clicked():
    """
    Displays a separate window with adjustable settings for the minusdm indicator
    """
    wnd = QDialog(widget)
    wnd.setWindowTitle("Minus Directional Movement")
    wnd.setLayout(QVBoxLayout())
    period_widget = QWidget()
    period_widget.setLayout(QHBoxLayout())
    period_spinbox = QSpinBox()
    period_spinbox.setValue(selected_ta[get_indicator_index(
        "talib.MINUS_DM")][2][0] if minusdm_checkbox.isChecked() else 14)
    period_widget.layout().addWidget(QLabel("Period"))
    period_widget.layout().addWidget(period_spinbox)
    wnd.layout().addWidget(period_widget)

    defaults_button = QPushButton("Reset to Defaults")
    defaults_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    defaults_button.clicked.connect(lambda: period_spinbox.setValue(10))
    cancel_button = QPushButton("Cancel")
    cancel_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    cancel_button.clicked.connect(lambda: wnd.done(0))
    ok_button = QPushButton("Save" if minusdm_checkbox.isChecked() else "Save and Add")
    ok_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    def ok_button_clicked():
        settings_tuple = (
            "talib.MINUS_DM", minusdm_panel_cb.currentIndex(), [period_spinbox.value()]
        )

        if minusdm_checkbox.isChecked():
            selected_ta[get_indicator_index("talib.MINUS_DM")] = settings_tuple
        else:
            selected_ta.append(settings_tuple)
            minusdm_checkbox.setChecked(True)

        wnd.done(0)
    ok_button.clicked.connect(ok_button_clicked)
    buttons_widget = QWidget()
    buttons_widget.setLayout(QHBoxLayout())
    buttons_widget.layout().addWidget(defaults_button)
    buttons_widget.layout().addWidget(cancel_button)
    buttons_widget.layout().addWidget(ok_button)
    wnd.layout().addWidget(buttons_widget)
    wnd.exec_()
minusdm_settings_button.clicked.connect(minusdm_button_clicked)
minusdm_widget.layout().addWidget(minusdm_settings_button)
minusdm_checkbox = QCheckBox()
minusdm_checkbox.clicked.connect(
    lambda: indicator_box_clicked(
        minusdm_checkbox, minusdm_panel_cb.currentIndex(), "talib.MINUS_DM", [14], selected_ta
    )
)
minusdm_widget.layout().addWidget(minusdm_checkbox)
momentum_widget.layout().addWidget(minusdm_widget)

# add momentum to momentum indicator scrollable
mom_widget = QWidget()
mom_widget.setLayout(QHBoxLayout())
mom_widget.layout().addWidget(QLabel("Momentum"))
mom_panel_cb = QComboBox()
mom_panel_cb.addItems(ta_combobox_items)
mom_panel_cb.currentTextChanged.connect(
    lambda state: change_indicator_panel(
        "talib.MOM", state, selected_ta[get_indicator_index("talib.MOM")][2]
    )
    if mom_checkbox.isChecked()
    else None
)
mom_widget.layout().addWidget(mom_panel_cb)
mom_settings_button = QPushButton()
mom_settings_button.setVisible(False)
size_retain = mom_settings_button.sizePolicy()
size_retain.setRetainSizeWhenHidden(True)
mom_settings_button.setSizePolicy(size_retain)
mom_settings_button.setIcon(GEAR_ICON)
mom_widget.enterEvent = lambda event: on_enter(event, mom_widget, mom_settings_button)
mom_widget.leaveEvent = lambda event: on_exit(event, mom_widget, mom_settings_button)
def mom_button_clicked():
    """
    Displays a separate window with adjustable settings for the mom indicator
    """
    wnd = QDialog(widget)
    wnd.setWindowTitle("Momentum")
    wnd.setLayout(QVBoxLayout())
    period_widget = QWidget()
    period_widget.setLayout(QHBoxLayout())
    period_spinbox = QSpinBox()
    period_spinbox.setValue(selected_ta[get_indicator_index(
        "talib.MOM")][2][0] if mom_checkbox.isChecked() else 10)
    period_widget.layout().addWidget(QLabel("Period"))
    period_widget.layout().addWidget(period_spinbox)
    wnd.layout().addWidget(period_widget)

    defaults_button = QPushButton("Reset to Defaults")
    defaults_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    defaults_button.clicked.connect(lambda: period_spinbox.setValue(10))
    cancel_button = QPushButton("Cancel")
    cancel_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    cancel_button.clicked.connect(lambda: wnd.done(0))
    ok_button = QPushButton("Save" if mom_checkbox.isChecked() else "Save and Add")
    ok_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    def ok_button_clicked():
        settings_tuple = ("talib.MOM", mom_panel_cb.currentIndex(), [period_spinbox.value()])

        if mom_checkbox.isChecked():
            selected_ta[get_indicator_index("talib.MOM")] = settings_tuple
        else:
            selected_ta.append(settings_tuple)
            mom_checkbox.setChecked(True)

        wnd.done(0)
    ok_button.clicked.connect(ok_button_clicked)
    buttons_widget = QWidget()
    buttons_widget.setLayout(QHBoxLayout())
    buttons_widget.layout().addWidget(defaults_button)
    buttons_widget.layout().addWidget(cancel_button)
    buttons_widget.layout().addWidget(ok_button)
    wnd.layout().addWidget(buttons_widget)
    wnd.exec_()
mom_settings_button.clicked.connect(mom_button_clicked)
mom_widget.layout().addWidget(mom_settings_button)
mom_checkbox = QCheckBox()
mom_checkbox.clicked.connect(
    lambda: indicator_box_clicked(
        mom_checkbox, mom_panel_cb.currentIndex(), "talib.MOM", [10], selected_ta
    )
)
mom_widget.layout().addWidget(mom_checkbox)
momentum_widget.layout().addWidget(mom_widget)

# add plus directional indicator to momentum indicator scrollable
plusdi_widget = QWidget()
plusdi_widget.setLayout(QHBoxLayout())
plusdi_widget.layout().addWidget(QLabel("Plus Directional Indicator"))
plusdi_panel_cb = QComboBox()
plusdi_panel_cb.addItems(ta_combobox_items)
plusdi_panel_cb.currentTextChanged.connect(
    lambda state: change_indicator_panel(
        "talib.PLUS_DI", state, selected_ta[get_indicator_index("talib.PLUS_DI")][2]
    )
    if plusdi_checkbox.isChecked()
    else None
)
plusdi_widget.layout().addWidget(plusdi_panel_cb)
plusdi_settings_button = QPushButton()
plusdi_settings_button.setVisible(False)
size_retain = plusdi_settings_button.sizePolicy()
size_retain.setRetainSizeWhenHidden(True)
plusdi_settings_button.setSizePolicy(size_retain)
plusdi_settings_button.setIcon(GEAR_ICON)
plusdi_widget.enterEvent = lambda event: on_enter(event, plusdi_widget, plusdi_settings_button)
plusdi_widget.leaveEvent = lambda event: on_exit(event, plusdi_widget, plusdi_settings_button)
def plusdi_button_clicked():
    """
    Displays a separate window with adjustable settings for the plusdi indicator
    """
    wnd = QDialog(widget)
    wnd.setWindowTitle("Plus Directional Indicator")
    wnd.setLayout(QVBoxLayout())
    period_widget = QWidget()
    period_widget.setLayout(QHBoxLayout())
    period_spinbox = QSpinBox()
    period_spinbox.setValue(selected_ta[get_indicator_index(
        "talib.PLUS_DI")][2][0] if plusdi_checkbox.isChecked() else 14)
    period_widget.layout().addWidget(QLabel("Period"))
    period_widget.layout().addWidget(period_spinbox)
    wnd.layout().addWidget(period_widget)

    defaults_button = QPushButton("Reset to Defaults")
    defaults_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    defaults_button.clicked.connect(lambda: period_spinbox.setValue(10))
    cancel_button = QPushButton("Cancel")
    cancel_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    cancel_button.clicked.connect(lambda: wnd.done(0))
    ok_button = QPushButton("Save" if plusdi_checkbox.isChecked() else "Save and Add")
    ok_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    def ok_button_clicked():
        settings_tuple = (
            "talib.PLUS_DI", plusdi_panel_cb.currentIndex(), [period_spinbox.value()]
        )

        if plusdi_checkbox.isChecked():
            selected_ta[get_indicator_index("talib.PLUS_DI")] = settings_tuple
        else:
            selected_ta.append(settings_tuple)
            plusdi_checkbox.setChecked(True)

        wnd.done(0)
    ok_button.clicked.connect(ok_button_clicked)
    buttons_widget = QWidget()
    buttons_widget.setLayout(QHBoxLayout())
    buttons_widget.layout().addWidget(defaults_button)
    buttons_widget.layout().addWidget(cancel_button)
    buttons_widget.layout().addWidget(ok_button)
    wnd.layout().addWidget(buttons_widget)
    wnd.exec_()
plusdi_settings_button.clicked.connect(plusdi_button_clicked)
plusdi_widget.layout().addWidget(plusdi_settings_button)
plusdi_checkbox = QCheckBox()
plusdi_checkbox.clicked.connect(
    lambda: indicator_box_clicked(
        plusdi_checkbox, plusdi_panel_cb.currentIndex(), "talib.PLUS_DI", [14], selected_ta
    )
)
plusdi_widget.layout().addWidget(plusdi_checkbox)
momentum_widget.layout().addWidget(plusdi_widget)

# add plus directional movement to momentum indicator scrollable
plusdm_widget = QWidget()
plusdm_widget.setLayout(QHBoxLayout())
plusdm_widget.layout().addWidget(QLabel("Plus Directional Movement"))
plusdm_panel_cb = QComboBox()
plusdm_panel_cb.addItems(ta_combobox_items)
plusdm_panel_cb.currentTextChanged.connect(
    lambda state: change_indicator_panel(
        "talib.PLUS_DM", state, selected_ta[get_indicator_index("talib.PLUS_DM")][2]
    )
    if plusdm_checkbox.isChecked()
    else None
)
plusdm_widget.layout().addWidget(plusdm_panel_cb)
plusdm_settings_button = QPushButton()
plusdm_settings_button.setVisible(False)
size_retain = plusdm_settings_button.sizePolicy()
size_retain.setRetainSizeWhenHidden(True)
plusdm_settings_button.setSizePolicy(size_retain)
plusdm_settings_button.setIcon(GEAR_ICON)
plusdm_widget.enterEvent = lambda event: on_enter(event, plusdm_widget, plusdm_settings_button)
plusdm_widget.leaveEvent = lambda event: on_exit(event, plusdm_widget, plusdm_settings_button)
def plusdm_button_clicked():
    """
    Displays a separate window with adjustable settings for the plusdm indicator
    """
    wnd = QDialog(widget)
    wnd.setWindowTitle("Plus Directional Movement")
    wnd.setLayout(QVBoxLayout())
    period_widget = QWidget()
    period_widget.setLayout(QHBoxLayout())
    period_spinbox = QSpinBox()
    period_spinbox.setValue(selected_ta[get_indicator_index(
        "talib.PLUS_DM")][2][0] if plusdm_checkbox.isChecked() else 14)
    period_widget.layout().addWidget(QLabel("Period"))
    period_widget.layout().addWidget(period_spinbox)
    wnd.layout().addWidget(period_widget)

    defaults_button = QPushButton("Reset to Defaults")
    defaults_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    defaults_button.clicked.connect(lambda: period_spinbox.setValue(10))
    cancel_button = QPushButton("Cancel")
    cancel_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    cancel_button.clicked.connect(lambda: wnd.done(0))
    ok_button = QPushButton("Save" if plusdm_checkbox.isChecked() else "Save and Add")
    ok_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    def ok_button_clicked():
        settings_tuple = ("talib.PLUS_DM", plusdm_panel_cb.currentIndex(), [period_spinbox.value()]
        )

        if plusdm_checkbox.isChecked():
            selected_ta[get_indicator_index("talib.PLUS_DM")] = settings_tuple
        else:
            selected_ta.append(settings_tuple)
            plusdm_checkbox.setChecked(True)

        wnd.done(0)
    ok_button.clicked.connect(ok_button_clicked)
    buttons_widget = QWidget()
    buttons_widget.setLayout(QHBoxLayout())
    buttons_widget.layout().addWidget(defaults_button)
    buttons_widget.layout().addWidget(cancel_button)
    buttons_widget.layout().addWidget(ok_button)
    wnd.layout().addWidget(buttons_widget)
    wnd.exec_()
plusdm_settings_button.clicked.connect(plusdm_button_clicked)
plusdm_widget.layout().addWidget(plusdm_settings_button)
plusdm_checkbox = QCheckBox()
plusdm_checkbox.clicked.connect(
    lambda: indicator_box_clicked(
        plusdm_checkbox, plusdm_panel_cb.currentIndex(), "talib.PLUS_DM", [14], selected_ta
    )
)
plusdm_widget.layout().addWidget(plusdm_checkbox)
momentum_widget.layout().addWidget(plusdm_widget)

# add percentage price oscillator to momentum indicator scrollable
kama_widget = QWidget()
kama_widget.setLayout(QHBoxLayout())
kama_widget.layout().addWidget(QLabel("KAMA Indicator"))
kama_panel_cb = QComboBox()
kama_panel_cb.addItems(ta_combobox_items)
kama_panel_cb.currentTextChanged.connect(
    lambda state: change_indicator_panel(
        "ta.momentum.kama", state, selected_ta[get_indicator_index("ta.momentum.kama")][2]
    )
    if kama_checkbox.isChecked()
    else None
)
kama_widget.layout().addWidget(kama_panel_cb)
kama_settings_button = QPushButton()
kama_settings_button.setVisible(False)
size_retain = kama_settings_button.sizePolicy()
size_retain.setRetainSizeWhenHidden(True)
kama_settings_button.setSizePolicy(size_retain)
kama_settings_button.setIcon(GEAR_ICON)
kama_widget.enterEvent = lambda event: on_enter(event, kama_widget, kama_settings_button)
kama_widget.leaveEvent = lambda event: on_exit(event, kama_widget, kama_settings_button)
def kama_button_clicked():
    """
    Displays a separate window with adjustable settings for the kama indicator
    """
    wnd = QDialog(widget)
    wnd.setWindowTitle("KAMA Indicator")
    wnd.setLayout(QVBoxLayout())
    er_widget = QWidget()
    er_widget.setLayout(QHBoxLayout())
    er_spinbox = QSpinBox()
    er_spinbox.setValue(selected_ta[get_indicator_index(
        "ta.momentum.kama")][2][0] if kama_checkbox.isChecked() else 10)
    er_widget.layout().addWidget(QLabel("Efficiency Ratio"))
    er_widget.layout().addWidget(er_spinbox)
    wnd.layout().addWidget(er_widget)

    fastma_widget = QWidget()
    fastma_widget.setLayout(QHBoxLayout())
    fastma_spinbox = QSpinBox()
    fastma_spinbox.setValue(selected_ta[get_indicator_index(
        "ta.momentum.kama")][2][1] if kama_checkbox.isChecked() else 2)
    fastma_widget.layout().addWidget(QLabel("Fast EMA Period"))
    fastma_widget.layout().addWidget(fastma_spinbox)
    wnd.layout().addWidget(fastma_widget)

    slowma_widget = QWidget()
    slowma_widget.setLayout(QHBoxLayout())
    slowma_spinbox = QSpinBox()
    slowma_spinbox.setValue(selected_ta[get_indicator_index(
        "ta.momentum.kama")][2][2] if kama_checkbox.isChecked() else 30)
    slowma_widget.layout().addWidget(QLabel("Slow EMA Period"))
    slowma_widget.layout().addWidget(slowma_spinbox)
    wnd.layout().addWidget(slowma_widget)

    defaults_button = QPushButton("Reset to Defaults")
    defaults_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    def restore_defaults():
        er_spinbox.setValue(12)
        fastma_spinbox.setValue(26)
        slowma_spinbox.setValue(9)
    defaults_button.clicked.connect(restore_defaults)
    cancel_button = QPushButton("Cancel")
    cancel_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    cancel_button.clicked.connect(lambda: wnd.done(0))
    ok_button = QPushButton("Save" if kama_checkbox.isChecked() else "Save and Add")
    ok_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    def ok_button_clicked():
        new_vals = [
            er_spinbox.value(), fastma_spinbox.value(), slowma_spinbox.value()
        ]
        settings_tuple = ("ta.momentum.kama", kama_panel_cb.currentIndex(), new_vals)
        if kama_checkbox.isChecked():
            selected_ta[get_indicator_index("ta.momentum.kama")] = settings_tuple
        else:
            selected_ta.append(settings_tuple)
            kama_checkbox.setChecked(True)
        wnd.done(0)
    ok_button.clicked.connect(ok_button_clicked)
    buttons_widget = QWidget()
    buttons_widget.setLayout(QHBoxLayout())
    buttons_widget.layout().addWidget(defaults_button)
    buttons_widget.layout().addWidget(cancel_button)
    buttons_widget.layout().addWidget(ok_button)
    wnd.layout().addWidget(buttons_widget)
    wnd.exec_()
kama_settings_button.clicked.connect(kama_button_clicked)
kama_widget.layout().addWidget(kama_settings_button)
kama_checkbox = QCheckBox()
kama_checkbox.clicked.connect(
    lambda: indicator_box_clicked(
        kama_checkbox, kama_panel_cb.currentIndex(), "ta.momentum.kama", [10, 2, 30], selected_ta
    )
)
kama_widget.layout().addWidget(kama_checkbox)
momentum_widget.layout().addWidget(kama_widget)

# add percentage volume oscillator to momentum indicator scrollable
pvo_widget = QWidget()
pvo_widget.setLayout(QHBoxLayout())
pvo_widget.layout().addWidget(QLabel("Percentage Volume Oscillator"))
pvo_panel_cb = QComboBox()
pvo_panel_cb.addItems(ta_combobox_items)
pvo_panel_cb.currentTextChanged.connect(
    lambda state: change_indicator_panel(
        "ta.momentum.pvo", state, selected_ta[get_indicator_index("ta.momentum.pvo")][2]
    )
    if pvo_checkbox.isChecked()
    else None
)
pvo_widget.layout().addWidget(pvo_panel_cb)
pvo_settings_button = QPushButton()
pvo_settings_button.setVisible(False)
size_retain = pvo_settings_button.sizePolicy()
size_retain.setRetainSizeWhenHidden(True)
pvo_settings_button.setSizePolicy(size_retain)
pvo_settings_button.setIcon(GEAR_ICON)
pvo_widget.enterEvent = lambda event: on_enter(event, pvo_widget, pvo_settings_button)
pvo_widget.leaveEvent = lambda event: on_exit(event, pvo_widget, pvo_settings_button)
def pvo_button_clicked():
    """
    Displays a separate window with adjustable settings for the pvo indicator
    """
    wnd = QDialog(widget)
    wnd.setWindowTitle("Percentage Volume Oscillator")
    wnd.setLayout(QVBoxLayout())
    slowma_widget = QWidget()
    slowma_widget.setLayout(QHBoxLayout())
    slowma_spinbox = QSpinBox()
    slowma_spinbox.setValue(selected_ta[get_indicator_index(
        "ta.momentum.pvo")][2][0] if pvo_checkbox.isChecked() else 12)
    slowma_widget.layout().addWidget(QLabel("Slow MA Period"))
    slowma_widget.layout().addWidget(slowma_spinbox)
    wnd.layout().addWidget(slowma_widget)

    fastma_widget = QWidget()
    fastma_widget.setLayout(QHBoxLayout())
    fastma_spinbox = QSpinBox()
    fastma_spinbox.setValue(selected_ta[get_indicator_index(
        "ta.momentum.pvo")][2][1] if pvo_checkbox.isChecked() else 26)
    fastma_widget.layout().addWidget(QLabel("Fast MA Period"))
    fastma_widget.layout().addWidget(fastma_spinbox)
    wnd.layout().addWidget(fastma_widget)

    signal_widget = QWidget()
    signal_widget.setLayout(QHBoxLayout())
    signal_spinbox = QSpinBox()
    signal_spinbox.setValue(selected_ta[get_indicator_index(
        "ta.momentum.pvo")][2][2] if pvo_checkbox.isChecked() else 9)
    signal_widget.layout().addWidget(QLabel("Signal Period"))
    signal_widget.layout().addWidget(signal_spinbox)
    wnd.layout().addWidget(signal_widget)

    defaults_button = QPushButton("Reset to Defaults")
    defaults_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    def restore_defaults():
        slowma_spinbox.setValue(12)
        fastma_spinbox.setValue(26)
        signal_spinbox.setValue(9)
    defaults_button.clicked.connect(restore_defaults)
    cancel_button = QPushButton("Cancel")
    cancel_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    cancel_button.clicked.connect(lambda: wnd.done(0))
    ok_button = QPushButton("Save" if pvo_checkbox.isChecked() else "Save and Add")
    ok_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    def ok_button_clicked():
        new_vals = [
            slowma_spinbox.value(), fastma_spinbox.value(), signal_spinbox.value()
        ]
        settings_tuple = ("ta.momentum.pvo", pvo_panel_cb.currentIndex(), new_vals)
        if pvo_checkbox.isChecked():
            selected_ta[get_indicator_index("ta.momentum.pvo")] = settings_tuple
        else:
            selected_ta.append(settings_tuple)
            pvo_checkbox.setChecked(True)
        wnd.done(0)
    ok_button.clicked.connect(ok_button_clicked)
    buttons_widget = QWidget()
    buttons_widget.setLayout(QHBoxLayout())
    buttons_widget.layout().addWidget(defaults_button)
    buttons_widget.layout().addWidget(cancel_button)
    buttons_widget.layout().addWidget(ok_button)
    wnd.layout().addWidget(buttons_widget)
    wnd.exec_()
pvo_settings_button.clicked.connect(pvo_button_clicked)
pvo_widget.layout().addWidget(pvo_settings_button)
pvo_checkbox = QCheckBox()
pvo_checkbox.clicked.connect(
    lambda: indicator_box_clicked(
        pvo_checkbox, pvo_panel_cb.currentIndex(), "ta.momentum.pvo", [12, 26, 9], selected_ta
    )
)
pvo_widget.layout().addWidget(pvo_checkbox)
momentum_widget.layout().addWidget(pvo_widget)

# add rate of change indicator to momentum indicator scrollable
roc_widget = QWidget()
roc_widget.setLayout(QHBoxLayout())
roc_widget.layout().addWidget(QLabel("Rate of Change"))
roc_panel_cb = QComboBox()
roc_panel_cb.addItems(ta_combobox_items)
roc_panel_cb.currentTextChanged.connect(
    lambda state: change_indicator_panel(
        "talib.ROC", state, selected_ta[get_indicator_index("talib.ROC")][2]
    )
    if roc_checkbox.isChecked()
    else None
)
roc_widget.layout().addWidget(roc_panel_cb)
roc_settings_button = QPushButton()
roc_settings_button.setVisible(False)
size_retain = roc_settings_button.sizePolicy()
size_retain.setRetainSizeWhenHidden(True)
roc_settings_button.setSizePolicy(size_retain)
roc_settings_button.setIcon(GEAR_ICON)
roc_widget.enterEvent = lambda event: on_enter(event, roc_widget, roc_settings_button)
roc_widget.leaveEvent = lambda event: on_exit(event, roc_widget, roc_settings_button)
def roc_button_clicked():
    """
    Displays a separate window with adjustable settings for the roc indicator
    """
    wnd = QDialog(widget)
    wnd.setWindowTitle("Rate of Change")
    wnd.setLayout(QVBoxLayout())
    period_widget = QWidget()
    period_widget.setLayout(QHBoxLayout())
    period_spinbox = QSpinBox()
    period_spinbox.setValue(selected_ta[get_indicator_index(
        "talib.ROC")][2][0] if roc_checkbox.isChecked() else 10)
    period_widget.layout().addWidget(QLabel("Period"))
    period_widget.layout().addWidget(period_spinbox)
    wnd.layout().addWidget(period_widget)
    defaults_button = QPushButton("Reset to Defaults")
    defaults_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    defaults_button.clicked.connect(lambda: period_spinbox.setValue(10))
    cancel_button = QPushButton("Cancel")
    cancel_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    cancel_button.clicked.connect(lambda: wnd.done(0))
    ok_button = QPushButton("Save" if roc_checkbox.isChecked() else "Save and Add")
    ok_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    def ok_button_clicked():
        settings_tuple = ("talib.ROC", roc_panel_cb.currentIndex(), [period_spinbox.value()])

        if roc_checkbox.isChecked():
            selected_ta[get_indicator_index("talib.ROC")] = settings_tuple
        else:
            selected_ta.append(settings_tuple)
            roc_checkbox.setChecked(True)

        wnd.done(0)
    ok_button.clicked.connect(ok_button_clicked)
    buttons_widget = QWidget()
    buttons_widget.setLayout(QHBoxLayout())
    buttons_widget.layout().addWidget(defaults_button)
    buttons_widget.layout().addWidget(cancel_button)
    buttons_widget.layout().addWidget(ok_button)
    wnd.layout().addWidget(buttons_widget)
    wnd.exec_()
roc_settings_button.clicked.connect(roc_button_clicked)
roc_widget.layout().addWidget(roc_settings_button)
roc_checkbox = QCheckBox()
roc_checkbox.clicked.connect(
    lambda: indicator_box_clicked(
        roc_checkbox, roc_panel_cb.currentIndex(), "talib.ROC", [10], selected_ta
    )
)
roc_widget.layout().addWidget(roc_checkbox)
momentum_widget.layout().addWidget(roc_widget)

# add ROC percentage to momentum indicator scrollable
rocp_widget = QWidget()
rocp_widget.setLayout(QHBoxLayout())
rocp_widget.layout().addWidget(QLabel("ROC Percentage"))
rocp_panel_cb = QComboBox()
rocp_panel_cb.addItems(ta_combobox_items)
rocp_panel_cb.currentTextChanged.connect(
    lambda state: change_indicator_panel(
        "talib.ROCP", state, selected_ta[get_indicator_index("talib.ROCP")][2]
    )
    if rocp_checkbox.isChecked()
    else None
)
rocp_widget.layout().addWidget(rocp_panel_cb)
rocp_settings_button = QPushButton()
rocp_settings_button.setVisible(False)
size_retain = rocp_settings_button.sizePolicy()
size_retain.setRetainSizeWhenHidden(True)
rocp_settings_button.setSizePolicy(size_retain)
rocp_settings_button.setIcon(GEAR_ICON)
rocp_widget.enterEvent = lambda event: on_enter(event, rocp_widget, rocp_settings_button)
rocp_widget.leaveEvent = lambda event: on_exit(event, rocp_widget, rocp_settings_button)
def rocp_button_clicked():
    """
    Displays a separate window with adjustable settings for the rocp indicator
    """
    wnd = QDialog(widget)
    wnd.setWindowTitle("ROC Percentage")
    wnd.setLayout(QVBoxLayout())
    period_widget = QWidget()
    period_widget.setLayout(QHBoxLayout())
    period_spinbox = QSpinBox()
    period_spinbox.setValue(selected_ta[get_indicator_index(
        "talib.ROCP")][2][0] if rocp_checkbox.isChecked() else 10)
    period_widget.layout().addWidget(QLabel("Period"))
    period_widget.layout().addWidget(period_spinbox)
    wnd.layout().addWidget(period_widget)
    defaults_button = QPushButton("Reset to Defaults")
    defaults_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    defaults_button.clicked.connect(lambda: period_spinbox.setValue(10))
    cancel_button = QPushButton("Cancel")
    cancel_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    cancel_button.clicked.connect(lambda: wnd.done(0))
    ok_button = QPushButton("Save" if rocp_checkbox.isChecked() else "Save and Add")
    ok_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    def ok_button_clicked():
        settings_tuple = ("talib.ROCP", rocp_panel_cb.currentIndex(), [period_spinbox.value()])

        if rocp_checkbox.isChecked():
            selected_ta[get_indicator_index("talib.ROCP")] = settings_tuple
        else:
            selected_ta.append(settings_tuple)
            rocp_checkbox.setChecked(True)

        wnd.done(0)
    ok_button.clicked.connect(ok_button_clicked)
    buttons_widget = QWidget()
    buttons_widget.setLayout(QHBoxLayout())
    buttons_widget.layout().addWidget(defaults_button)
    buttons_widget.layout().addWidget(cancel_button)
    buttons_widget.layout().addWidget(ok_button)
    wnd.layout().addWidget(buttons_widget)
    wnd.exec_()
rocp_settings_button.clicked.connect(rocp_button_clicked)
rocp_widget.layout().addWidget(rocp_settings_button)
rocp_checkbox = QCheckBox()
rocp_checkbox.clicked.connect(
    lambda: indicator_box_clicked(
        rocp_checkbox, rocp_panel_cb.currentIndex(), "talib.ROCP", [10], selected_ta
    )
)
rocp_widget.layout().addWidget(rocp_checkbox)
momentum_widget.layout().addWidget(rocp_widget)

# add rate of change ratio to momentum indicator scrollable
rocr_widget = QWidget()
rocr_widget.setLayout(QHBoxLayout())
rocr_label = QLabel("ROCR Ratio")
rocr_widget.layout().addWidget(rocr_label)
rocr_label.setAutoFillBackground(False)
rocr_panel_cb = QComboBox()
rocr_panel_cb.addItems(ta_combobox_items)
rocr_panel_cb.currentTextChanged.connect(
    lambda state: change_indicator_panel(
        "talib.ROCR", state, selected_ta[get_indicator_index("talib.ROCR")][2]
    )
    if rocr_checkbox.isChecked()
    else None
)
rocr_widget.layout().addWidget(rocr_panel_cb)
rocr_settings_button = QPushButton()
rocr_settings_button.setVisible(False)
size_retain = rocr_settings_button.sizePolicy()
size_retain.setRetainSizeWhenHidden(True)
rocr_settings_button.setSizePolicy(size_retain)
rocr_settings_button.setIcon(GEAR_ICON)
rocr_widget.enterEvent = lambda event: on_enter(event, rocr_widget, rocr_settings_button)
rocr_widget.leaveEvent = lambda event: on_exit(event, rocr_widget, rocr_settings_button)
def rocr_button_clicked():
    """
    Displays a separate window with adjustable settings for the rocr indicator
    """
    wnd = QDialog(widget)
    wnd.setWindowTitle("ROCR Ratio")
    wnd.setLayout(QVBoxLayout())
    period_widget = QWidget()
    period_widget.setLayout(QHBoxLayout())
    period_spinbox = QSpinBox()
    period_spinbox.setValue(selected_ta[get_indicator_index(
        "talib.ROCR")][2][0] if rocr_checkbox.isChecked() else 10)
    period_widget.layout().addWidget(QLabel("Period"))
    period_widget.layout().addWidget(period_spinbox)
    wnd.layout().addWidget(period_widget)

    defaults_button = QPushButton("Reset to Defaults")
    defaults_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    defaults_button.clicked.connect(lambda: period_spinbox.setValue(10))
    cancel_button = QPushButton("Cancel")
    cancel_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    cancel_button.clicked.connect(lambda: wnd.done(0))
    ok_button = QPushButton("Save" if rocr_checkbox.isChecked() else "Save and Add")
    ok_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    def ok_button_clicked():
        settings_tuple = ("talib.ROCR", rocr_panel_cb.currentIndex(), [period_spinbox.value()])

        if rocr_checkbox.isChecked():
            selected_ta[get_indicator_index("talib.ROCR")] = settings_tuple
        else:
            selected_ta.append(settings_tuple)
            rocr_checkbox.setChecked(True)

        wnd.done(0)
    ok_button.clicked.connect(ok_button_clicked)
    buttons_widget = QWidget()
    buttons_widget.setLayout(QHBoxLayout())
    buttons_widget.layout().addWidget(defaults_button)
    buttons_widget.layout().addWidget(cancel_button)
    buttons_widget.layout().addWidget(ok_button)
    wnd.layout().addWidget(buttons_widget)
    wnd.exec_()
rocr_settings_button.clicked.connect(rocr_button_clicked)
rocr_widget.layout().addWidget(rocr_settings_button)
rocr_checkbox = QCheckBox()
rocr_checkbox.clicked.connect(
    lambda: indicator_box_clicked(
        rocr_checkbox, rocr_panel_cb.currentIndex(), "talib.ROCR", [10], selected_ta
    )
)
rocr_widget.layout().addWidget(rocr_checkbox)
momentum_widget.layout().addWidget(rocr_widget)

# add 100-scale ROCR to momentum indicator scrollable
rocr100_widget = QWidget()
rocr100_widget.setLayout(QHBoxLayout())
rocr100_widget.layout().addWidget(QLabel("ROCR Indexed to 100"))
rocr100_cb = QComboBox()
rocr100_cb.addItems(ta_combobox_items)
rocr100_cb.currentTextChanged.connect(
    lambda state: change_indicator_panel(
        "talib.ROCR100", state, selected_ta[get_indicator_index("talib.ROCR100")][2]
    )
    if rocr100_checkbox.isChecked()
    else None
)
rocr100_widget.layout().addWidget(rocr100_cb)
rocr100_settings_button = QPushButton()
rocr100_settings_button.setVisible(False)
size_retain = rocr100_settings_button.sizePolicy()
size_retain.setRetainSizeWhenHidden(True)
rocr100_settings_button.setSizePolicy(size_retain)
rocr100_settings_button.setIcon(GEAR_ICON)
rocr100_widget.enterEvent = lambda event: on_enter(event, rocr100_widget, rocr100_settings_button)
rocr100_widget.leaveEvent = lambda event: on_exit(event, rocr100_widget, rocr100_settings_button)
def rocr100_button_clicked():
    """
    Displays a separate window with adjustable settings for the rocr100 indicator
    """
    wnd = QDialog(widget)
    wnd.setWindowTitle("ROCR Indexed to 100")
    wnd.setLayout(QVBoxLayout())
    period_widget = QWidget()
    period_widget.setLayout(QHBoxLayout())
    period_spinbox = QSpinBox()
    period_spinbox.setValue(selected_ta[get_indicator_index(
        "talib.ROCR100")][2][0] if rocr100_checkbox.isChecked() else 10)
    period_widget.layout().addWidget(QLabel("Period"))
    period_widget.layout().addWidget(period_spinbox)
    wnd.layout().addWidget(period_widget)

    defaults_button = QPushButton("Reset to Defaults")
    defaults_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    defaults_button.clicked.connect(lambda: period_spinbox.setValue(10))
    cancel_button = QPushButton("Cancel")
    cancel_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    cancel_button.clicked.connect(lambda: wnd.done(0))
    ok_button = QPushButton("Save" if rocr100_checkbox.isChecked() else "Save and Add")
    ok_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    def ok_button_clicked():
        settings_tuple = ("talib.ROCR100", rocr100_cb.currentIndex(), [period_spinbox.value()])

        if rocr100_checkbox.isChecked():
            selected_ta[get_indicator_index("talib.ROCR100")] = settings_tuple
        else:
            selected_ta.append(settings_tuple)
            rocr100_checkbox.setChecked(True)

        wnd.done(0)
    ok_button.clicked.connect(ok_button_clicked)
    buttons_widget = QWidget()
    buttons_widget.setLayout(QHBoxLayout())
    buttons_widget.layout().addWidget(defaults_button)
    buttons_widget.layout().addWidget(cancel_button)
    buttons_widget.layout().addWidget(ok_button)
    wnd.layout().addWidget(buttons_widget)
    wnd.exec_()
rocr100_settings_button.clicked.connect(rocr100_button_clicked)
rocr100_widget.layout().addWidget(rocr100_settings_button)
rocr100_checkbox = QCheckBox()
rocr100_checkbox.clicked.connect(
    lambda: indicator_box_clicked(
        rocr100_checkbox,
        rocr100_cb.currentIndex(),
        "talib.ROCR100",
        [10],
        selected_ta
    )
)
rocr100_widget.layout().addWidget(rocr100_checkbox)
momentum_widget.layout().addWidget(rocr100_widget)

# add relative strength index to momentum indicator scrollable
rsi_widget = QWidget()
rsi_widget.setLayout(QHBoxLayout())
rsi_widget.layout().addWidget(QLabel("Relative Strength Index"))
rsi_panel_cb = QComboBox()
rsi_panel_cb.addItems(ta_combobox_items)
rsi_panel_cb.currentTextChanged.connect(
    lambda state: change_indicator_panel(
        "talib.RSI", state, selected_ta[get_indicator_index("talib.RSI")][2]
    )
    if rsi_checkbox.isChecked()
    else None
)
rsi_widget.layout().addWidget(rsi_panel_cb)
rsi_settings_button = QPushButton()
rsi_settings_button.setVisible(False)
size_retain = rsi_settings_button.sizePolicy()
size_retain.setRetainSizeWhenHidden(True)
rsi_settings_button.setSizePolicy(size_retain)
rsi_settings_button.setIcon(GEAR_ICON)
rsi_widget.enterEvent = lambda event: on_enter(event, rsi_widget, rsi_settings_button)
rsi_widget.leaveEvent = lambda event: on_exit(event, rsi_widget, rsi_settings_button)
def rsi_button_clicked():
    """
    Displays a separate window with adjustable settings for the rsi indicator
    """
    wnd = QDialog(widget)
    wnd.setWindowTitle("Relative Strength Index")
    wnd.setLayout(QVBoxLayout())
    period_widget = QWidget()
    period_widget.setLayout(QHBoxLayout())
    period_spinbox = QSpinBox()
    period_spinbox.setValue(selected_ta[get_indicator_index(
        "talib.RSI")][2][0] if rsi_checkbox.isChecked() else 20)
    period_widget.layout().addWidget(QLabel("Period"))
    period_widget.layout().addWidget(period_spinbox)
    wnd.layout().addWidget(period_widget)

    defaults_button = QPushButton("Reset to Defaults")
    defaults_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    defaults_button.clicked.connect(lambda: period_spinbox.setValue(20))
    cancel_button = QPushButton("Cancel")
    cancel_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    cancel_button.clicked.connect(lambda: wnd.done(0))
    ok_button = QPushButton("Save" if rsi_checkbox.isChecked() else "Save and Add")
    ok_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    def ok_button_clicked():
        settings_tuple = ("talib.RSI", rsi_panel_cb.currentIndex(), [period_spinbox.value()])

        if rsi_checkbox.isChecked():
            selected_ta[get_indicator_index("talib.RSI")] = settings_tuple
        else:
            selected_ta.append(settings_tuple)
            rsi_checkbox.setChecked(True)

        wnd.done(0)
    ok_button.clicked.connect(ok_button_clicked)
    buttons_widget = QWidget()
    buttons_widget.setLayout(QHBoxLayout())
    buttons_widget.layout().addWidget(defaults_button)
    buttons_widget.layout().addWidget(cancel_button)
    buttons_widget.layout().addWidget(ok_button)
    wnd.layout().addWidget(buttons_widget)
    wnd.exec_()
rsi_settings_button.clicked.connect(rsi_button_clicked)
rsi_widget.layout().addWidget(rsi_settings_button)
rsi_checkbox = QCheckBox()
rsi_checkbox.clicked.connect(
    lambda: indicator_box_clicked(
        rsi_checkbox,
        rsi_panel_cb.currentIndex(),
        "talib.RSI",
        [20],
        selected_ta
    )
)
rsi_widget.layout().addWidget(rsi_checkbox)
momentum_widget.layout().addWidget(rsi_widget)

# add slow stochastic indicator to momentum indicator scrollable
slowstoch_widget = QWidget()
slowstoch_widget.setLayout(QHBoxLayout())
slowstoch_widget.layout().addWidget(QLabel("Slow Stochastic"))
slowstoch_panel_cb = QComboBox()
slowstoch_panel_cb.addItems(ta_combobox_items)
slowstoch_panel_cb.currentTextChanged.connect(
    lambda state: change_indicator_panel(
        "talib.STOCH", state, selected_ta[get_indicator_index("talib.STOCH")][2]
    )
    if slowstoch_checkbox.isChecked()
    else None
)
slowstoch_widget.layout().addWidget(slowstoch_panel_cb)
slowstoch_settings_button = QPushButton()
slowstoch_settings_button.setVisible(False)
size_retain = slowstoch_settings_button.sizePolicy()
size_retain.setRetainSizeWhenHidden(True)
slowstoch_settings_button.setSizePolicy(size_retain)
slowstoch_settings_button.setIcon(GEAR_ICON)
slowstoch_widget.enterEvent = lambda e: on_enter(e, slowstoch_widget, slowstoch_settings_button)
slowstoch_widget.leaveEvent = lambda e: on_exit(e, slowstoch_widget, slowstoch_settings_button)
def slowstoch_button_clicked():
    """
    Displays a separate window with adjustable settings for the slowstoch indicator
    """
    wnd = QDialog(widget)
    wnd.setWindowTitle("Parabolic SAR")
    wnd.setLayout(QVBoxLayout())
    fastk_widget = QWidget()
    fastk_widget.setLayout(QHBoxLayout())
    fastk_spinbox = QSpinBox()
    fastk_spinbox.setValue(selected_ta[get_indicator_index(
        "talib.STOCH")][2][0] if slowstoch_checkbox.isChecked() else 5)
    fastk_widget.layout().addWidget(QLabel("Fast %k Period"))
    fastk_widget.layout().addWidget(fastk_spinbox)
    wnd.layout().addWidget(fastk_widget)

    slowk_widget = QWidget()
    slowk_widget.setLayout(QHBoxLayout())
    slowk_spinbox = QSpinBox()
    slowk_spinbox.setValue(selected_ta[get_indicator_index(
        "talib.STOCH")][2][1] if slowstoch_checkbox.isChecked() else 3)
    slowk_widget.layout().addWidget(QLabel("Slow %k Period"))
    slowk_widget.layout().addWidget(slowk_spinbox)
    wnd.layout().addWidget(slowk_widget)

    slowk_matype_widget = QWidget()
    slowk_matype_widget.setLayout(QHBoxLayout())
    slowk_matype_spinbox = QSpinBox()
    slowk_matype_spinbox.setValue(selected_ta[get_indicator_index(
        "talib.STOCH")][2][2] if slowstoch_checkbox.isChecked() else 0)
    slowk_matype_widget.layout().addWidget(QLabel("Slow %k MA Type"))
    slowk_matype_widget.layout().addWidget(slowk_matype_spinbox)
    wnd.layout().addWidget(slowk_matype_widget)

    slowd_widget = QWidget()
    slowd_widget.setLayout(QHBoxLayout())
    slowd_spinbox = QSpinBox()
    slowd_spinbox.setValue(selected_ta[get_indicator_index(
        "talib.STOCH")][2][3] if slowstoch_checkbox.isChecked() else 3)
    slowd_widget.layout().addWidget(QLabel("Slow %d Period"))
    slowd_widget.layout().addWidget(slowd_spinbox)
    wnd.layout().addWidget(slowd_widget)

    slowd_matype_widget = QWidget()
    slowd_matype_widget.setLayout(QHBoxLayout())
    slowd_matype_spinbox = QSpinBox()
    slowd_matype_spinbox.setValue(selected_ta[get_indicator_index(
        "talib.STOCH")][2][4] if slowstoch_checkbox.isChecked() else 0)
    slowd_matype_widget.layout().addWidget(QLabel("Slow %d MA Type"))
    slowd_matype_widget.layout().addWidget(slowd_matype_spinbox)
    wnd.layout().addWidget(slowd_matype_widget)

    defaults_button = QPushButton("Reset to Defaults")
    defaults_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    def restore_defaults():
        fastk_spinbox.setValue(5)
        slowk_spinbox.setValue(3)
        slowk_matype_spinbox.setValue(0)
        slowd_spinbox.setValue(3)
        slowd_matype_spinbox.setValue(0)
    defaults_button.clicked.connect(restore_defaults)
    cancel_button = QPushButton("Cancel")
    cancel_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    cancel_button.clicked.connect(lambda: wnd.done(0))
    ok_button = QPushButton("Save" if slowstoch_checkbox.isChecked() else "Save and Add")
    ok_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    def ok_button_clicked():
        new_vals = [
            fastk_spinbox.value(),
            slowk_spinbox.value(),
            slowk_matype_spinbox.value(),
            slowd_spinbox.value(),
            slowd_matype_spinbox.value()
        ]
        settings_tuple = ("talib.STOCH", slowstoch_panel_cb.currentIndex(), new_vals)
        if slowstoch_checkbox.isChecked():
            selected_ta[get_indicator_index("talib.STOCH")] = settings_tuple
        else:
            selected_ta.append(settings_tuple)
            slowstoch_checkbox.setChecked(True)
        wnd.done(0)
    ok_button.clicked.connect(ok_button_clicked)
    buttons_widget = QWidget()
    buttons_widget.setLayout(QHBoxLayout())
    buttons_widget.layout().addWidget(defaults_button)
    buttons_widget.layout().addWidget(cancel_button)
    buttons_widget.layout().addWidget(ok_button)
    wnd.layout().addWidget(buttons_widget)
    wnd.exec_()
slowstoch_settings_button.clicked.connect(slowstoch_button_clicked)
slowstoch_widget.layout().addWidget(slowstoch_settings_button)
slowstoch_checkbox = QCheckBox()
slowstoch_checkbox.clicked.connect(
    lambda: indicator_box_clicked(
        slowstoch_checkbox,
        slowstoch_panel_cb.currentIndex(),
        "talib.STOCH",
        [5, 3, 0, 3, 0],
        selected_ta
    )
)
slowstoch_widget.layout().addWidget(slowstoch_checkbox)
momentum_widget.layout().addWidget(slowstoch_widget)

# add fast stochastic to momentum indicator scrollable
faststoch_widget = QWidget()
faststoch_widget.setLayout(QHBoxLayout())
faststoch_widget.layout().addWidget(QLabel("Fast Stochastic"))
faststoch_panel_cb = QComboBox()
faststoch_panel_cb.addItems(ta_combobox_items)
faststoch_panel_cb.currentTextChanged.connect(
    lambda state: change_indicator_panel(
        "talib.STOCHF",
        state,
        selected_ta[get_indicator_index("talib.STOCHF")][2]
    )
    if faststoch_checkbox.isChecked()
    else None
)
faststoch_widget.layout().addWidget(faststoch_panel_cb)
faststoch_settings_button = QPushButton()
faststoch_settings_button.setVisible(False)
size_retain = faststoch_settings_button.sizePolicy()
size_retain.setRetainSizeWhenHidden(True)
faststoch_settings_button.setSizePolicy(size_retain)
faststoch_settings_button.setIcon(GEAR_ICON)
faststoch_widget.enterEvent = lambda e: on_enter(e, faststoch_widget, faststoch_settings_button)
faststoch_widget.leaveEvent = lambda e: on_exit(e, faststoch_widget, faststoch_settings_button)
def faststoch_button_clicked():
    """
    Displays a separate window with adjustable settings for the faststoch indicator
    """
    wnd = QDialog(widget)
    wnd.setWindowTitle("Fast Stochastic")
    wnd.setLayout(QVBoxLayout())
    fastk_widget = QWidget()
    fastk_widget.setLayout(QHBoxLayout())
    fastk_spinbox = QSpinBox()
    fastk_spinbox.setValue(selected_ta[get_indicator_index(
        "talib.STOCHF")][2][0] if faststoch_checkbox.isChecked() else 5)
    fastk_widget.layout().addWidget(QLabel("Fast %k Period"))
    fastk_widget.layout().addWidget(fastk_spinbox)
    wnd.layout().addWidget(fastk_widget)

    fastd_widget = QWidget()
    fastd_widget.setLayout(QHBoxLayout())
    fastd_spinbox = QSpinBox()
    fastd_spinbox.setValue(selected_ta[get_indicator_index(
        "talib.STOCHF")][2][1] if faststoch_checkbox.isChecked() else 3)
    fastd_widget.layout().addWidget(QLabel("Fast %d Period"))
    fastd_widget.layout().addWidget(fastd_spinbox)
    wnd.layout().addWidget(fastd_widget)

    fastd_matype_widget = QWidget()
    fastd_matype_widget.setLayout(QHBoxLayout())
    fastd_matype_spinbox = QSpinBox()
    fastd_matype_spinbox.setValue(selected_ta[get_indicator_index(
        "talib.STOCHF")][2][2] if faststoch_checkbox.isChecked() else 0)
    fastd_matype_widget.layout().addWidget(QLabel("Fast %d MA Type"))
    fastd_matype_widget.layout().addWidget(fastd_matype_spinbox)
    wnd.layout().addWidget(fastd_matype_widget)

    defaults_button = QPushButton("Reset to Defaults")
    defaults_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    def restore_defaults():
        fastk_spinbox.setValue(5)
        fastd_spinbox.setValue(3)
        fastd_matype_spinbox.setValue(0)
    defaults_button.clicked.connect(restore_defaults)
    cancel_button = QPushButton("Cancel")
    cancel_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    cancel_button.clicked.connect(lambda: wnd.done(0))
    ok_button = QPushButton("Save" if faststoch_checkbox.isChecked() else "Save and Add")
    ok_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    def ok_button_clicked():
        new_vals = [fastk_spinbox.value(), fastd_spinbox.value(), fastd_matype_spinbox.value()]
        settings_tuple = ("talib.STOCHF", faststoch_panel_cb.currentIndex(), new_vals)
        if faststoch_checkbox.isChecked():
            selected_ta[get_indicator_index("talib.STOCHF")] = settings_tuple
        else:
            selected_ta.append(settings_tuple)
            faststoch_checkbox.setChecked(True)
        wnd.done(0)
    ok_button.clicked.connect(ok_button_clicked)
    buttons_widget = QWidget()
    buttons_widget.setLayout(QHBoxLayout())
    buttons_widget.layout().addWidget(defaults_button)
    buttons_widget.layout().addWidget(cancel_button)
    buttons_widget.layout().addWidget(ok_button)
    wnd.layout().addWidget(buttons_widget)
    wnd.exec_()
faststoch_settings_button.clicked.connect(faststoch_button_clicked)
faststoch_widget.layout().addWidget(faststoch_settings_button)
faststoch_checkbox = QCheckBox()
faststoch_checkbox.clicked.connect(
    lambda: indicator_box_clicked(
        faststoch_checkbox,
        faststoch_panel_cb.currentIndex(),
        "talib.STOCHF",
        [5, 3, 0],
        selected_ta
    )
)
faststoch_widget.layout().addWidget(faststoch_checkbox)
momentum_widget.layout().addWidget(faststoch_widget)

# add stochastic RSI to momentum indicator scrollable
stochrsi_widget = QWidget()
stochrsi_widget.setLayout(QHBoxLayout())
stochrsi_widget.layout().addWidget(QLabel("Stochastic RSI"))
stochrsi_panel_cb = QComboBox()
stochrsi_panel_cb.addItems(ta_combobox_items)
stochrsi_panel_cb.currentTextChanged.connect(
    lambda state: change_indicator_panel(
        "talib.STOCHRSI",
        state,
        selected_ta[get_indicator_index("talib.STOCHRSI")][2]
    )
    if stochrsi_checkbox.isChecked()
    else None
)
stochrsi_widget.layout().addWidget(stochrsi_panel_cb)
stochrsi_settings_button = QPushButton()
stochrsi_settings_button.setVisible(False)
size_retain = stochrsi_settings_button.sizePolicy()
size_retain.setRetainSizeWhenHidden(True)
stochrsi_settings_button.setSizePolicy(size_retain)
stochrsi_settings_button.setIcon(GEAR_ICON)
stochrsi_widget.enterEvent = lambda e: on_enter(e, stochrsi_widget, stochrsi_settings_button)
stochrsi_widget.leaveEvent = lambda e: on_exit(e, stochrsi_widget, stochrsi_settings_button)
def stochrsi_button_clicked():
    """
    Displays a separate window with adjustable settings for the stochrsi indicator
    """
    wnd = QDialog(widget)
    wnd.setWindowTitle("Stochastic RSI")
    wnd.setLayout(QVBoxLayout())

    period_widget = QWidget()
    period_widget.setLayout(QHBoxLayout())
    period_spinbox = QSpinBox()
    period_spinbox.setValue(selected_ta[get_indicator_index(
        "talib.STOCHRSI")][2][0] if stochrsi_checkbox.isChecked() else 14)
    period_widget.layout().addWidget(QLabel("RSI Period"))
    period_widget.layout().addWidget(period_spinbox)
    wnd.layout().addWidget(period_widget)

    fastk_widget = QWidget()
    fastk_widget.setLayout(QHBoxLayout())
    fastk_spinbox = QSpinBox()
    fastk_spinbox.setValue(selected_ta[get_indicator_index(
        "talib.STOCHRSI")][2][0] if stochrsi_checkbox.isChecked() else 5)
    fastk_widget.layout().addWidget(QLabel("Fast %k Period"))
    fastk_widget.layout().addWidget(fastk_spinbox)
    wnd.layout().addWidget(fastk_widget)

    fastd_widget = QWidget()
    fastd_widget.setLayout(QHBoxLayout())
    fastd_spinbox = QSpinBox()
    fastd_spinbox.setValue(selected_ta[get_indicator_index(
        "talib.STOCHRSI")][2][1] if stochrsi_checkbox.isChecked() else 3)
    fastd_widget.layout().addWidget(QLabel("Fast %d Period"))
    fastd_widget.layout().addWidget(fastd_spinbox)
    wnd.layout().addWidget(fastd_widget)

    fastd_matype_widget = QWidget()
    fastd_matype_widget.setLayout(QHBoxLayout())
    fastd_matype_spinbox = QSpinBox()
    fastd_matype_spinbox.setValue(selected_ta[get_indicator_index(
        "talib.STOCHRSI")][2][2] if stochrsi_checkbox.isChecked() else 0)
    fastd_matype_widget.layout().addWidget(QLabel("Fast %d MA Type"))
    fastd_matype_widget.layout().addWidget(fastd_matype_spinbox)
    wnd.layout().addWidget(fastd_matype_widget)

    defaults_button = QPushButton("Reset to Defaults")
    defaults_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    def restore_defaults():
        period_spinbox.setValue(14)
        fastk_spinbox.setValue(5)
        fastd_spinbox.setValue(3)
        fastd_matype_spinbox.setValue(0)
    defaults_button.clicked.connect(restore_defaults)
    cancel_button = QPushButton("Cancel")
    cancel_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    cancel_button.clicked.connect(lambda: wnd.done(0))
    ok_button = QPushButton("Save" if stochrsi_checkbox.isChecked() else "Save and Add")
    ok_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    def ok_button_clicked():
        new_vals = [
            period_spinbox.value(), fastk_spinbox.value(),
            fastd_spinbox.value(), fastd_matype_spinbox.value()
            ]
        settings_tuple = ("talib.STOCHRSI", stochrsi_panel_cb.currentIndex(), new_vals)
        if stochrsi_checkbox.isChecked():
            selected_ta[get_indicator_index("talib.STOCHRSI")] = settings_tuple
        else:
            selected_ta.append(settings_tuple)
            stochrsi_checkbox.setChecked(True)
        wnd.done(0)
    ok_button.clicked.connect(ok_button_clicked)
    buttons_widget = QWidget()
    buttons_widget.setLayout(QHBoxLayout())
    buttons_widget.layout().addWidget(defaults_button)
    buttons_widget.layout().addWidget(cancel_button)
    buttons_widget.layout().addWidget(ok_button)
    wnd.layout().addWidget(buttons_widget)
    wnd.exec_()
stochrsi_settings_button.clicked.connect(stochrsi_button_clicked)
stochrsi_widget.layout().addWidget(stochrsi_settings_button)
stochrsi_checkbox = QCheckBox()
stochrsi_checkbox.clicked.connect(
    lambda: indicator_box_clicked(
        stochrsi_checkbox,
        stochrsi_panel_cb.currentIndex(),
        "talib.STOCHRSI",
        [5, 3, 0],
        selected_ta
    )
)
stochrsi_widget.layout().addWidget(stochrsi_checkbox)
momentum_widget.layout().addWidget(stochrsi_widget)

# add true strength index to momentum indicator scrollable
tsi_widget = QWidget()
tsi_widget.setLayout(QHBoxLayout())
tsi_widget.layout().addWidget(QLabel("True Strength Index (TSI)"))
tsi_panel_cb = QComboBox()
tsi_panel_cb.addItems(ta_combobox_items)
tsi_panel_cb.currentTextChanged.connect(
    lambda state: change_indicator_panel(
        "ta.momentum.tsi",
        state,
        selected_ta[get_indicator_index("ta.momentum.tsi")][2]
    )
    if tsi_checkbox.isChecked()
    else None
)
tsi_widget.layout().addWidget(tsi_panel_cb)
tsi_settings_button = QPushButton()
tsi_settings_button.setVisible(False)
size_retain = tsi_settings_button.sizePolicy()
size_retain.setRetainSizeWhenHidden(True)
tsi_settings_button.setSizePolicy(size_retain)
tsi_settings_button.setIcon(GEAR_ICON)
tsi_widget.enterEvent = lambda e: on_enter(e, tsi_widget, tsi_settings_button)
tsi_widget.leaveEvent = lambda e: on_exit(e, tsi_widget, tsi_settings_button)
def tsi_button_clicked():
    """
    Displays a separate window with adjustable settings for the tsi indicator
    """
    wnd = QDialog(widget)
    wnd.setWindowTitle("True Strength Index")
    wnd.setLayout(QVBoxLayout())
    slow_period_widget = QWidget()
    slow_period_widget.setLayout(QHBoxLayout())
    slow_period_spinbox = QSpinBox()
    slow_period_spinbox.setValue(selected_ta[get_indicator_index(
        "ta.momentum.tsi")][2][0] if tsi_checkbox.isChecked() else 25)
    slow_period_widget.layout().addWidget(QLabel("Slow Period"))
    slow_period_widget.layout().addWidget(slow_period_spinbox)
    wnd.layout().addWidget(slow_period_widget)

    fast_period_widget = QWidget()
    fast_period_widget.setLayout(QHBoxLayout())
    fast_period_spinbox = QSpinBox()
    fast_period_spinbox.setValue(selected_ta[get_indicator_index(
        "ta.momentum.tsi")][2][1] if tsi_checkbox.isChecked() else 13)
    fast_period_widget.layout().addWidget(QLabel("Fast Period"))
    fast_period_widget.layout().addWidget(fast_period_spinbox)
    wnd.layout().addWidget(fast_period_widget)

    defaults_button = QPushButton("Reset to Defaults")
    defaults_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)

    def restore_defaults():
        fast_period_spinbox.setValue(13)
        slow_period_spinbox.setValue(25)

    defaults_button.clicked.connect(restore_defaults)
    cancel_button = QPushButton("Cancel")
    cancel_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    cancel_button.clicked.connect(lambda: wnd.done(0))
    ok_button = QPushButton("Save" if tsi_checkbox.isChecked() else "Save and Add")
    ok_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)

    def ok_button_clicked():
        new_vals =  [slow_period_spinbox.value(), fast_period_spinbox.value()]
        settings_tuple = ("ta.momentum.tsi", tsi_panel_cb.currentIndex(), new_vals)

        if tsi_checkbox.isChecked():
            selected_ta[get_indicator_index("ta.momentum.tsi")] = settings_tuple
        else:
            selected_ta.append(settings_tuple)
            tsi_checkbox.setChecked(True)
        wnd.done(0)

    ok_button.clicked.connect(ok_button_clicked)
    buttons_widget = QWidget()
    buttons_widget.setLayout(QHBoxLayout())
    buttons_widget.layout().addWidget(defaults_button)
    buttons_widget.layout().addWidget(cancel_button)
    buttons_widget.layout().addWidget(ok_button)
    wnd.layout().addWidget(buttons_widget)
    wnd.exec_()
tsi_settings_button.clicked.connect(tsi_button_clicked)
tsi_widget.layout().addWidget(tsi_settings_button)
tsi_checkbox = QCheckBox()
tsi_checkbox.clicked.connect(
    lambda: indicator_box_clicked(
        tsi_checkbox,
        tsi_panel_cb.currentIndex(),
        "ta.momentum.tsi",
        [13, 25],
        selected_ta
    )
)
tsi_widget.layout().addWidget(tsi_checkbox)
momentum_widget.layout().addWidget(tsi_widget)

# add ultimate oscillator to momentum indicator scrollable
ultosc_widget = QWidget()
ultosc_widget.setLayout(QHBoxLayout())
ultosc_widget.layout().addWidget(QLabel("Ultimate Oscillator"))
ultosc_panel_cb = QComboBox()
ultosc_panel_cb.addItems(ta_combobox_items)
ultosc_panel_cb.currentTextChanged.connect(
    lambda state: change_indicator_panel(
        "talib.ULTOSC",
        state,
        selected_ta[get_indicator_index("talib.ULTOSC")][2]
    )
    if ultosc_checkbox.isChecked()
    else None
)
ultosc_widget.layout().addWidget(ultosc_panel_cb)
ultosc_settings_button = QPushButton()
ultosc_settings_button.setVisible(False)
size_retain = ultosc_settings_button.sizePolicy()
size_retain.setRetainSizeWhenHidden(True)
ultosc_settings_button.setSizePolicy(size_retain)
ultosc_settings_button.setIcon(GEAR_ICON)
ultosc_widget.enterEvent = lambda e: on_enter(e, ultosc_widget, ultosc_settings_button)
ultosc_widget.leaveEvent = lambda e: on_exit(e, ultosc_widget, ultosc_settings_button)
def ultosc_button_clicked():
    """
    Displays a separate window with adjustable settings for the ultosc indicator
    """
    wnd = QDialog(widget)
    wnd.setWindowTitle("Ultimate Oscillator")
    wnd.setLayout(QVBoxLayout())
    fast_widget = QWidget()
    fast_widget.setLayout(QHBoxLayout())
    fast_spinbox = QSpinBox()
    fast_spinbox.setValue(selected_ta[get_indicator_index(
        "talib.ULTOSC")][2][0] if ultosc_checkbox.isChecked() else 7)
    fast_widget.layout().addWidget(QLabel("Fast Length"))
    fast_widget.layout().addWidget(fast_spinbox)
    wnd.layout().addWidget(fast_widget)

    medium_widget = QWidget()
    medium_widget.setLayout(QHBoxLayout())
    medium_spinbox = QSpinBox()
    medium_spinbox.setValue(selected_ta[get_indicator_index(
        "talib.ULTOSC")][2][1] if ultosc_checkbox.isChecked() else 14)
    medium_widget.layout().addWidget(QLabel("Medium Length"))
    medium_widget.layout().addWidget(medium_spinbox)
    wnd.layout().addWidget(medium_widget)

    slow_widget = QWidget()
    slow_widget.setLayout(QHBoxLayout())
    slow_spinbox = QSpinBox()
    slow_spinbox.setValue(selected_ta[get_indicator_index(
        "talib.ULTOSC")][2][2] if ultosc_checkbox.isChecked() else 28)
    slow_widget.layout().addWidget(QLabel("Slow Length"))
    slow_widget.layout().addWidget(slow_spinbox)
    wnd.layout().addWidget(slow_widget)

    defaults_button = QPushButton("Reset to Defaults")
    defaults_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    def restore_defaults():
        fast_spinbox.setValue(7)
        medium_spinbox.setValue(14)
        slow_spinbox.setValue(28)
    defaults_button.clicked.connect(restore_defaults)
    cancel_button = QPushButton("Cancel")
    cancel_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    cancel_button.clicked.connect(lambda: wnd.done(0))
    ok_button = QPushButton("Save" if ultosc_checkbox.isChecked() else "Save and Add")
    ok_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    def ok_button_clicked():
        new_vals = [fast_spinbox.value(), medium_spinbox.value(), slow_spinbox.value()]
        settings_tuple = ("talib.ULTOSC", ultosc_panel_cb.currentIndex(), new_vals)
        if ultosc_checkbox.isChecked():
            selected_ta[get_indicator_index("talib.ULTOSC")] = settings_tuple
        else:
            selected_ta.append(settings_tuple)
            ultosc_checkbox.setChecked(True)
        wnd.done(0)
    ok_button.clicked.connect(ok_button_clicked)
    buttons_widget = QWidget()
    buttons_widget.setLayout(QHBoxLayout())
    buttons_widget.layout().addWidget(defaults_button)
    buttons_widget.layout().addWidget(cancel_button)
    buttons_widget.layout().addWidget(ok_button)
    wnd.layout().addWidget(buttons_widget)
    wnd.exec_()
ultosc_settings_button.clicked.connect(ultosc_button_clicked)
ultosc_widget.layout().addWidget(ultosc_settings_button)
ultosc_checkbox = QCheckBox()
ultosc_checkbox.clicked.connect(
    lambda: indicator_box_clicked(
        ultosc_checkbox,
        ultosc_panel_cb.currentIndex(),
        "talib.ULTOSC",
        [7, 14, 28],
        selected_ta
    )
)
ultosc_widget.layout().addWidget(ultosc_checkbox)
momentum_widget.layout().addWidget(ultosc_widget)

# add williams %r to momentum indicator scrollable
willr_widget = QWidget()
willr_widget.setLayout(QHBoxLayout())
willr_widget.layout().addWidget(QLabel("Williams' %r"))
willr_panel_cb = QComboBox()
willr_panel_cb.addItems(ta_combobox_items)
willr_panel_cb.currentTextChanged.connect(
    lambda state: change_indicator_panel(
        "talib.WILLR",
        state,
        selected_ta[get_indicator_index("talib.WILLR")][2]
    )
    if willr_checkbox.isChecked()
    else None
)
willr_widget.layout().addWidget(willr_panel_cb)
willr_settings_button = QPushButton()
willr_settings_button.setVisible(False)
size_retain = willr_settings_button.sizePolicy()
size_retain.setRetainSizeWhenHidden(True)
willr_settings_button.setSizePolicy(size_retain)
willr_settings_button.setIcon(GEAR_ICON)
willr_widget.enterEvent = lambda e: on_enter(e, willr_widget, willr_settings_button)
willr_widget.leaveEvent = lambda e: on_exit(e, willr_widget, willr_settings_button)
def willr_button_clicked():
    """
    Displays a separate window with adjustable settings for the willr indicator
    """
    wnd = QDialog(widget)
    wnd.setWindowTitle("William's %R")
    wnd.setLayout(QVBoxLayout())
    period_widget = QWidget()
    period_widget.setLayout(QHBoxLayout())
    period_spinbox = QSpinBox()
    period_spinbox.setValue(selected_ta[get_indicator_index(
        "talib.WILLR")][2][0] if willr_checkbox.isChecked() else 14)
    period_widget.layout().addWidget(QLabel("Period"))
    period_widget.layout().addWidget(period_spinbox)
    wnd.layout().addWidget(period_widget)
    defaults_button = QPushButton("Reset to Defaults")
    defaults_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    defaults_button.clicked.connect(lambda: period_spinbox.setValue(14))
    cancel_button = QPushButton("Cancel")
    cancel_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    cancel_button.clicked.connect(lambda: wnd.done(0))
    ok_button = QPushButton("Save" if willr_checkbox.isChecked() else "Save and Add")
    ok_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    def ok_button_clicked():
        settings_tuple = (
            "talib.WILLR", willr_panel_cb.currentIndex(), [period_spinbox.value()]
        )
        if willr_checkbox.isChecked():
            selected_ta[get_indicator_index("talib.WILLR")] = settings_tuple
        else:
            selected_ta.append(settings_tuple)
            willr_checkbox.setChecked(True)
        wnd.done(0)
    ok_button.clicked.connect(ok_button_clicked)
    buttons_widget = QWidget()
    buttons_widget.setLayout(QHBoxLayout())
    buttons_widget.layout().addWidget(defaults_button)
    buttons_widget.layout().addWidget(cancel_button)
    buttons_widget.layout().addWidget(ok_button)
    wnd.layout().addWidget(buttons_widget)
    wnd.exec_()
willr_settings_button.clicked.connect(willr_button_clicked)
willr_widget.layout().addWidget(willr_settings_button)
willr_checkbox = QCheckBox()
willr_checkbox.clicked.connect(
    lambda: indicator_box_clicked(
        willr_checkbox,
        willr_panel_cb.currentIndex(),
        "talib.WILLR",
        [14],
        selected_ta
    )
)
willr_widget.layout().addWidget(willr_checkbox)
momentum_widget.layout().addWidget(willr_widget)


# create trend indicator scrollable
indicators_dialog.trend_gb = QGroupBox(indicators_dialog)
indicators_dialog.trend_gb.setTitle("Trend Indicators")
indicators_dialog.trend_gb.setGeometry(320, 10, 300, 620)
indicators_dialog.trend_gb.setStyleSheet('background-color: white')
indicators_dialog.trend_gb.trend_scrollarea = QScrollArea(indicators_dialog.trend_gb)
indicators_dialog.trend_gb.trend_scrollarea.setGeometry(10, 20, 280, 600)
trend_widget = QWidget()
trend_widget.resize(280, 400)
trend_widget.setLayout(QVBoxLayout())
indicators_dialog.trend_gb.trend_scrollarea.setWidget(trend_widget)
indicators_dialog.trend_gb.trend_scrollarea.setVerticalScrollBarPolicy(SCROLLBAR_ALWAYSON)

# add dpo to trend indicator scrollable
dpo_widget = QWidget()
dpo_widget.setLayout(QHBoxLayout())
dpo_widget.layout().addWidget(QLabel("Detrended Price Oscillator"))
dpo_panel_cb = QComboBox()
dpo_panel_cb.addItems(ta_combobox_items)
dpo_panel_cb.currentTextChanged.connect(
    lambda state: change_indicator_panel(
        "ta.trend.dpo",
        state,
        selected_ta[get_indicator_index("ta.trend.dpo")][2]
    )
    if dpo_checkbox.isChecked()
    else None
)
dpo_widget.layout().addWidget(dpo_panel_cb)
dpo_settings_button = QPushButton()
dpo_settings_button.setVisible(False)
size_retain = dpo_settings_button.sizePolicy()
size_retain.setRetainSizeWhenHidden(True)
dpo_settings_button.setSizePolicy(size_retain)
dpo_settings_button.setIcon(GEAR_ICON)
dpo_widget.enterEvent = lambda e: on_enter(e, dpo_widget, dpo_settings_button)
dpo_widget.leaveEvent = lambda e: on_exit(e, dpo_widget, dpo_settings_button)
def dpo_button_clicked():
    """
    Displays a separate window with adjustable settings for the dpo indicator
    """
    wnd = QDialog(widget)
    wnd.setWindowTitle("Detrended Price Oscillator")
    wnd.setLayout(QVBoxLayout())
    period_widget = QWidget()
    period_widget.setLayout(QHBoxLayout())
    period_spinbox = QSpinBox()
    period_spinbox.setValue(selected_ta[get_indicator_index(
        "ta.trend.dpo")][2][0] if dpo_checkbox.isChecked() else 20)
    period_widget.layout().addWidget(QLabel("Period"))
    period_widget.layout().addWidget(period_spinbox)
    wnd.layout().addWidget(period_widget)

    defaults_button = QPushButton("Reset to Defaults")
    defaults_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    defaults_button.clicked.connect(lambda: period_spinbox.setValue(20))
    cancel_button = QPushButton("Cancel")
    cancel_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    cancel_button.clicked.connect(lambda: wnd.done(0))
    ok_button = QPushButton("Save" if dpo_checkbox.isChecked() else "Save and Add")
    ok_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    def ok_button_clicked():
        settings_tuple = (
            "ta.trend.dpo", dpo_panel_cb.currentIndex(), [period_spinbox.value()]
        )

        if dpo_checkbox.isChecked():
            selected_ta[get_indicator_index("ta.trend.dpo")] = settings_tuple
        else:
            selected_ta.append(settings_tuple)
            dpo_checkbox.setChecked(True)

        wnd.done(0)
    ok_button.clicked.connect(ok_button_clicked)
    buttons_widget = QWidget()
    buttons_widget.setLayout(QHBoxLayout())
    buttons_widget.layout().addWidget(defaults_button)
    buttons_widget.layout().addWidget(cancel_button)
    buttons_widget.layout().addWidget(ok_button)
    wnd.layout().addWidget(buttons_widget)
    wnd.exec_()
dpo_settings_button.clicked.connect(dpo_button_clicked)
dpo_widget.layout().addWidget(dpo_settings_button)
dpo_checkbox = QCheckBox()
dpo_checkbox.clicked.connect(
    lambda: indicator_box_clicked(
        dpo_checkbox,
        dpo_panel_cb.currentIndex(),
        "ta.trend.dpo",
        [20],
        selected_ta
    )
)
dpo_widget.layout().addWidget(dpo_checkbox)
trend_widget.layout().addWidget(dpo_widget)

# add kst oscillator to trend indicator scrollable
kst_widget = QWidget()
kst_widget.setLayout(QHBoxLayout())
kst_widget.layout().addWidget(QLabel("KST Oscillator"))
kst_panel_cb = QComboBox()
kst_panel_cb.addItems(ta_combobox_items)
kst_panel_cb.currentTextChanged.connect(
    lambda state: change_indicator_panel(
        "ta.trend.KSTIndicator",
        state,
        selected_ta[get_indicator_index("ta.trend.KSTIndicator")][2]
    )
    if kst_checkbox.isChecked()
    else None
)
kst_widget.layout().addWidget(kst_panel_cb)
kst_settings_button = QPushButton()
kst_settings_button.setVisible(False)
size_retain = kst_settings_button.sizePolicy()
size_retain.setRetainSizeWhenHidden(True)
kst_settings_button.setSizePolicy(size_retain)
kst_settings_button.setIcon(GEAR_ICON)
kst_widget.enterEvent = lambda e: on_enter(e, kst_widget, kst_settings_button)
kst_widget.leaveEvent = lambda e: on_exit(e, kst_widget, kst_settings_button)
def kst_button_clicked():
    """
    Displays a separate window with adjustable settings for the kst indicator
    """
    wnd = QDialog(widget)
    wnd.setWindowTitle("KST Oscillator")
    wnd.setLayout(QVBoxLayout())
    roc1_widget = QWidget()
    roc1_widget.setLayout(QHBoxLayout())
    roc1_spinbox = QSpinBox()
    roc1_spinbox.setValue(selected_ta[get_indicator_index(
        "ta.trend.KSTIndicator")][2][0] if kst_checkbox.isChecked() else 10)
    roc1_widget.layout().addWidget(QLabel("Rate of Change 1 Length"))
    roc1_widget.layout().addWidget(roc1_spinbox)
    wnd.layout().addWidget(roc1_widget)
    roc2_widget = QWidget()
    roc2_widget.setLayout(QHBoxLayout())
    roc2_spinbox = QSpinBox()
    roc2_spinbox.setValue(selected_ta[get_indicator_index(
        "ta.trend.KSTIndicator")][2][1] if kst_checkbox.isChecked() else 15)
    roc2_widget.layout().addWidget(QLabel("Rate of Chnage 2 Length"))
    roc2_widget.layout().addWidget(roc2_spinbox)
    wnd.layout().addWidget(roc2_widget)
    roc3_widget = QWidget()
    roc3_widget.setLayout(QHBoxLayout())
    roc3_spinbox = QSpinBox()
    roc3_spinbox.setValue(selected_ta[get_indicator_index(
        "ta.trend.KSTIndicator")][2][2] if kst_checkbox.isChecked() else 20)
    roc3_widget.layout().addWidget(QLabel("Rate of Change 3 Length"))
    roc3_widget.layout().addWidget(roc3_spinbox)
    wnd.layout().addWidget(roc3_widget)
    roc4_widget = QWidget()
    roc4_widget.setLayout(QHBoxLayout())
    roc4_spinbox = QSpinBox()
    roc4_spinbox.setValue(selected_ta[get_indicator_index(
        "ta.trend.KSTIndicator")][2][3] if kst_checkbox.isChecked() else 30)
    roc4_widget.layout().addWidget(QLabel("Rate of Change 4 Length"))
    roc4_widget.layout().addWidget(roc4_spinbox)
    wnd.layout().addWidget(roc4_widget)
    sma1_widget = QWidget()
    sma1_widget.setLayout(QHBoxLayout())
    sma1_spinbox = QSpinBox()
    sma1_spinbox.setValue(selected_ta[get_indicator_index(
        "ta.trend.KSTIndicator")][2][4] if kst_checkbox.isChecked() else 10)
    sma1_widget.layout().addWidget(QLabel("Simple Moving Average 1 Length"))
    sma1_widget.layout().addWidget(sma1_spinbox)
    wnd.layout().addWidget(sma1_widget)
    sma2_widget = QWidget()
    sma2_widget.setLayout(QHBoxLayout())
    sma2_spinbox = QSpinBox()
    sma2_spinbox.setValue(selected_ta[get_indicator_index(
        "ta.trend.KSTIndicator")][2][5] if kst_checkbox.isChecked() else 10)
    sma2_widget.layout().addWidget(QLabel("Simple Moving Average 2 Length"))
    sma2_widget.layout().addWidget(sma2_spinbox)
    wnd.layout().addWidget(sma2_widget)
    sma3_widget = QWidget()
    sma3_widget.setLayout(QHBoxLayout())
    sma3_spinbox = QSpinBox()
    sma3_spinbox.setValue(selected_ta[get_indicator_index(
        "ta.trend.KSTIndicator")][2][6] if kst_checkbox.isChecked() else 10)
    sma3_widget.layout().addWidget(QLabel("Simple Moving Average 3 Length"))
    sma3_widget.layout().addWidget(sma3_spinbox)
    wnd.layout().addWidget(sma3_widget)
    sma4_widget = QWidget()
    sma4_widget.setLayout(QHBoxLayout())
    sma4_spinbox = QSpinBox()
    sma4_spinbox.setValue(selected_ta[get_indicator_index(
        "ta.trend.KSTIndicator")][2][7] if kst_checkbox.isChecked() else 15)
    sma4_widget.layout().addWidget(QLabel("Simple Moving Average 4 Length"))
    sma4_widget.layout().addWidget(sma4_spinbox)
    wnd.layout().addWidget(sma4_widget)
    signal_widget = QWidget()
    signal_widget.setLayout(QHBoxLayout())
    signal_label = QLabel("Signal Line Length")
    signal_spinbox = QSpinBox()
    signal_spinbox.setValue(selected_ta[get_indicator_index(
        "ta.trend.KSTIndicator")][2][8] if kst_checkbox.isChecked() else 9)
    signal_widget.layout().addWidget(signal_label)
    signal_widget.layout().addWidget(signal_spinbox)
    wnd.layout().addWidget(signal_widget)
    defaults_button = QPushButton("Reset to Defaults")
    defaults_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    def restore_defaults():
        roc1_spinbox.setValue(10)
        roc2_spinbox.setValue(15)
        roc3_spinbox.setValue(20)
        roc4_spinbox.setValue(30)
        sma1_spinbox.setValue(10)
        sma2_spinbox.setValue(10)
        sma3_spinbox.setValue(10)
        sma4_spinbox.setValue(15)
        signal_spinbox.setValue(9)
    defaults_button.clicked.connect(restore_defaults)
    cancel_button = QPushButton("Cancel")
    cancel_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    cancel_button.clicked.connect(lambda: wnd.done(0))
    ok_button = QPushButton(
        "Save" if kst_checkbox.isChecked() else "Save and Add")
    ok_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    def ok_button_clicked():
        new_vals = [
                roc1_spinbox.value(),
                roc2_spinbox.value(),
                roc3_spinbox.value(),
                roc4_spinbox.value(),
                sma1_spinbox.value(),
                sma2_spinbox.value(),
                sma3_spinbox.value(),
                sma4_spinbox.value(),
                signal_spinbox.value()
        ]
        settings_tuple = ("ta.trend.KSTIndicator", kst_panel_cb.currentIndex(), new_vals)

        if kst_checkbox.isChecked():
            selected_ta[get_indicator_index("ta.trend.KSTIndicator")] = settings_tuple
        else:
            selected_ta.append(settings_tuple)
            kst_checkbox.setChecked(True)
        wnd.done(0)
    ok_button.clicked.connect(ok_button_clicked)
    buttons_widget = QWidget()
    buttons_widget.setLayout(QHBoxLayout())
    buttons_widget.layout().addWidget(defaults_button)
    buttons_widget.layout().addWidget(cancel_button)
    buttons_widget.layout().addWidget(ok_button)
    wnd.layout().addWidget(buttons_widget)
    wnd.exec_()
kst_settings_button.clicked.connect(kst_button_clicked)
kst_widget.layout().addWidget(kst_settings_button)
kst_checkbox = QCheckBox()
kst_checkbox.clicked.connect(
    lambda: indicator_box_clicked(
        kst_checkbox,
        kst_panel_cb.currentIndex(),
        "ta.trend.KSTIndicator",
        [10, 15, 20, 30, 10, 10, 15, 9,],
        selected_ta
    )
)
kst_widget.layout().addWidget(kst_checkbox)
trend_widget.layout().addWidget(kst_widget)

# add ichimoku to trend indicator scrollable
ichimoku_widget = QWidget()
ichimoku_widget.setLayout(QHBoxLayout())
ichimoku_widget.layout().addWidget(QLabel("Ichimoku Cloud"))
ichimoku_panel_cb = QComboBox()
ichimoku_panel_cb.addItems(ta_combobox_items)
ichimoku_panel_cb.currentTextChanged.connect(
    lambda state: change_indicator_panel(
        "ta.trend.IchimokuIndicator",
        state,
        selected_ta[get_indicator_index("ta.trend.IchimokuIndicator")][2]
    )
    if ichimoku_checkbox.isChecked()
    else None
)
ichimoku_widget.layout().addWidget(ichimoku_panel_cb)
ichimoku_settings_button = QPushButton()
ichimoku_settings_button.setVisible(False)
size_retain = ichimoku_settings_button.sizePolicy()
size_retain.setRetainSizeWhenHidden(True)
ichimoku_settings_button.setSizePolicy(size_retain)
ichimoku_settings_button.setIcon(GEAR_ICON)
ichimoku_widget.enterEvent = lambda e: on_enter(e, ichimoku_widget, ichimoku_settings_button)
ichimoku_widget.leaveEvent = lambda e: on_exit(e, ichimoku_widget, ichimoku_settings_button)
def ichimoku_button_clicked():
    """
    Displays a separate window with adjustable settings for the ichimoku indicator
    """
    wnd = QDialog(widget)
    wnd.setWindowTitle("Ichimoku Indicator")
    wnd.setLayout(QVBoxLayout())
    low_period_widget = QWidget()
    low_period_widget.setLayout(QHBoxLayout())
    low_period_spinbox = QSpinBox()
    low_period_spinbox.setValue(selected_ta[get_indicator_index(
        "ta.trend.IchimokuIndicator")][2][0] if ichimoku_checkbox.isChecked() else 9)
    low_period_widget.layout().addWidget(QLabel("MACD Slow Period"))
    low_period_widget.layout().addWidget(low_period_spinbox)
    wnd.layout().addWidget(low_period_widget)
    med_period_widget = QWidget()
    med_period_widget.setLayout(QHBoxLayout())
    med_period_spinbox = QSpinBox()
    med_period_spinbox.setValue(selected_ta[get_indicator_index(
        "ta.trend.IchimokuIndicator")][2][1] if ichimoku_checkbox.isChecked() else 26)
    med_period_widget.layout().addWidget(QLabel("MACD Fast Period"))
    med_period_widget.layout().addWidget(med_period_spinbox)
    wnd.layout().addWidget(med_period_widget)
    high_period_widget = QWidget()
    high_period_widget.setLayout(QHBoxLayout())
    high_period_spinbox = QSpinBox()
    high_period_spinbox.setValue(selected_ta[get_indicator_index(
        "ta.trend.IchimokuIndicator")][2][2] if ichimoku_checkbox.isChecked() else 52)
    high_period_widget.layout().addWidget(QLabel("Cycles"))
    high_period_widget.layout().addWidget(high_period_spinbox)
    wnd.layout().addWidget(high_period_widget)
    shift_widget = QWidget()
    shift_widget.setLayout(QHBoxLayout())
    shift_checkbox = QCheckBox()
    shift_checkbox.setChecked(selected_ta[get_indicator_index(
        "ta.trend.IchimokuIndicator")][2][3] if ichimoku_checkbox.isChecked() else False)
    shift_widget.layout().addWidget(QLabel("Shift Medium"))
    shift_widget.layout().addWidget(shift_checkbox)
    wnd.layout().addWidget(shift_widget)
    defaults_button = QPushButton("Reset to Defaults")
    defaults_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    def restore_defaults():
        low_period_spinbox.setValue(9)
        med_period_spinbox.setValue(26)
        high_period_spinbox.setValue(52)
        shift_checkbox.setChecked(False)
    defaults_button.clicked.connect(restore_defaults)
    cancel_button = QPushButton("Cancel")
    cancel_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    cancel_button.clicked.connect(lambda: wnd.done(0))
    ok_button = QPushButton(
        "Save" if ichimoku_checkbox.isChecked() else "Save and Add")
    ok_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)

    def ok_button_clicked():
        new_vals = [
            low_period_spinbox.value(), med_period_spinbox.value(),
            high_period_spinbox.value(), shift_checkbox.isChecked()
        ]
        settings_tuple = (
            "ta.trend.IchimokuIndicator", ichimoku_panel_cb.currentIndex(), new_vals
        )
        if ichimoku_checkbox.isChecked():
            selected_ta[get_indicator_index("ta.trend.IchimokuIndicator")] = settings_tuple
        else:
            selected_ta.append(settings_tuple)
            ichimoku_checkbox.setChecked(True)
        wnd.done(0)
    ok_button.clicked.connect(ok_button_clicked)
    buttons_widget = QWidget()
    buttons_widget.setLayout(QHBoxLayout())
    buttons_widget.layout().addWidget(defaults_button)
    buttons_widget.layout().addWidget(cancel_button)
    buttons_widget.layout().addWidget(ok_button)
    wnd.layout().addWidget(buttons_widget)
    wnd.exec_()
ichimoku_settings_button.clicked.connect(ichimoku_button_clicked)
ichimoku_widget.layout().addWidget(ichimoku_settings_button)
ichimoku_checkbox = QCheckBox()
ichimoku_checkbox.clicked.connect(
    lambda: indicator_box_clicked(
        ichimoku_checkbox,
        ichimoku_panel_cb.currentIndex(),
        "ta.trend.IchimokuIndicator",
        [9, 26, 52, False],
        selected_ta
    )
)
ichimoku_widget.layout().addWidget(ichimoku_checkbox)
trend_widget.layout().addWidget(ichimoku_widget)

# add mass index to trend indicator scrollable
mi_widget = QWidget()
mi_widget.setLayout(QHBoxLayout())
mi_widget.layout().addWidget(QLabel("Mass Index"))
mi_panel_cb = QComboBox()
mi_panel_cb.addItems(ta_combobox_items)
mi_panel_cb.currentTextChanged.connect(
    lambda state: change_indicator_panel(
        "ta.trend.mass_index",
        state,
        selected_ta[get_indicator_index("ta.trend.mass_index")][2]
    )
    if mi_checkbox.isChecked()
    else None
)
mi_widget.layout().addWidget(mi_panel_cb)
mi_settings_button = QPushButton()
mi_settings_button.setVisible(False)
size_retain = mi_settings_button.sizePolicy()
size_retain.setRetainSizeWhenHidden(True)
mi_settings_button.setSizePolicy(size_retain)
mi_settings_button.setIcon(GEAR_ICON)
mi_widget.enterEvent = lambda e: on_enter(e, mi_widget, mi_settings_button)
mi_widget.leaveEvent = lambda e: on_exit(e, mi_widget, mi_settings_button)
def mi_button_clicked():
    """
    Displays a separate window with adjustable settings for the mass index
    """
    wnd = QDialog(widget)
    wnd.setWindowTitle("Mass Index")
    wnd.setLayout(QVBoxLayout())
    fast_period_widget = QWidget()
    fast_period_widget.setLayout(QHBoxLayout())
    fast_period_spinbox = QSpinBox()
    fast_period_spinbox.setValue(selected_ta[get_indicator_index(
        "ta.trend.mass_index")][2][0] if mi_checkbox.isChecked() else 9)
    fast_period_widget.layout().addWidget(QLabel("Fast Period"))
    fast_period_widget.layout().addWidget(fast_period_spinbox)
    wnd.layout().addWidget(fast_period_widget)
    slow_period_widget = QWidget()
    slow_period_widget.setLayout(QHBoxLayout())
    slow_period_spinbox = QSpinBox()
    slow_period_spinbox.setValue(selected_ta[get_indicator_index(
        "ta.trend.mass_index")][2][1] if mi_checkbox.isChecked() else 25)
    slow_period_widget.layout().addWidget(QLabel("Slow Period"))
    slow_period_widget.layout().addWidget(slow_period_spinbox)
    wnd.layout().addWidget(slow_period_widget)
    defaults_button = QPushButton("Reset to Defaults")
    defaults_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    def restore_defaults():
        fast_period_spinbox.setValue(9)
        slow_period_spinbox.setValue(25)
    defaults_button.clicked.connect(restore_defaults)
    cancel_button = QPushButton("Cancel")
    cancel_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    cancel_button.clicked.connect(lambda: wnd.done(0))
    ok_button = QPushButton("Save" if mi_checkbox.isChecked() else "Save and Add")
    ok_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    def ok_button_clicked():
        new_vals = [fast_period_spinbox.value(), slow_period_spinbox.value()]
        settings_tuple = ("ta.trend.mass_index", mi_panel_cb.currentIndex(), new_vals)
        if mi_checkbox.isChecked():
            selected_ta[get_indicator_index("ta.trend.mass_index")] = settings_tuple
        else:
            selected_ta.append(settings_tuple)
            mi_checkbox.setChecked(True)
        wnd.done(0)
    ok_button.clicked.connect(ok_button_clicked)
    buttons_widget = QWidget()
    buttons_widget.setLayout(QHBoxLayout())
    buttons_widget.layout().addWidget(defaults_button)
    buttons_widget.layout().addWidget(cancel_button)
    buttons_widget.layout().addWidget(ok_button)
    wnd.layout().addWidget(buttons_widget)
    wnd.exec_()
mi_settings_button.clicked.connect(mi_button_clicked)
mi_widget.layout().addWidget(mi_settings_button)
mi_checkbox = QCheckBox()
mi_checkbox.clicked.connect(
    lambda: indicator_box_clicked(
        mi_checkbox,
        mi_panel_cb.currentIndex(),
        "ta.trend.mass_index",
        [9, 25],
        selected_ta
    )
)
mi_widget.layout().addWidget(mi_checkbox)
trend_widget.layout().addWidget(mi_widget)

# add schaff to trend indicator scrollable
schaff_widget = QWidget()
schaff_widget.setLayout(QHBoxLayout())
schaff_widget.layout().addWidget(QLabel("Schaff Trend Cycle"))
schaff_panel_cb = QComboBox()
schaff_panel_cb.addItems(ta_combobox_items)
schaff_panel_cb.currentTextChanged.connect(
    lambda state: change_indicator_panel(
        "ta.trend.stc",
        state,
        selected_ta[get_indicator_index("ta.trend.stc")][2]
    )
    if schaff_checkbox.isChecked()
    else None
)
schaff_widget.layout().addWidget(schaff_panel_cb)
schaff_settings_button = QPushButton()
schaff_settings_button.setVisible(False)
size_retain = schaff_settings_button.sizePolicy()
size_retain.setRetainSizeWhenHidden(True)
schaff_settings_button.setSizePolicy(size_retain)
schaff_settings_button.setIcon(GEAR_ICON)
schaff_widget.enterEvent = lambda e: on_enter(e, schaff_widget, schaff_settings_button)
schaff_widget.leaveEvent = lambda e: on_exit(e, schaff_widget, schaff_settings_button)
def schaff_button_clicked():
    """
    Displays a separate window with adjustable settings for the schaff indicator
    """
    wnd = QDialog(widget)
    wnd.setWindowTitle("Schaff Indicator")
    wnd.setLayout(QVBoxLayout())
    macd_slow_widget = QWidget()
    macd_slow_widget.setLayout(QHBoxLayout())
    macd_slow_spinbox = QSpinBox()
    macd_slow_spinbox.setValue(selected_ta[get_indicator_index(
        "ta.trend.stc")][2][0] if schaff_checkbox.isChecked() else 50)
    macd_slow_widget.layout().addWidget(QLabel("MACD Slow Period"))
    macd_slow_widget.layout().addWidget(macd_slow_spinbox)
    wnd.layout().addWidget(macd_slow_widget)

    macd_fast_widget = QWidget()
    macd_fast_widget.setLayout(QHBoxLayout())
    macd_fast_spinbox = QSpinBox()
    macd_fast_spinbox.setValue(selected_ta[get_indicator_index(
        "ta.trend.stc")][2][1] if schaff_checkbox.isChecked() else 23)
    macd_fast_widget.layout().addWidget(QLabel("MACD Fast Period"))
    macd_fast_widget.layout().addWidget(macd_fast_spinbox)
    wnd.layout().addWidget(macd_fast_widget)

    cycle_widget = QWidget()
    cycle_widget.setLayout(QHBoxLayout())
    cycle_spinbox = QSpinBox()
    cycle_spinbox.setValue(selected_ta[get_indicator_index(
        "ta.trend.stc")][2][2] if schaff_checkbox.isChecked() else 10)
    cycle_widget.layout().addWidget(QLabel("Cycles"))
    cycle_widget.layout().addWidget(cycle_spinbox)
    wnd.layout().addWidget(cycle_widget)

    length1_widget = QWidget()
    length1_widget.setLayout(QHBoxLayout())
    length1_spinbox = QSpinBox()
    length1_spinbox.setValue(selected_ta[get_indicator_index(
        "ta.trend.stc")][2][3] if schaff_checkbox.isChecked() else 3)
    length1_widget.layout().addWidget(QLabel("First %D Length"))
    length1_widget.layout().addWidget(length1_spinbox)
    wnd.layout().addWidget(length1_widget)

    length2_widget = QWidget()
    length2_widget.setLayout(QHBoxLayout())
    length2_spinbox = QSpinBox()
    length2_spinbox.setValue(selected_ta[get_indicator_index(
        "ta.trend.stc")][2][4] if schaff_checkbox.isChecked() else 3)
    length2_widget.layout().addWidget(QLabel("Second %D Length"))
    length2_widget.layout().addWidget(length2_spinbox)
    wnd.layout().addWidget(length2_widget)

    defaults_button = QPushButton("Reset to Defaults")
    defaults_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    def restore_defaults():
        macd_slow_spinbox.setValue(50)
        macd_fast_spinbox.setValue(23)
        cycle_spinbox.setValue(10)
        length1_spinbox.setValue(3)
        length2_spinbox.setValue(3)
    defaults_button.clicked.connect(restore_defaults)
    cancel_button = QPushButton("Cancel")
    cancel_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    cancel_button.clicked.connect(lambda: wnd.done(0))
    ok_button = QPushButton("Save" if schaff_checkbox.isChecked() else "Save and Add")
    ok_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    def ok_button_clicked():
        new_vals = [
            macd_slow_spinbox.value(), macd_fast_spinbox.value(), cycle_spinbox.value(),
            length1_spinbox.value(), length2_spinbox.value()
        ]
        settings_tuple = ("ta.trend.stc", schaff_panel_cb.currentIndex(), new_vals)
        if schaff_checkbox.isChecked():
            selected_ta[get_indicator_index("ta.trend.stc")] = settings_tuple
        else:
            selected_ta.append(settings_tuple)
            schaff_checkbox.setChecked(True)
        wnd.done(0)
    ok_button.clicked.connect(ok_button_clicked)
    buttons_widget = QWidget()
    buttons_widget.setLayout(QHBoxLayout())
    buttons_widget.layout().addWidget(defaults_button)
    buttons_widget.layout().addWidget(cancel_button)
    buttons_widget.layout().addWidget(ok_button)
    wnd.layout().addWidget(buttons_widget)
    wnd.exec_()
schaff_settings_button.clicked.connect(schaff_button_clicked)
schaff_widget.layout().addWidget(schaff_settings_button)
schaff_checkbox = QCheckBox()
schaff_checkbox.clicked.connect(
    lambda: indicator_box_clicked(
        schaff_checkbox,
        schaff_panel_cb.currentIndex(),
        "ta.trend.stc",
        [50, 23, 10, 3, 3],
        selected_ta
    )
)
schaff_widget.layout().addWidget(schaff_checkbox)
trend_widget.layout().addWidget(schaff_widget)

# add trix indicator to trend indicator scrollable
trix_widget = QWidget()
trix_widget.setLayout(QHBoxLayout())
trix_widget.layout().addWidget(QLabel("Trix Indicator"))
trix_panel_cb = QComboBox()
trix_panel_cb.addItems(ta_combobox_items)
trix_panel_cb.currentTextChanged.connect(
    lambda state: change_indicator_panel(
        "ta.trend.trix",
        state,
        selected_ta[get_indicator_index("ta.trend.trix")][2]
    )
    if trix_checkbox.isChecked()
    else None
)
trix_widget.layout().addWidget(trix_panel_cb)
trix_settings_button = QPushButton()
trix_settings_button.setVisible(False)
size_retain = trix_settings_button.sizePolicy()
size_retain.setRetainSizeWhenHidden(True)
trix_settings_button.setSizePolicy(size_retain)
trix_settings_button.setIcon(GEAR_ICON)
trix_widget.enterEvent = lambda e: on_enter(e, trix_widget, trix_settings_button)
trix_widget.leaveEvent = lambda e: on_exit(e, trix_widget, trix_settings_button)
def trix_button_clicked():
    """
    Displays a separate window with adjustable settings for the trix indicator
    """
    wnd = QDialog(widget)
    wnd.setWindowTitle("Trix Indicator")
    wnd.setLayout(QVBoxLayout())
    period_widget = QWidget()
    period_widget.setLayout(QHBoxLayout())
    period_spinbox = QSpinBox()
    period_spinbox.setValue(selected_ta[get_indicator_index(
        "ta.trend.trix")][2][0] if trix_checkbox.isChecked() else 15)
    period_widget.layout().addWidget(QLabel("Period"))
    period_widget.layout().addWidget(period_spinbox)
    wnd.layout().addWidget(period_widget)

    defaults_button = QPushButton("Reset to Defaults")
    defaults_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    defaults_button.clicked.connect(lambda: period_spinbox.setValue(14))
    cancel_button = QPushButton("Cancel")
    cancel_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    cancel_button.clicked.connect(lambda: wnd.done(0))
    ok_button = QPushButton("Save" if trix_checkbox.isChecked() else "Save and Add")
    ok_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    def ok_button_clicked():
        settings_tuple = ("ta.trend.trix", trix_panel_cb.currentIndex(), [period_spinbox.value()])
        if trix_checkbox.isChecked():
            selected_ta[get_indicator_index("ta.trend.trix")] = settings_tuple
        else:
            selected_ta.append(settings_tuple)
            trix_checkbox.setChecked(True)
        wnd.done(0)
    ok_button.clicked.connect(ok_button_clicked)
    buttons_widget = QWidget()
    buttons_widget.setLayout(QHBoxLayout())
    buttons_widget.layout().addWidget(defaults_button)
    buttons_widget.layout().addWidget(cancel_button)
    buttons_widget.layout().addWidget(ok_button)
    wnd.layout().addWidget(buttons_widget)
    wnd.exec_()
trix_settings_button.clicked.connect(trix_button_clicked)
trix_widget.layout().addWidget(trix_settings_button)
trix_checkbox = QCheckBox()
trix_checkbox.clicked.connect(
    lambda: indicator_box_clicked(
        trix_checkbox,
        trix_panel_cb.currentIndex(),
        "ta.trend.trix",
        [15],
        selected_ta
    )
)
trix_widget.layout().addWidget(trix_checkbox)
trend_widget.layout().addWidget(trix_widget)

# add parabolic sar to trend indicator scrollable
psar_widget = QWidget()
psar_widget.setLayout(QHBoxLayout())
psar_widget.layout().addWidget(QLabel("Parabolic SAR"))
psar_panel_cb = QComboBox()
psar_panel_cb.addItems(ta_combobox_items)
psar_panel_cb.currentTextChanged.connect(
    lambda state: change_indicator_panel(
        "ta.trend.PSARIndicator",
        state,
        selected_ta[get_indicator_index("ta.trend.PSARIndicator")][2]
    )
    if psar_checkbox.isChecked()
    else None
)
psar_widget.layout().addWidget(psar_panel_cb)
psar_settings_button = QPushButton()
psar_settings_button.setVisible(False)
size_retain = psar_settings_button.sizePolicy()
size_retain.setRetainSizeWhenHidden(True)
psar_settings_button.setSizePolicy(size_retain)
psar_settings_button.setIcon(GEAR_ICON)
psar_widget.enterEvent = lambda e: on_enter(e, psar_widget, psar_settings_button)
psar_widget.leaveEvent = lambda e: on_exit(e, psar_widget, psar_settings_button)
def psar_button_clicked():
    """
    Displays a separate window with adjustable settings for the PSAR indicator
    """
    wnd = QDialog(widget)
    wnd.setWindowTitle("Parabolic SAR")
    wnd.setLayout(QVBoxLayout())
    acc_fac_widget = QWidget()
    acc_fac_widget.setLayout(QHBoxLayout())
    acc_fac_spinbox = QDoubleSpinBox()
    acc_fac_spinbox.setValue(selected_ta[get_indicator_index(
        "ta.trend.PSARIndicator")][2][0] if psar_checkbox.isChecked() else .02)
    acc_fac_widget.layout().addWidget(QLabel("Acceleration Factor"))
    acc_fac_widget.layout().addWidget(acc_fac_spinbox)
    wnd.layout().addWidget(acc_fac_widget)

    max_acc_fac_widget = QWidget()
    max_acc_fac_widget.setLayout(QHBoxLayout())
    max_acc_fac_spinbox = QDoubleSpinBox()
    max_acc_fac_spinbox.setValue(selected_ta[get_indicator_index(
        "ta.trend.PSARIndicator")][2][1] if psar_checkbox.isChecked() else .2)
    max_acc_fac_widget.layout().addWidget(QLabel("Maximum Acceleration Factor"))
    max_acc_fac_widget.layout().addWidget(max_acc_fac_spinbox)
    wnd.layout().addWidget(max_acc_fac_widget)

    defaults_button = QPushButton("Reset to Defaults")
    defaults_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)

    def restore_defaults():
        acc_fac_spinbox.setValue(.02)
        max_acc_fac_spinbox.setValue(.2)

    defaults_button.clicked.connect(restore_defaults)
    cancel_button = QPushButton("Cancel")
    cancel_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    cancel_button.clicked.connect(lambda: wnd.done(0))
    ok_button = QPushButton("Save" if psar_checkbox.isChecked() else "Save and Add")
    ok_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)

    def ok_button_clicked():
        new_vals = [acc_fac_spinbox.value(), max_acc_fac_spinbox.value()]
        settings_tuple = ("ta.trend.PSARIndicator", psar_panel_cb.currentIndex(), new_vals)
        if psar_checkbox.isChecked():
            selected_ta[get_indicator_index("ta.trend.PSARIndicator")] = settings_tuple
        else:
            selected_ta.append(settings_tuple)
            psar_checkbox.setChecked(True)
        wnd.done(0)

    ok_button.clicked.connect(ok_button_clicked)
    buttons_widget = QWidget()
    buttons_widget.setLayout(QHBoxLayout())
    buttons_widget.layout().addWidget(defaults_button)
    buttons_widget.layout().addWidget(cancel_button)
    buttons_widget.layout().addWidget(ok_button)
    wnd.layout().addWidget(buttons_widget)
    wnd.exec_()
psar_settings_button.clicked.connect(psar_button_clicked)
psar_widget.layout().addWidget(psar_settings_button)
psar_checkbox = QCheckBox()
psar_checkbox.clicked.connect(
    lambda: indicator_box_clicked(
        psar_checkbox,
        psar_panel_cb.currentIndex(),
        "ta.trend.PSARIndicator",
        [.02, .2],
        selected_ta
    )
)
psar_widget.layout().addWidget(psar_checkbox)
trend_widget.layout().addWidget(psar_widget)

# add vortex to trend indicator scrollable
vortex_widget = QWidget()
vortex_widget.setLayout(QHBoxLayout())
vortex_widget.layout().addWidget(QLabel("Vortex Indicator"))
vortex_panel_cb = QComboBox()
vortex_panel_cb.addItems(ta_combobox_items)
vortex_panel_cb.currentTextChanged.connect(
    lambda state: change_indicator_panel(
        "ta.trend.VortexIndicator",
        state,
        selected_ta[get_indicator_index("ta.trend.VortexIndicator")][2]
    )
    if vortex_checkbox.isChecked()
    else None
)
vortex_widget.layout().addWidget(vortex_panel_cb)
vortex_settings_button = QPushButton()
vortex_settings_button.setVisible(False)
size_retain = vortex_settings_button.sizePolicy()
size_retain.setRetainSizeWhenHidden(True)
vortex_settings_button.setSizePolicy(size_retain)
vortex_settings_button.setIcon(GEAR_ICON)
vortex_widget.enterEvent = lambda e: on_enter(e, vortex_widget, vortex_settings_button)
vortex_widget.leaveEvent = lambda e: on_exit(e, vortex_widget, vortex_settings_button)
def vortex_button_clicked():
    """
    Displays a separate window with adjustable settings for the trix indicator
    """
    wnd = QDialog(widget)
    wnd.setWindowTitle("Vortex Indicator")
    wnd.setLayout(QVBoxLayout())
    period_widget = QWidget()
    period_widget.setLayout(QHBoxLayout())
    period_spinbox = QSpinBox()
    period_spinbox.setValue(
        selected_ta[get_indicator_index("ta.trend.VortexIndicator")][2][0]
        if vortex_checkbox.isChecked()
        else 14
    )
    period_widget.layout().addWidget(QLabel("Period"))
    period_widget.layout().addWidget(period_spinbox)
    wnd.layout().addWidget(period_widget)
    defaults_button = QPushButton("Reset to Defaults")
    defaults_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    defaults_button.clicked.connect(lambda: period_spinbox.setValue(14))
    cancel_button = QPushButton("Cancel")
    cancel_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    cancel_button.clicked.connect(lambda: wnd.done(0))
    ok_button = QPushButton("Save" if vortex_checkbox.isChecked() else "Save and Add")
    ok_button.setStyleSheet(SETTINGS_DIALOG_BTN_STYLESHEET)
    def ok_button_clicked():
        settings_tuple = (
            "ta.trend.VortexIndicator", vortex_panel_cb.currentIndex(), [period_spinbox.value()]
        )
        if vortex_checkbox.isChecked():
            selected_ta[get_indicator_index("ta.trend.VortexIndicator")] = settings_tuple
        else:
            selected_ta.append(settings_tuple)
            vortex_checkbox.setChecked(True)
        wnd.done(0)
    ok_button.clicked.connect(ok_button_clicked)
    buttons_widget = QWidget()
    buttons_widget.setLayout(QHBoxLayout())
    buttons_widget.layout().addWidget(defaults_button)
    buttons_widget.layout().addWidget(cancel_button)
    buttons_widget.layout().addWidget(ok_button)
    wnd.layout().addWidget(buttons_widget)
    wnd.exec_()
vortex_settings_button.clicked.connect(vortex_button_clicked)
vortex_widget.layout().addWidget(vortex_settings_button)
vortex_checkbox = QCheckBox()
vortex_checkbox.clicked.connect(
    lambda: indicator_box_clicked(
        vortex_checkbox,
        vortex_panel_cb.currentIndex(),
        "ta.trend.VortexIndicator",
        [14],
        selected_ta
    )
)
vortex_widget.layout().addWidget(vortex_checkbox)
trend_widget.layout().addWidget(vortex_widget)

def indicator_box_clicked(box: QCheckBox, index: int, function: str, settings: list, ta_list: list):
    """
    A function that is called whenever an indicator's checkbox is clicked.
    If the click is to add the indicator, an indicator tuple is created from the function
    string, selected index, and indicator settings and added to the global TA list.
    If the click is to remove the indicator, the global list is cleared and replaced with
    a new list that doesn't have the given indicator tuple.
    """
    if box.isChecked():
        ta_list.append((function, index, settings))
    else:
        new_list = list(filter(lambda ta: ta[0] != function, ta_list))
        ta_list.clear()
        ta_list.extend(new_list)

# create moving average indicator scrollable
indicators_dialog.ma_groupbox = QGroupBox(indicators_dialog)
indicators_dialog.ma_groupbox.setTitle("Moving Averages")
indicators_dialog.ma_groupbox.setGeometry(630, 10, 300, 620)
indicators_dialog.ma_groupbox.setStyleSheet('background-color: white')
indicators_dialog.ma_groupbox.ma_scrollarea = QScrollArea(indicators_dialog.ma_groupbox)
indicators_dialog.ma_groupbox.ma_scrollarea.setGeometry(10, 20, 280, 600)
ma_widget = QWidget()
ma_widget.resize(280, 1500)
ma_widget.setLayout(QVBoxLayout())
indicators_dialog.ma_groupbox.ma_scrollarea.setWidget(ma_widget)
indicators_dialog.ma_groupbox.ma_scrollarea.setVerticalScrollBarPolicy(SCROLLBAR_ALWAYSON)
chart_dialog.addTab(chart_configs, "Chart Configurations")
chart_dialog.addTab(indicators_dialog, "Technical Indicators")


################
# trade dialog #
################
trade_dialog = QDialog()
trade_dialog.setStyleSheet('background-color: deepskyblue;')

trade_dialog.searchbar_gb = QGroupBox(trade_dialog)
trade_dialog.searchbar_gb.setStyleSheet('background-color: white;')
trade_dialog.searchbar_gb.setTitle("Find a Stock")
trade_dialog.searchbar_gb.setGeometry(10, 10, 960, 70)
trade_dialog.searchbar_gb.searchBar = QLineEdit(trade_dialog.searchbar_gb)
trade_dialog.searchbar_gb.searchBar.setGeometry(10, 20, 850, 40)
trade_dialog.searchbar_gb.searchBar.textChanged.connect(search_text_changed)
trade_dialog.searchbar_gb.searchBar.setFont(ARIAL_10)
trade_dialog.searchbar_gb.searchBar.setCompleter(completer)
trade_dialog.searchbar_gb.search_button = QPushButton(trade_dialog.searchbar_gb)
trade_dialog.searchbar_gb.search_button.setGeometry(870, 20, 80, 40)
trade_dialog.searchbar_gb.search_button.setText("Trade")

trade_dialog.basic_info_gb = QGroupBox(trade_dialog)
trade_dialog.basic_info_gb.setStyleSheet('background-color: white;')
trade_dialog.basic_info_gb.setTitle("Information")
trade_dialog.basic_info_gb.setGeometry(980, 10, 300, 70)

trade_dialog.basic_info_gb.full_name_label = QLabel(trade_dialog.basic_info_gb)
trade_dialog.basic_info_gb.full_name_label.setText("")
trade_dialog.basic_info_gb.full_name_label.setGeometry(10, 15, 150, 15)

trade_dialog.basic_info_gb.price_label = QLabel(trade_dialog.basic_info_gb)
trade_dialog.basic_info_gb.price_label.setText("Price (+/-)")
trade_dialog.basic_info_gb.price_label.setGeometry(160, 15, 100, 20)

trade_dialog.basic_info_gb.bid_label = QLabel(trade_dialog.basic_info_gb)
trade_dialog.basic_info_gb.bid_label.setText("Bid: <bid_price> (bid_size)")
trade_dialog.basic_info_gb.bid_label.setGeometry(10, 30, 140, 20)

trade_dialog.basic_info_gb.ask_label = QLabel(trade_dialog.basic_info_gb)
trade_dialog.basic_info_gb.ask_label.setText("Ask: <ask_price> (ask_size)")
trade_dialog.basic_info_gb.ask_label.setGeometry(160, 30, 140, 20)

trade_dialog.order_gb = QGroupBox(trade_dialog)
trade_dialog.order_gb.setStyleSheet('background-color: white;')
trade_dialog.order_gb.setTitle("Create Order")
trade_dialog.order_gb.setGeometry(10, 90, 450, 400)

trade_dialog.order_gb.action_label = QLabel(trade_dialog.order_gb)
trade_dialog.order_gb.action_label.setText("Action")
trade_dialog.order_gb.action_label.setGeometry(10, 50, 100, 15)

trade_dialog.order_gb.action_combobox = QComboBox(trade_dialog.order_gb)
trade_dialog.order_gb.action_combobox.addItems(['Buy', 'Sell'])
trade_dialog.order_gb.action_combobox.setGeometry(10, 70, 100, 40)

trade_dialog.order_gb.qty_label = QLabel(trade_dialog.order_gb)
trade_dialog.order_gb.qty_label.setText("Quantity")
trade_dialog.order_gb.qty_label.setGeometry(10, 150, 100, 15)

trade_dialog.order_gb.qty_spinbox = QSpinBox(trade_dialog.order_gb)
trade_dialog.order_gb.qty_spinbox.setGeometry(10, 170, 100, 40)

trade_dialog.order_gb.max_btn = QPushButton(trade_dialog.order_gb)
trade_dialog.order_gb.max_btn.setText("Max")
trade_dialog.order_gb.max_btn.setGeometry(120, 170, 100, 40)
trade_dialog.order_gb.max_btn.setEnabled(False)

trade_dialog.order_gb.type_label = QLabel(trade_dialog.order_gb)
trade_dialog.order_gb.type_label.setText("Order Type")
trade_dialog.order_gb.type_label.setGeometry(10, 230, 100, 15)

def trade_searchbar_click():
    """
    Updates trade dialog when a stock is selected for trading
    """
    global CURRENT_TRADE_STOCK

    ticker = trade_dialog.searchbar_gb.searchBar.text().split(' ')[0]
    CURRENT_TRADE_STOCK = ticker
    trade_dialog.order_gb.max_btn.setEnabled(True)

    prices = yq.Ticker(ticker).history('1d', '1m')
    day_chart.removeAllSeries()
    day_chart_series = QLineSeries()
    for idx, close in enumerate(prices.loc[:, 'close']):
        price_dt = QDateTime().fromString(str(prices.index[idx][1])[0:19], "yyyy-MM-dd hh:mm:ss")
        epoch_dt = float(price_dt.toMSecsSinceEpoch())
        day_chart_series.append(epoch_dt, close)

    day_chart.addSeries(day_chart_series)

    day_chart.createDefaultAxes()
    day_chart.axes(Qt.Orientation.Horizontal)[0].hide()

    day_chart_x_axis = QDateTimeAxis()
    day_chart_x_axis.setTickCount(7)
    day_chart_x_axis.setFormat("h:mm")
    day_chart_x_axis.setTitleText("Date")
    day_chart_x_axis.setVisible(True)

    day_chart.addAxis(day_chart_x_axis, Qt.AlignmentFlag.AlignBottom)
    day_chart_series.attachAxis(day_chart_x_axis)


def update_trade_dialog():
    """
    Updates the trade dialog UI with current bid, ask, and last trade price information
    """
    ticker_symbol = CURRENT_TRADE_STOCK
    yq_ticker = yq.Ticker(ticker_symbol)
    all_modules = yq_ticker.all_modules[ticker_symbol]

    quote_type = all_modules['quoteType']
    prices = all_modules['price']
    summary = all_modules['summaryDetail']

    trade_dialog.basic_info_gb.full_name_label.setText(quote_type['shortName'])
    trade_dialog.basic_info_gb.price_label.setText(
        f"{prices['regularMarketPrice']} ({prices['regularMarketChange']})"
    )
    trade_dialog.basic_info_gb.bid_label.setText(f"Bid: {summary['bid']} ({summary['bidSize']})")
    trade_dialog.basic_info_gb.ask_label.setText(f"Ask: {summary['ask']} ({summary['askSize']})")

    trade_dialog.order_gb.limit_stop_bid.setText(f"Bid:\n{summary['bid']}\n({summary['bidSize']})")
    trade_dialog.order_gb.limit_stop_ask.setText(f"Ask:\n{summary['ask']}\n({summary['askSize']})")
    trade_dialog.order_gb.limit_stop_mid.setText(f"Mid:\n{(summary['bid'] + summary['ask']) / 2}")
    slider_range = (summary['ask'] - summary['bid']) * 100
    trade_dialog.order_gb.price_slider.setRange(0, slider_range)


def on_ordertype_change(value):
    """
    Shows or hides the price slider depending on the type of order selected
    (show for limit/stop, hide for market)
    """
    match value:
        case 'Market':
            trade_dialog.order_gb.price_slider.setVisible(False)
            trade_dialog.order_gb.limit_stop_bid.setVisible(False)
            trade_dialog.order_gb.limit_stop_ask.setVisible(False)
            trade_dialog.order_gb.limit_stop_mid.setVisible(False)
        case _:
            trade_dialog.order_gb.price_slider.setVisible(True)
            trade_dialog.order_gb.limit_stop_bid.setVisible(True)
            trade_dialog.order_gb.limit_stop_ask.setVisible(True)
            trade_dialog.order_gb.limit_stop_mid.setVisible(True)


def on_previeworder_click():
    """
    Shows dialog with preview of the user's order
    """
    wnd = QDialog(widget)
    wnd.setWindowTitle("Preview Order")
    wnd.setLayout(QVBoxLayout())

    ticker_widget = QWidget()
    ticker_widget.setLayout(QHBoxLayout())
    ticker_widget.layout().addWidget(QLabel('Ticker:'))
    ticker_label = QLabel(CURRENT_TRADE_STOCK)
    ticker_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
    ticker_widget.layout().addWidget(ticker_label)
    wnd.layout().addWidget(ticker_widget)

    transaction_widget = QWidget()
    transaction_widget.setLayout(QHBoxLayout())
    transaction_widget.layout().addWidget(QLabel('Transaction:'))
    transaction_label = QLabel(trade_dialog.order_gb.action_combobox.currentText())
    transaction_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
    transaction_widget.layout().addWidget(transaction_label)
    wnd.layout().addWidget(transaction_widget)


    ordertype_widget = QWidget()
    ordertype_widget.setLayout(QHBoxLayout())
    ordertype_widget.layout().addWidget(QLabel('Order Type:'))
    ordertype_label = QLabel(trade_dialog.order_gb.type_combobox.currentText())
    ordertype_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
    ordertype_widget.layout().addWidget(ordertype_label)
    wnd.layout().addWidget(ordertype_widget)

    estprice_widget = QWidget()
    estprice_widget.setLayout(QHBoxLayout())
    estprice_widget.layout().addWidget(QLabel('Estimated Price'))
    estprice_label = QLabel()
    if trade_dialog.order_gb.type_combobox.currentText() == 'Market':
        if trade_dialog.order_gb.action_combobox.currentText() == 'Buy':
            estprice_label.setText(trade_dialog.order_gb.limit_stop_ask.text().split('\n')[1])
        else:
            estprice_label.setText(trade_dialog.order_gb.limit_stop_bid.text().split('\n')[1])
    else:
        # change to limit/stop price
        estprice_label.setText(trade_dialog.order_gb.limit_stop_bid.text())
    estprice_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
    estprice_widget.layout().addWidget(estprice_label)
    wnd.layout().addWidget(estprice_widget)

    qty_widget = QWidget()
    qty_widget.setLayout(QHBoxLayout())
    qty_widget.layout().addWidget(QLabel('Quantity:'))
    qty_label = QLabel(str(trade_dialog.order_gb.qty_spinbox.value()))
    qty_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
    qty_widget.layout().addWidget(qty_label)
    wnd.layout().addWidget(qty_widget)

    est_cost_widget = QWidget()
    est_cost_widget.setLayout(QHBoxLayout())
    est_cost_widget.layout().addWidget(
        QLabel(
            "Estimated Net Debit"
            if transaction_label.text() == "Buy"
            else "Estimated Net Credit"
        )
    )

    est_cost_label = QLabel(str(int(qty_label.text()) * float(estprice_label.text())))
    est_cost_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
    est_cost_widget.layout().addWidget(est_cost_label)
    wnd.layout().addWidget(est_cost_widget)

    actions_widget = QWidget()
    actions_widget.setLayout(QHBoxLayout())
    cancel_button = QPushButton('Change Order')
    cancel_button.clicked.connect(wnd.done(0))
    actions_widget.layout().addWidget(cancel_button)
    ok_button = QPushButton('Confirm Order')
    def ok_button_clicked():
        OPEN_ORDERS.append(
            [
                CURRENT_TRADE_STOCK,
                transaction_label.text(),
                ordertype_label.text(),
                estprice_label.text(),
                qty_label.text()
            ]
        )
        wnd.done(0)
    ok_button.clicked.connect(ok_button_clicked)
    actions_widget.layout().addWidget(ok_button)
    wnd.layout().addWidget(actions_widget)

    wnd.exec()

trade_dialog.order_gb.type_combobox = QComboBox(trade_dialog.order_gb)
trade_dialog.order_gb.type_combobox.addItems(['Market', 'Limit', 'Stop'])
trade_dialog.order_gb.type_combobox.setGeometry(10, 250, 100, 40)
trade_dialog.order_gb.type_combobox.currentTextChanged.connect(on_ordertype_change)

trade_dialog.order_gb.price_slider = QSlider(trade_dialog.order_gb)
trade_dialog.order_gb.price_slider.setOrientation(Qt.Orientation.Horizontal)
trade_dialog.order_gb.price_slider.setRange(0, 10)
trade_dialog.order_gb.price_slider.setGeometry(120, 250, 250, 40)
trade_dialog.order_gb.price_slider.setVisible(False)

trade_dialog.order_gb.limit_stop_bid = QLabel(trade_dialog.order_gb)
trade_dialog.order_gb.limit_stop_bid.setText("<bid>")
trade_dialog.order_gb.limit_stop_bid.setGeometry(120, 300, 50, 50)
trade_dialog.order_gb.limit_stop_bid.setVisible(False)

trade_dialog.order_gb.limit_stop_ask = QLabel(trade_dialog.order_gb)
trade_dialog.order_gb.limit_stop_ask.setText("<ask>")
trade_dialog.order_gb.limit_stop_ask.setGeometry(350, 300, 50, 50)
trade_dialog.order_gb.limit_stop_ask.setVisible(False)

trade_dialog.order_gb.limit_stop_mid = QLabel(trade_dialog.order_gb)
trade_dialog.order_gb.limit_stop_mid.setText("<mid>")
trade_dialog.order_gb.limit_stop_mid.setGeometry(240, 300, 50, 50)
trade_dialog.order_gb.limit_stop_mid.setVisible(False)

trade_dialog.order_gb.preview_order = QPushButton(trade_dialog.order_gb)
trade_dialog.order_gb.preview_order.setText("Preview Order")
trade_dialog.order_gb.preview_order.setGeometry(50, 340, 360, 50)
trade_dialog.order_gb.preview_order.clicked.connect(on_previeworder_click)

trade_dialog.searchbar_gb.search_button.clicked.connect(trade_searchbar_click)

trade_dialog.chart_groupbox = QGroupBox(trade_dialog)
trade_dialog.chart_groupbox.setTitle('Chart')
trade_dialog.chart_groupbox.setStyleSheet('background-color: white')
trade_dialog.chart_groupbox.setGeometry(500, 90, 650, 400)

day_chart = QChart()

day_chartview = QChartView(trade_dialog.chart_groupbox)
day_lineseries = QLineSeries()
day_chart.addSeries(day_lineseries)
day_lineseries.setName('Stock')


x_axis = QDateTimeAxis()
x_axis.setFormat('h:mm')
x_axis.setTitleText('Time')
x_axis.setVisible(True)
day_chart.addAxis(x_axis, Qt.AlignmentFlag.AlignBottom)
day_lineseries.attachAxis(x_axis)

y_axis = QValueAxis()
day_chart.addAxis(y_axis, Qt.AlignmentFlag.AlignLeft)
day_lineseries.attachAxis(y_axis)


day_chartview.setGeometry(10, 20, 600, 400)
day_chartview.setChart(day_chart)

#####################
# stock info dialog #
#####################
stockinfo_dialog = QTabWidget()
stockinfo_dialog.setStyleSheet('background-color: deepskyblue;')

stockinfo_main = QDialog()
stockinfo_main.setStyleSheet('background-color: deepskyblue')
stockinfo_main.searchbar_gb = QGroupBox(stockinfo_main)
stockinfo_main.searchbar_gb.setStyleSheet('background-color: white;')
stockinfo_main.searchbar_gb.setTitle("Find a Stock")
stockinfo_main.searchbar_gb.setGeometry(10, 10, 960, 70)
stockinfo_main.searchbar_gb.searchBar = QLineEdit(stockinfo_main.searchbar_gb)
stockinfo_main.searchbar_gb.searchBar.setGeometry(10, 20, 850, 40)
stockinfo_main.searchbar_gb.searchBar.textChanged.connect(search_text_changed)
stockinfo_main.searchbar_gb.searchBar.setFont(ARIAL_10)
stockinfo_main.searchbar_gb.searchBar.setCompleter(completer)
stockinfo_main.searchbar_gb.search_button = QPushButton(stockinfo_main.searchbar_gb)
stockinfo_main.searchbar_gb.search_button.setGeometry(870, 20, 80, 40)
stockinfo_main.searchbar_gb.search_button.setText("Show Info")
stockinfo_main.searchbar_gb.search_button.clicked.connect(stockinfo_searchbar_click)

stockinfo_main.asset_info_gb = QGroupBox(stockinfo_main)
stockinfo_main.asset_info_gb.setStyleSheet('background-color: white')
stockinfo_main.asset_info_gb.setTitle("Asset Profile")
stockinfo_main.asset_info_gb.setGeometry(10, 90, 310, 550)
stockinfo_main.asset_info_gb.setVisible(False)
stockinfo_main.asset_info_gb.content_container = QScrollArea(stockinfo_main.asset_info_gb)
assetinfo_scrollarea_widget = QWidget()
assetinfo_scrollarea_widget.resize(300, 800)
assetinfo_scrollarea_widget.setLayout(QVBoxLayout())
stockinfo_main.asset_info_gb.content_container.setWidget(assetinfo_scrollarea_widget)
stockinfo_main.asset_info_gb.content_container.setGeometry(5, 15, 305, 520)
stockinfo_main.asset_info_gb.content_container.setVerticalScrollBarPolicy(SCROLLBAR_ALWAYSON)

stockinfo_main.about_groupbox = QGroupBox(stockinfo_main)
stockinfo_main.about_groupbox.setStyleSheet('background-color: white')
stockinfo_main.about_groupbox.setTitle("About the Asset")
stockinfo_main.about_groupbox.setGeometry(330, 90, 540, 550)
stockinfo_main.about_groupbox.setVisible(False)
stockinfo_main.about_groupbox.content_container = QScrollArea(stockinfo_main.about_groupbox)
about_scrollarea_widget = QWidget()
about_scrollarea_widget.resize(540, 800)
about_scrollarea_widget.setLayout(QVBoxLayout())
stockinfo_main.about_groupbox.content_container.setWidget(about_scrollarea_widget)
stockinfo_main.about_groupbox.content_container.setGeometry(5, 15, 530, 520)
stockinfo_main.about_groupbox.content_container.setVerticalScrollBarPolicy(SCROLLBAR_ALWAYSON)

stockinfo_main.news_groupbox = QGroupBox(stockinfo_main)
stockinfo_main.news_groupbox.setStyleSheet('background-color: white')
stockinfo_main.news_groupbox.setTitle("News")
stockinfo_main.news_groupbox.setGeometry(880, 90, 400, 550)
stockinfo_main.news_groupbox.setVisible(False)
stockinfo_main.news_groupbox.setLayout(QVBoxLayout())

stockinfo_recs = QDialog()
stockinfo_recs.setStyleSheet('background-color: deepskyblue')
stockinfo_recs.analyst_rec_groupbox = QGroupBox(stockinfo_recs)
stockinfo_recs.analyst_rec_groupbox.setStyleSheet('background-color: white')
stockinfo_recs.analyst_rec_groupbox.setTitle("Analyst Recommendations")
stockinfo_recs.analyst_rec_groupbox.setGeometry(10, 10, 310, 630)
stockinfo_recs.analyst_rec_groupbox.setVisible(False)
stockinfo_recs.analyst_rec_groupbox.setLayout(QVBoxLayout())
stockinfo_recs.iandi_groupbox = QGroupBox(stockinfo_recs)
stockinfo_recs.iandi_groupbox.setStyleSheet('background-color: white')
stockinfo_recs.iandi_groupbox.setTitle("Insiders and Institutions")
stockinfo_recs.iandi_groupbox.setGeometry(330, 10, 470, 630)
stockinfo_recs.iandi_groupbox.setVisible(False)
stockinfo_recs.iandi_groupbox.setLayout(QVBoxLayout())
stockinfo_recs.mutfund_groupbox = QGroupBox(stockinfo_recs)
stockinfo_recs.mutfund_groupbox.setStyleSheet('background-color: white')
stockinfo_recs.mutfund_groupbox.setTitle("Mutual Fund Holders")
stockinfo_recs.mutfund_groupbox.setGeometry(810, 10, 470, 630)
stockinfo_recs.mutfund_groupbox.setVisible(False)
stockinfo_recs.mutfund_groupbox.setLayout(QVBoxLayout())
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
stockinfo_dialog_forecasts.chart_groupbox.content_container.setVerticalScrollBarPolicy(SCROLLBAR_ALWAYSON)
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
qtr_earnings_table.setFont(ARIAL_10)
qtr_earnings_table.setStyleSheet('background-color: white;')
qtr_revtrend_chart = QChart()
qtr_revtrend_chart.setTitle("Quarterly Revenue Trend")
qtr_revtrend_barseries = QBarSeries()
qtr_revtrend_chart.addSeries(qtr_revtrend_barseries)
qtr_revtrend_gb = QGroupBox(prediction_chart_widget)
qtr_revtrend_gb.setTitle("Revenue History and Projections")
qtr_revtrend_gb.setGeometry(10, 730, 1200, 350)
qtr_revtrend_chartview = QChartView(qtr_revtrend_chart)
qtr_revtrend_chartview.setParent(qtr_revtrend_gb)
qtr_revtrend_chartview.setVisible(True)
qtr_revtrend_chartview.setGeometry(10, 15, 800, 300)
qtr_revtrend_label_container = QWidget(qtr_revtrend_gb)
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
yr_revtrend_gb = QGroupBox(prediction_chart_widget)
yr_revtrend_gb.setTitle("Revenue History and Projections")
yr_revtrend_gb.setGeometry(10, 1450, 1200, 360)
yr_revtrend_chartview = QChartView(yr_revtrend_chart)
yr_revtrend_chartview.setParent(yr_revtrend_gb)
yr_revtrend_chartview.setVisible(True)
yr_revtrend_chartview.setGeometry(10, 15, 800, 300)
yr_revtrend_label_container = QWidget(yr_revtrend_gb)
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
stockinfo_dialog_financials.content_container.setVerticalScrollBarPolicy(SCROLLBAR_ALWAYSON)
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
financials_table.setFont(ARIAL_10)
financials_table.setStyleSheet('background-color: white;')
stockinfo_dialog.addTab(stockinfo_main, "Overview")
stockinfo_dialog.addTab(stockinfo_recs, "Insiders and Institutions")
stockinfo_dialog.addTab(stockinfo_dialog_forecasts, "Forecasts")
stockinfo_dialog.addTab(stockinfo_dialog_financials, "Financials")
stockinfo_dialog.connect(stockinfo_dialog, SIGNAL(
    'currentChanged(int)'), lambda: stockinfo_dialog_changed(stockinfo_dialog.currentIndex()))


####################
# DCF model dialog #
####################
dcf_dialog = QDialog()
dcf_dialog.setStyleSheet('background-color: deepskyblue;')

# searchbar init
dcf_dialog.searchbar_gb = QGroupBox(dcf_dialog)
dcf_dialog.searchbar_gb.setStyleSheet('background-color: white;')
dcf_dialog.searchbar_gb.setTitle("Find a Stock")
dcf_dialog.searchbar_gb.setGeometry(10, 10, 960, 70)
dcf_dialog.searchbar_gb.searchBar = QLineEdit(dcf_dialog.searchbar_gb)
dcf_dialog.searchbar_gb.searchBar.setGeometry(10, 20, 850, 40)
dcf_dialog.searchbar_gb.searchBar.textChanged.connect(search_text_changed)
dcf_dialog.searchbar_gb.searchBar.setFont(ARIAL_10)
dcf_dialog.searchbar_gb.searchBar.setCompleter(completer)
dcf_dialog.searchbar_gb.search_button = QPushButton(dcf_dialog.searchbar_gb)
dcf_dialog.searchbar_gb.search_button.setGeometry(870, 20, 80, 40)
dcf_dialog.searchbar_gb.search_button.setText("Show Model")
dcf_dialog.searchbar_gb.search_button.clicked.connect(dcf_findstock_button_click)

# inputs init
dcf_dialog.inputs_gb = QGroupBox(dcf_dialog)
dcf_dialog.inputs_gb.setStyleSheet('background-color: white;')
dcf_dialog.inputs_gb.setTitle("Model Inputs")
dcf_dialog.inputs_gb.setGeometry(10, 90, 630, 570)
dcf_dialog.inputs_gb.company_label = QLabel(dcf_dialog.inputs_gb)
dcf_dialog.inputs_gb.company_label.setText("Company:")
dcf_dialog.inputs_gb.company_label.setGeometry(10, 20, 100, 50)
dcf_dialog.inputs_gb.mkt_price_label = QLabel(dcf_dialog.inputs_gb)
dcf_dialog.inputs_gb.mkt_price_label.setText("Market Price:")
dcf_dialog.inputs_gb.mkt_price_label.setGeometry(10, 70, 100, 50)
dcf_dialog.inputs_gb.mkt_price = QLabel(dcf_dialog.inputs_gb)
dcf_dialog.inputs_gb.mkt_price.setGeometry(570, 70, 100, 50)
dcf_dialog.inputs_gb.eps_label = QLabel(dcf_dialog.inputs_gb)
dcf_dialog.inputs_gb.eps_label.setText("Earnings per Share:")
dcf_dialog.inputs_gb.eps_label.setGeometry(10, 120, 100, 50)
dcf_dialog.inputs_gb.eps = QLabel(dcf_dialog.inputs_gb)
dcf_dialog.inputs_gb.eps.setGeometry(570, 120, 100, 50)
dcf_dialog.inputs_gb.growth_label = QLabel(dcf_dialog.inputs_gb)
dcf_dialog.inputs_gb.growth_label.setText("Growth Estimate:")
dcf_dialog.inputs_gb.growth_label.setGeometry(10, 170, 100, 50)
dcf_dialog.inputs_gb.growth_slider = QSlider(dcf_dialog.inputs_gb)
dcf_dialog.inputs_gb.growth_slider.setOrientation(Qt.Orientation.Horizontal)
dcf_dialog.inputs_gb.growth_slider.setTickPosition(QSlider.TickPosition.TicksBothSides)
dcf_dialog.inputs_gb.growth_slider.setGeometry(110, 170, 450, 50)
dcf_dialog.inputs_gb.growth_slider.setTickInterval(10)
dcf_dialog.inputs_gb.growth_slider.setRange(-500, 4000)
dcf_dialog.inputs_gb.growth_slider.setSliderPosition(0)
dcf_dialog.inputs_gb.growth_slider.valueChanged.connect(growth_slider_moved)
dcf_dialog.inputs_gb.growth = QLabel(dcf_dialog.inputs_gb)
dcf_dialog.inputs_gb.growth.setGeometry(570, 170, 100, 50)
dcf_dialog.inputs_gb.def_growth_button = QCheckBox(dcf_dialog.inputs_gb)
dcf_dialog.inputs_gb.def_growth_button.setText("Use Analyst 5-Year Growth Estimate")
dcf_dialog.inputs_gb.def_growth_button.setGeometry(1100, 170, 100, 50)
dcf_dialog.inputs_gb.term_label = QLabel(dcf_dialog.inputs_gb)
dcf_dialog.inputs_gb.term_label.setText("Term:")
dcf_dialog.inputs_gb.term_label.setGeometry(10, 220, 100, 50)
dcf_dialog.inputs_gb.term_slider = QSlider(dcf_dialog.inputs_gb)
dcf_dialog.inputs_gb.term_slider.setOrientation(Qt.Orientation.Horizontal)
dcf_dialog.inputs_gb.term_slider.setTickPosition(QSlider.TickPosition.TicksBothSides)
dcf_dialog.inputs_gb.term_slider.setGeometry(110, 220, 450, 50)
dcf_dialog.inputs_gb.term_slider.setTickInterval(1)
dcf_dialog.inputs_gb.term_slider.setRange(1, 10)
dcf_dialog.inputs_gb.term_slider.setSliderPosition(5)
dcf_dialog.inputs_gb.term_slider.valueChanged.connect(term_slider_moved)
dcf_dialog.inputs_gb.term = QLabel(dcf_dialog.inputs_gb)
dcf_dialog.inputs_gb.term.setText("5 years")
dcf_dialog.inputs_gb.term.setGeometry(570, 220, 100, 50)
dcf_dialog.inputs_gb.discount_rate_label = QLabel(dcf_dialog.inputs_gb)
dcf_dialog.inputs_gb.discount_rate_label.setText("Discount Rate: ")
dcf_dialog.inputs_gb.discount_rate_label.setGeometry(10, 270, 100, 50)
dcf_dialog.inputs_gb.discount_rate_slider = QSlider(dcf_dialog.inputs_gb)
dcf_dialog.inputs_gb.discount_rate_slider.setOrientation(Qt.Orientation.Horizontal)
dcf_dialog.inputs_gb.discount_rate_slider.setTickPosition(QSlider.TickPosition.TicksBothSides)
dcf_dialog.inputs_gb.discount_rate_slider.setGeometry(110, 270, 450, 50)
dcf_dialog.inputs_gb.discount_rate_slider.setTickInterval(10)
dcf_dialog.inputs_gb.discount_rate_slider.setRange(-500, 2000)
dcf_dialog.inputs_gb.discount_rate_slider.setSliderPosition(1000)
dcf_dialog.inputs_gb.discount_rate_slider.valueChanged.connect(discount_slider_moved)
dcf_dialog.inputs_gb.discount_rate = QLabel(dcf_dialog.inputs_gb)
dcf_dialog.inputs_gb.discount_rate.setGeometry(570, 270, 100, 50)
dcf_dialog.inputs_gb.perpetual_rate_label = QLabel(dcf_dialog.inputs_gb)
dcf_dialog.inputs_gb.perpetual_rate_label.setText("Perpetual Rate:")
dcf_dialog.inputs_gb.perpetual_rate_label.setGeometry(10, 320, 100, 50)
dcf_dialog.inputs_gb.perpetual_rate_slider = QSlider(dcf_dialog.inputs_gb)
dcf_dialog.inputs_gb.perpetual_rate_slider.setOrientation(Qt.Orientation.Horizontal)
dcf_dialog.inputs_gb.perpetual_rate_slider.setGeometry(110, 320, 450, 50)
dcf_dialog.inputs_gb.perpetual_rate_slider.setTickInterval(10)
dcf_dialog.inputs_gb.perpetual_rate_slider.setTickPosition(QSlider.TickPosition.TicksBothSides)
dcf_dialog.inputs_gb.perpetual_rate_slider.setRange(-500, 1000)
dcf_dialog.inputs_gb.perpetual_rate_slider.setSliderPosition(250)
dcf_dialog.inputs_gb.perpetual_rate_slider.valueChanged.connect(perpetual_slider_moved)
dcf_dialog.inputs_gb.perpetual_rate = QLabel(dcf_dialog.inputs_gb)
dcf_dialog.inputs_gb.perpetual_rate.setGeometry(570, 320, 100, 50)
dcf_dialog.inputs_gb.last_fcf_label = QLabel(dcf_dialog.inputs_gb)
dcf_dialog.inputs_gb.last_fcf_label.setText("Last Free Cash Flow:")
dcf_dialog.inputs_gb.last_fcf_label.setGeometry(10, 370, 100, 50)
dcf_dialog.inputs_gb.last_fcf = QLabel(dcf_dialog.inputs_gb)
dcf_dialog.inputs_gb.last_fcf.setGeometry(570, 370, 100, 50)
dcf_dialog.inputs_gb.shares_label = QLabel(dcf_dialog.inputs_gb)
dcf_dialog.inputs_gb.shares_label.setText("Shares in Circulation:")
dcf_dialog.inputs_gb.shares_label.setGeometry(10, 420, 100, 50)
dcf_dialog.inputs_gb.shares = QLabel(dcf_dialog.inputs_gb)
dcf_dialog.inputs_gb.shares.setGeometry(570, 420, 100, 50)
dcf_dialog.inputs_gb.get_analysis_button = QPushButton(dcf_dialog.inputs_gb)
dcf_dialog.inputs_gb.get_analysis_button.setGeometry(210, 480, 200, 100)
dcf_dialog.inputs_gb.get_analysis_button.setText("Get Fair Value")
dcf_dialog.inputs_gb.get_analysis_button.clicked.connect(dcf_getanalysis_button_click)

# outputs init
dcf_dialog.outputs_gb = QGroupBox(dcf_dialog)
dcf_dialog.outputs_gb.setStyleSheet('background-color: white;')
dcf_dialog.outputs_gb.setTitle("Model Outputs")
dcf_dialog.outputs_gb.setGeometry(650, 90, 630, 570)
dcf_dialog.outputs_gb.verdict_label = QLabel(dcf_dialog.outputs_gb)
dcf_dialog.outputs_gb.verdict_label.setGeometry(200, 10, 200, 50)
dcf_dialog.outputs_gb.basic_gb = QGroupBox(dcf_dialog.outputs_gb)
dcf_dialog.outputs_gb.basic_gb.setGeometry(10, 20, 610, 350)
dcf_dialog.outputs_gb.basic_gb.setTitle("Basic Model")

# chart for future cashflows init
future_cashflows_chart = QChart()
future_cashflows_lineseries = QLineSeries()
future_cashflows_lineseries.setName("Future Cashflows")
future_cashflows_chart.addSeries(future_cashflows_lineseries)
future_cashflows_chartview = QChartView(future_cashflows_chart)
future_cashflows_chartview.setParent(dcf_dialog.outputs_gb.basic_gb)
future_cashflows_chartview.setGeometry(10, 20, 590, 200)

# basic DCF model output
dcf_dialog.outputs_gb.basic_gb.fair_value_label = QLabel(dcf_dialog.outputs_gb.basic_gb)
dcf_dialog.outputs_gb.basic_gb.fair_value_label.setText("Fair Value:")
dcf_dialog.outputs_gb.basic_gb.fair_value_label.setGeometry(250, 230, 100, 50)
dcf_dialog.outputs_gb.basic_gb.fair_value = QLabel(dcf_dialog.outputs_gb.basic_gb)
dcf_dialog.outputs_gb.basic_gb.fair_value.setGeometry(200, 280, 100, 50)

# graham model output
dcf_dialog.outputs_gb.graham_gb = QGroupBox(dcf_dialog.outputs_gb)
dcf_dialog.outputs_gb.graham_gb.setGeometry(10, 380, 610, 150)
dcf_dialog.outputs_gb.graham_gb.setTitle("Graham Model")
dcf_dialog.outputs_gb.graham_gb.ev_label = QLabel(dcf_dialog.outputs_gb.graham_gb)
dcf_dialog.outputs_gb.graham_gb.ev_label.setText("Expected value implied by growth rate:")
dcf_dialog.outputs_gb.graham_gb.ev_label.setGeometry(10, 20, 200, 50)
dcf_dialog.outputs_gb.graham_gb.ev = QLabel(dcf_dialog.outputs_gb.graham_gb)
dcf_dialog.outputs_gb.graham_gb.ev.setGeometry(490, 20, 100, 50)
dcf_dialog.outputs_gb.graham_gb.graham_ge_label = QLabel(dcf_dialog.outputs_gb.graham_gb)
dcf_dialog.outputs_gb.graham_gb.graham_ge_label.setText("Growth rate implied by stock price:")
dcf_dialog.outputs_gb.graham_gb.graham_ge_label.setGeometry(10, 80, 200, 50)
dcf_dialog.outputs_gb.graham_gb.graham_growth_estimate = QLabel(dcf_dialog.outputs_gb.graham_gb)
dcf_dialog.outputs_gb.graham_gb.graham_growth_estimate.setGeometry(490, 80, 100, 50)

######################
# trade ideas dialog #
######################
ideas_dialog = QTabWidget()
ideas_dialog.setStyleSheet('background-color: deepskyblue')

scanner_dialog = QDialog()
scanner_dialog.setStyleSheet('background-color: deepskyblue')
scanner_dialog.setLayout(QGridLayout())

def create_results_dialog(search_criteria=None, search_results: list[dict] | pd.DataFrame=None, sort_field=None, results_iterable=None):
    """
    Changes the content of the "Scanner" dialog in the "Trade Ideas" tab to the scanner search results
    """
    new_scanner_dialog = QDialog()
    new_scanner_dialog.setStyleSheet('background-color: deepskyblue')

    new_scanner_dialog.back_button = QPushButton(new_scanner_dialog)

    new_scanner_dialog.back_button.setIcon(QIcon(f"{CWD}icons/backarrow.png"))
    new_scanner_dialog.back_button.setGeometry(10, 20, 50, 50)

    def back_button_clicked():
        ideas_dialog.removeTab(0)
        ideas_dialog.insertTab(0, scanner_dialog, 'Scanner')
        ideas_dialog.setCurrentIndex(0)

    new_scanner_dialog.back_button.clicked.connect(back_button_clicked)

    new_scanner_dialog.results_scroll = QScrollArea(new_scanner_dialog)
    new_scanner_dialog.results_scroll.setGeometry(100, 20, 1100, 550)
    new_scanner_dialog.results_scroll.setStyleSheet('background-color: white')
    new_scanner_dialog.results_scroll.setSizePolicy(
        QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
    )

    new_scanner_dialog.results_widget = QWidget(new_scanner_dialog)
    new_scanner_dialog.results_widget.setLayout(QVBoxLayout())
    new_scanner_dialog.setMinimumWidth(1000)

    if search_criteria is not None and sort_field is not None:
        for result in sc.get_results(search_criteria, sort_field):
            result_widget = QWidget()
            result_widget.setLayout(QHBoxLayout())
            for key in result.keys():
                result_widget.layout().addWidget(QLabel(str(result[key])))

            new_scanner_dialog.results_widget.layout().addWidget(result_widget)
    elif search_results is not None:
        for result in results_iterable:
            result_widget = QWidget()
            result_widget.setLayout(QHBoxLayout())
            for item in result:
                result_widget.layout().addWidget(QLabel(str(item)))

            new_scanner_dialog.results_widget.layout().addWidget(result_widget)



    new_scanner_dialog.results_scroll.setWidget(new_scanner_dialog.results_widget)
    ideas_dialog.removeTab(0)
    ideas_dialog.insertTab(0, new_scanner_dialog, 'Scanner')
    ideas_dialog.setCurrentIndex(0)


def create_scanner(title, desc, search_criteria, xpos, ypos, sort_field=None):
    """
    Creates a scanner widget and adds it to the scanner dialog
    """
    scanner_groupbox = QGroupBox(scanner_dialog)
    scanner_groupbox.setTitle(title)
    scanner_groupbox.setStyleSheet('background-color: white')

    scanner_groupbox.desc_label = QLabel(scanner_groupbox)
    scanner_groupbox.desc_label.setText(desc)
    scanner_groupbox.desc_label.setWordWrap(True)
    scanner_groupbox.desc_label.setGeometry(10, 15, 130, 90)

    scanner_groupbox.run_button = QPushButton(scanner_groupbox)
    scanner_groupbox.run_button.setText('Run')
    scanner_groupbox.run_button.setGeometry(25, 110, 100, 20)

    scanner_groupbox.run_button.clicked.connect(
        lambda: create_results_dialog(search_criteria=search_criteria, sort_field=sort_field)
    )

    scanner_dialog.layout().addWidget(scanner_groupbox, ypos, xpos)

create_scanner(
    'Day Gainers',
    "Find stocks that have gained the most relative to their close yesterday",
    "day_gainers",
    0, 0,
    'regularMarketChangePercent',
)

create_scanner(
    "Day Losers",
    "Find stocks that have lost the most relative to their close yesterday",
    "day_losers",
    1, 0,
    "regularMarketChangePercent"
)

create_scanner(
    "Most Active",
    "Find stocks that have traded the most shares today",
    "most_actives",
    2, 0,
    "regularMarketVolume"
)

create_scanner(
    "Options Open Interest",
    "Find options with the highest Open Interest",
    "top_options_open_interest",
    3, 0
)

create_scanner(
    "Options Implied Volatility",
    "Find options with the highest Implied Volatility",
    "top_options_implied_volatility",
    4, 0
)

create_scanner(
    "Undervalued Growth Stocks",
    "Find stocks with earnings growth above 25% and low PE ratios",
    "undervalued_growth_stocks",
    5, 0
)

create_scanner(
    "Undervalued Large Caps",
    "Find large cap stocks trading at low multiples",
    "undervalued_large_caps",
    6, 0
)

create_scanner(
    "Small Cap Gainers",
    "Find small cap stocks up more than 5% today",
    "small_cap_gainers",
    0, 1
)

uncon_strats_dialog = QDialog()
uncon_strats_dialog.setStyleSheet('background-color: deepskyblue')

uncon_strats_dialog.cramer_gb = QGroupBox(uncon_strats_dialog)
uncon_strats_dialog.cramer_gb.setTitle('Inverse Jim Cramer')
uncon_strats_dialog.cramer_gb.setGeometry(10, 20, 350, 350)
uncon_strats_dialog.cramer_gb.setStyleSheet('background-color: white')

uncon_strats_dialog.cramer_gb.cramer_btn = QPushButton(uncon_strats_dialog.cramer_gb)
uncon_strats_dialog.cramer_gb.cramer_btn.setIcon(QIcon(rf"{CWD}\icons\index.jpg"))
uncon_strats_dialog.cramer_gb.cramer_btn.setIconSize(QSize(200, 300))
uncon_strats_dialog.cramer_gb.cramer_btn.setGeometry(10, 20, 300, 190)
uncon_strats_dialog.cramer_gb.cramer_btn.setEnabled(False)


def uncon_strat_enter(_: QEnterEvent, button: QPushButton):
    """
    Triggered when one of the unconventional strategy buttons is entered by the mouse
    """

    button.setEnabled(True)
    button.setStyleSheet(
        """
        border: 3px solid green;
        """
    )


def uncon_strat_leave(_, button: QPushButton):
    button.setEnabled(False)
    button.setStyleSheet("")


def cramer_btn_clicked():
    results = us.get_cramer_recs()
    results_iter = zip(
        results['Stock'], results['Direction'], results['Date'], results['Return Since']
    )
    create_results_dialog(search_results=results, results_iterable=results_iter)

uncon_strats_dialog.cramer_gb.cramer_btn.enterEvent = lambda e: uncon_strat_enter(
    e, uncon_strats_dialog.cramer_gb.cramer_btn
)
uncon_strats_dialog.cramer_gb.cramer_btn.leaveEvent = lambda e: uncon_strat_leave(
    e, uncon_strats_dialog.cramer_gb.cramer_btn
)
uncon_strats_dialog.cramer_gb.cramer_btn.clicked.connect(cramer_btn_clicked)

uncon_strats_dialog.cramer_gb.cramer_label_header = QLabel(uncon_strats_dialog.cramer_gb)
uncon_strats_dialog.cramer_gb.cramer_label_header.setText('Inverse Cramer Scanner')
uncon_strats_dialog.cramer_gb.cramer_label_header.setGeometry(10, 240, 300, 30)
uncon_strats_dialog.cramer_gb.cramer_label_header.setFont(QFont('arial', 20))

uncon_strats_dialog.cramer_gb.cramer_label_text = QLabel(uncon_strats_dialog.cramer_gb)
uncon_strats_dialog.cramer_gb.cramer_label_text.setText(
    "Find CNBC analyst Jim Cramer's most recent buy and sell recommendations"
)
uncon_strats_dialog.cramer_gb.cramer_label_text.setGeometry(10, 270, 300, 50)
uncon_strats_dialog.cramer_gb.cramer_label_text.setWordWrap(True)


uncon_strats_dialog.wsb_gb = QGroupBox(uncon_strats_dialog)
uncon_strats_dialog.wsb_gb.setTitle('WSB Scanner')
uncon_strats_dialog.wsb_gb.setGeometry(500, 20, 350, 350)
uncon_strats_dialog.wsb_gb.setStyleSheet('background-color: white')

uncon_strats_dialog.wsb_gb.wsb_btn = QPushButton(uncon_strats_dialog.wsb_gb)
uncon_strats_dialog.wsb_gb.wsb_btn.setIcon(QIcon(rf"{CWD}\icons\index.jpg"))
uncon_strats_dialog.wsb_gb.wsb_btn.setIconSize(QSize(200, 300))
uncon_strats_dialog.wsb_gb.wsb_btn.setGeometry(10, 20, 300, 190)
uncon_strats_dialog.wsb_gb.wsb_btn.setEnabled(False)


def wsb_btn_clicked():
    results = us.get_wsb_tickers()
    results_iter = zip(results['Stock'], results['Mentions'], results['% Change'])
    create_results_dialog(search_results=results, results_iterable=results_iter)

uncon_strats_dialog.wsb_gb.wsb_btn.enterEvent = lambda e: uncon_strat_enter(
    e, uncon_strats_dialog.wsb_gb.wsb_btn
)
uncon_strats_dialog.wsb_gb.wsb_btn.leaveEvent = lambda e: uncon_strat_leave(
    e, uncon_strats_dialog.wsb_gb.wsb_btn
)
uncon_strats_dialog.wsb_gb.wsb_btn.clicked.connect(wsb_btn_clicked)

uncon_strats_dialog.wsb_gb.wsb_label_header = QLabel(uncon_strats_dialog.wsb_gb)
uncon_strats_dialog.wsb_gb.wsb_label_header.setText('WallStreetBets Trending')
uncon_strats_dialog.wsb_gb.wsb_label_header.setGeometry(10, 240, 300, 30)
uncon_strats_dialog.wsb_gb.wsb_label_header.setFont(QFont('arial', 20))

uncon_strats_dialog.wsb_gb.wsb_label_text = QLabel(uncon_strats_dialog.wsb_gb)
uncon_strats_dialog.wsb_gb.wsb_label_text.setText(
    "Find tickers that are recieving the most attention from r/WallStreetBets"
)
uncon_strats_dialog.wsb_gb.wsb_label_text.setGeometry(10, 270, 300, 50)
uncon_strats_dialog.wsb_gb.wsb_label_text.setWordWrap(True)



uncon_strats_dialog.google_gb = QGroupBox(uncon_strats_dialog)
uncon_strats_dialog.google_gb.setTitle('Google Trends Scanner')
uncon_strats_dialog.google_gb.setGeometry(250, 400, 350, 350)
uncon_strats_dialog.google_gb.setStyleSheet('background-color: white')

uncon_strats_dialog.google_gb.google_btn = QPushButton(uncon_strats_dialog.google_gb)
uncon_strats_dialog.google_gb.google_btn.setIcon(QIcon(rf"{CWD}\icons\index.jpg"))
uncon_strats_dialog.google_gb.google_btn.setIconSize(QSize(200, 300))
uncon_strats_dialog.google_gb.google_btn.setGeometry(10, 20, 300, 190)
uncon_strats_dialog.google_gb.google_btn.setEnabled(False)


def google_btn_clicked():
    results = us.get_google_trends()
    results_iter = zip(results['Ticker'], results['Trend Score'])
    create_results_dialog(search_results=results, results_iterable=results_iter)

uncon_strats_dialog.google_gb.google_btn.enterEvent = lambda e: uncon_strat_enter(
    e, uncon_strats_dialog.google_gb.google_btn
)
uncon_strats_dialog.google_gb.google_btn.leaveEvent = lambda e: uncon_strat_leave(
    e, uncon_strats_dialog.google_gb.google_btn
)
uncon_strats_dialog.google_gb.google_btn.clicked.connect(google_btn_clicked)

uncon_strats_dialog.google_gb.google_label_header = QLabel(uncon_strats_dialog.google_gb)
uncon_strats_dialog.google_gb.google_label_header.setText('Google Trending')
uncon_strats_dialog.google_gb.google_label_header.setGeometry(10, 240, 300, 30)
uncon_strats_dialog.google_gb.google_label_header.setFont(QFont('arial', 20))

uncon_strats_dialog.google_gb.google_label_text = QLabel(uncon_strats_dialog.google_gb)
uncon_strats_dialog.google_gb.google_label_text.setText(
    "Find tickers that are recieving the most search interest"
)
uncon_strats_dialog.google_gb.google_label_text.setGeometry(10, 270, 300, 50)
uncon_strats_dialog.google_gb.google_label_text.setWordWrap(True)


ideas_dialog.addTab(scanner_dialog, "Scanner")

ideas_dialog.addTab(uncon_strats_dialog, "Unconventional Strategies")


###################
# minigame dialog #
###################

minigame_dialog = QDialog()
minigame_dialog.setStyleSheet('background-color: deepskyblue;')

minigame_dialog.minigame_label = QLabel(minigame_dialog)
minigame_dialog.minigame_label.setStyleSHeet('background-color: deepskyblue;')
minigame_dialog.minigame_label.setText('Launch Minigame')
minigame_dialog.minigame_label.setFong(QFont('arial', 20))
minigame_dialog.minigame_label.setGeometry(550, 410, 200, 100)

minigame_dialog.minigame_btn = QPushButton(minigame_dialog)
minigame_dialog.minigame_btn.setGeometry(550, 200, 200, 200)


###################
# settings dialog #
###################

# create lists of colors for up and down candles and chart styles
up_colors = ['Green', 'Red', 'Cyan', 'Purple']
down_colors = ['Green', 'Red', 'Cyan', 'Purple']
chart_styles = ['binance', 'blueskies', 'brasil', 'charles', 'checkers', 'classic',
                'default', 'ibd', 'kenan', 'mike', 'nightclouds', 'sas', 'starsandstripes', 'yahoo']
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
settings_dialog.apply_button.clicked.connect(apply_settings_changes)


#################
# wallet dialog #
#################

wallet_dialog = QDialog()
wallet_dialog.setStyleSheet('background-color: goldenrod')
# user's crypto wallet NAV
wallet_dialog.nav_gb = QGroupBox(wallet_dialog)
wallet_dialog.nav_gb.setTitle("Your NAV")
wallet_dialog.nav_gb.setGeometry(10, 10, 250, 250)
wallet_dialog.nav_gb.setStyleSheet('background-color: black; color: white;')
# net liquidation value labels
wallet_dialog.nav_gb.netLiq = QLabel(wallet_dialog.nav_gb)
wallet_dialog.nav_gb.netLiq.setText("Net Liq: ")
wallet_dialog.nav_gb.netLiq.setGeometry(10, 20, 80, 20)
wallet_dialog.nav_gb.netLiq.setFont(QFont('genius', 10))
wallet_dialog.nav_gb.liq = QLabel(wallet_dialog.nav_gb)
wallet_dialog.nav_gb.liq.setGeometry(10, 40, 160, 40)
wallet_dialog.nav_gb.liq.setFont(QFont('genius', 20))
# positions table settings
wallet_dialog.pos_view_gb = QGroupBox(wallet_dialog)
wallet_dialog.pos_view_gb.setGeometry(10, 300, 900, 250)
wallet_dialog.pos_view_gb.setTitle("Your Portfolio")
wallet_dialog.pos_view_gb.setStyleSheet('background-color: black; color: white;')
wallet_dialog.pos_view_gb.pos_view = QTableWidget(wallet_dialog.pos_view_gb)
wallet_dialog.pos_view_gb.pos_view.setEditTriggers(
    QAbstractItemView.EditTrigger.NoEditTriggers)
wallet_dialog.pos_view_gb.pos_view.setFont(ARIAL_10)
wallet_dialog.pos_view_gb.pos_view.setRowCount(len(wallet_amts) - 1)
wallet_dialog.pos_view_gb.pos_view.setColumnCount(8)
wallet_dialog.pos_view_gb.pos_view.setGeometry(10, 20, 850, 200)
wallet_dialog.pos_view_gb.pos_view.setStyleSheet('background-color: black;')
wallet_dialog.pos_view_gb.pos_view.horizontalHeader().setStyleSheet(
    "::section{background-color: black; color: white}"
)
btn = wallet_dialog.pos_view_gb.pos_view.cornerWidget()
wallet_dialog.pos_view_gb.pos_view.setHorizontalHeaderItem(
    0, QTableWidgetItem("Ticker"))
wallet_dialog.pos_view_gb.pos_view.setHorizontalHeaderItem(
    1, QTableWidgetItem("Today's Performance"))
wallet_dialog.pos_view_gb.pos_view.setHorizontalHeaderItem(
    2, QTableWidgetItem("Current Price"))
wallet_dialog.pos_view_gb.pos_view.setHorizontalHeaderItem(
    3, QTableWidgetItem("Gain/Loss Per Share Today"))
wallet_dialog.pos_view_gb.pos_view.setHorizontalHeaderItem(
    4, QTableWidgetItem("Purchase Price"))
wallet_dialog.pos_view_gb.pos_view.setHorizontalHeaderItem(
    5, QTableWidgetItem("# of Shares"))
wallet_dialog.pos_view_gb.pos_view.setHorizontalHeaderItem(
    6, QTableWidgetItem("Total Value"))
wallet_dialog.pos_view_gb.pos_view.setHorizontalHeaderItem(
    7, QTableWidgetItem("Position Gain/Loss"))
for i in range(8):
    wallet_dialog.pos_view_gb.pos_view.horizontalHeaderItem(i).setFont(ARIAL_10)

for i in range(wallet_dialog.pos_view_gb.pos_view.rowCount()):
    wallet_dialog.pos_view_gb.pos_view.setVerticalHeaderItem(0, QTableWidgetItem("1"))
    wallet_dialog.pos_view_gb.pos_view.verticalHeaderItem(i).setFont(ARIAL_10)
    for j in range(wallet_dialog.pos_view_gb.pos_view.columnCount()):
        wallet_dialog.pos_view_gb.pos_view.setItem(i, j, QTableWidgetItem())

update_wallet_table()
# cash labels
wallet_dialog.nav_gb.cashLabel = QLabel(wallet_dialog.nav_gb)
wallet_dialog.nav_gb.cashLabel.setText("Cash: ")
wallet_dialog.nav_gb.cashLabel.setGeometry(10, 90, 80, 20)
wallet_dialog.nav_gb.cash = QLabel(wallet_dialog.nav_gb)
wallet_dialog.nav_gb.cash.setGeometry(100, 90, 80, 20)
# buying power labels
wallet_dialog.nav_gb.bp_label = QLabel(wallet_dialog.nav_gb)
wallet_dialog.nav_gb.bp_label.setText("Buying Power: ")
wallet_dialog.nav_gb.bp_label.setGeometry(10, 110, 80, 20)
wallet_dialog.nav_gb.bp = QLabel(wallet_dialog.nav_gb)
wallet_dialog.nav_gb.bp.setGeometry(100, 110, 80, 20)
# assets labels
wallet_dialog.nav_gb.assetsLabel = QLabel(wallet_dialog.nav_gb)
wallet_dialog.nav_gb.assetsLabel.setText("Long Assets: ")
wallet_dialog.nav_gb.assetsLabel.setGeometry(10, 130, 80, 20)
wallet_dialog.nav_gb.assets = QLabel(wallet_dialog.nav_gb)
wallet_dialog.nav_gb.assets.setGeometry(100, 130, 80, 20)
# liabilities labels
wallet_dialog.nav_gb.liabilitiesLabel = QLabel(wallet_dialog.nav_gb)
wallet_dialog.nav_gb.liabilitiesLabel.setText("Short Assets: ")
wallet_dialog.nav_gb.liabilitiesLabel.setGeometry(10, 150, 80, 20)
wallet_dialog.nav_gb.liabilities = QLabel(wallet_dialog.nav_gb)
wallet_dialog.nav_gb.liabilities.setGeometry(100, 150, 80, 20)
# return since inception labels
wallet_dialog.nav_gb.returnSinceInceptionLabel = QLabel(wallet_dialog.nav_gb)
wallet_dialog.nav_gb.returnSinceInceptionLabel.setText("Return Since Inception: ")
wallet_dialog.nav_gb.returnSinceInceptionLabel.setGeometry(10, 170, 120, 20)
wallet_dialog.nav_gb.returnSinceInception = QLabel(wallet_dialog.nav_gb)
wallet_dialog.nav_gb.returnSinceInception.setFont(QFont('genius', 20))
wallet_dialog.nav_gb.returnSinceInception.setGeometry(10, 190, 120, 30)
wallet_dialog.pos_view_gb.pos_view.resizeColumnsToContents()
update_wallet_nav()


######################
# end of dialog init #
######################

# adding tabs to main window
widget.addTab(port_dialog, "Your Portfolio")
widget.addTab(chart_dialog, "Chart Stocks")
widget.addTab(trade_dialog, "Trade Stocks")
widget.addTab(stockinfo_dialog, "Get Stock Info")
widget.addTab(dcf_dialog, "DCF Modelling")
widget.addTab(ideas_dialog, "Trade Ideas")
widget.addTab(wallet_dialog, "Your Crypto Wallet")
widget.addTab(minigame_dialog, "Minigame")
widget.addTab(settings_dialog, "Settings")
widget.resize(1300, 700)
widget.show()
splash.close()

# instantiate thread which runs the updateNav function in an infinite loop
Thread(target=update_ui, daemon=True).start()
sys.exit(app.exec())
