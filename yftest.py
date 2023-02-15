# Started by Ray Ikome on 11/16/22
import sys
import os
from locale import atof, setlocale, LC_NUMERIC
from threading import Thread
import time
import xml.etree.ElementTree as et

import pandas as pd
# pylint: disable-msg=E0611
from PySide6.QtCharts import (QChart, QChartView, QPieSeries, QLineSeries,
                              QDateTimeAxis, QValueAxis, QBarSeries, QBarSet)
from PySide6.QtWidgets import (QWidget, QTabWidget, QGroupBox, QLabel, QTableWidget,
                               QTableWidgetItem, QAbstractItemView, QHBoxLayout,
                               QSplashScreen, QPushButton, QDialog, QLineEdit, QComboBox,
                               QRadioButton, QCalendarWidget, QCheckBox, QApplication,
                               QProgressBar, QVBoxLayout, QScrollArea, QButtonGroup,
                               QSlider, QSpinBox, QDoubleSpinBox)
from PySide6.QtGui import QFont, QFontDatabase, QPixmap, QIcon, QColor
from PySide6.QtCore import QRect, QStringListModel, QDateTime, Qt, SIGNAL, QPropertyAnimation
import yfinance as yf
import mplfinance as mpf
from bs4 import BeautifulSoup

import yahooquery as yq

from dependencies import autocomplete as ac
from dependencies import IsMarketOpen as mktopen
from dependencies import dcfmodel as dcf
from dependencies import numberformat as nf
from dependencies import finviznews as fn
tab2_isloaded = False
tab3_isloaded = False
tab4_isloaded = False

CURRENT_DIR = os.getcwd() + '\\'

QPropertyAnimation()

current_ticker = ''

selected_ta = []


def spy_button_clicked():
    """
    Is called when the "Chart SPY" button is clicked.
    Charts SPY with the current user settings
    """
    chart_configurations.search_bar_groupbox.searchBar.setText(
        "SPY - SPDR S&P 500 ETF Trust"
    )
    searchButtonClicked()


def qqq_button_clicked():
    """
    Is called when the "Chart QQQ" button is clicked.
    Charts QQQ with the current user settings
    """
    chart_configurations.search_bar_groupbox.searchBar.setText(
        "QQQ - Invesco QQQ Trust"
    )
    searchButtonClicked()


def dia_button_clicked():
    """
    Is called when the "Chart DIA" button is clicked.
    Charts DIA with the current user settings
    """
    chart_configurations.search_bar_groupbox.searchBar.setText(
        "DIA - SPDR Dow Jones Industrial Average ETF Trust"
    )
    searchButtonClicked()


def vix_button_clicked():
    """
    Is called when the "Chart VIX" button is clicked.
    Charts VIX with the current user settings
    """
    chart_configurations.search_bar_groupbox.searchBar.setText("^VIX ")
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
        if widget.currentWidget() == wallet_dialog:
                update_wallet_table()
                time.sleep(5)
        if mktopen.isMarketOpen():
            if widget.currentWidget() == portfolio_dialog:
                update_portfolio_table()
                update_watchlist_tickers()
                update_portfolio_nav()
                update_portfolio_piechart()
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

    for idx, amount in enumerate(portfolio_amts):
        if portfolio_asset_types[idx].text != 'Liquidity':
            asset_price = float(
                portfolio_dialog.positions_view_groupbox.positions_view.item(idx - 1, 2).text()[1:]
            )

        match portfolio_asset_types[idx].text:
            case "ETF":
                etf_amount += int(amount.text) * asset_price
            case "Liquidity":
                cash_amount += float(amount.text)
            case "Stock":
                stock_amount += int(amount.text) * asset_price
            case "Futures":
                futures_amount += int(amount.text) * asset_price
            case "Option":
                option_amount += int(amount.text) * asset_price

    # loads values into pie chart and displays them
    asset_class_chart.slices()[0].setValue(
        round(etf_amount / portfolio_nav * 100, 2))
    if etf_amount != 0:
        asset_class_chart.slices()[0].setLabel(
            f"ETFs: {round(etf_amount / portfolio_nav * 100, 2)}%"
        )
        asset_class_chart.slices()[0].setLabelVisible(True)

    asset_class_chart.slices()[1].setValue(
        round(stock_amount / portfolio_nav * 100, 2)
    )
    if stock_amount != 0:
        asset_class_chart.slices()[1].setLabel(
            f"Stocks: {round(stock_amount / portfolio_nav * 100, 2)}%"
        )
        asset_class_chart.slices()[1].setLabelVisible(True)

    asset_class_chart.slices()[2].setValue(option_amount / portfolio_nav * 100)
    if option_amount != 0:
        asset_class_chart.slices()[2].setLabel(
            f"Options: {round(option_amount / portfolio_nav * 100, 2)}%"
        )
        asset_class_chart.slices()[2].setLabelVisible(True)

    asset_class_chart.slices()[3].setValue(
        futures_amount / portfolio_nav * 100)
    if futures_amount != 0:
        asset_class_chart.slices()[3].setLabel(
            f"Futures: {round(futures_amount / portfolio_nav * 100, 2)}%"
        )
        asset_class_chart.slices()[3].setLabelVisible(True)

    asset_class_chart.slices()[4].setValue(cash_amount / portfolio_nav * 100)
    if cash_amount != 0:
        asset_class_chart.slices()[4].setLabel(
            f"Cash: {round(cash_amount / portfolio_nav * 100, 2)}%"
        )
        asset_class_chart.slices()[4].setLabelVisible(True)


def update_wallet_table():
    """
    Updates the positions table on the crypto wallet dialog.
    """
    wallet_zip = zip(wallet_tickers[1:], wallet_costbases, wallet_amts[1:])
    for idx, (ticker, basis, amt) in enumerate(wallet_zip):

        # get the current price and the price it last closed at
        ticker_data = yf.download(tickers=ticker.text, period='5d')

        # edge case where yf.download returns a dataframe of size 4
        try:
            ticker_current = ticker_data.iloc[4][3]
            ticker_last_close = ticker_data.iloc[3][3]
        except IndexError:
            ticker_current = ticker_data.iloc[3][3]
            ticker_last_close = ticker_data.iloc[2][3]

        # calculate the return since the position was opened in dollar and percent terms
        total_return = (ticker_current - float(basis.text)) * float(amt.text)
        percent_change = round(total_return / (float(basis.text) * float(amt.text)) * 100, 2)

        # update the table with the new information

        # first cell in the row is the coin symbol
        wallet_dialog.positions_view_groupbox.positions_view.setItem(
            idx, 0, QTableWidgetItem(ticker.text.upper()))

        # second cell is the coin's performance icon
        wallet_dialog.positions_view_groupbox.positions_view.setItem(
            idx, 1, updateTickerIcon(ticker_data))

        # third cell is the coin's current price
        wallet_dialog.positions_view_groupbox.positions_view.setItem(
            idx, 2, QTableWidgetItem(f'${ticker_current:0,.2f}'))

        # fourth cell is the change in the coin's price from it's last close,
        # in dollar and percent terms
        last_close_change = ticker_current - ticker_last_close
        wallet_dialog.positions_view_groupbox.positions_view.setItem(idx, 3, QTableWidgetItem(
            f'${last_close_change:0,.2f} ({round(last_close_change / ticker_last_close * 100, 2)}%)'
        ))


        # fifth cell is the user's costbasis for the token
        wallet_dialog.positions_view_groupbox.positions_view.setItem(
            idx, 4, QTableWidgetItem(f'${float(basis.text):0,.2f}')
        )


        # sixth cell is the amount of the coin the user has (or is short)
        wallet_dialog.positions_view_groupbox.positions_view.setItem(
            idx, 5, QTableWidgetItem(amt.text)
        )

        # seventh cell is the NLV the user has in the coin
        wallet_dialog.positions_view_groupbox.positions_view.setItem(
            idx, 6, QTableWidgetItem(f'${(ticker_current * float(amt.text)):0,.2f}')
        )

        # eighth cell is the user's net P/L on the position from when it was opened
        wallet_dialog.positions_view_groupbox.positions_view.setItem(idx, 7, QTableWidgetItem(
            f'${total_return:0,.2f} ({percent_change}%)')
        )


def update_portfolio_table():
    """
    Updates the table with all the user's positions in the portfolio dialog
    """
    # for each asset in the portfolio
    port_zip = zip(portfolio_tickers[1:], purchase_prices, portfolio_amts[1:])
    for idx, (ticker, basis, amt) in enumerate(port_zip):

        # get the current price and the price it last closed at
        ticker_data = yf.download(tickers=ticker.text, period='5d')
        ticker_current = ticker_data.iloc[4][3]
        ticker_last_close = ticker_data.iloc[3][3]
        # calculate the return since the position was opened in dollar and percent terms
        total_return = (
            ticker_current - float(basis.text)) * int(amt.text)
        percent_change = round(
            total_return / (float(basis.text) * float(amt.text)) * 100, 2)
        # update the table with the new information
        portfolio_dialog.positions_view_groupbox.positions_view.setItem(
            idx, 0, QTableWidgetItem(ticker.text.upper())
        )

        portfolio_dialog.positions_view_groupbox.positions_view.setItem(
            idx, 1, updateTickerIcon(ticker_data)
        )

        portfolio_dialog.positions_view_groupbox.positions_view.setItem(
            idx, 2, QTableWidgetItem(f'${ticker_current:0,.2f}')
        )

        last_close_change = ticker_current - ticker_last_close
        portfolio_dialog.positions_view_groupbox.positions_view.setItem(idx, 3, QTableWidgetItem(
            f'{last_close_change:0,.2f} ({round(last_close_change / ticker_last_close * 100, 2)}%)')
        )

        portfolio_dialog.positions_view_groupbox.positions_view.setItem(idx, 4, QTableWidgetItem(
            f'${float(basis.text):0,.2f}')
        )

        portfolio_dialog.positions_view_groupbox.positions_view.setItem(
            idx, 5, QTableWidgetItem(amt.text)
        )

        portfolio_dialog.positions_view_groupbox.positions_view.setItem(
            idx, 6, QTableWidgetItem(f'${(ticker_current * int(amt.text)):0,.2f}')
        )

        portfolio_dialog.positions_view_groupbox.positions_view.setItem(
            idx, 7, QTableWidgetItem(f'${total_return:0,.2f} ({percent_change}%)')
        )



def update_watchlist_tickers():
    """
    Updates the table with all the tickers in the user's watchlist in the portfolio dialog
    """

    # for each ticker in the watchlist
    for idx, item in enumerate(watchlist_tickers):

        ticker = yf.download(tickers=item.text, period='5d')
        ticker_current = ticker.iloc[4][3]
        ticker_last_close = ticker.iloc[3][3]

        portfolio_dialog.watchlist_groupbox.watchlist_view.setItem(
            idx, 0, QTableWidgetItem(item.text.upper()))
        portfolio_dialog.watchlist_groupbox.watchlist_view.setItem(
            idx, 1, updateTickerIcon(ticker))
        portfolio_dialog.watchlist_groupbox.watchlist_view.setItem(
            idx, 2, QTableWidgetItem('${:0,.2f}'.format(ticker_current)))

        portfolio_dialog.watchlist_groupbox.watchlist_view.setItem(idx, 3, QTableWidgetItem('${:0,.2f}'.format(
            ticker_current - ticker_last_close) + " (" + str(round(((ticker_current - ticker_last_close) / ticker_last_close * 100), 2)) + "%)"))


def daterange_radiobutton_clicked():
    """
    Should run only when the player clicks the "Chart by Date Range" radiobutton on the "Chart Stocks"
    dialog. Disables the combobox that lets the user select a period to chart over and enables the
    calendars so that the user can pick a start and end date for the chart.
    """
    chart_configurations.settings_groupbox.start_date.setEnabled(True)
    chart_configurations.settings_groupbox.end_date.setEnabled(True)
    chart_configurations.settings_groupbox.data_period_combobox.setEnabled(
        False)


def period_radiobutton_clicked():
    """
    Should run only when the player clicks the "Chart by Period" radiobutton on the
    "Chart Stocks" dialog. Disables the calendars that let the user select a start
    and end date for the chart and enables the period
    combobox so that the user can pick a start and end date for the chart.
    """
    chart_configurations.settings_groupbox.start_date.setEnabled(False)
    chart_configurations.settings_groupbox.end_date.setEnabled(False)
    chart_configurations.settings_groupbox.data_period_combobox.setEnabled(
        True)


def searchTextChanged(txt: str):
    """
    Executed when text is typed into the search bar on the "Chart Stocks" tab.
    The function takes the entered text and appends it to the search bar.
    """
    chart_configurations.search_bar_groupbox.searchBar.setText(txt.upper())


def searchButtonClicked():
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
    ticker = ''
    i = 0
    while chart_configurations.search_bar_groupbox.searchBar.text()[i] != ' ':
        ticker += chart_configurations.search_bar_groupbox.searchBar.text()[i]
        i += 1

    # get the interval the user selected
    interval = chart_configurations.settings_groupbox.data_timeframe_combobox.currentText()

    # get all chart settings the user selected on the chart menu
    include_prepost = False
    if (chart_configurations.settings_groupbox.prepost_checkbox.isChecked()):
        include_prepost = True

    adjust_ohlc = False
    if (chart_configurations.settings_groupbox.adjust_ohlc_checkbox.isChecked()):
        adjust_ohlc = True

    split_dividend = False
    if (chart_configurations.settings_groupbox.split_dividend_checkbox.isChecked()):
        split_dividend = True

    include_volume = False
    if (chart_configurations.settings_groupbox.volume_checkbox.isChecked()):
        include_volume = True

    non_trading = False
    if (chart_configurations.settings_groupbox.nontrading_checkbox.isChecked()):
        non_trading = True

    start_date = None
    end_date = None

    up_color = getXMLData('assets/settings.xml', 'upcolor')
    down_color = getXMLData('assets/settings.xml', 'downcolor')
    base_style = getXMLData('assets/settings.xml', 'basestyle')

    # creates a chart style based on the user's settings
    mc = mpf.make_marketcolors(up=up_color[0].text.lower(
    ), down=down_color[0].text.lower(), inherit=True)
    s = mpf.make_mpf_style(base_mpf_style=base_style[0].text, marketcolors=mc)

   # shows the requested ticker's chart
    if (chart_configurations.settings_groupbox.daterange_radiobutton.isChecked()):

        def thread_worker(title, start_date, end_date, interval):
            os.system(
                f'python3 {CURRENT_DIR}dependencies\stockchart.py {title} {interval} "{selected_ta}" {start_date} {end_date} ')

        start_date = chart_configurations.settings_groupbox.start_date.selectedDate(
        ).toString("yyyy-MM-dd")
        end_date = chart_configurations.settings_groupbox.end_date.selectedDate().toString("yyyy-MM-dd")

        t1 = Thread(daemon=True, target=thread_worker, args=(
            ticker, start_date, end_date, interval)).start()
    else:
        # only get period if user chose to chart by period

        def thread_worker(title, period, interval):
            os.system(
                f'python3 {CURRENT_DIR}dependencies\stockchart.py {title} {interval} "{selected_ta}" {period}')

        period = chart_configurations.settings_groupbox.data_period_combobox.currentText()

        t1 = Thread(daemon=True, target=thread_worker,
                    args=(ticker, period, interval)).start()


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
    close_change = (ticker_current - ticker_last_close) / \
        ticker_last_close * 100

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
                    w.setIcon(
                        QIcon(CURRENT_DIR + 'icons/greenarrowgreenbox.png'))
                case "FLAT":
                    w.setIcon(QIcon(CURRENT_DIR + 'icons/greenarrowflatbox.png'))
                case "DOWN":
                    w.setIcon(QIcon(CURRENT_DIR + 'icons/greenarrowredbox.png'))

        case "FLAT":
            match close_pos:
                case "UP":
                    w.setIcon(QIcon(CURRENT_DIR + 'icons/flatarrowgreenbox.png'))
                case "FLAT":
                    w.setIcon(QIcon(CURRENT_DIR + 'icons/flatarrowflatbox.png'))
                case "DOWN":
                    w.setIcon(QIcon(CURRENT_DIR + 'icons/flatarrowredbox.png'))

        case "DOWN":
            match close_pos:
                case "UP":
                    w.setIcon(QIcon(CURRENT_DIR + 'icons/redarrowgreenbox.png'))
                case "FLAT":
                    w.setIcon(QIcon(CURRENT_DIR + 'icons/redarrowflatbox.png'))
                case "DOWN":
                    w.setIcon(QIcon(CURRENT_DIR + 'icons/redarrowredbox.png'))

    # returns a tablewidgetitem containing the new icon
    return w


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
        # slice returns only the dollar value without the '$'
        price = float(portfolio_dialog.positions_view_groupbox.positions_view.item(
            idx, 2).text()[1:])

        if int(amt.text) > 0:
            # if it's long, add its value to the new value and to the assets tally
            newVal += float(price) * int(amt.text)
            assets += float(price) * float(amt.text)
        elif int(amt.text) < 0:
            # if it's short, subtract its value from the new value and add to the liabilities tally
            newVal -= float(price) * int(amt.text)
            liabilites += float(price) * float(amt.text)

    buying_power = get_portfolio_bp()
    portfolio_dialog.currentNAV.liq.setText(
        '${:0,.2f}'.format(float(str(newVal))))
    portfolio_dialog.currentNAV.buyingPower.setText(
        '${:0,.2f}'.format(buying_power))
    portfolio_dialog.currentNAV.assets.setText('${:0,.2f}'.format(assets))
    portfolio_dialog.currentNAV.liabilities.setText(
        '${:0,.2f}'.format(liabilities))
    portfolio_dialog.currentNAV.returnSinceInception.setText(
        '{:0.2f}'.format((newVal / 10000 - 1) * 100) + "%")


def update_wallet_nav():
    """Updates the user's NAV tab. Calculated as cash + (.5 * value of all long positions) -
    (1.5 * value of all short positions)."""

    # sets buying power to user's cash
    newVal = float(wallet_amts[0].text)
    liabilities = 0
    assets = 0
    for idx, amt in enumerate(wallet_amts[1:]):
        price = float(wallet_dialog.positions_view_groupbox.positions_view.item(
            idx - 1, 2).text()[1:])
        if float(amt.text) > 0:
            newVal += float(price) * float(amt.text)
            assets += float(price) * float(amt.text)
        elif float(amt.text) < 0:
            newVal -= float(price) * float(amt.text)
            liabilites += float(price) * float(amt.text)

    buying_power = get_wallet_bp()
    wallet_dialog.currentNAV.liq.setText(
        '${:0,.2f}'.format(float(str(newVal))))
    wallet_dialog.currentNAV.buyingPower.setText(
        '${:0,.2f}'.format(buying_power))
    wallet_dialog.currentNAV.assets.setText('${:0,.2f}'.format(assets))
    wallet_dialog.currentNAV.liabilities.setText(
        '${:0,.2f}'.format(liabilities))
    wallet_dialog.currentNAV.returnSinceInception.setText(
        '{:0.2f}'.format((newVal / 10000 - 1) * 100) + "%")


def get_portfolio_bp() -> float:
    buying_power = portfolio_cash
    total_long = 0
    total_short = 0

    for i in range(1, len(portfolio_amts)):
        price = float(portfolio_dialog.positions_view_groupbox.positions_view.item(
            i - 1, 2).text()[1:])
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
    return BeautifulSoup(open(currentdir + '\\' + file, 'r').read(), "xml").find_all(keyword)


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

    yq_ticker = yq.Ticker(ticker)

    if (yq_ticker.quote_type[ticker]['quoteType'] == 'ETF'):
        stockinfo_dialog.setTabEnabled(1, False)
        stockinfo_dialog.setTabEnabled(2, False)
        stockinfo_dialog.setTabEnabled(3, False)
        setup_etf_info(yq_ticker, ticker)
    elif (yq_ticker.quote_type[ticker]['quoteType'] == 'EQUITY'):
        stockinfo_dialog.setTabEnabled(1, True)
        stockinfo_dialog.setTabEnabled(2, True)
        stockinfo_dialog.setTabEnabled(3, True)
        setup_stock_info(yq_ticker, ticker)


def get_etf_weights(ticker_info: pd.DataFrame) -> list:
    weights_list = []

    weights_list.append(["Real Estate", ticker_info.iloc[0]])
    weights_list.append(["Consumer Cyclicals", ticker_info.iloc[1]])
    weights_list.append(["Basic Materials", ticker_info.iloc[2]])
    weights_list.append(["Consumer Defensives", ticker_info.iloc[3]])
    weights_list.append(["Technology", ticker_info.iloc[4]])
    weights_list.append(["Communication Services", ticker_info.iloc[5]])
    weights_list.append(["Financial Services", ticker_info.iloc[6]])
    weights_list.append(["Utilities", ticker_info.iloc[7]])
    weights_list.append(["Industrials", ticker_info.iloc[8]])
    weights_list.append(["Energy", ticker_info.iloc[9]])
    weights_list.append(["Healthcare", ticker_info.iloc[10]])
    return weights_list


def clear_layout(layout: QVBoxLayout):
    for i in reversed(range(layout.count())):
        layout.itemAt(i).widget().setParent(None)


def setup_etf_info(ticker: yq.Ticker, name: str):
    t1 = time.perf_counter()
    ticker_data = ticker.all_modules

    price_data = ticker_data[name]['price']
    fund_profile = ticker_data[name]['fundProfile']
    quote_type = ticker_data[name]['quoteType']
    summary_detail = ticker_data[name]['summaryDetail']
    asset_profile = ticker_data[name]['assetProfile']
    key_stats = ticker_data[name]['defaultKeyStatistics']
    etf_weights = get_etf_weights(ticker.fund_sector_weightings)
    ticker_news = fn.get_finviz_news(name)

    stockinfo_dialog_main.about_groupbox.setVisible(True)
    stockinfo_dialog_main.asset_info_groupbox.setVisible(True)
    stockinfo_dialog_main.news_groupbox.setVisible(True)


    full_name_label = QLabel(f"Full Name: {price_data['longName']}")

    category_label = QLabel(f"Category: {fund_profile['categoryName']}")

    exchange_label = QLabel(f"Exchange: {quote_type['exchange']}")

    total_assets_label = QLabel(f"Total Assets: {summary_detail['totalAssets']}")

    description_label = QLabel("Description: " + asset_profile['longBusinessSummary'])
    description_label.setWordWrap(True)

    inception_label = QLabel(f"Date of Inception: {key_stats['fundInceptionDate']}")

    weights_piechart = QPieSeries()

    for index, weight in enumerate(etf_weights):
        weights_piechart.append(weight[0], index + 1)
        weights_piechart.slices()[index].setValue(weight[1] * 100)
        weights_piechart.slices()[index].setLabelVisible(True)

    weights_chart = QChart()
    weights_chart.addSeries(weights_piechart)
    weights_chart.setTitle(f"{name} Holdings by Sector")
    weights_chart.setVisible(True)

    weights_chartview = QChartView(weights_chart)

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

    threeyear_return_label = QLabel(f"Three-Year CAGR: {ticker.fund_performance[name]['trailingReturns']['threeYear'] * 100}% per annum")
    fiveyear_return_label = QLabel(f"Five-Year CAGR: {ticker.fund_performance[name]['trailingReturns']['fiveYear'] * 100}% per annum")

    try:
        dividend_label = QLabel(f"Trailing Annual Dividend Yield: {summary_detail['trailingAnnualDividendYield'] * 100}% per annum")
    except KeyError:  # ETF does not pay a dividend
        dividend_label = QLabel("Trailing Annual Dividend Yield: 0% per annum")

    try:
        dividend_rate_label = QLabel(f"Trailing Annual Dividend Rate: ${summary_detail['trailingAnnualDividendRate']}")
    except KeyError:
        dividend_rate_label = QLabel("Trailing Annual Dividend Rate: $0.00")

    beta_3y_label = QLabel(f"3-Year Beta (Relative to SPY): {key_stats['beta3Year']}")


    clear_layout(about_scrollarea_widget.layout())
    clear_layout(assetinfo_scrollarea_widget.layout())
    clear_layout(stockinfo_dialog_main.news_groupbox.layout())

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
        stockinfo_dialog_main.news_groupbox.layout().addWidget(news_label)

    about_scrollarea_widget.layout().addWidget(full_name_label)
    about_scrollarea_widget.layout().addWidget(category_label)
    about_scrollarea_widget.layout().addWidget(exchange_label)
    about_scrollarea_widget.layout().addWidget(total_assets_label)
    about_scrollarea_widget.layout().addWidget(inception_label)
    about_scrollarea_widget.layout().addWidget(description_label)
    about_scrollarea_widget.layout().addWidget(weights_chartview)

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
    assetinfo_scrollarea_widget.layout().addWidget(beta_3y_label)
    t2 = time.perf_counter()
    print(f"{t2 - t1} seconds")


def setup_stock_info(ticker: yq.Ticker, name: str):
    t1 = time.perf_counter()
    ticker_data = ticker.all_modules
    ticker_news = fn.get_finviz_news(name)

    price_data = ticker_data[name]['price']
    asset_profile = ticker_data[name]['assetProfile']
    summary_detail = ticker_data[name]['summaryDetail']

    stockinfo_dialog_main.about_groupbox.setVisible(True)
    stockinfo_dialog_main.asset_info_groupbox.setVisible(True)
    stockinfo_dialog_main.news_groupbox.setVisible(True)
    stockinfo_dialog_recs.analyst_rec_groupbox.setVisible(True)
    stockinfo_dialog_recs.iandi_groupbox.setVisible(True)
    stockinfo_dialog_recs.mutfund_groupbox.setVisible(True)

    full_name_label = QLabel(f"Full Name: {price_data['longName']}")

    sector_label = QLabel(
        f"Sector: {asset_profile['sector']}: {asset_profile['industry']}")

    country_label = QLabel(f"Country: {asset_profile['country']}")

    description_label = QLabel(
        "Description: " + asset_profile['longBusinessSummary'])

    description_label.setWordWrap(True)

    location_label = QLabel(
        f"Location: {asset_profile['city']}, {asset_profile['state']}")

    website_label = QLabel(
        f"Website: <a href=\"{asset_profile['website']}\"> {asset_profile['website']} </a>")

    current_price_label = QLabel(
        f"Current Price: {price_data['regularMarketPrice']}")
    open_price_label = QLabel(f"\tOpen: {price_data['regularMarketOpen']}")
    high_price_label = QLabel(f"\tHigh: {price_data['regularMarketDayHigh']}")
    low_price_label = QLabel(f"\tLow: {price_data['regularMarketDayLow']}")
    close_price_label = QLabel(
        f"\tLast Close: {price_data['regularMarketPreviousClose']}")

    bid_label = QLabel(f"Bid: {summary_detail['bid']} ({summary_detail['bidSize']})")
    ask_label = QLabel(f"Ask: {summary_detail['ask']} ({summary_detail['askSize']})")

    volume_label = QLabel(f"Volume: {price_data['regularMarketVolume']}")
    avg_volume_label = QLabel(
        f"Average Volume (10d): {summary_detail['averageVolume10days']}")
    long_avg_volume_label = QLabel(
        f"Average Volume (3M): {summary_detail['averageVolume']} ")

    year_high_label = QLabel(f"52 Week High: {summary_detail['fiftyTwoWeekHigh']}")
    year_low_label = QLabel(f"52 Week Low: {summary_detail['fiftyTwoWeekLow']}")

    averages_label = QLabel("Price Averages: ")
    fifty_avg_label = QLabel(
        f"\t50d MA: {summary_detail['fiftyDayAverage']}")
    twohundred_avg_label = QLabel(
        f"\t200d MA: {summary_detail['twoHundredDayAverage']}")


    clear_layout(about_scrollarea_widget.layout())
    clear_layout(assetinfo_scrollarea_widget.layout())
    clear_layout(stockinfo_dialog_main.news_groupbox.layout())
    clear_layout(stockinfo_dialog_recs.analyst_rec_groupbox.layout())
    clear_layout(stockinfo_dialog_recs.iandi_groupbox.layout())
    clear_layout(stockinfo_dialog_recs.mutfund_groupbox.layout())

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
        stockinfo_dialog_main.news_groupbox.layout().addWidget(news_label)



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
    t2 = time.perf_counter()
    print(f"{t2 - t1} seconds")


def stockinfo_dialog_changed(tab_id: int):
    t = ''
    i = 0
    while stockinfo_dialog_main.search_bar_groupbox.searchBar.text()[i] != ' ':
        t += stockinfo_dialog_main.search_bar_groupbox.searchBar.text()[i]
        i += 1

    ticker = yq.Ticker(t)

    ticker_data = ticker.all_modules
    global tab2_isloaded
    global tab3_isloaded
    global tab4_isloaded

    if (tab_id == 1 and not tab2_isloaded):
        t1 = time.perf_counter()
        ticker_recommendations = ticker_data[t]['upgradeDowngradeHistory']['history'][:9]
        ticker_instholders = ticker_data[t]['institutionOwnership']['ownershipList'][:9]
        ticker_mutfundholders = ticker_data[t]['fundOwnership']['ownershipList'][:9]

        for recommendation in ticker_recommendations:
            l = QLabel(f"{recommendation['firm']}: {recommendation['toGrade']} <br> {recommendation['epochGradeDate']}")
            stockinfo_dialog_recs.analyst_rec_groupbox.layout().addWidget(l)

        for instholder in ticker_instholders:
            l = QLabel(
                f"{instholder['organization']}: {instholder['position']} shares ({instholder['pctHeld'] * 100}%) <br> {instholder['reportDate']}")
            stockinfo_dialog_recs.iandi_groupbox.layout().addWidget(l)

        for mutfundholder in ticker_mutfundholders:
            l = QLabel(
                f"{mutfundholder['organization']}: {mutfundholder['position']} shares ({mutfundholder['pctHeld'] * 100}%) <br> {mutfundholder['reportDate']}")
            stockinfo_dialog_recs.mutfund_groupbox.layout().addWidget(l)

            tab2_isloaded = True

        t2 = time.perf_counter()
        print(f"{t2 - t1} seconds")

    elif (tab_id == 2 and not tab3_isloaded):
        t1 = time.perf_counter()
        ticker_pts = ticker_data[t]['financialData']
        ticker_hist = ticker.history(period="2y", interval="1wk")
        ticker_qtr_earnings = ticker_data[t]['earningsHistory']['history']
        ticker_qtr_rev = ticker_data[t]['earnings']['financialsChart']['quarterly']
        ticker_yr_earnings_rev = ticker_data[t]['earnings']['financialsChart']['yearly']

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
            series.append(float(QDateTime().fromString(str(ticker_hist.index[i][1])[
                          0:19], date_format).toMSecsSinceEpoch()), ticker_hist.iloc[i][3])
        series.append(float(prediction_date), ticker_pts['currentPrice'])
        series.setName("Current Price")
        series.setColor(QColor("blue"))

        series2.setName("Worst Case")
        series2.setColor(QColor("red"))

        series3.setName("Mean Target Price")
        series3.setColor(QColor("black"))

        series4.setName("Best Case")
        series4.setColor(QColor("green"))

        series2.append(float(current_dt),
                       ticker_hist.iloc[ticker_hist.count().iloc[0] - 1][3])
        series2.append(float(prediction_date), ticker_pts['targetLowPrice'])

        series3.append(float(current_dt),
                       ticker_hist.iloc[ticker_hist.count().iloc[0] - 1][3])
        series3.append(float(prediction_date), ticker_pts['targetMeanPrice'])

        series4.append(float(current_dt),
                       ticker_hist.iloc[ticker_hist.count().iloc[0] - 1][3])
        series4.append(float(prediction_date), ticker_pts['targetHighPrice'])

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
        pt_label_container.layout().addWidget(
            QLabel(f"Current Price: {ticker_pts['currentPrice']}"))
        pt_label_container.layout().addWidget(
            QLabel(f"Target Low Price: {ticker_pts['targetLowPrice']}"))
        pt_label_container.layout().addWidget(
            QLabel(f"Target Mean Price: {ticker_pts['targetMeanPrice']}"))
        pt_label_container.layout().addWidget(
            QLabel(f"Target High Price: {ticker_pts['targetHighPrice']}"))
        pt_label_container.layout().addWidget(
            QLabel(f"Number of Analyst Opinions: {ticker_pts['numberOfAnalystOpinions']}"))


        qtr_earnings_chart.removeAllSeries()
        series = QBarSeries()

        actual_qtr_earnings_set = QBarSet("Actual")
        estimate_qtr_earnings_set = QBarSet("Estimate")
        earnings_trend_max = 0
        earnings_trend_min = 0

        qtr_earnings_table.setRowCount(5)
        qtr_earnings_table.setColumnCount(3)
        qtr_earnings_table.setHorizontalHeaderItem(
            0, QTableWidgetItem("Actual"))
        qtr_earnings_table.setHorizontalHeaderItem(
            1, QTableWidgetItem("Expected"))
        qtr_earnings_table.setHorizontalHeaderItem(
            2, QTableWidgetItem("Surprise"))
        for i in range(qtr_earnings_table.columnCount()):

            qtr_earnings_table.horizontalHeaderItem(
                i).setFont(QFont('arial', 10))

        for i in range(qtr_earnings_table.rowCount()):
            qtr_earnings_table.setVerticalHeaderItem(
                i, QTableWidgetItem(str(i + 1)))
            qtr_earnings_table.verticalHeaderItem(
                i).setFont(QFont('arial', 10))

        for idx, er in enumerate(ticker_qtr_earnings):
            reported = er['epsActual']
            actual_qtr_earnings_set.append(reported)
            if (reported > earnings_trend_max):
                earnings_trend_max = reported
            if (reported < earnings_trend_min):
                earnings_trend_min = reported

            estimate = er['epsEstimate']
            if (estimate > earnings_trend_max):
                earnings_trend_max = estimate
            if (estimate < earnings_trend_min):
                earnings_trend_min = estimate
            estimate_qtr_earnings_set.append(estimate)

            qtr_earnings_table.setItem(idx, 0, QTableWidgetItem(str(reported)))
            qtr_earnings_table.setItem(idx, 1, QTableWidgetItem(str(estimate)))
            qtr_earnings_table.setItem(
                idx, 2, QTableWidgetItem(str(reported - estimate)))

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
            if (revenue > qtr_revtrend_max):
                qtr_revtrend_max = revenue
            if (revenue < qtr_revtrend_min):
                qtr_revtrend_min = revenue
            qtr_revtrend_label_container.layout().addWidget(
                QLabel(f"{rev['date']}: {revenue}"))

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

        for er in ticker_yr_earnings_rev:
            earnings = float(er['earnings'])
            if (earnings > yr_eps_max):
                yr_eps_max = earnings
            if (earnings < yr_eps_min):
                yr_eps_min = earnings
            yr_er_barset.append(earnings)
            yr_earnings_label_container.layout().addWidget(
                QLabel(f"{er['date']}: {earnings}"))

        yr_er_barseries.append(yr_er_barset)
        yr_earnings_chart.addSeries(yr_er_barseries)
        yr_earnings_chart.createDefaultAxes()
        yr_earnings_chart.axes(Qt.Orientation.Vertical)[0].setRange(
            yr_eps_min * 1.1, yr_eps_max * 1.1)

        yr_revtrend_chart.removeAllSeries()
        clear_layout(yr_revtrend_label_container.layout())
        s = QBarSeries()
        set = QBarSet("Revenue")

        yr_revtrend_max = 0
        yr_revtrend_min = 0
        for er in ticker_yr_earnings_rev:
            rev = float(er['revenue'])
            set.append(rev)
            yr_revtrend_max = rev if rev > yr_revtrend_max else yr_revtrend_max
            yr_revtrend_min = rev if rev < yr_revtrend_min else yr_revtrend_min
            yr_revtrend_label_container.layout().addWidget(
                QLabel(f"{er['date']}: {rev}"))

        set.setPen(QColor("green"))

        s.append(set)

        yr_revtrend_chart.addSeries(s)
        yr_revtrend_chart.createDefaultAxes()
        yr_revtrend_chart.axes(Qt.Orientation.Vertical)[0].setRange(
            yr_revtrend_min * 1.1, yr_revtrend_max * 1.1)

        tab3_isloaded = True

        t2 = time.perf_counter()
        print(f"{t2 - t1} seconds")

    elif (tab_id == 3 and not tab4_isloaded):
        t1 = time.perf_counter()
        ticker_financials = ticker.all_financial_data()
        financials_table.setRowCount(ticker_financials.columns.size)
        financials_table.setColumnCount(5)
        for i in range(4):
            tw_item = QTableWidgetItem(str(ticker_financials.iloc[i][0])[:10])
            financials_table.setHorizontalHeaderItem(i, tw_item)
            financials_table.horizontalHeaderItem(i).setFont(QFont('arial', 10))

        for i in range(4):
            for j in range(3, ticker_financials.iloc[0].size):
                current_data = float(ticker_financials.iloc[i][j])
                if current_data > 1000:
                    formatted_data = nf.simplify(current_data, True)
                    financials_table.setItem(
                        j, i, QTableWidgetItem(formatted_data))
                elif current_data < -1000:
                    formatted_data = nf.simplify(abs(current_data), True)
                    financials_table.setItem(
                        j, i, QTableWidgetItem(f"-{formatted_data}"))
                else:
                    financials_table.setItem(j, i, QTableWidgetItem(
                        str(current_data)))

        checkboxes = QButtonGroup()

        for i in range(ticker_financials.iloc[0].size):

            checkbox = QCheckBox()
            checkboxes.addButton(checkbox)
            item = QTableWidgetItem(ticker_financials.columns[i])
            financials_table.setVerticalHeaderItem(i, item)
            financials_table.verticalHeaderItem(i).setFont(QFont('arial', 10))
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

                val = financials_table.item(i, j).text()
                last_char = val[-1]
                match last_char:
                    case 'k':
                        set.append(float(val[:-1]) * 10**3)
                    case 'M':
                        set.append(float(val[:-1]) * 10**6)
                    case 'B':
                        set.append(float(val[:-1]) * 10**9)
                    case 'T':
                        set.append(float(val[:-1]) * 10**12)
                    case _:
                        set.append(float(val))
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
    dcf_dialog.inputs_groupbox.company_label.setText(
        f"Company: {input_info['company_name']}")
    dcf_dialog.inputs_groupbox.mkt_price.setText(
        '${:0,.2f}'.format(input_info['mp']))
    dcf_dialog.inputs_groupbox.eps.setText(str(input_info['eps']))
    dcf_dialog.inputs_groupbox.growth.setText(
        str(input_info['ge']) + "% per annum")
    dcf_dialog.inputs_groupbox.growth_slider.setValue(input_info['ge'] * 100)
    dcf_dialog.inputs_groupbox.discount_rate.setText(
        str(dcf_dialog.inputs_groupbox.discount_rate_slider.value() / 100.0) + "%")
    dcf_dialog.inputs_groupbox.perpetual_rate.setText(
        str(dcf_dialog.inputs_groupbox.perpetual_rate_slider.value() / 100.0) + "%")
    dcf_dialog.inputs_groupbox.last_fcf.setText(
        nf.simplify(input_info['fcf'], True))
    dcf_dialog.inputs_groupbox.shares.setText(
        nf.simplify(input_info['shares'], True))


def growth_slider_moved():
    dcf_dialog.inputs_groupbox.growth.setText(
        str(dcf_dialog.inputs_groupbox.growth_slider.value() / 100.0) + "%")


def term_slider_moved():
    dcf_dialog.inputs_groupbox.term.setText(
        str(dcf_dialog.inputs_groupbox.term_slider.value()) + " years")


def discount_slider_moved():
    dcf_dialog.inputs_groupbox.discount_rate.setText(
        str(dcf_dialog.inputs_groupbox.discount_rate_slider.value() / 100.0) + "%")


def perpetual_slider_moved():
    dcf_dialog.inputs_groupbox.perpetual_rate.setText(
        str(dcf_dialog.inputs_groupbox.perpetual_rate_slider.value() / 100.0) + "%")


def dcf_getanalysis_button_click():
    global current_ticker
    discount_rate = dcf_dialog.inputs_groupbox.discount_rate_slider.value() / 100.0
    perpetual_rate = dcf_dialog.inputs_groupbox.perpetual_rate_slider.value() / \
        100.0
    growth_estimate = dcf_dialog.inputs_groupbox.growth_slider.value() / 100.0
    term = dcf_dialog.inputs_groupbox.term_slider.value()
    eps = float(dcf_dialog.inputs_groupbox.eps.text())

    dcf_analysis = dcf.get_fairval(
        current_ticker, discount_rate, perpetual_rate, growth_estimate, term, eps)
    future_cashflows_chartview.setVisible(True)

    future_cashflows_chart.removeAllSeries()
    future_cashflows_lineseries = QLineSeries()
    future_cashflows_lineseries.setName("Forecasted Cash Flows")
    future_cashflows_pv_lineseries = QLineSeries()
    future_cashflows_pv_lineseries.setName(
        "Present Value of Forecasted Cash Flows")
    current_year = QDateTime().currentDateTime().date().year()

    for i in range(term):
        future_cashflows_lineseries.append(
            current_year + i, dcf_analysis['forecasted_cash_flows'][i])
        future_cashflows_pv_lineseries.append(
            current_year + i, dcf_analysis['cashflow_present_values'][i])

    future_cashflows_chart.addSeries(future_cashflows_lineseries)
    future_cashflows_chart.addSeries(future_cashflows_pv_lineseries)

    future_cashflows_chart.createDefaultAxes()
    future_cashflows_chart.axes(Qt.Orientation.Horizontal)[
        0].setTickCount(term)

    upside = round((dcf_analysis['fair_value'] /
                   dcf_analysis['mp'] - 1) * 100, 2)
    dcf_dialog.outputs_groupbox.basic_model_output.fair_value.setText(
        f"${round(dcf_analysis['fair_value'], 2)} ({upside}%)")

    upside = round(
        (dcf_analysis['graham_expected_value'] / dcf_analysis['mp'] - 1) * 100, 2)
    dcf_dialog.outputs_groupbox.graham_model_output.ev.setText(
        f"${round(dcf_analysis['graham_expected_value'], 2)} ({upside}%)")

    dcf_dialog.outputs_groupbox.graham_model_output.graham_growth_estimate.setText(
        f"{round(dcf_analysis['graham_growth_estimate'], 2)}% per annum")


def removeIndicator(indicator_fn):
    for ta in selected_ta:
        if ta[0] == indicator_fn:
            selected_ta.remove(ta)


def change_indicator_panel(indicator_fn, value, args):
    for ta in selected_ta:
        if ta[0] == indicator_fn:
            index = selected_ta.index(ta)
            tuple = (indicator_fn, int(value))
            tuple += (args, )
            selected_ta[index] = tuple


def get_indicator_index(indicator_fn) -> int:
    for ta in selected_ta:
        if ta[0] == indicator_fn:
            return selected_ta.index(ta)


def close_event(event):
    """Function that is called when the user exits the game. WIP"""
    print("closed")


app = QApplication(sys.argv)
widget = QTabWidget()
widget.setWindowTitle("Ray's Paper Trading Game")
splash = QSplashScreen(
    QPixmap(CURRENT_DIR + 'splashscreen-images/splash.png')
)
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

up_color = getXMLData(r'assets\settings.xml', 'upcolor')
down_color = getXMLData(r'assets\settings.xml', 'downcolor')
base_style = getXMLData(r'assets\settings.xml', 'basestyle')
portfolio_tickers = getXMLData(r'assets\portfolio.xml', 'name')
portfolio_asset_types = getXMLData(r'assets\portfolio.xml', 'type')
portfolio_amts = getXMLData(r'assets\portfolio.xml', 'amount')
purchase_prices = getXMLData(r'assets\portfolio.xml', 'costbasis')
wallet_tickers = getXMLData(r'assets\wallet.xml', 'name')
wallet_amts = getXMLData(r'assets\wallet.xml', 'amount')
wallet_costbases = getXMLData(r'assets\wallet.xml', 'costbasis')
watchlist_tickers = getXMLData(r'assets\watchlist.xml', 'name')

all_tickers_list = pd.read_csv(
    CURRENT_DIR + r"assets\stock_list.csv"
)['Symbol'].tolist()
all_names_list = pd.read_csv(
    CURRENT_DIR + r"assets\stock_list.csv"
)['Name'].tolist()

all_tickers_list[5023] = 'NAN'

all_tickers_list = [
                     f"{all_tickers_list[i]} - {all_names_list[i]}"
                     for i, val
                     in enumerate(all_tickers_list)
                    ]

# set user's NAV equal to cash first, then iterate through stocks,
# find their current price, and add their values to user's NAV
portfolio_nav = float(portfolio_amts[0].text)
portfolio_cash = float(portfolio_amts[0].text)
for port_ticker, port_amt in zip(portfolio_tickers[1:], portfolio_amts[1:]):
    price = yq.Ticker(port_ticker.text).history(period='5d').iloc[4][3]
    portfolio_nav += float(price) * int(port_amt.text)

wallet_nav = float(wallet_amts[0].text)
wallet_cash = float(wallet_amts[0].text)
for wallet_ticker, wallet_amt in zip(wallet_tickers[1:], wallet_amts[1:]):
    try:
        price = yf.download(
            tickers=wallet_ticker.text, period='5d'
        ).iloc[4][3]
    except IndexError:
        price = yf.download(
            tickers=wallet_ticker.text, period='5d'
        ).iloc[3][3]
    wallet_nav += float(price) * float(wallet_amt.text)

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
portfolio_dialog.positions_view_groupbox.setStyleSheet(
    'background-color: white;'
)

portfolio_dialog.positions_view_groupbox.positions_view = QTableWidget(
    portfolio_dialog.positions_view_groupbox)
portfolio_dialog.positions_view_groupbox.positions_view.setEditTriggers(
    QAbstractItemView.EditTrigger.NoEditTriggers)
portfolio_dialog.positions_view_groupbox.positions_view.setFont(
    QFont('arial', 10))
portfolio_dialog.positions_view_groupbox.positions_view.setRowCount(
    len(portfolio_amts) - 1)
portfolio_dialog.positions_view_groupbox.positions_view.setColumnCount(8)
portfolio_dialog.positions_view_groupbox.positions_view.setGeometry(
    10, 20, 850, 200)
portfolio_dialog.positions_view_groupbox.positions_view.setStyleSheet(
    'background-color: white;')
portfolio_dialog.positions_view_groupbox.positions_view.setHorizontalHeaderItem(
    0, QTableWidgetItem("Ticker"))
portfolio_dialog.positions_view_groupbox.positions_view.setHorizontalHeaderItem(
    1, QTableWidgetItem("Today's Performance"))
portfolio_dialog.positions_view_groupbox.positions_view.setHorizontalHeaderItem(
    2, QTableWidgetItem("Current Price"))
portfolio_dialog.positions_view_groupbox.positions_view.setHorizontalHeaderItem(
    3, QTableWidgetItem("Gain/Loss Per Share"))
portfolio_dialog.positions_view_groupbox.positions_view.setHorizontalHeaderItem(
    4, QTableWidgetItem("Purchase Price"))
portfolio_dialog.positions_view_groupbox.positions_view.setHorizontalHeaderItem(
    5, QTableWidgetItem("# of Shares"))
portfolio_dialog.positions_view_groupbox.positions_view.setHorizontalHeaderItem(
    6, QTableWidgetItem("Total Value"))
portfolio_dialog.positions_view_groupbox.positions_view.setHorizontalHeaderItem(
    7, QTableWidgetItem("Position Gain/Loss"))
for i in range(8):
    portfolio_dialog.positions_view_groupbox.positions_view.horizontalHeaderItem(
        i).setFont(QFont('arial', 10))
for i in range(portfolio_dialog.positions_view_groupbox.positions_view.rowCount()):
    portfolio_dialog.positions_view_groupbox.positions_view.setVerticalHeaderItem(
        0, QTableWidgetItem("1"))
    portfolio_dialog.positions_view_groupbox.positions_view.verticalHeaderItem(
        i).setFont(QFont('arial', 10))
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
portfolio_dialog.currentNAV.liq.setText(
    '${:0,.2f}'.format(float(str(portfolio_nav))))
portfolio_dialog.currentNAV.liq.setGeometry(10, 40, 160, 40)
portfolio_dialog.currentNAV.liq.setFont(QFont('genius', 20))
# cash value labels
portfolio_dialog.currentNAV.cashLabel = QLabel(portfolio_dialog.currentNAV)
portfolio_dialog.currentNAV.cashLabel.setText("Cash: ")
portfolio_dialog.currentNAV.cashLabel.setGeometry(10, 90, 80, 20)
portfolio_dialog.currentNAV.cash = QLabel(portfolio_dialog.currentNAV)
portfolio_dialog.currentNAV.cash.setText(f'${portfolio_cash:0,.2f}')
portfolio_dialog.currentNAV.cash.setGeometry(100, 90, 80, 20)
progressBar.setValue(70)
# buying power labels
portfolio_dialog.currentNAV.buyingPowerLabel = QLabel(
    portfolio_dialog.currentNAV)
portfolio_dialog.currentNAV.buyingPowerLabel.setText("Buying Power: ")
portfolio_dialog.currentNAV.buyingPowerLabel.setGeometry(10, 110, 80, 20)
portfolio_dialog.currentNAV.buyingPower = QLabel(
    portfolio_dialog.currentNAV)
portfolio_dialog.currentNAV.buyingPower.setText(f'${get_portfolio_bp():0,.2f}')
portfolio_dialog.currentNAV.buyingPower.setGeometry(100, 110, 80, 20)
# assets labels
portfolio_dialog.currentNAV.assetsLabel = QLabel(
    portfolio_dialog.currentNAV)
portfolio_dialog.currentNAV.assetsLabel.setText("Long Assets: ")
portfolio_dialog.currentNAV.assetsLabel.setGeometry(10, 130, 80, 20)
portfolio_dialog.currentNAV.assets = QLabel(portfolio_dialog.currentNAV)
total_long = 0
for i in range(1, len(portfolio_amts)):
    price = float(portfolio_dialog.positions_view_groupbox.positions_view.item(
        i - 1, 2).text()[1:])
    if int(portfolio_amts[i].text) > 0:
        total_long += float(price) * int(portfolio_amts[i].text)
portfolio_dialog.currentNAV.assets.setText('${:0,.2f}'.format(total_long))
portfolio_dialog.currentNAV.assets.setGeometry(100, 130, 80, 20)
# liabilities labels
portfolio_dialog.currentNAV.liabilitiesLabel = QLabel(
    portfolio_dialog.currentNAV)
portfolio_dialog.currentNAV.liabilitiesLabel.setText("Short Assets: ")
portfolio_dialog.currentNAV.liabilitiesLabel.setGeometry(10, 150, 80, 20)
portfolio_dialog.currentNAV.liabilities = QLabel(
    portfolio_dialog.currentNAV)
total_short = 0
for i in range(1, len(portfolio_amts)):
    price = float(portfolio_dialog.positions_view_groupbox.positions_view.item(
        i - 1, 2).text()[1:])
    if int(portfolio_amts[i].text) < 0:
        total_short -= float(price) * int(portfolio_amts[i].text)
portfolio_dialog.currentNAV.liabilities.setText(
    '${:0,.2f}'.format(total_short))
portfolio_dialog.currentNAV.liabilities.setGeometry(100, 150, 80, 20)
# return since inception labels
portfolio_dialog.currentNAV.returnSinceInceptionLabel = QLabel(
    portfolio_dialog.currentNAV)
portfolio_dialog.currentNAV.returnSinceInceptionLabel.setText(
    "Return Since Inception: ")
portfolio_dialog.currentNAV.returnSinceInceptionLabel.setGeometry(
    10, 170, 120, 20)
portfolio_dialog.currentNAV.returnSinceInception = QLabel(
    portfolio_dialog.currentNAV)
portfolio_dialog.currentNAV.returnSinceInception.setFont(
    QFont('genius', 20))
portfolio_dialog.currentNAV.returnSinceInception.setText(
    '{:0.2f}'.format((portfolio_nav / 10000 - 1) * 100) + "%")
portfolio_dialog.currentNAV.returnSinceInception.setGeometry(
    10, 190, 120, 30)
progressBar.setValue(80)
# watchlist table settings
portfolio_dialog.watchlist_groupbox = QGroupBox(portfolio_dialog)
portfolio_dialog.watchlist_groupbox.setTitle("Your Watchlist")
portfolio_dialog.watchlist_groupbox.setGeometry(270, 10, 500, 250)
portfolio_dialog.watchlist_groupbox.setStyleSheet(
    'background-color: white;')
portfolio_dialog.watchlist_groupbox.watchlist_view = QTableWidget(
    portfolio_dialog.watchlist_groupbox)
portfolio_dialog.watchlist_groupbox.watchlist_view.setEditTriggers(
    QAbstractItemView.EditTrigger.NoEditTriggers)
portfolio_dialog.watchlist_groupbox.watchlist_view.setRowCount(
    len(watchlist_tickers))
portfolio_dialog.watchlist_groupbox.watchlist_view.setColumnCount(4)
portfolio_dialog.watchlist_groupbox.watchlist_view.setHorizontalHeaderItem(
    0, QTableWidgetItem("Ticker"))
portfolio_dialog.watchlist_groupbox.watchlist_view.setHorizontalHeaderItem(
    1, QTableWidgetItem("Today's Performance"))
portfolio_dialog.watchlist_groupbox.watchlist_view.setHorizontalHeaderItem(
    2, QTableWidgetItem("Current Price"))
portfolio_dialog.watchlist_groupbox.watchlist_view.setHorizontalHeaderItem(
    3, QTableWidgetItem("Gain/Loss Per Share"))
for i in range(4):
    portfolio_dialog.watchlist_groupbox.watchlist_view.horizontalHeaderItem(
        i).setFont(QFont('arial', 10))
for i in range(portfolio_dialog.watchlist_groupbox.watchlist_view.rowCount()):
    portfolio_dialog.watchlist_groupbox.watchlist_view.setVerticalHeaderItem(
        i, QTableWidgetItem(str(i + 1)))
    portfolio_dialog.watchlist_groupbox.watchlist_view.verticalHeaderItem(
        i).setFont(QFont('arial', 10))
portfolio_dialog.watchlist_groupbox.watchlist_view.setFont(
    QFont('arial', 10))
portfolio_dialog.watchlist_groupbox.watchlist_view.setGeometry(
    10, 20, 500, 200)
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
chart_dialog = QTabWidget()
chart_dialog.setObjectName("Dialog")
chart_dialog.resize(1000, 600)
chart_dialog.setStyleSheet('background-color: deepskyblue;')
chart_configurations = QDialog()
chart_configurations.broad_market_groupbox = QGroupBox(
    chart_configurations)
chart_configurations.broad_market_groupbox.setTitle(
    "Broad Market Indicies"
)
chart_configurations.broad_market_groupbox.setStyleSheet(
    'background-color: white;'
)
chart_configurations.broad_market_groupbox.setGeometry(10, 10, 700, 50)
chart_configurations.broad_market_groupbox.spyButton = QPushButton(
    text="Chart SPY", parent=chart_configurations.broad_market_groupbox
)
chart_configurations.broad_market_groupbox.spyButton.setGeometry(
    QRect(10, 20, 150, 20)
)
chart_configurations.broad_market_groupbox.spyButton.clicked.connect(
    spy_button_clicked
)
chart_configurations.broad_market_groupbox.qqqButton = QPushButton(
    text="Chart QQQ", parent=chart_configurations.broad_market_groupbox
)
chart_configurations.broad_market_groupbox.qqqButton.setGeometry(
    QRect(170, 20, 150, 20)
)
chart_configurations.broad_market_groupbox.qqqButton.clicked.connect(
    qqq_button_clicked
)
chart_configurations.broad_market_groupbox.diaButton = QPushButton(
    text="Chart DIA", parent=chart_configurations.broad_market_groupbox
)
chart_configurations.broad_market_groupbox.diaButton.setGeometry(
    QRect(330, 20, 150, 20)
)
chart_configurations.broad_market_groupbox.diaButton.clicked.connect(
    dia_button_clicked
)
chart_configurations.broad_market_groupbox.vixButton = QPushButton(
    text="Chart VIX", parent=chart_configurations.broad_market_groupbox
)
chart_configurations.broad_market_groupbox.vixButton.setGeometry(
    QRect(490, 20, 150, 20)
)
chart_configurations.broad_market_groupbox.vixButton.clicked.connect(
    vix_button_clicked
)

# search bar for searching for a stock to chart
chart_configurations.search_bar_groupbox = QGroupBox(chart_configurations)
chart_configurations.search_bar_groupbox.setStyleSheet(
    'background-color: white;')
chart_configurations.search_bar_groupbox.setTitle("Find a Stock")
chart_configurations.search_bar_groupbox.setGeometry(10, 70, 960, 70)
chart_configurations.search_bar_groupbox.searchBar = QLineEdit(
    chart_configurations.search_bar_groupbox)
chart_configurations.search_bar_groupbox.searchBar.setGeometry(
    10, 20, 850, 40)
chart_configurations.search_bar_groupbox.searchBar.textChanged.connect(
    lambda txt: searchTextChanged(txt))
chart_configurations.search_bar_groupbox.searchBar.setFont(
    QFont('arial', 10))
chart_configurations.search_bar_groupbox.search_button = QPushButton(
    chart_configurations.search_bar_groupbox)
chart_configurations.search_bar_groupbox.search_button.setGeometry(
    870, 20, 80, 40)
chart_configurations.search_bar_groupbox.search_button.setText("Chart")
chart_configurations.search_bar_groupbox.search_button.setEnabled(False)
chart_configurations.search_bar_groupbox.search_button.clicked.connect(
    searchButtonClicked)
chart_configurations.settings_groupbox = QGroupBox(chart_configurations)
chart_configurations.settings_groupbox.setStyleSheet(
    'background-color: white;')
chart_configurations.settings_groupbox.setGeometry(10, 150, 1280, 600)
chart_configurations.settings_groupbox.setTitle("Chart Settings")
periods = ["1d", "5d", "1mo", "3mo", "6mo",
           "1y", "2y", "5y", "10y", "ytd", "max"]
timeframes = ["1m", "2m", "5m", "15m", "30m", "60m",
              "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"]
chart_configurations.settings_groupbox.period_radiobutton = QRadioButton(
    chart_configurations.settings_groupbox)
chart_configurations.settings_groupbox.period_radiobutton.setText(
    "Chart by Period")
chart_configurations.settings_groupbox.period_radiobutton.setGeometry(
    10, 50, 100, 30)
chart_configurations.settings_groupbox.period_radiobutton.setChecked(True)
chart_configurations.settings_groupbox.period_radiobutton.clicked.connect(
    period_radiobutton_clicked)
chart_configurations.settings_groupbox.daterange_radiobutton = QRadioButton(
    chart_configurations.settings_groupbox)
chart_configurations.settings_groupbox.daterange_radiobutton.setText(
    "Chart by Date Range")
chart_configurations.settings_groupbox.daterange_radiobutton.setGeometry(
    10, 100, 170, 30)
chart_configurations.settings_groupbox.daterange_radiobutton.clicked.connect(
    daterange_radiobutton_clicked)
chart_configurations.settings_groupbox.data_period_combobox = QComboBox(
    chart_configurations.settings_groupbox)
chart_configurations.settings_groupbox.data_period_combobox.addItems(
    periods)
chart_configurations.settings_groupbox.data_period_combobox.setGeometry(
    120, 60, 50, 20)
chart_configurations.settings_groupbox.data_timeframe_combobox = QComboBox(
    chart_configurations.settings_groupbox)
chart_configurations.settings_groupbox.data_timeframe_combobox.addItems(
    timeframes)
chart_configurations.settings_groupbox.data_timeframe_combobox.setGeometry(
    850, 50, 50, 30)
chart_configurations.settings_groupbox.prepost_checkbox = QCheckBox(
    chart_configurations.settings_groupbox)
chart_configurations.settings_groupbox.prepost_checkbox.setText(
    "Include Pre/Post Market Data")
chart_configurations.settings_groupbox.prepost_checkbox.setGeometry(
    10, 20, 180, 30)
chart_configurations.settings_groupbox.split_dividend_checkbox = QCheckBox(
    chart_configurations.settings_groupbox)
chart_configurations.settings_groupbox.split_dividend_checkbox.setText(
    "Show Split and Dividend Actions")
chart_configurations.settings_groupbox.split_dividend_checkbox.setGeometry(
    200, 20, 190, 30)
chart_configurations.settings_groupbox.adjust_ohlc_checkbox = QCheckBox(
    chart_configurations.settings_groupbox)
chart_configurations.settings_groupbox.adjust_ohlc_checkbox.setText(
    "Adjust OHLC")
chart_configurations.settings_groupbox.adjust_ohlc_checkbox.setGeometry(
    400, 20, 100, 30)
chart_configurations.settings_groupbox.volume_checkbox = QCheckBox(
    chart_configurations.settings_groupbox)
chart_configurations.settings_groupbox.volume_checkbox.setText(
    "Include Volume Bars")
chart_configurations.settings_groupbox.volume_checkbox.setGeometry(
    500, 20, 140, 30)
chart_configurations.settings_groupbox.nontrading_checkbox = QCheckBox(
    chart_configurations.settings_groupbox)
chart_configurations.settings_groupbox.nontrading_checkbox.setText(
    "Include Non-Trading Days")
chart_configurations.settings_groupbox.nontrading_checkbox.setGeometry(
    650, 20, 160, 30)
chart_configurations.settings_groupbox.timeframe_label = QLabel(
    chart_configurations.settings_groupbox)
chart_configurations.settings_groupbox.timeframe_label.setText(
    "Chart Timeframe:")
chart_configurations.settings_groupbox.timeframe_label.setGeometry(
    820, 20, 100, 30)
chart_configurations.settings_groupbox.start_date = QCalendarWidget(
    chart_configurations.settings_groupbox)
chart_configurations.settings_groupbox.start_date.setGeometry(
    10, 130, 600, 370)
chart_configurations.settings_groupbox.start_date.setStyleSheet(
    'background-color: deepskyblue; border: 3px solid black;')
chart_configurations.settings_groupbox.start_date.setEnabled(False)
chart_configurations.settings_groupbox.end_date = QCalendarWidget(
    chart_configurations.settings_groupbox)
chart_configurations.settings_groupbox.end_date.setGeometry(
    620, 130, 600, 370)
chart_configurations.settings_groupbox.end_date.setStyleSheet(
    'background-color: deepskyblue; border: 3px solid black;')
chart_configurations.settings_groupbox.end_date.setEnabled(False)
model = QStringListModel()
model.setStringList(all_tickers_list)
completer = ac.CustomQCompleter()
completer.setModel(model)
chart_configurations.search_bar_groupbox.searchBar.setCompleter(completer)
completer.activated.connect(
    lambda: chart_configurations.search_bar_groupbox.search_button.setEnabled(True))
completer.setMaxVisibleItems(5)
technical_indicators_dialog = QDialog()
technical_indicators_dialog.momentum_groupbox = QGroupBox(
    technical_indicators_dialog)
technical_indicators_dialog.momentum_groupbox.setTitle(
    "Momentum Indicators")
technical_indicators_dialog.momentum_groupbox.setGeometry(10, 10, 300, 620)
technical_indicators_dialog.momentum_groupbox.setStyleSheet(
    'background-color: white')
ta_combobox_items = [str(i) for i in range(0, 16)]
SETTINGS_DIALOG_BUTTON_STYLESHEET = "QPushButton::hover{background-color : deepskyblue; color : white;}"
def on_enter(event, widget, widget_button):
    widget_button.setVisible(True)
    widget.setStyleSheet("background-color : #E3E3E3;")
    for child in widget.children()[1:]:
        child.setStyleSheet("background-color : #E3E3E3;")
def on_exit(event, widget, widget_button):
    widget_button.setVisible(False)
    widget.setStyleSheet("background-color : white;")
    for child in widget.children()[1:]:
        child.setStyleSheet("background-color : white;")
technical_indicators_dialog.momentum_groupbox.momentum_scrollarea = QScrollArea(
    technical_indicators_dialog.momentum_groupbox)
technical_indicators_dialog.momentum_groupbox.momentum_scrollarea.setGeometry(
    10, 20, 280, 600)
momentum_widget = QWidget()
momentum_widget.resize(280, 1500)
momentum_widget.setLayout(QVBoxLayout())
technical_indicators_dialog.momentum_groupbox.momentum_scrollarea.setWidget(
    momentum_widget)
technical_indicators_dialog.momentum_groupbox.momentum_scrollarea.setVerticalScrollBarPolicy(
    Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
# add average directional index indicator to momentum indicator scrollable
adx_widget = QWidget()
adx_widget.setLayout(QHBoxLayout())
adx_label = QLabel()
adx_label.setText("Average Directional Index (ADX)")
adx_widget.layout().addWidget(adx_label)
adx_panel_combobox = QComboBox()
adx_panel_combobox.addItems(ta_combobox_items)
adx_panel_combobox.currentTextChanged.connect(
    lambda state: change_indicator_panel("talib.ADX", state))
adx_widget.layout().addWidget(adx_panel_combobox)
adx_checkbox = QCheckBox()
adx_checkbox.clicked.connect(
    lambda: selected_ta.append(("talib.ADX", adx_panel_combobox.currentIndex(
    ))) if adx_checkbox.isChecked() else removeIndicator("talib.ADX")
)
adx_widget.layout().addWidget(adx_checkbox)
momentum_widget.layout().addWidget(adx_widget)
# add ADX rating indicator to momentum indicator scrollable
adxr_widget = QWidget()
adxr_widget.setLayout(QHBoxLayout())
adxr_label = QLabel()
adxr_label.setText("Average Directional Index Rating (ADXR)")
adxr_widget.layout().addWidget(adxr_label)
adxr_panel_combobox = QComboBox()
adxr_panel_combobox.addItems(ta_combobox_items)
adxr_panel_combobox.currentTextChanged.connect(
    lambda state: change_indicator_panel("talib.ADXR", state)
)
adxr_widget.layout().addWidget(adxr_panel_combobox)
adxr_checkbox = QCheckBox()
adxr_checkbox.clicked.connect(
    lambda: selected_ta.append(("talib.ADXR", adxr_panel_combobox.currentIndex(
    ))) if adxr_checkbox.isChecked() else removeIndicator("talib.ADXR")
)
adxr_widget.layout().addWidget(adxr_checkbox)
momentum_widget.layout().addWidget(adxr_widget)
# add abs. price osc. to momentum indicator scrollable
apo_widget = QWidget()
apo_widget.setLayout(QHBoxLayout())
apo_label = QLabel()
apo_label.setText("Absolute Price Oscillator (APO)")
apo_widget.layout().addWidget(apo_label)
apo_panel_combobox = QComboBox()
apo_panel_combobox.addItems(ta_combobox_items)
apo_panel_combobox.currentTextChanged.connect(
    lambda state: change_indicator_panel("talib.APO", state))
apo_widget.layout().addWidget(apo_panel_combobox)
apo_checkbox = QCheckBox()
apo_checkbox.clicked.connect(
    lambda: selected_ta.append(("talib.APO", apo_panel_combobox.currentIndex(
    ))) if apo_checkbox.isChecked() else removeIndicator("talib.APO")
)
apo_widget.layout().addWidget(apo_checkbox)
momentum_widget.layout().addWidget(apo_widget)
# add aroon indicator to momentum indicator scrollable
aroon_widget = QWidget()
aroon_widget.setLayout(QHBoxLayout())
aroon_label = QLabel()
aroon_label.setText("Aroon Indicator")
aroon_widget.layout().addWidget(aroon_label)
aroon_panel_combobox = QComboBox()
aroon_panel_combobox.addItems(ta_combobox_items)
aroon_panel_combobox.currentTextChanged.connect(
    lambda state: change_indicator_panel("talib.AROON", state))
aroon_widget.layout().addWidget(aroon_panel_combobox)
aroon_checkbox = QCheckBox()
aroon_checkbox.clicked.connect(
    lambda: selected_ta.append(("talib.AROON", aroon_panel_combobox.currentIndex(
    ))) if aroon_checkbox.isChecked() else removeIndicator("talib.AROON")
)
aroon_widget.layout().addWidget(aroon_checkbox)
momentum_widget.layout().addWidget(aroon_widget)
# add aroon oscillator to momentum indicator scrollable
aroonosc_widget = QWidget()
aroonosc_widget.setLayout(QHBoxLayout())
aroonosc_label = QLabel()
aroonosc_label.setText("Aroon Oscillator")
aroonosc_widget.layout().addWidget(aroonosc_label)
aroonosc_panel_combobox = QComboBox()
aroonosc_panel_combobox.addItems(ta_combobox_items)
aroonosc_panel_combobox.currentTextChanged.connect(
    lambda state: change_indicator_panel("talib.AROONOSC", state))
aroonosc_widget.layout().addWidget(aroonosc_panel_combobox)
aroonosc_checkbox = QCheckBox()
aroonosc_checkbox.clicked.connect(
    lambda: selected_ta.append(("talib.AROONOSC", aroonosc_panel_combobox.currentIndex(
    ))) if aroonosc_checkbox.isChecked() else removeIndicator("talib.AROONOSC")
)
aroonosc_widget.layout().addWidget(aroonosc_checkbox)
momentum_widget.layout().addWidget(aroonosc_widget)
# add balance of power to momentum indicator scrollable
bop_widget = QWidget()
bop_widget.setLayout(QHBoxLayout())
bop_label = QLabel()
bop_label.setText("Balance of Power (BOP)")
bop_widget.layout().addWidget(bop_label)
bop_panel_combobox = QComboBox()
bop_panel_combobox.addItems(ta_combobox_items)
bop_panel_combobox.currentTextChanged.connect(
    lambda state: change_indicator_panel("talib.BOP", state))
bop_widget.layout().addWidget(bop_panel_combobox)
bop_checkbox = QCheckBox()
bop_checkbox.clicked.connect(
    lambda: selected_ta.append(("talib.BOP", bop_panel_combobox.currentIndex(
    ))) if bop_checkbox.isChecked() else removeIndicator("talib.BOP")
)
bop_widget.layout().addWidget(bop_checkbox)
momentum_widget.layout().addWidget(bop_widget)
# add commodity channel index to momentum indicator scrollable
cci_widget = QWidget()
cci_widget.setLayout(QHBoxLayout())
cci_label = QLabel()
cci_label.setText("Commodity Channel Index (CCI)")
cci_widget.layout().addWidget(cci_label)
cci_panel_combobox = QComboBox()
cci_panel_combobox.addItems(ta_combobox_items)
cci_panel_combobox.currentTextChanged.connect(
    lambda state: change_indicator_panel("talib.CCI", state))
cci_widget.layout().addWidget(cci_panel_combobox)
cci_checkbox = QCheckBox()
cci_checkbox.clicked.connect(
    lambda: selected_ta.append(("talib.CCI", cci_panel_combobox.currentIndex(
    ))) if cci_checkbox.isChecked() else removeIndicator("talib.CCI")
)
cci_widget.layout().addWidget(cci_checkbox)
momentum_widget.layout().addWidget(cci_widget)
# add chande momentum oscillator to momentum indicator scrollable
cmo_widget = QWidget()
cmo_widget.setLayout(QHBoxLayout())
cmo_label = QLabel()
cmo_label.setText("Chande Momentum Oscillator (CMO)")
cmo_widget.layout().addWidget(cmo_label)
cmo_panel_combobox = QComboBox()
cmo_panel_combobox.addItems(ta_combobox_items)
cmo_panel_combobox.currentTextChanged.connect(
    lambda state: change_indicator_panel("talib.CMO", state))
cmo_widget.layout().addWidget(cmo_panel_combobox)
cmo_checkbox = QCheckBox()
cmo_checkbox.clicked.connect(
    lambda: selected_ta.append(("talib.CMO", cmo_panel_combobox.currentIndex(
    ))) if cmo_checkbox.isChecked() else removeIndicator("talib.CMO")
)
cmo_widget.layout().addWidget(cmo_checkbox)
momentum_widget.layout().addWidget(cmo_widget)
# add directional movement index to momentum indicator scrollable
dx_widget = QWidget()
dx_widget.setLayout(QHBoxLayout())
dx_label = QLabel()
dx_label.setText("Directional Movement Index (DX)")
dx_widget.layout().addWidget(dx_label)
dx_panel_combobox = QComboBox()
dx_panel_combobox.addItems(ta_combobox_items)
dx_panel_combobox.currentTextChanged.connect(
    lambda state: change_indicator_panel("talib.DX", state))
dx_widget.layout().addWidget(dx_panel_combobox)
dx_checkbox = QCheckBox()
dx_checkbox.clicked.connect(
    lambda: selected_ta.append(("talib.DX", dx_panel_combobox.currentIndex(
    ))) if dx_checkbox.isChecked() else removeIndicator("talib.DX")
)
dx_widget.layout().addWidget(dx_checkbox)
momentum_widget.layout().addWidget(dx_widget)
# add directional movement index to momentum indicator scrollable
dx_widget = QWidget()
dx_widget.setLayout(QHBoxLayout())
dx_label = QLabel()
dx_label.setText("Directional Movement Index (DX)")
dx_widget.layout().addWidget(dx_label)
dx_panel_combobox = QComboBox()
dx_panel_combobox.addItems(ta_combobox_items)
dx_panel_combobox.currentTextChanged.connect(
    lambda state: change_indicator_panel("talib.DX", state))
dx_widget.layout().addWidget(dx_panel_combobox)
dx_checkbox = QCheckBox()
dx_checkbox.clicked.connect(
    lambda: selected_ta.append(("talib.DX", dx_panel_combobox.currentIndex(
    ))) if dx_checkbox.isChecked() else removeIndicator("talib.DX")
)
dx_widget.layout().addWidget(dx_checkbox)
momentum_widget.layout().addWidget(dx_widget)
# add moving average convergence divergence to momentum indicator scrollable
macd_widget = QWidget()
macd_widget.setLayout(QHBoxLayout())
macd_label = QLabel()
macd_label.setText("MACD")
macd_widget.layout().addWidget(macd_label)
macd_panel_combobox = QComboBox()
macd_panel_combobox.addItems(ta_combobox_items)
macd_panel_combobox.currentTextChanged.connect(
    lambda state: change_indicator_panel("talib.MACD", state))
macd_widget.layout().addWidget(macd_panel_combobox)
macd_checkbox = QCheckBox()
macd_checkbox.clicked.connect(
    lambda: selected_ta.append(("talib.MACD", macd_panel_combobox.currentIndex(
    ))) if macd_checkbox.isChecked() else removeIndicator("talib.MACD")
)
macd_widget.layout().addWidget(macd_checkbox)
momentum_widget.layout().addWidget(macd_widget)
# add moving average convergence divergence w/controllable MA type to momentum indicator scrollable
macdext_widget = QWidget()
macdext_widget.setLayout(QHBoxLayout())
macdext_label = QLabel()
macdext_label.setText("MACDEXT")
macdext_widget.layout().addWidget(macdext_label)
macdext_panel_combobox = QComboBox()
macdext_panel_combobox.addItems(ta_combobox_items)
macdext_panel_combobox.currentTextChanged.connect(
    lambda state: change_indicator_panel("talib.MACDEXT", state))
macdext_widget.layout().addWidget(macdext_panel_combobox)
macdext_checkbox = QCheckBox()
macdext_checkbox.clicked.connect(
    lambda: selected_ta.append(("talib.MACDEXT", macdext_panel_combobox.currentIndex(
    ))) if macdext_checkbox.isChecked() else removeIndicator("talib.MACDEXT")
)
macdext_widget.layout().addWidget(macdext_checkbox)
momentum_widget.layout().addWidget(macdext_widget)
# add money flow index to momentum indicator scrollable
mfi_widget = QWidget()
mfi_widget.setLayout(QHBoxLayout())
mfi_label = QLabel()
mfi_label.setText("Money Flow Index (MFI)")
mfi_widget.layout().addWidget(mfi_label)
mfi_panel_combobox = QComboBox()
mfi_panel_combobox.addItems(ta_combobox_items)
mfi_panel_combobox.currentTextChanged.connect(
    lambda state: change_indicator_panel("talib.MFI", state))
mfi_widget.layout().addWidget(mfi_panel_combobox)
mfi_checkbox = QCheckBox()
mfi_checkbox.clicked.connect(
    lambda: selected_ta.append(("talib.MFI", mfi_panel_combobox.currentIndex(
    ))) if mfi_checkbox.isChecked() else removeIndicator("talib.MFI")
)
mfi_widget.layout().addWidget(mfi_checkbox)
momentum_widget.layout().addWidget(mfi_widget)
chart_dialog.addTab(chart_configurations, "Chart Configurations")
chart_dialog.addTab(technical_indicators_dialog, "Technical Indicators")
# add minus directional index to momentum indicator scrollable
minusdi_widget = QWidget()
minusdi_widget.setLayout(QHBoxLayout())
minusdi_label = QLabel()
minusdi_label.setText("Minus Directional Index")
minusdi_widget.layout().addWidget(minusdi_label)
minusdi_panel_combobox = QComboBox()
minusdi_panel_combobox.addItems(ta_combobox_items)
minusdi_panel_combobox.currentTextChanged.connect(
    lambda state: change_indicator_panel("talib.MINUS_DI", state))
minusdi_widget.layout().addWidget(minusdi_panel_combobox)
minusdi_checkbox = QCheckBox()
minusdi_checkbox.clicked.connect(
    lambda: selected_ta.append(("talib.MINUS_DI", minusdi_panel_combobox.currentIndex(
    ))) if minusdi_checkbox.isChecked() else removeIndicator("talib.MINUS_DI")
)
minusdi_widget.layout().addWidget(minusdi_checkbox)
momentum_widget.layout().addWidget(minusdi_widget)
# add minus directional movement to momentum indicator scrollable
minusdm_widget = QWidget()
minusdm_widget.setLayout(QHBoxLayout())
minusdm_label = QLabel()
minusdm_label.setText("Minus Directional Movement")
minusdm_widget.layout().addWidget(minusdm_label)
minusdm_panel_combobox = QComboBox()
minusdm_panel_combobox.addItems(ta_combobox_items)
minusdm_panel_combobox.currentTextChanged.connect(
    lambda state: change_indicator_panel("talib.MINUS_DM", state))
minusdm_widget.layout().addWidget(minusdm_panel_combobox)
minusdm_checkbox = QCheckBox()
minusdm_checkbox.clicked.connect(
    lambda: selected_ta.append(("talib.MINUS_DM", minusdm_panel_combobox.currentIndex(
    ))) if minusdm_checkbox.isChecked() else removeIndicator("talib.MINUS_DM")
)
minusdm_widget.layout().addWidget(minusdm_checkbox)
momentum_widget.layout().addWidget(minusdm_widget)
# add momentum to momentum indicator scrollableMINUS_DM
mom_widget = QWidget()
mom_widget.setLayout(QHBoxLayout())
mom_label = QLabel()
mom_label.setText("Momentum")
mom_widget.layout().addWidget(mom_label)
mom_panel_combobox = QComboBox()
mom_panel_combobox.addItems(ta_combobox_items)
mom_panel_combobox.currentTextChanged.connect(
    lambda state: change_indicator_panel("talib.MOM", state))
mom_widget.layout().addWidget(mom_panel_combobox)
mom_checkbox = QCheckBox()
mom_checkbox.clicked.connect(
    lambda: selected_ta.append(("talib.MOM", mom_panel_combobox.currentIndex(
    ))) if mom_checkbox.isChecked() else removeIndicator("talib.MOM")
)
mom_widget.layout().addWidget(mom_checkbox)
momentum_widget.layout().addWidget(mom_widget)
# add plus directional indicator to momentum indicator scrollable
plusdi_widget = QWidget()
plusdi_widget.setLayout(QHBoxLayout())
plusdi_label = QLabel()
plusdi_label.setText("Plus Directional Indicator")
plusdi_widget.layout().addWidget(plusdi_label)
plusdi_panel_combobox = QComboBox()
plusdi_panel_combobox.addItems(ta_combobox_items)
plusdi_panel_combobox.currentTextChanged.connect(
    lambda state: change_indicator_panel("talib.PLUS_DI", state))
plusdi_widget.layout().addWidget(plusdi_panel_combobox)
plusdi_checkbox = QCheckBox()
plusdi_checkbox.clicked.connect(
    lambda: selected_ta.append(("talib.PLUS_DI", plusdi_panel_combobox.currentIndex(
    ))) if plusdi_checkbox.isChecked() else removeIndicator("talib.PLUS_DI")
)
plusdi_widget.layout().addWidget(plusdi_checkbox)
momentum_widget.layout().addWidget(plusdi_widget)
# add plus directional movement to momentum indicator scrollable
plusdm_widget = QWidget()
plusdm_widget.setLayout(QHBoxLayout())
plusdm_label = QLabel()
plusdm_label.setText("Plus Directional Movement")
plusdm_widget.layout().addWidget(plusdm_label)
plusdm_panel_combobox = QComboBox()
plusdm_panel_combobox.addItems(ta_combobox_items)
plusdm_panel_combobox.currentTextChanged.connect(
    lambda state: change_indicator_panel("talib.PLUS_DM", state))
plusdm_widget.layout().addWidget(plusdm_panel_combobox)
plusdm_checkbox = QCheckBox()
plusdm_checkbox.clicked.connect(
    lambda: selected_ta.append(("talib.PLUS_DM", plusdm_panel_combobox.currentIndex(
    ))) if plusdm_checkbox.isChecked() else removeIndicator("talib.PLUS_DM")
)
plusdm_widget.layout().addWidget(plusdm_checkbox)
momentum_widget.layout().addWidget(plusdm_widget)
# add percentage price oscillator to momentum indicator scrollable
kama_widget = QWidget()
kama_widget.setLayout(QHBoxLayout())
kama_label = QLabel()
kama_label.setText("KAMA Indicator")
kama_widget.layout().addWidget(kama_label)
kama_panel_combobox = QComboBox()
kama_panel_combobox.addItems(ta_combobox_items)
kama_panel_combobox.currentTextChanged.connect(
    lambda state: change_indicator_panel("ta.momentum.kama", state))
kama_widget.layout().addWidget(kama_panel_combobox)
kama_checkbox = QCheckBox()
kama_checkbox.clicked.connect(
    lambda: selected_ta.append(("ta.momentum.kama", kama_panel_combobox.currentIndex(
    ))) if kama_checkbox.isChecked() else removeIndicator("ta.momentum.kama")
)
kama_widget.layout().addWidget(kama_checkbox)
momentum_widget.layout().addWidget(kama_widget)
# add percentage volume oscillator to momentum indicator scrollable
pvo_widget = QWidget()
pvo_widget.setLayout(QHBoxLayout())
pvo_label = QLabel()
pvo_label.setText("Percentage Volume Oscillator")
pvo_widget.layout().addWidget(pvo_label)
pvo_panel_combobox = QComboBox()
pvo_panel_combobox.addItems(ta_combobox_items)
pvo_panel_combobox.currentTextChanged.connect(
    lambda state: change_indicator_panel("ta.momentum.pvo", state))
pvo_widget.layout().addWidget(pvo_panel_combobox)
pvo_checkbox = QCheckBox()
pvo_checkbox.clicked.connect(
    lambda: selected_ta.append(("ta.momentum.pvo", pvo_panel_combobox.currentIndex(
    ))) if pvo_checkbox.isChecked() else removeIndicator("ta.momentum.pvo")
)
pvo_widget.layout().addWidget(pvo_checkbox)
momentum_widget.layout().addWidget(pvo_widget)
# add rate of change indicator to momentum indicator scrollable
roc_widget = QWidget()
roc_widget.setLayout(QHBoxLayout())
roc_label = QLabel()
roc_label.setText("Rate of Change")
roc_widget.layout().addWidget(roc_label)
roc_panel_combobox = QComboBox()
roc_panel_combobox.addItems(ta_combobox_items)
roc_panel_combobox.currentTextChanged.connect(
    lambda state: change_indicator_panel("talib.ROC", state))
roc_widget.layout().addWidget(roc_panel_combobox)
roc_checkbox = QCheckBox()
roc_checkbox.clicked.connect(
    lambda: selected_ta.append(("talib.ROC", roc_panel_combobox.currentIndex(
    ))) if roc_checkbox.isChecked() else removeIndicator("talib.ROC")
)
roc_widget.layout().addWidget(roc_checkbox)
momentum_widget.layout().addWidget(roc_widget)
# add ROC percentage to momentum indicator scrollable
rocp_widget = QWidget()
rocp_widget.setLayout(QHBoxLayout())
rocp_label = QLabel()
rocp_label.setText("Rate of Change (%)")
rocp_widget.layout().addWidget(rocp_label)
rocp_panel_combobox = QComboBox()
rocp_panel_combobox.addItems(ta_combobox_items)
rocp_panel_combobox.currentTextChanged.connect(
    lambda state: change_indicator_panel("talib.ROCP", state))
rocp_widget.layout().addWidget(rocp_panel_combobox)
rocp_checkbox = QCheckBox()
rocp_checkbox.clicked.connect(
    lambda: selected_ta.append(("talib.ROCP", rocp_panel_combobox.currentIndex(
    ))) if rocp_checkbox.isChecked() else removeIndicator("talib.ROCP")
)
rocp_widget.layout().addWidget(rocp_checkbox)
momentum_widget.layout().addWidget(rocp_widget)
# add rate of change ratio to momentum indicator scrollable
rocr_widget = QWidget()
rocr_widget.setLayout(QHBoxLayout())
rocr_label = QLabel()
rocr_label.setText("Rate of Change Ratio")
rocr_widget.layout().addWidget(rocr_label)
rocr_panel_combobox = QComboBox()
rocr_panel_combobox.addItems(ta_combobox_items)
rocr_panel_combobox.currentTextChanged.connect(
    lambda state: change_indicator_panel("talib.ROCR", state))
rocr_widget.layout().addWidget(rocr_panel_combobox)
rocr_checkbox = QCheckBox()
rocr_checkbox.clicked.connect(
    lambda: selected_ta.append(("talib.ROCR", rocr_panel_combobox.currentIndex(
    ))) if rocr_checkbox.isChecked() else removeIndicator("talib.ROCR")
)
rocr_widget.layout().addWidget(rocr_checkbox)
momentum_widget.layout().addWidget(rocr_widget)
# add 100-scale ROCR to momentum indicator scrollable
rocr100_widget = QWidget()
rocr100_widget.setLayout(QHBoxLayout())
rocr100_label = QLabel()
rocr100_label.setText("ROCR Indexed to 100")
rocr100_widget.layout().addWidget(rocr100_label)
rocr100_panel_combobox = QComboBox()
rocr100_panel_combobox.addItems(ta_combobox_items)
rocr100_panel_combobox.currentTextChanged.connect(
    lambda state: change_indicator_panel("talib.ROCR100", state))
rocr100_widget.layout().addWidget(rocr100_panel_combobox)
rocr100_checkbox = QCheckBox()
rocr100_checkbox.clicked.connect(
    lambda: selected_ta.append(("talib.ROCR100", rocr100_panel_combobox.currentIndex(
    ))) if rocr100_checkbox.isChecked() else removeIndicator("talib.ROCR100")
)
rocr100_widget.layout().addWidget(rocr100_checkbox)
momentum_widget.layout().addWidget(rocr100_widget)
# add relative strength index to momentum indicator scrollable
rsi_widget = QWidget()
rsi_widget.setLayout(QHBoxLayout())
rsi_label = QLabel()
rsi_label.setText("Relative Strength Index")
rsi_widget.layout().addWidget(rsi_label)
rsi_panel_combobox = QComboBox()
rsi_panel_combobox.addItems(ta_combobox_items)
rsi_panel_combobox.currentTextChanged.connect(
    lambda state: change_indicator_panel("talib.RSI", state))
rsi_widget.layout().addWidget(rsi_panel_combobox)
rsi_checkbox = QCheckBox()
rsi_checkbox.clicked.connect(
    lambda: selected_ta.append(("talib.RSI", rsi_panel_combobox.currentIndex(
    ))) if rsi_checkbox.isChecked() else removeIndicator("talib.RSI")
)
rsi_widget.layout().addWidget(rsi_checkbox)
momentum_widget.layout().addWidget(rsi_widget)
# add slow stochastic indicator to momentum indicator scrollable
slowstoch_widget = QWidget()
slowstoch_widget.setLayout(QHBoxLayout())
slowstoch_label = QLabel()
slowstoch_label.setText("Slow Stochastic")
slowstoch_widget.layout().addWidget(slowstoch_label)
slowstoch_panel_combobox = QComboBox()
slowstoch_panel_combobox.addItems(ta_combobox_items)
slowstoch_panel_combobox.currentTextChanged.connect(
    lambda state: change_indicator_panel("talib.STOCH", state))
slowstoch_widget.layout().addWidget(slowstoch_panel_combobox)
slowstoch_checkbox = QCheckBox()
slowstoch_checkbox.clicked.connect(
    lambda: selected_ta.append(("talib.STOCH", slowstoch_panel_combobox.currentIndex(
    ))) if slowstoch_checkbox.isChecked() else removeIndicator("talib.STOCH")
)
slowstoch_widget.layout().addWidget(slowstoch_checkbox)
momentum_widget.layout().addWidget(slowstoch_widget)
# add fast stochastic to momentum indicator scrollable
faststoch_widget = QWidget()
faststoch_widget.setLayout(QHBoxLayout())
faststoch_label = QLabel()
faststoch_label.setText("Fast Stochastic")
faststoch_widget.layout().addWidget(faststoch_label)
faststoch_panel_combobox = QComboBox()
faststoch_panel_combobox.addItems(ta_combobox_items)
faststoch_panel_combobox.currentTextChanged.connect(
    lambda state: change_indicator_panel("talib.STOCHF", state))
faststoch_widget.layout().addWidget(faststoch_panel_combobox)
faststoch_checkbox = QCheckBox()
faststoch_checkbox.clicked.connect(
    lambda: selected_ta.append(("talib.STOCHF", faststoch_panel_combobox.currentIndex(
    ))) if faststoch_checkbox.isChecked() else removeIndicator("talib.STOCHF")
)
faststoch_widget.layout().addWidget(faststoch_checkbox)
momentum_widget.layout().addWidget(faststoch_widget)
# add stochastic RSI to momentum indicator scrollable
stochrsi_widget = QWidget()
stochrsi_widget.setLayout(QHBoxLayout())
stochrsi_label = QLabel()
stochrsi_label.setText("Stochastic RSI")
stochrsi_widget.layout().addWidget(stochrsi_label)
stochrsi_label.setAutoFillBackground(False)
stochrsi_panel_combobox = QComboBox()
stochrsi_panel_combobox.addItems(ta_combobox_items)
stochrsi_panel_combobox.currentTextChanged.connect(lambda state: change_indicator_panel(
    "talib.STOCHRSI", state, selected_ta[get_indicator_index("talib.STOCHRSI")][2]) if stochrsi_checkbox.isChecked() else None)
stochrsi_widget.layout().addWidget(stochrsi_panel_combobox)
stochrsi_settings_button = QPushButton()
stochrsi_settings_button.setVisible(False)
size_retain = stochrsi_settings_button.sizePolicy()
size_retain.setRetainSizeWhenHidden(True)
stochrsi_settings_button.setSizePolicy(size_retain)
stochrsi_settings_button.setIcon(QIcon('icons/gear.jpg'))
stochrsi_widget.enterEvent = lambda event: on_enter(
    event, stochrsi_widget, stochrsi_settings_button)
stochrsi_widget.leaveEvent = lambda event: on_exit(
    event, stochrsi_widget, stochrsi_settings_button)
def stochrsi_button_clicked():
    wnd = QDialog(widget)
    wnd.setWindowTitle("Parabolic SAR")
    wnd.setLayout(QVBoxLayout())
    fastk_widget = QWidget()
    fastk_widget.setLayout(QHBoxLayout())
    fastk_label = QLabel("Fast %k Period")
    fastk_spinbox = QSpinBox()
    fastk_spinbox.setValue(selected_ta[get_indicator_index(
        "talib.STOCHRSI")][2][0] if stochrsi_checkbox.isChecked() else 5)
    fastk_widget.layout().addWidget(fastk_label)
    fastk_widget.layout().addWidget(fastk_spinbox)
    wnd.layout().addWidget(fastk_widget)
    fastd_widget = QWidget()
    fastd_widget.setLayout(QHBoxLayout())
    fastd_label = QLabel("Fast %d Period")
    fastd_spinbox = QSpinBox()
    fastd_spinbox.setValue(selected_ta[get_indicator_index(
        "talib.STOCHRSI")][2][1] if stochrsi_checkbox.isChecked() else 3)
    fastd_widget.layout().addWidget(fastd_label)
    fastd_widget.layout().addWidget(fastd_spinbox)
    wnd.layout().addWidget(fastd_widget)
    fastd_matype_widget = QWidget()
    fastd_matype_widget.setLayout(QHBoxLayout())
    fastd_matype_label = QLabel("Fast %d MA Type")
    fastd_matype_spinbox = QSpinBox()
    fastd_matype_spinbox.setValue(selected_ta[get_indicator_index(
        "talib.STOCHRSI")][2][2] if stochrsi_checkbox.isChecked() else 0)
    fastd_matype_widget.layout().addWidget(fastd_matype_label)
    fastd_matype_widget.layout().addWidget(fastd_matype_spinbox)
    wnd.layout().addWidget(fastd_matype_widget)
    defaults_button = QPushButton("Reset to Defaults")
    defaults_button.setStyleSheet(SETTINGS_DIALOG_BUTTON_STYLESHEET)
    def restore_defaults():
        fastk_spinbox.setValue(5)
        fastd_spinbox.setValue(3)
        fastd_matype_spinbox.setValue(0)
    defaults_button.clicked.connect(restore_defaults)
    cancel_button = QPushButton("Cancel")
    cancel_button.setStyleSheet(SETTINGS_DIALOG_BUTTON_STYLESHEET)
    cancel_button.clicked.connect(lambda: wnd.done(0))
    ok_button = QPushButton(
        "Save" if stochrsi_checkbox.isChecked() else "Save and Add")
    ok_button.setStyleSheet(SETTINGS_DIALOG_BUTTON_STYLESHEET)
    def ok_button_clicked():
        if (stochrsi_checkbox.isChecked()):
            selected_ta[get_indicator_index("talib.STOCHRSI")] = ("talib.STOCHRSI", stochrsi_panel_combobox.currentIndex(), [
                fastk_spinbox.value(), fastd_spinbox.value(), fastd_matype_spinbox.value()])
        else:
            selected_ta.append(("talib.STOCHRSI", stochrsi_panel_combobox.currentIndex(), [
                               fastk_spinbox.value(), fastd_spinbox.value(), fastd_matype_spinbox.value()]))
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
    lambda: selected_ta.append(("talib.STOCHRSI", stochrsi_panel_combobox.currentIndex(
    ))) if stochrsi_checkbox.isChecked() else removeIndicator("talib.STOCHRSI")
)
stochrsi_widget.layout().addWidget(stochrsi_checkbox)
momentum_widget.layout().addWidget(stochrsi_widget)
# add true strength index to momentum indicator scrollable
tsi_widget = QWidget()
tsi_widget.setLayout(QHBoxLayout())
tsi_label = QLabel()
tsi_label.setText("True Strength Index (TSI)")
tsi_widget.layout().addWidget(tsi_label)
tsi_label.setAutoFillBackground(False)
tsi_panel_combobox = QComboBox()
tsi_panel_combobox.addItems(ta_combobox_items)
tsi_panel_combobox.currentTextChanged.connect(
    lambda state: change_indicator_panel(
        "ta.momentum.tsi", state, selected_ta[get_indicator_index("ta.momentum.tsi")][2]
    ) if tsi_checkbox.isChecked() else None
)
tsi_widget.layout().addWidget(tsi_panel_combobox)
tsi_settings_button = QPushButton()
tsi_settings_button.setVisible(False)
size_retain = tsi_settings_button.sizePolicy()
size_retain.setRetainSizeWhenHidden(True)
tsi_settings_button.setSizePolicy(size_retain)
tsi_settings_button.setIcon(QIcon('icons/gear.jpg'))
tsi_widget.enterEvent = lambda event: on_enter(
    event, tsi_widget, tsi_settings_button)
tsi_widget.leaveEvent = lambda event: on_exit(
    event, tsi_widget, tsi_settings_button)
def tsi_button_clicked():
    wnd = QDialog(widget)
    wnd.setWindowTitle("True Strength Index")
    wnd.setLayout(QVBoxLayout())
    slow_period_widget = QWidget()
    slow_period_widget.setLayout(QHBoxLayout())
    slow_period_label = QLabel("Slow Period")
    slow_period_spinbox = QSpinBox()
    slow_period_spinbox.setValue(selected_ta[get_indicator_index(
        "ta.momentum.tsi")][2][0] if tsi_checkbox.isChecked() else 25)
    slow_period_widget.layout().addWidget(slow_period_label)
    slow_period_widget.layout().addWidget(slow_period_spinbox)
    wnd.layout().addWidget(slow_period_widget)
    fast_period_widget = QWidget()
    fast_period_widget.setLayout(QHBoxLayout())
    fast_period_label = QLabel("Fast Period")
    fast_period_spinbox = QSpinBox()
    fast_period_spinbox.setValue(selected_ta[get_indicator_index(
        "ta.momentum.tsi")][2][1] if tsi_checkbox.isChecked() else 13)
    fast_period_widget.layout().addWidget(fast_period_label)
    fast_period_widget.layout().addWidget(fast_period_spinbox)
    wnd.layout().addWidget(fast_period_widget)
    defaults_button = QPushButton("Reset to Defaults")
    defaults_button.setStyleSheet(SETTINGS_DIALOG_BUTTON_STYLESHEET)
    def restore_defaults():
        fast_period_spinbox.setValue(13)
        slow_period_spinbox.setValue(25)
    defaults_button.clicked.connect(restore_defaults)
    cancel_button = QPushButton("Cancel")
    cancel_button.setStyleSheet(SETTINGS_DIALOG_BUTTON_STYLESHEET)
    cancel_button.clicked.connect(lambda: wnd.done(0))
    ok_button = QPushButton(
        "Save" if tsi_checkbox.isChecked() else "Save and Add")
    ok_button.setStyleSheet(SETTINGS_DIALOG_BUTTON_STYLESHEET)
    def ok_button_clicked():
        if (tsi_checkbox.isChecked()):
            selected_ta[get_indicator_index("ta.momentum.tsi")] = ("ta.momentum.tsi", tsi_panel_combobox.currentIndex(), [
                slow_period_spinbox.value(), fast_period_spinbox.value()])
        else:
            selected_ta.append(("ta.momentum.tsi", tsi_panel_combobox.currentIndex(), [
                               slow_period_spinbox.value(), fast_period_spinbox.value()]))
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
    lambda: selected_ta.append(("ta.momentum.tsi", tsi_panel_combobox.currentIndex(
    ))) if tsi_checkbox.isChecked() else removeIndicator("ta.momentum.tsi")
)
tsi_widget.layout().addWidget(tsi_checkbox)
momentum_widget.layout().addWidget(tsi_widget)
# add ultimate oscillator to momentum indicator scrollable
ultosc_widget = QWidget()
ultosc_widget.setLayout(QHBoxLayout())
ultosc_label = QLabel()
ultosc_label.setText("Ultimate Oscillator")
ultosc_widget.layout().addWidget(ultosc_label)
ultosc_label.setAutoFillBackground(False)
ultosc_panel_combobox = QComboBox()
ultosc_panel_combobox.addItems(ta_combobox_items)
ultosc_panel_combobox.currentTextChanged.connect(lambda state: change_indicator_panel(
    "talib.ULTOSC", state, selected_ta[get_indicator_index("talib.ULTOSC")][2]) if ultosc_checkbox.isChecked() else None)
ultosc_widget.layout().addWidget(ultosc_panel_combobox)
ultosc_settings_button = QPushButton()
ultosc_settings_button.setVisible(False)
size_retain = ultosc_settings_button.sizePolicy()
size_retain.setRetainSizeWhenHidden(True)
ultosc_settings_button.setSizePolicy(size_retain)
ultosc_settings_button.setIcon(QIcon('icons/gear.jpg'))
ultosc_widget.enterEvent = lambda event: on_enter(
    event, ultosc_widget, ultosc_settings_button)
ultosc_widget.leaveEvent = lambda event: on_exit(
    event, ultosc_widget, ultosc_settings_button)
def ultosc_button_clicked():
    wnd = QDialog(widget)
    wnd.setWindowTitle("Parabolic SAR")
    wnd.setLayout(QVBoxLayout())
    fast_widget = QWidget()
    fast_widget.setLayout(QHBoxLayout())
    fast_label = QLabel("Fast Length")
    fast_spinbox = QSpinBox()
    fast_spinbox.setValue(selected_ta[get_indicator_index(
        "talib.ULTOSC")][2][0] if ultosc_checkbox.isChecked() else 7)
    fast_widget.layout().addWidget(fast_label)
    fast_widget.layout().addWidget(fast_spinbox)
    wnd.layout().addWidget(fast_widget)
    medium_widget = QWidget()
    medium_widget.setLayout(QHBoxLayout())
    medium_label = QLabel("Medium Length")
    medium_spinbox = QSpinBox()
    medium_spinbox.setValue(selected_ta[get_indicator_index(
        "talib.ULTOSC")][2][1] if ultosc_checkbox.isChecked() else 14)
    medium_widget.layout().addWidget(medium_label)
    medium_widget.layout().addWidget(medium_spinbox)
    wnd.layout().addWidget(medium_widget)
    slow_widget = QWidget()
    slow_widget.setLayout(QHBoxLayout())
    slow_label = QLabel("Slow Length")
    slow_spinbox = QSpinBox()
    slow_spinbox.setValue(selected_ta[get_indicator_index(
        "talib.ULTOSC")][2][2] if ultosc_checkbox.isChecked() else 28)
    slow_widget.layout().addWidget(slow_label)
    slow_widget.layout().addWidget(slow_spinbox)
    wnd.layout().addWidget(slow_widget)
    defaults_button = QPushButton("Reset to Defaults")
    defaults_button.setStyleSheet(SETTINGS_DIALOG_BUTTON_STYLESHEET)
    def restore_defaults():
        fast_spinbox.setValue(7)
        medium_spinbox.setValue(14)
        slow_spinbox.setValue(28)
    defaults_button.clicked.connect(restore_defaults)
    cancel_button = QPushButton("Cancel")
    cancel_button.setStyleSheet(SETTINGS_DIALOG_BUTTON_STYLESHEET)
    cancel_button.clicked.connect(lambda: wnd.done(0))
    ok_button = QPushButton(
        "Save" if ultosc_checkbox.isChecked() else "Save and Add")
    ok_button.setStyleSheet(SETTINGS_DIALOG_BUTTON_STYLESHEET)
    def ok_button_clicked():
        if (ultosc_checkbox.isChecked()):
            selected_ta[get_indicator_index("talib.ULTOSC")] = ("talib.ULTOSC", ultosc_panel_combobox.currentIndex(), [
                fast_spinbox.value(), medium_spinbox.value(), slow_spinbox.value()])
        else:
            selected_ta.append(("talib.ULTOSC", ultosc_panel_combobox.currentIndex(), [
                               fast_spinbox.value(), medium_spinbox.value(), slow_spinbox.value()]))
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
    lambda: selected_ta.append(("talib.ULTOSC", ultosc_panel_combobox.currentIndex(
    ))) if ultosc_checkbox.isChecked() else removeIndicator("talib.ULTOSC")
)
ultosc_widget.layout().addWidget(ultosc_checkbox)
momentum_widget.layout().addWidget(ultosc_widget)
# add williams %r to momentum indicator scrollable
willr_widget = QWidget()
willr_widget.setLayout(QHBoxLayout())
willr_label = QLabel()
willr_label.setText("Williams' %r")
willr_widget.layout().addWidget(willr_label)
willr_label.setAutoFillBackground(False)
willr_panel_combobox = QComboBox()
willr_panel_combobox.addItems(ta_combobox_items)
willr_panel_combobox.currentTextChanged.connect(lambda state: change_indicator_panel(
    "talib.WILLR", state,  selected_ta[get_indicator_index("talib.WILLR")][2]) if willr_checkbox.isChecked() else None)
willr_widget.layout().addWidget(willr_panel_combobox)
willr_settings_button = QPushButton()
willr_settings_button.setVisible(False)
size_retain = willr_settings_button.sizePolicy()
size_retain.setRetainSizeWhenHidden(True)
willr_settings_button.setSizePolicy(size_retain)
willr_settings_button.setIcon(QIcon('icons/gear.jpg'))
willr_widget.enterEvent = lambda event: on_enter(
    event, willr_widget, willr_settings_button)
willr_widget.leaveEvent = lambda event: on_exit(
    event, willr_widget, willr_settings_button)
def willr_button_clicked():
    wnd = QDialog(widget)
    wnd.setWindowTitle("William's %R")
    wnd.setLayout(QVBoxLayout())
    period_widget = QWidget()
    period_widget.setLayout(QHBoxLayout())
    period_label = QLabel("Period")
    period_spinbox = QSpinBox()
    period_spinbox.setValue(selected_ta[get_indicator_index(
        "talib.WILLR")][2][0] if willr_checkbox.isChecked() else 14)
    period_widget.layout().addWidget(period_label)
    period_widget.layout().addWidget(period_spinbox)
    wnd.layout().addWidget(period_widget)
    defaults_button = QPushButton("Reset to Defaults")
    defaults_button.setStyleSheet(SETTINGS_DIALOG_BUTTON_STYLESHEET)
    defaults_button.clicked.connect(lambda: period_spinbox.setValue(14))
    cancel_button = QPushButton("Cancel")
    cancel_button.setStyleSheet(SETTINGS_DIALOG_BUTTON_STYLESHEET)
    cancel_button.clicked.connect(lambda: wnd.done(0))
    ok_button = QPushButton(
        "Save" if willr_checkbox.isChecked() else "Save and Add")
    ok_button.setStyleSheet(SETTINGS_DIALOG_BUTTON_STYLESHEET)
    def ok_button_clicked():
        if (willr_checkbox.isChecked()):
            selected_ta[get_indicator_index("talib.WILLR")] = (
                "talib.WILLR", willr_panel_combobox.currentIndex(), [period_spinbox.value()])
        else:
            selected_ta.append(
                ("talib.WILLR", willr_panel_combobox.currentIndex(), [period_spinbox.value()]))
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
    lambda: selected_ta.append(("talib.WILLR", willr_panel_combobox.currentIndex(
    ))) if willr_checkbox.isChecked() else removeIndicator("talib.WILLR")
)
willr_widget.layout().addWidget(willr_checkbox)
momentum_widget.layout().addWidget(willr_widget)
# create trend indicator scrollable
technical_indicators_dialog.trend_groupbox = QGroupBox(
    technical_indicators_dialog)
technical_indicators_dialog.trend_groupbox.setTitle("Trend Indicators")
technical_indicators_dialog.trend_groupbox.setGeometry(320, 10, 300, 620)
technical_indicators_dialog.trend_groupbox.setStyleSheet(
    'background-color: white')
technical_indicators_dialog.trend_groupbox.trend_scrollarea = QScrollArea(
    technical_indicators_dialog.trend_groupbox)
technical_indicators_dialog.trend_groupbox.trend_scrollarea.setGeometry(
    10, 20, 280, 600)
trend_widget = QWidget()
trend_widget.resize(280, 400)
trend_widget.setLayout(QVBoxLayout())
technical_indicators_dialog.trend_groupbox.trend_scrollarea.setWidget(
    trend_widget)
technical_indicators_dialog.trend_groupbox.trend_scrollarea.setVerticalScrollBarPolicy(
    Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
# add dpo to trend indicator scrollable
dpo_widget = QWidget()
dpo_widget.setLayout(QHBoxLayout())
dpo_label = QLabel()
dpo_label.setText("Detrended Price Oscillator")
dpo_widget.layout().addWidget(dpo_label)
dpo_label.setAutoFillBackground(False)
dpo_panel_combobox = QComboBox()
dpo_panel_combobox.addItems(ta_combobox_items)
dpo_panel_combobox.currentTextChanged.connect(
    lambda state: change_indicator_panel(
        "ta.trend.dpo", state, selected_ta[get_indicator_index("ta.trend.dpo")][2]
    ) if dpo_checkbox.isChecked() else None
)
dpo_widget.layout().addWidget(dpo_panel_combobox)
dpo_settings_button = QPushButton()
dpo_settings_button.setVisible(False)
size_retain = dpo_settings_button.sizePolicy()
size_retain.setRetainSizeWhenHidden(True)
dpo_settings_button.setSizePolicy(size_retain)
dpo_settings_button.setIcon(QIcon('icons/gear.jpg'))
dpo_widget.enterEvent = lambda event: on_enter(
    event, dpo_widget, dpo_settings_button)
dpo_widget.leaveEvent = lambda event: on_exit(
    event, dpo_widget, dpo_settings_button)
def dpo_button_clicked():
    wnd = QDialog(widget)
    wnd.setWindowTitle("Trix Indicator")
    wnd.setLayout(QVBoxLayout())
    period_widget = QWidget()
    period_widget.setLayout(QHBoxLayout())
    period_label = QLabel("Period")
    period_spinbox = QSpinBox()
    period_spinbox.setValue(selected_ta[get_indicator_index(
        "ta.trend.dpo")][2][0] if dpo_checkbox.isChecked() else 20)
    period_widget.layout().addWidget(period_label)
    period_widget.layout().addWidget(period_spinbox)
    wnd.layout().addWidget(period_widget)
    defaults_button = QPushButton("Reset to Defaults")
    defaults_button.setStyleSheet(SETTINGS_DIALOG_BUTTON_STYLESHEET)
    defaults_button.clicked.connect(lambda: period_spinbox.setValue(20))
    cancel_button = QPushButton("Cancel")
    cancel_button.setStyleSheet(SETTINGS_DIALOG_BUTTON_STYLESHEET)
    cancel_button.clicked.connect(lambda: wnd.done(0))
    ok_button = QPushButton(
        "Save" if dpo_checkbox.isChecked() else "Save and Add")
    ok_button.setStyleSheet(SETTINGS_DIALOG_BUTTON_STYLESHEET)
    def ok_button_clicked():
        if (dpo_checkbox.isChecked()):
            selected_ta[get_indicator_index("ta.trend.dpo")] = (
                "ta.trend.dpo", dpo_panel_combobox.currentIndex(), [period_spinbox.value()])
        else:
            selected_ta.append(
                ("ta.trend.dpo", dpo_panel_combobox.currentIndex(), [period_spinbox.value()]))
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
    lambda: selected_ta.append(("ta.trend.dpo", dpo_panel_combobox.currentIndex(
    ))) if dpo_checkbox.isChecked() else removeIndicator("ta.trend.dpo")
)
dpo_widget.layout().addWidget(dpo_checkbox)
trend_widget.layout().addWidget(dpo_widget)
# add kst oscillator to trend indicator scrollable
kst_widget = QWidget()
kst_widget.setLayout(QHBoxLayout())
kst_label = QLabel()
kst_label.setText("KST Oscillator")
kst_widget.layout().addWidget(kst_label)
kst_widget.setAutoFillBackground(False)
kst_panel_combobox = QComboBox()
kst_panel_combobox.addItems(ta_combobox_items)
kst_panel_combobox.currentTextChanged.connect(
    lambda state: change_indicator_panel(
        "ta.trend.KSTIndicator", state, selected_ta[get_indicator_index("ta.trend.KSTIndicator")][2]
    ) if kst_checkbox.isChecked() else None
)
kst_widget.layout().addWidget(kst_panel_combobox)
kst_settings_button = QPushButton()
kst_settings_button.setVisible(False)
size_retain = kst_settings_button.sizePolicy()
size_retain.setRetainSizeWhenHidden(True)
kst_settings_button.setSizePolicy(size_retain)
kst_settings_button.setIcon(QIcon('icons/gear.jpg'))
kst_widget.enterEvent = lambda event: on_enter(
    event, kst_widget, kst_settings_button)
kst_widget.leaveEvent = lambda event: on_exit(
    event, kst_widget, kst_settings_button)
def kst_button_clicked():
    wnd = QDialog(widget)
    wnd.setWindowTitle("KST Oscillator")
    wnd.setLayout(QVBoxLayout())
    roc1_widget = QWidget()
    roc1_widget.setLayout(QHBoxLayout())
    roc1_label = QLabel("Rate of Change 1 Length")
    roc1_spinbox = QSpinBox()
    roc1_spinbox.setValue(selected_ta[get_indicator_index(
        "ta.trend.KSTIndicator")][2][0] if kst_checkbox.isChecked() else 10)
    roc1_widget.layout().addWidget(roc1_label)
    roc1_widget.layout().addWidget(roc1_spinbox)
    wnd.layout().addWidget(roc1_widget)
    roc2_widget = QWidget()
    roc2_widget.setLayout(QHBoxLayout())
    roc2_label = QLabel("Rate of Chnage 2 Length")
    roc2_spinbox = QSpinBox()
    roc2_spinbox.setValue(selected_ta[get_indicator_index(
        "ta.trend.KSTIndicator")][2][1] if kst_checkbox.isChecked() else 15)
    roc2_widget.layout().addWidget(roc2_label)
    roc2_widget.layout().addWidget(roc2_spinbox)
    wnd.layout().addWidget(roc2_widget)
    roc3_widget = QWidget()
    roc3_widget.setLayout(QHBoxLayout())
    roc3_label = QLabel("Rate of Change 3 Length")
    roc3_spinbox = QSpinBox()
    roc3_spinbox.setValue(selected_ta[get_indicator_index(
        "ta.trend.KSTIndicator")][2][2] if kst_checkbox.isChecked() else 20)
    roc3_widget.layout().addWidget(roc3_label)
    roc3_widget.layout().addWidget(roc3_spinbox)
    wnd.layout().addWidget(roc3_widget)
    roc4_widget = QWidget()
    roc4_widget.setLayout(QHBoxLayout())
    roc4_label = QLabel("Rate of Change 4 Length")
    roc4_spinbox = QSpinBox()
    roc4_spinbox.setValue(selected_ta[get_indicator_index(
        "ta.trend.KSTIndicator")][2][3] if kst_checkbox.isChecked() else 30)
    roc4_widget.layout().addWidget(roc4_label)
    roc4_widget.layout().addWidget(roc4_spinbox)
    wnd.layout().addWidget(roc4_widget)
    sma1_widget = QWidget()
    sma1_widget.setLayout(QHBoxLayout())
    sma1_label = QLabel("Simple Moving Average 1 Length")
    sma1_spinbox = QSpinBox()
    sma1_spinbox.setValue(selected_ta[get_indicator_index(
        "ta.trend.KSTIndicator")][2][4] if kst_checkbox.isChecked() else 10)
    sma1_widget.layout().addWidget(sma1_label)
    sma1_widget.layout().addWidget(sma1_spinbox)
    wnd.layout().addWidget(sma1_widget)
    sma2_widget = QWidget()
    sma2_widget.setLayout(QHBoxLayout())
    sma2_label = QLabel("Simple Moving Average 2 Length")
    sma2_spinbox = QSpinBox()
    sma2_spinbox.setValue(selected_ta[get_indicator_index(
        "ta.trend.KSTIndicator")][2][5] if kst_checkbox.isChecked() else 10)
    sma2_widget.layout().addWidget(sma2_label)
    sma2_widget.layout().addWidget(sma2_spinbox)
    wnd.layout().addWidget(sma2_widget)
    sma3_widget = QWidget()
    sma3_widget.setLayout(QHBoxLayout())
    sma3_label = QLabel("Simple Moving Average 3 Length")
    sma3_spinbox = QSpinBox()
    sma3_spinbox.setValue(selected_ta[get_indicator_index(
        "ta.trend.KSTIndicator")][2][6] if kst_checkbox.isChecked() else 10)
    sma3_widget.layout().addWidget(sma3_label)
    sma3_widget.layout().addWidget(sma3_spinbox)
    wnd.layout().addWidget(sma3_widget)
    sma4_widget = QWidget()
    sma4_widget.setLayout(QHBoxLayout())
    sma4_label = QLabel("Simple Moving Average 4 Length")
    sma4_spinbox = QSpinBox()
    sma4_spinbox.setValue(selected_ta[get_indicator_index(
        "ta.trend.KSTIndicator")][2][7] if kst_checkbox.isChecked() else 15)
    sma4_widget.layout().addWidget(sma4_label)
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
    defaults_button.setStyleSheet(SETTINGS_DIALOG_BUTTON_STYLESHEET)
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
    cancel_button.setStyleSheet(SETTINGS_DIALOG_BUTTON_STYLESHEET)
    cancel_button.clicked.connect(lambda: wnd.done(0))
    ok_button = QPushButton(
        "Save" if kst_checkbox.isChecked() else "Save and Add")
    ok_button.setStyleSheet(SETTINGS_DIALOG_BUTTON_STYLESHEET)
    def ok_button_clicked():
        if kst_checkbox.isChecked():
            selected_ta[get_indicator_index("ta.trend.KSTIndicator")] = ("ta.trend.KSTIndicator",
                                                                            kst_panel_combobox.currentIndex(),
                                                                            [
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
                                                                        )
        else:
            selected_ta.append(("ta.trend.KSTIndicator", kst_panel_combobox.currentIndex(),
                                [roc1_spinbox.value(), roc2_spinbox.value(), roc3_spinbox.value(), roc4_spinbox.value(), sma1_spinbox.value(), sma2_spinbox.value(), sma3_spinbox.value(), sma4_spinbox.value(), signal_spinbox.value()]))
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
    lambda: selected_ta.append(("ta.trend.KSTIndicator", kst_panel_combobox.currentIndex(
    ))) if kst_checkbox.isChecked() else removeIndicator("ta.trend.KSTIndicator")
)
kst_widget.layout().addWidget(kst_checkbox)
trend_widget.layout().addWidget(kst_widget)
# add ichimoku to trend indicator scrollable
ichimoku_widget = QWidget()
ichimoku_widget.setLayout(QHBoxLayout())
ichimoku_label = QLabel()
ichimoku_label.setText("Ichimoku Cloud")
ichimoku_widget.layout().addWidget(ichimoku_label)
ichimoku_label.setAutoFillBackground(False)
ichimoku_panel_combobox = QComboBox()
ichimoku_panel_combobox.addItems(ta_combobox_items)
ichimoku_panel_combobox.currentTextChanged.connect(lambda state: change_indicator_panel(
    "ta.trend.IchimokuIndicator", state, selected_ta[get_indicator_index("ta.trend.IchimokuIndicator")][2]) if ichimoku_checkbox.isChecked() else None)
ichimoku_widget.layout().addWidget(ichimoku_panel_combobox)
ichimoku_settings_button = QPushButton()
ichimoku_settings_button.setVisible(False)
size_retain = ichimoku_settings_button.sizePolicy()
size_retain.setRetainSizeWhenHidden(True)
ichimoku_settings_button.setSizePolicy(size_retain)
ichimoku_settings_button.setIcon(QIcon('icons/gear.jpg'))
ichimoku_widget.enterEvent = lambda event: on_enter(
    event, ichimoku_widget, ichimoku_settings_button)
ichimoku_widget.leaveEvent = lambda event: on_exit(
    event, ichimoku_widget, ichimoku_settings_button)
def ichimoku_button_clicked():
    wnd = QDialog(widget)
    wnd.setWindowTitle("Schaff Indicator")
    wnd.setLayout(QVBoxLayout())
    low_period_widget = QWidget()
    low_period_widget.setLayout(QHBoxLayout())
    low_period_label = QLabel("MACD Slow Period")
    low_period_spinbox = QSpinBox()
    low_period_spinbox.setValue(selected_ta[get_indicator_index(
        "ta.trend.IchimokuIndicator")][2][0] if ichimoku_checkbox.isChecked() else 9)
    low_period_widget.layout().addWidget(low_period_label)
    low_period_widget.layout().addWidget(low_period_spinbox)
    wnd.layout().addWidget(low_period_widget)
    med_period_widget = QWidget()
    med_period_widget.setLayout(QHBoxLayout())
    med_period_label = QLabel("MACD Fast Period")
    med_period_spinbox = QSpinBox()
    med_period_spinbox.setValue(selected_ta[get_indicator_index(
        "ta.trend.IchimokuIndicator")][2][1] if ichimoku_checkbox.isChecked() else 26)
    med_period_widget.layout().addWidget(med_period_label)
    med_period_widget.layout().addWidget(med_period_spinbox)
    wnd.layout().addWidget(med_period_widget)
    high_period_widget = QWidget()
    high_period_widget.setLayout(QHBoxLayout())
    high_period_label = QLabel("Cycles")
    high_period_spinbox = QSpinBox()
    high_period_spinbox.setValue(selected_ta[get_indicator_index(
        "ta.trend.IchimokuIndicator")][2][2] if ichimoku_checkbox.isChecked() else 52)
    high_period_widget.layout().addWidget(high_period_label)
    high_period_widget.layout().addWidget(high_period_spinbox)
    wnd.layout().addWidget(high_period_widget)
    shift_widget = QWidget()
    shift_widget.setLayout(QHBoxLayout())
    shift_label = QLabel("Shift Medium")
    shift_checkbox = QCheckBox()
    shift_checkbox.setChecked(selected_ta[get_indicator_index(
        "ta.trend.IchimokuIndicator")][2][3] if ichimoku_checkbox.isChecked() else False)
    shift_widget.layout().addWidget(shift_label)
    shift_widget.layout().addWidget(shift_checkbox)
    wnd.layout().addWidget(shift_widget)
    defaults_button = QPushButton("Reset to Defaults")
    defaults_button.setStyleSheet(SETTINGS_DIALOG_BUTTON_STYLESHEET)
    def restore_defaults():
        low_period_spinbox.setValue(9)
        med_period_spinbox.setValue(26)
        high_period_spinbox.setValue(52)
        shift_checkbox.setChecked(False)
    defaults_button.clicked.connect(restore_defaults)
    cancel_button = QPushButton("Cancel")
    cancel_button.setStyleSheet(SETTINGS_DIALOG_BUTTON_STYLESHEET)
    cancel_button.clicked.connect(lambda: wnd.done(0))
    ok_button = QPushButton(
        "Save" if ichimoku_checkbox.isChecked() else "Save and Add")
    ok_button.setStyleSheet(SETTINGS_DIALOG_BUTTON_STYLESHEET)
    def ok_button_clicked():
        if (ichimoku_checkbox.isChecked()):
            selected_ta[get_indicator_index("ta.trend.IchimokuIndicator")] = ("ta.trend.IchimokuIndicator", ichimoku_panel_combobox.currentIndex(), [
                low_period_spinbox.value(), med_period_spinbox.value(), high_period_spinbox.value(), shift_checkbox.isChecked()])
        else:
            selected_ta.append(("ta.trend.IchimokuIndicator", ichimoku_panel_combobox.currentIndex(), [
                               low_period_spinbox.value(), med_period_spinbox.value(), high_period_spinbox.value(), shift_checkbox.isChecked()]))
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
    lambda: selected_ta.append(("ta.trend.IchimokuIndicator", ichimoku_panel_combobox.currentIndex(
    ))) if ichimoku_checkbox.isChecked() else removeIndicator("ta.trend.IchimokuIndicator")
)
ichimoku_widget.layout().addWidget(ichimoku_checkbox)
trend_widget.layout().addWidget(ichimoku_widget)
# add mass index to trend indicator scrollable
mi_widget = QWidget()
mi_widget.setLayout(QHBoxLayout())
mi_label = QLabel()
mi_label.setText("Mass Index")
mi_widget.layout().addWidget(mi_label)
mi_label.setAutoFillBackground(False)
mi_panel_combobox = QComboBox()
mi_panel_combobox.addItems(ta_combobox_items)
mi_panel_combobox.currentTextChanged.connect(lambda state: change_indicator_panel(
    "ta.trend.mass_index", state, selected_ta[get_indicator_index("ta.trend.mass_index")][2]) if mi_checkbox.isChecked() else None)
mi_widget.layout().addWidget(mi_panel_combobox)
mi_settings_button = QPushButton()
mi_settings_button.setVisible(False)
size_retain = mi_settings_button.sizePolicy()
size_retain.setRetainSizeWhenHidden(True)
mi_settings_button.setSizePolicy(size_retain)
mi_settings_button.setIcon(QIcon('icons/gear.jpg'))
mi_widget.enterEvent = lambda event: on_enter(
    event, mi_widget, mi_settings_button)
mi_widget.leaveEvent = lambda event: on_exit(
    event, mi_widget, mi_settings_button)
def mi_button_clicked():
    wnd = QDialog(widget)
    wnd.setWindowTitle("Mass Index")
    wnd.setLayout(QVBoxLayout())
    fast_period_widget = QWidget()
    fast_period_widget.setLayout(QHBoxLayout())
    fast_period_label = QLabel("Fast Period")
    fast_period_spinbox = QSpinBox()
    fast_period_spinbox.setValue(selected_ta[get_indicator_index(
        "ta.trend.mass_index")][2][0] if mi_checkbox.isChecked() else 9)
    fast_period_widget.layout().addWidget(fast_period_label)
    fast_period_widget.layout().addWidget(fast_period_spinbox)
    wnd.layout().addWidget(fast_period_widget)
    slow_period_widget = QWidget()
    slow_period_widget.setLayout(QHBoxLayout())
    slow_period_label = QLabel("Slow Period")
    slow_period_spinbox = QSpinBox()
    slow_period_spinbox.setValue(selected_ta[get_indicator_index(
        "ta.trend.mass_index")][2][1] if mi_checkbox.isChecked() else 25)
    slow_period_widget.layout().addWidget(slow_period_label)
    slow_period_widget.layout().addWidget(slow_period_spinbox)
    wnd.layout().addWidget(slow_period_widget)
    defaults_button = QPushButton("Reset to Defaults")
    defaults_button.setStyleSheet(SETTINGS_DIALOG_BUTTON_STYLESHEET)
    def restore_defaults():
        fast_period_spinbox.setValue(9)
        slow_period_spinbox.setValue(25)
    defaults_button.clicked.connect(restore_defaults)
    cancel_button = QPushButton("Cancel")
    cancel_button.setStyleSheet(SETTINGS_DIALOG_BUTTON_STYLESHEET)
    cancel_button.clicked.connect(lambda: wnd.done(0))
    ok_button = QPushButton(
        "Save" if mi_checkbox.isChecked() else "Save and Add")
    ok_button.setStyleSheet(SETTINGS_DIALOG_BUTTON_STYLESHEET)
    def ok_button_clicked():
        if (mi_checkbox.isChecked()):
            selected_ta[get_indicator_index("ta.trend.mass_index")] = ("ta.trend.mass_index", mi_panel_combobox.currentIndex(), [
                fast_period_spinbox.value(), slow_period_spinbox.value()])
        else:
            selected_ta.append(("ta.trend.mass_index", mi_panel_combobox.currentIndex(), [
                               fast_period_spinbox.value(), slow_period_spinbox.value()]))
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
    lambda: selected_ta.append(("ta.trend.mass_index", mi_panel_combobox.currentIndex(
    ))) if mi_checkbox.isChecked() else removeIndicator("ta.trend.mass_index")
)
mi_widget.layout().addWidget(mi_checkbox)
trend_widget.layout().addWidget(mi_widget)
# add schaff to trend indicator scrollable
schaff_widget = QWidget()
schaff_widget.setLayout(QHBoxLayout())
schaff_label = QLabel()
schaff_label.setText("Schaff Trend Cycle")
schaff_widget.layout().addWidget(schaff_label)
schaff_label.setAutoFillBackground(False)
schaff_panel_combobox = QComboBox()
schaff_panel_combobox.addItems(ta_combobox_items)
schaff_panel_combobox.currentTextChanged.connect(lambda state: change_indicator_panel(
    "ta.trend.stc", state, selected_ta[get_indicator_index("ta.trend.stc")][2]) if schaff_checkbox.isChecked() else None)
schaff_widget.layout().addWidget(schaff_panel_combobox)
schaff_settings_button = QPushButton()
schaff_settings_button.setVisible(False)
size_retain = schaff_settings_button.sizePolicy()
size_retain.setRetainSizeWhenHidden(True)
schaff_settings_button.setSizePolicy(size_retain)
schaff_settings_button.setIcon(QIcon('icons/gear.jpg'))
schaff_widget.enterEvent = lambda event: on_enter(
    event, schaff_widget, schaff_settings_button)
schaff_widget.leaveEvent = lambda event: on_exit(
    event, schaff_widget, schaff_settings_button)
def schaff_button_clicked():
    wnd = QDialog(widget)
    wnd.setWindowTitle("Schaff Indicator")
    wnd.setLayout(QVBoxLayout())
    macd_slow_widget = QWidget()
    macd_slow_widget.setLayout(QHBoxLayout())
    macd_slow_label = QLabel("MACD Slow Period")
    macd_slow_spinbox = QSpinBox()
    macd_slow_spinbox.setValue(selected_ta[get_indicator_index(
        "ta.trend.stc")][2][0] if schaff_checkbox.isChecked() else 50)
    macd_slow_widget.layout().addWidget(macd_slow_label)
    macd_slow_widget.layout().addWidget(macd_slow_spinbox)
    wnd.layout().addWidget(macd_slow_widget)
    macd_fast_widget = QWidget()
    macd_fast_widget.setLayout(QHBoxLayout())
    macd_fast_label = QLabel("MACD Fast Period")
    macd_fast_spinbox = QSpinBox()
    macd_fast_spinbox.setValue(selected_ta[get_indicator_index(
        "ta.trend.stc")][2][1] if schaff_checkbox.isChecked() else 23)
    macd_fast_widget.layout().addWidget(macd_fast_label)
    macd_fast_widget.layout().addWidget(macd_fast_spinbox)
    wnd.layout().addWidget(macd_fast_widget)
    cycle_widget = QWidget()
    cycle_widget.setLayout(QHBoxLayout())
    cycle_label = QLabel("Cycles")
    cycle_spinbox = QSpinBox()
    cycle_spinbox.setValue(selected_ta[get_indicator_index(
        "ta.trend.stc")][2][2] if schaff_checkbox.isChecked() else 10)
    cycle_widget.layout().addWidget(cycle_label)
    cycle_widget.layout().addWidget(cycle_spinbox)
    wnd.layout().addWidget(cycle_widget)
    length1_widget = QWidget()
    length1_widget.setLayout(QHBoxLayout())
    length1_label = QLabel("First %D Length")
    length1_spinbox = QSpinBox()
    length1_spinbox.setValue(selected_ta[get_indicator_index(
        "ta.trend.stc")][2][3] if schaff_checkbox.isChecked() else 3)
    length1_widget.layout().addWidget(length1_label)
    length1_widget.layout().addWidget(length1_spinbox)
    wnd.layout().addWidget(length1_widget)
    length2_widget = QWidget()
    length2_widget.setLayout(QHBoxLayout())
    length2_label = QLabel("Second %D Length")
    length2_spinbox = QSpinBox()
    length2_spinbox.setValue(selected_ta[get_indicator_index(
        "ta.trend.stc")][2][4] if schaff_checkbox.isChecked() else 3)
    length2_widget.layout().addWidget(length2_label)
    length2_widget.layout().addWidget(length2_spinbox)
    wnd.layout().addWidget(length2_widget)
    defaults_button = QPushButton("Reset to Defaults")
    defaults_button.setStyleSheet(SETTINGS_DIALOG_BUTTON_STYLESHEET)
    def restore_defaults():
        macd_slow_spinbox.setValue(50)
        macd_fast_spinbox.setValue(23)
        cycle_spinbox.setValue(10)
        length1_spinbox.setValue(3)
        length2_spinbox.setValue(3)
    defaults_button.clicked.connect(restore_defaults)
    cancel_button = QPushButton("Cancel")
    cancel_button.setStyleSheet(SETTINGS_DIALOG_BUTTON_STYLESHEET)
    cancel_button.clicked.connect(lambda: wnd.done(0))
    ok_button = QPushButton(
        "Save" if schaff_checkbox.isChecked() else "Save and Add")
    ok_button.setStyleSheet(SETTINGS_DIALOG_BUTTON_STYLESHEET)
    def ok_button_clicked():
        if (schaff_checkbox.isChecked()):
            selected_ta[get_indicator_index("ta.trend.stc")] = ("ta.trend.stc", schaff_panel_combobox.currentIndex(),
                                                                [macd_slow_spinbox.value(), macd_fast_spinbox.value(), cycle_spinbox.value(), length1_spinbox.value(), length2_spinbox.value()])
        else:
            selected_ta.append(("ta.trend.stc", schaff_panel_combobox.currentIndex(),
                                [macd_slow_spinbox.value(), macd_fast_spinbox.value(), cycle_spinbox.value(), length1_spinbox.value(), length2_spinbox.value()]))
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
    lambda: selected_ta.append(("ta.trend.stc", schaff_panel_combobox.currentIndex(
    ))) if schaff_checkbox.isChecked() else removeIndicator("ta.trend.stc")
)
schaff_widget.layout().addWidget(schaff_checkbox)
trend_widget.layout().addWidget(schaff_widget)
# add trix indicator to trend indicator scrollable
trix_widget = QWidget()
trix_widget.setLayout(QHBoxLayout())
trix_label = QLabel()
trix_label.setText("Trix Indicator")
trix_widget.layout().addWidget(trix_label)
trix_label.setAutoFillBackground(False)
trix_panel_combobox = QComboBox()
trix_panel_combobox.addItems(ta_combobox_items)
trix_panel_combobox.currentTextChanged.connect(lambda state: change_indicator_panel(
    "ta.trend.trix", state, selected_ta[get_indicator_index("ta.trend.trix")][2]) if trix_checkbox.isChecked() else None)
trix_widget.layout().addWidget(trix_panel_combobox)
trix_settings_button = QPushButton()
trix_settings_button.setVisible(False)
size_retain = trix_settings_button.sizePolicy()
size_retain.setRetainSizeWhenHidden(True)
trix_settings_button.setSizePolicy(size_retain)
trix_settings_button.setIcon(QIcon('icons/gear.jpg'))
trix_widget.enterEvent = lambda event: on_enter(
    event, trix_widget, trix_settings_button)
trix_widget.leaveEvent = lambda event: on_exit(
    event, trix_widget, trix_settings_button)
def trix_button_clicked():
    wnd = QDialog(widget)
    wnd.setWindowTitle("Trix Indicator")
    wnd.setLayout(QVBoxLayout())
    period_widget = QWidget()
    period_widget.setLayout(QHBoxLayout())
    period_label = QLabel("Period")
    period_spinbox = QSpinBox()
    period_spinbox.setValue(selected_ta[get_indicator_index(
        "ta.trend.trix")][2][0] if trix_checkbox.isChecked() else 15)
    period_widget.layout().addWidget(period_label)
    period_widget.layout().addWidget(period_spinbox)
    wnd.layout().addWidget(period_widget)
    defaults_button = QPushButton("Reset to Defaults")
    defaults_button.setStyleSheet(SETTINGS_DIALOG_BUTTON_STYLESHEET)
    defaults_button.clicked.connect(lambda: period_spinbox.setValue(14))
    cancel_button = QPushButton("Cancel")
    cancel_button.setStyleSheet(SETTINGS_DIALOG_BUTTON_STYLESHEET)
    cancel_button.clicked.connect(lambda: wnd.done(0))
    ok_button = QPushButton(
        "Save" if trix_checkbox.isChecked() else "Save and Add")
    ok_button.setStyleSheet(SETTINGS_DIALOG_BUTTON_STYLESHEET)
    def ok_button_clicked():
        if (trix_checkbox.isChecked()):
            selected_ta[get_indicator_index("ta.trend.trix")] = (
                "ta.trend.trix", trix_panel_combobox.currentIndex(), [period_spinbox.value()])
        else:
            selected_ta.append(
                ("ta.trend.trix", trix_panel_combobox.currentIndex(), [period_spinbox.value()]))
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
    lambda: selected_ta.append(("ta.trend.trix", trix_panel_combobox.currentIndex(
    ), 15)) if trix_checkbox.isChecked() else removeIndicator("ta.trend.trix")
)
trix_widget.layout().addWidget(trix_checkbox)
trend_widget.layout().addWidget(trix_widget)
# add parabolic sar to trend indicator scrollable
psar_widget = QWidget()
psar_widget.setLayout(QHBoxLayout())
psar_label = QLabel()
psar_label.setText("Parabolic SAR")
psar_widget.layout().addWidget(psar_label)
psar_label.setAutoFillBackground(False)
psar_panel_combobox = QComboBox()
psar_panel_combobox.addItems(ta_combobox_items)
psar_panel_combobox.currentTextChanged.connect(lambda state: change_indicator_panel(
    "ta.trend.PSARIndicator", state, selected_ta[get_indicator_index("ta.trend.PSARIndicator")][2]) if psar_checkbox.isChecked() else None)
psar_widget.layout().addWidget(psar_panel_combobox)
psar_settings_button = QPushButton()
psar_settings_button.setVisible(False)
size_retain = psar_settings_button.sizePolicy()
size_retain.setRetainSizeWhenHidden(True)
psar_settings_button.setSizePolicy(size_retain)
psar_settings_button.setIcon(QIcon('icons/gear.jpg'))
psar_widget.enterEvent = lambda event: on_enter(
    event, psar_widget, psar_settings_button)
psar_widget.leaveEvent = lambda event: on_exit(
    event, psar_widget, psar_settings_button)
def psar_button_clicked():
    wnd = QDialog(widget)
    wnd.setWindowTitle("Parabolic SAR")
    wnd.setLayout(QVBoxLayout())
    acc_fac_widget = QWidget()
    acc_fac_widget.setLayout(QHBoxLayout())
    acc_fac_label = QLabel("Acceleration Factor")
    acc_fac_spinbox = QDoubleSpinBox()
    acc_fac_spinbox.setValue(selected_ta[get_indicator_index(
        "ta.trend.PSARIndicator")][2][0] if psar_checkbox.isChecked() else .02)
    acc_fac_widget.layout().addWidget(acc_fac_label)
    acc_fac_widget.layout().addWidget(acc_fac_spinbox)
    wnd.layout().addWidget(acc_fac_widget)
    max_acc_fac_widget = QWidget()
    max_acc_fac_widget.setLayout(QHBoxLayout())
    max_acc_fac_label = QLabel("Maximum Acceleration Factor")
    max_acc_fac_spinbox = QDoubleSpinBox()
    max_acc_fac_spinbox.setValue(selected_ta[get_indicator_index(
        "ta.trend.PSARIndicator")][2][1] if psar_checkbox.isChecked() else .2)
    max_acc_fac_widget.layout().addWidget(max_acc_fac_label)
    max_acc_fac_widget.layout().addWidget(max_acc_fac_spinbox)
    wnd.layout().addWidget(max_acc_fac_widget)
    defaults_button = QPushButton("Reset to Defaults")
    defaults_button.setStyleSheet(SETTINGS_DIALOG_BUTTON_STYLESHEET)
    def restore_defaults():
        acc_fac_spinbox.setValue(.02)
        max_acc_fac_spinbox.setValue(.2)
    defaults_button.clicked.connect(restore_defaults)
    cancel_button = QPushButton("Cancel")
    cancel_button.setStyleSheet(SETTINGS_DIALOG_BUTTON_STYLESHEET)
    cancel_button.clicked.connect(lambda: wnd.done(0))
    ok_button = QPushButton(
        "Save" if psar_checkbox.isChecked() else "Save and Add")
    ok_button.setStyleSheet(SETTINGS_DIALOG_BUTTON_STYLESHEET)
    def ok_button_clicked():
        if (psar_checkbox.isChecked()):
            selected_ta[get_indicator_index("ta.trend.PSARIndicator")] = (
                "ta.trend.PSARIndicator", psar_panel_combobox.currentIndex(), [acc_fac_spinbox.value(), max_acc_fac_spinbox.value()])
        else:
            selected_ta.append(("ta.trend.PSARIndicator", psar_panel_combobox.currentIndex(), [
                               acc_fac_spinbox.value(), max_acc_fac_spinbox.value()]))
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
    lambda: selected_ta.append(("ta.trend.PSARIndicator", psar_panel_combobox.currentIndex(
    ), [.02, .2])) if psar_checkbox.isChecked() else removeIndicator("ta.trend.PSARIndicator")
)
psar_widget.layout().addWidget(psar_checkbox)
trend_widget.layout().addWidget(psar_widget)
# add vortex to trend indicator scrollable
vortex_widget = QWidget()
vortex_widget.setLayout(QHBoxLayout())
vortex_label = QLabel()
vortex_label.setText("Vortex Indicator")
vortex_widget.layout().addWidget(vortex_label)
vortex_label.setAutoFillBackground(False)
vortex_panel_combobox = QComboBox()
vortex_panel_combobox.addItems(ta_combobox_items)
vortex_panel_combobox.currentTextChanged.connect(lambda state: change_indicator_panel(
    "ta.trend.VortexIndicator", state, selected_ta[get_indicator_index("ta.trend.VortexIndicator")][2]) if vortex_checkbox.isChecked() else None)
vortex_widget.layout().addWidget(vortex_panel_combobox)
vortex_settings_button = QPushButton()
vortex_settings_button.setVisible(False)
size_retain = vortex_settings_button.sizePolicy()
size_retain.setRetainSizeWhenHidden(True)
vortex_settings_button.setSizePolicy(size_retain)
vortex_settings_button.setIcon(QIcon('icons/gear.jpg'))
vortex_widget.enterEvent = lambda event: on_enter(
    event, vortex_widget, vortex_settings_button)
vortex_widget.leaveEvent = lambda event: on_exit(
    event, vortex_widget, vortex_settings_button)
def vortex_button_clicked():
    wnd = QDialog(widget)
    wnd.setWindowTitle("Vortex Indicator")
    wnd.setLayout(QVBoxLayout())
    period_widget = QWidget()
    period_widget.setLayout(QHBoxLayout())
    period_label = QLabel("Period")
    period_spinbox = QSpinBox()
    period_spinbox.setValue(selected_ta[get_indicator_index(
        "ta.trend.VortexIndicator")][2][0] if vortex_checkbox.isChecked() else 14)
    period_widget.layout().addWidget(period_label)
    period_widget.layout().addWidget(period_spinbox)
    wnd.layout().addWidget(period_widget)
    defaults_button = QPushButton("Reset to Defaults")
    defaults_button.setStyleSheet(SETTINGS_DIALOG_BUTTON_STYLESHEET)
    defaults_button.clicked.connect(lambda: period_spinbox.setValue(14))
    cancel_button = QPushButton("Cancel")
    cancel_button.setStyleSheet(SETTINGS_DIALOG_BUTTON_STYLESHEET)
    cancel_button.clicked.connect(lambda: wnd.done(0))
    ok_button = QPushButton(
        "Save" if vortex_checkbox.isChecked() else "Save and Add")
    ok_button.setStyleSheet(SETTINGS_DIALOG_BUTTON_STYLESHEET)
    def ok_button_clicked():
        if (vortex_checkbox.isChecked()):
            selected_ta[get_indicator_index("ta.trend.VortexIndicator")] = (
                "ta.trend.VortexIndicator", vortex_panel_combobox.currentIndex(), [period_spinbox.value()])
        else:
            selected_ta.append(("ta.trend.VortexIndicator", vortex_panel_combobox.currentIndex(), [
                               period_spinbox.value()]))
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
    lambda: selected_ta.append(("ta.trend.VortexIndicator", vortex_panel_combobox.currentIndex(
    ), [14])) if vortex_checkbox.isChecked() else removeIndicator("ta.trend.VortexIndicator")
)
vortex_widget.layout().addWidget(vortex_checkbox)
trend_widget.layout().addWidget(vortex_widget)
# create moving average indicator scrollable
technical_indicators_dialog.ma_groupbox = QGroupBox(
    technical_indicators_dialog)
technical_indicators_dialog.ma_groupbox.setTitle("Moving Averages")
technical_indicators_dialog.ma_groupbox.setGeometry(630, 10, 300, 620)
technical_indicators_dialog.ma_groupbox.setStyleSheet(
    'background-color: white')
technical_indicators_dialog.ma_groupbox.ma_scrollarea = QScrollArea(
    technical_indicators_dialog.ma_groupbox)
technical_indicators_dialog.ma_groupbox.ma_scrollarea.setGeometry(
    10, 20, 280, 600)
ma_widget = QWidget()
ma_widget.resize(280, 1500)
ma_widget.setLayout(QVBoxLayout())
technical_indicators_dialog.ma_groupbox.ma_scrollarea.setWidget(ma_widget)
technical_indicators_dialog.ma_groupbox.ma_scrollarea.setVerticalScrollBarPolicy(
    Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
chart_dialog.addTab(chart_configurations, "Chart Configurations")
chart_dialog.addTab(technical_indicators_dialog, "Technical Indicators")
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
stockinfo_dialog_main.search_bar_groupbox = QGroupBox(
    stockinfo_dialog_main)
stockinfo_dialog_main.search_bar_groupbox.setStyleSheet(
    'background-color: white;')
stockinfo_dialog_main.search_bar_groupbox.setTitle("Find a Stock")
stockinfo_dialog_main.search_bar_groupbox.setGeometry(10, 10, 960, 70)
stockinfo_dialog_main.search_bar_groupbox.searchBar = QLineEdit(
    stockinfo_dialog_main.search_bar_groupbox)
stockinfo_dialog_main.search_bar_groupbox.searchBar.setGeometry(
    10, 20, 850, 40)
stockinfo_dialog_main.search_bar_groupbox.searchBar.textChanged.connect(
    lambda txt: searchTextChanged(txt))
stockinfo_dialog_main.search_bar_groupbox.searchBar.setFont(
    QFont('arial', 10))
stockinfo_dialog_main.search_bar_groupbox.searchBar.setCompleter(completer)
stockinfo_dialog_main.search_bar_groupbox.search_button = QPushButton(
    stockinfo_dialog_main.search_bar_groupbox)
stockinfo_dialog_main.search_bar_groupbox.search_button.setGeometry(
    870, 20, 80, 40)
stockinfo_dialog_main.search_bar_groupbox.search_button.setText(
    "Show Info")
stockinfo_dialog_main.search_bar_groupbox.search_button.clicked.connect(
    lambda: stockinfo_searchbar_click(stockinfo_dialog_main))
stockinfo_dialog_main.asset_info_groupbox = QGroupBox(
    stockinfo_dialog_main)
stockinfo_dialog_main.asset_info_groupbox.setStyleSheet(
    'background-color: white')
stockinfo_dialog_main.asset_info_groupbox.setTitle("Asset Profile")
stockinfo_dialog_main.asset_info_groupbox.setGeometry(10, 90, 310, 550)
stockinfo_dialog_main.asset_info_groupbox.setVisible(False)
stockinfo_dialog_main.asset_info_groupbox.content_container = QScrollArea(
    stockinfo_dialog_main.asset_info_groupbox)
assetinfo_scrollarea_widget = QWidget()
assetinfo_scrollarea_widget.resize(300, 800)
assetinfo_scrollarea_widget.setLayout(QVBoxLayout())
stockinfo_dialog_main.asset_info_groupbox.content_container.setWidget(
    assetinfo_scrollarea_widget)
stockinfo_dialog_main.asset_info_groupbox.content_container.setGeometry(
    5, 15, 305, 520)
stockinfo_dialog_main.asset_info_groupbox.content_container.setVerticalScrollBarPolicy(
    Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
stockinfo_dialog_main.about_groupbox = QGroupBox(stockinfo_dialog_main)
stockinfo_dialog_main.about_groupbox.setStyleSheet(
    'background-color: white')
stockinfo_dialog_main.about_groupbox.setTitle("About the Asset")
stockinfo_dialog_main.about_groupbox.setGeometry(330, 90, 470, 550)
stockinfo_dialog_main.about_groupbox.setVisible(False)
stockinfo_dialog_main.about_groupbox.content_container = QScrollArea(
    stockinfo_dialog_main.about_groupbox)
about_scrollarea_widget = QWidget()
about_scrollarea_widget.resize(400, 800)
about_scrollarea_widget.setLayout(QVBoxLayout())
stockinfo_dialog_main.about_groupbox.content_container.setWidget(
    about_scrollarea_widget
)
stockinfo_dialog_main.about_groupbox.content_container.setGeometry(
    5, 15, 420, 520)
stockinfo_dialog_main.about_groupbox.content_container.setVerticalScrollBarPolicy(
    Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
stockinfo_dialog_main.news_groupbox = QGroupBox(stockinfo_dialog_main)
stockinfo_dialog_main.news_groupbox.setStyleSheet(
    'background-color: white')
stockinfo_dialog_main.news_groupbox.setTitle("News")
stockinfo_dialog_main.news_groupbox.setGeometry(810, 90, 470, 550)
stockinfo_dialog_main.news_groupbox.setVisible(False)
stockinfo_dialog_main.news_groupbox.setLayout(QVBoxLayout())
stockinfo_dialog_recs = QDialog()
stockinfo_dialog_recs.setStyleSheet('background-color: deepskyblue')
stockinfo_dialog_recs.analyst_rec_groupbox = QGroupBox(
    stockinfo_dialog_recs)
stockinfo_dialog_recs.analyst_rec_groupbox.setStyleSheet(
    'background-color: white')
stockinfo_dialog_recs.analyst_rec_groupbox.setTitle(
    "Analyst Recommendations")
stockinfo_dialog_recs.analyst_rec_groupbox.setGeometry(10, 10, 310, 630)
stockinfo_dialog_recs.analyst_rec_groupbox.setVisible(False)
stockinfo_dialog_recs.analyst_rec_groupbox.setLayout(QVBoxLayout())
stockinfo_dialog_recs.iandi_groupbox = QGroupBox(stockinfo_dialog_recs)
stockinfo_dialog_recs.iandi_groupbox.setStyleSheet(
    'background-color: white')
stockinfo_dialog_recs.iandi_groupbox.setTitle("Insiders and Institutions")
stockinfo_dialog_recs.iandi_groupbox.setGeometry(330, 10, 470, 630)
stockinfo_dialog_recs.iandi_groupbox.setVisible(False)
stockinfo_dialog_recs.iandi_groupbox.setLayout(QVBoxLayout())
stockinfo_dialog_recs.mutfund_groupbox = QGroupBox(stockinfo_dialog_recs)
stockinfo_dialog_recs.mutfund_groupbox.setStyleSheet(
    'background-color: white')
stockinfo_dialog_recs.mutfund_groupbox.setTitle("Mutual Fund Holders")
stockinfo_dialog_recs.mutfund_groupbox.setGeometry(810, 10, 470, 630)
stockinfo_dialog_recs.mutfund_groupbox.setVisible(False)
stockinfo_dialog_recs.mutfund_groupbox.setLayout(QVBoxLayout())
stockinfo_dialog_forecasts = QDialog()
stockinfo_dialog_forecasts.setStyleSheet('background-color: deepskyblue')
stockinfo_dialog_forecasts.chart_groupbox = QGroupBox(
    stockinfo_dialog_forecasts)
stockinfo_dialog_forecasts.chart_groupbox.setTitle("Charts and Graphs")
stockinfo_dialog_forecasts.chart_groupbox.setGeometry(0, 0, 1300, 600)
stockinfo_dialog_forecasts.chart_groupbox.content_container = QScrollArea(
    stockinfo_dialog_forecasts)
prediction_chart_widget = QWidget()
prediction_chart_widget.resize(1300, 2000)
prediction_chart_widget.setLayout(QVBoxLayout())
stockinfo_dialog_forecasts.chart_groupbox.content_container.setWidget(
    prediction_chart_widget)
stockinfo_dialog_forecasts.chart_groupbox.content_container.setVerticalScrollBarPolicy(
    Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
stockinfo_dialog_forecasts.chart_groupbox.content_container.setGeometry(
    5, 15, 1290, 650)
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
qtr_earnings_table.setEditTriggers(
    QAbstractItemView.EditTrigger.NoEditTriggers)
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
stockinfo_dialog_financials.content_container = QScrollArea(
    stockinfo_dialog_financials)
financials_chart_widget = QWidget()
financials_chart_widget.resize(1300, 2000)
financials_chart_widget.setLayout(QVBoxLayout())
stockinfo_dialog_financials.content_container.setWidget(
    financials_chart_widget)
stockinfo_dialog_financials.content_container.setVerticalScrollBarPolicy(
    Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
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
financials_table.setEditTriggers(
    QAbstractItemView.EditTrigger.NoEditTriggers)
financials_table.setFont(QFont('arial', 10))
financials_table.setStyleSheet('background-color: white;')
stockinfo_dialog.addTab(stockinfo_dialog_main, "Overview")
stockinfo_dialog.addTab(stockinfo_dialog_recs, "Insiders and Institutions")
stockinfo_dialog.addTab(stockinfo_dialog_forecasts, "Forecasts")
stockinfo_dialog.addTab(stockinfo_dialog_financials, "Financials")
stockinfo_dialog.connect(stockinfo_dialog, SIGNAL(
    'currentChanged(int)'), lambda: stockinfo_dialog_changed(stockinfo_dialog.currentIndex()))
####################
# DCF model dialog #
####################
dcf_dialog = QDialog()
dcf_dialog.setStyleSheet('background-color: deepskyblue;')
dcf_dialog.search_bar_groupbox = QGroupBox(dcf_dialog)
dcf_dialog.search_bar_groupbox.setStyleSheet('background-color: white;')
dcf_dialog.search_bar_groupbox.setTitle("Find a Stock")
dcf_dialog.search_bar_groupbox.setGeometry(10, 10, 960, 70)
dcf_dialog.search_bar_groupbox.searchBar = QLineEdit(
    dcf_dialog.search_bar_groupbox)
dcf_dialog.search_bar_groupbox.searchBar.setGeometry(10, 20, 850, 40)
dcf_dialog.search_bar_groupbox.searchBar.textChanged.connect(
    lambda txt: searchTextChanged(txt))
dcf_dialog.search_bar_groupbox.searchBar.setFont(QFont('arial', 10))
dcf_dialog.search_bar_groupbox.searchBar.setCompleter(completer)
dcf_dialog.search_bar_groupbox.search_button = QPushButton(
    dcf_dialog.search_bar_groupbox)
dcf_dialog.search_bar_groupbox.search_button.setGeometry(870, 20, 80, 40)
dcf_dialog.search_bar_groupbox.search_button.setText("Show Model")
dcf_dialog.search_bar_groupbox.search_button.clicked.connect(
    lambda: dcf_findstock_button_click())
dcf_dialog.inputs_groupbox = QGroupBox(dcf_dialog)
dcf_dialog.inputs_groupbox.setStyleSheet('background-color: white;')
dcf_dialog.inputs_groupbox.setTitle("Model Inputs")
dcf_dialog.inputs_groupbox.setGeometry(10, 90, 630, 570)
dcf_dialog.inputs_groupbox.company_label = QLabel(
    dcf_dialog.inputs_groupbox)
dcf_dialog.inputs_groupbox.company_label.setText("Company:")
dcf_dialog.inputs_groupbox.company_label.setGeometry(10, 20, 100, 50)
dcf_dialog.inputs_groupbox.mkt_price_label = QLabel(
    dcf_dialog.inputs_groupbox)
dcf_dialog.inputs_groupbox.mkt_price_label.setText("Market Price:")
dcf_dialog.inputs_groupbox.mkt_price_label.setGeometry(10, 70, 100, 50)
dcf_dialog.inputs_groupbox.mkt_price = QLabel(dcf_dialog.inputs_groupbox)
dcf_dialog.inputs_groupbox.mkt_price.setGeometry(570, 70, 100, 50)
dcf_dialog.inputs_groupbox.eps_label = QLabel(dcf_dialog.inputs_groupbox)
dcf_dialog.inputs_groupbox.eps_label.setText("Earnings per Share:")
dcf_dialog.inputs_groupbox.eps_label.setGeometry(10, 120, 100, 50)
dcf_dialog.inputs_groupbox.eps = QLabel(dcf_dialog.inputs_groupbox)
dcf_dialog.inputs_groupbox.eps.setGeometry(570, 120, 100, 50)
dcf_dialog.inputs_groupbox.growth_label = QLabel(
    dcf_dialog.inputs_groupbox)
dcf_dialog.inputs_groupbox.growth_label.setText("Growth Estimate:")
dcf_dialog.inputs_groupbox.growth_label.setGeometry(10, 170, 100, 50)
dcf_dialog.inputs_groupbox.growth_slider = QSlider(
    dcf_dialog.inputs_groupbox)
dcf_dialog.inputs_groupbox.growth_slider.setOrientation(
    Qt.Orientation.Horizontal)
dcf_dialog.inputs_groupbox.growth_slider.setTickPosition(
    QSlider.TickPosition.TicksBothSides)
dcf_dialog.inputs_groupbox.growth_slider.setGeometry(110, 170, 450, 50)
dcf_dialog.inputs_groupbox.growth_slider.setTickInterval(10)
dcf_dialog.inputs_groupbox.growth_slider.setRange(-500, 4000)
dcf_dialog.inputs_groupbox.growth_slider.setSliderPosition(0)
dcf_dialog.inputs_groupbox.growth_slider.valueChanged.connect(
    growth_slider_moved)
dcf_dialog.inputs_groupbox.growth = QLabel(dcf_dialog.inputs_groupbox)
dcf_dialog.inputs_groupbox.growth.setGeometry(570, 170, 100, 50)
dcf_dialog.inputs_groupbox.def_growth_button = QCheckBox(
    dcf_dialog.inputs_groupbox)
dcf_dialog.inputs_groupbox.def_growth_button.setText(
    "Use Analyst 5-Year Growth Estimate")
dcf_dialog.inputs_groupbox.def_growth_button.setGeometry(
    1100, 170, 100, 50)
dcf_dialog.inputs_groupbox.term_label = QLabel(dcf_dialog.inputs_groupbox)
dcf_dialog.inputs_groupbox.term_label.setText("Term:")
dcf_dialog.inputs_groupbox.term_label.setGeometry(10, 220, 100, 50)
dcf_dialog.inputs_groupbox.term_slider = QSlider(
    dcf_dialog.inputs_groupbox)
dcf_dialog.inputs_groupbox.term_slider.setOrientation(
    Qt.Orientation.Horizontal)
dcf_dialog.inputs_groupbox.term_slider.setTickPosition(
    QSlider.TickPosition.TicksBothSides)
dcf_dialog.inputs_groupbox.term_slider.setGeometry(110, 220, 450, 50)
dcf_dialog.inputs_groupbox.term_slider.setTickInterval(1)
dcf_dialog.inputs_groupbox.term_slider.setRange(1, 10)
dcf_dialog.inputs_groupbox.term_slider.setSliderPosition(5)
dcf_dialog.inputs_groupbox.term_slider.valueChanged.connect(
    term_slider_moved)
dcf_dialog.inputs_groupbox.term = QLabel(dcf_dialog.inputs_groupbox)
dcf_dialog.inputs_groupbox.term.setText("5 years")
dcf_dialog.inputs_groupbox.term.setGeometry(570, 220, 100, 50)
dcf_dialog.inputs_groupbox.discount_rate_label = QLabel(
    dcf_dialog.inputs_groupbox)
dcf_dialog.inputs_groupbox.discount_rate_label.setText("Discount Rate: ")
dcf_dialog.inputs_groupbox.discount_rate_label.setGeometry(
    10, 270, 100, 50)
dcf_dialog.inputs_groupbox.discount_rate_slider = QSlider(
    dcf_dialog.inputs_groupbox)
dcf_dialog.inputs_groupbox.discount_rate_slider.setOrientation(
    Qt.Orientation.Horizontal)
dcf_dialog.inputs_groupbox.discount_rate_slider.setTickPosition(
    QSlider.TickPosition.TicksBothSides)
dcf_dialog.inputs_groupbox.discount_rate_slider.setGeometry(
    110, 270, 450, 50)
dcf_dialog.inputs_groupbox.discount_rate_slider.setTickInterval(10)
dcf_dialog.inputs_groupbox.discount_rate_slider.setRange(-500, 2000)
dcf_dialog.inputs_groupbox.discount_rate_slider.setSliderPosition(1000)
dcf_dialog.inputs_groupbox.discount_rate_slider.valueChanged.connect(
    discount_slider_moved)
dcf_dialog.inputs_groupbox.discount_rate = QLabel(
    dcf_dialog.inputs_groupbox)
dcf_dialog.inputs_groupbox.discount_rate.setGeometry(570, 270, 100, 50)
dcf_dialog.inputs_groupbox.perpetual_rate_label = QLabel(
    dcf_dialog.inputs_groupbox)
dcf_dialog.inputs_groupbox.perpetual_rate_label.setText("Perpetual Rate:")
dcf_dialog.inputs_groupbox.perpetual_rate_label.setGeometry(
    10, 320, 100, 50)
dcf_dialog.inputs_groupbox.perpetual_rate_slider = QSlider(
    dcf_dialog.inputs_groupbox)
dcf_dialog.inputs_groupbox.perpetual_rate_slider.setOrientation(
    Qt.Orientation.Horizontal)
dcf_dialog.inputs_groupbox.perpetual_rate_slider.setGeometry(
    110, 320, 450, 50)
dcf_dialog.inputs_groupbox.perpetual_rate_slider.setTickInterval(10)
dcf_dialog.inputs_groupbox.perpetual_rate_slider.setTickPosition(
    QSlider.TickPosition.TicksBothSides)
dcf_dialog.inputs_groupbox.perpetual_rate_slider.setRange(-500, 1000)
dcf_dialog.inputs_groupbox.perpetual_rate_slider.setSliderPosition(250)
dcf_dialog.inputs_groupbox.perpetual_rate_slider.valueChanged.connect(
    perpetual_slider_moved)
dcf_dialog.inputs_groupbox.perpetual_rate = QLabel(
    dcf_dialog.inputs_groupbox)
dcf_dialog.inputs_groupbox.perpetual_rate.setGeometry(570, 320, 100, 50)
dcf_dialog.inputs_groupbox.last_fcf_label = QLabel(
    dcf_dialog.inputs_groupbox)
dcf_dialog.inputs_groupbox.last_fcf_label.setText("Last Free Cash Flow:")
dcf_dialog.inputs_groupbox.last_fcf_label.setGeometry(10, 370, 100, 50)
dcf_dialog.inputs_groupbox.last_fcf = QLabel(dcf_dialog.inputs_groupbox)
dcf_dialog.inputs_groupbox.last_fcf.setGeometry(570, 370, 100, 50)
dcf_dialog.inputs_groupbox.shares_label = QLabel(
    dcf_dialog.inputs_groupbox)
dcf_dialog.inputs_groupbox.shares_label.setText("Shares in Circulation:")
dcf_dialog.inputs_groupbox.shares_label.setGeometry(10, 420, 100, 50)
dcf_dialog.inputs_groupbox.shares = QLabel(dcf_dialog.inputs_groupbox)
dcf_dialog.inputs_groupbox.shares.setGeometry(570, 420, 100, 50)
dcf_dialog.inputs_groupbox.get_analysis_button = QPushButton(
    dcf_dialog.inputs_groupbox)
dcf_dialog.inputs_groupbox.get_analysis_button.setGeometry(
    210, 480, 200, 100)
dcf_dialog.inputs_groupbox.get_analysis_button.setText("Get Fair Value")
dcf_dialog.inputs_groupbox.get_analysis_button.clicked.connect(
    dcf_getanalysis_button_click)
dcf_dialog.outputs_groupbox = QGroupBox(dcf_dialog)
dcf_dialog.outputs_groupbox.setStyleSheet('background-color: white;')
dcf_dialog.outputs_groupbox.setTitle("Model Outputs")
dcf_dialog.outputs_groupbox.setGeometry(650, 90, 630, 570)
dcf_dialog.outputs_groupbox.verdict_label = QLabel(
    dcf_dialog.outputs_groupbox)
dcf_dialog.outputs_groupbox.verdict_label.setGeometry(200, 10, 200, 50)
dcf_dialog.outputs_groupbox.basic_model_output = QGroupBox(
    dcf_dialog.outputs_groupbox)
dcf_dialog.outputs_groupbox.basic_model_output.setGeometry(
    10, 20, 610, 350)
dcf_dialog.outputs_groupbox.basic_model_output.setTitle("Basic Model")
future_cashflows_chart = QChart()
future_cashflows_lineseries = QLineSeries()
future_cashflows_lineseries.setName("Future Cashflows")
future_cashflows_chart.addSeries(future_cashflows_lineseries)
future_cashflows_chartview = QChartView(future_cashflows_chart)
future_cashflows_chartview.setParent(
    dcf_dialog.outputs_groupbox.basic_model_output)
future_cashflows_chartview.setGeometry(10, 20, 590, 200)
dcf_dialog.outputs_groupbox.basic_model_output.fair_value_label = QLabel(
    dcf_dialog.outputs_groupbox.basic_model_output)
dcf_dialog.outputs_groupbox.basic_model_output.fair_value_label.setText(
    "Fair Value:")
dcf_dialog.outputs_groupbox.basic_model_output.fair_value_label.setGeometry(
    250, 230, 100, 50)
dcf_dialog.outputs_groupbox.basic_model_output.fair_value = QLabel(
    dcf_dialog.outputs_groupbox.basic_model_output)
dcf_dialog.outputs_groupbox.basic_model_output.fair_value.setGeometry(
    200, 280, 100, 50)
dcf_dialog.outputs_groupbox.graham_model_output = QGroupBox(
    dcf_dialog.outputs_groupbox)
dcf_dialog.outputs_groupbox.graham_model_output.setGeometry(
    10, 380, 610, 150)
dcf_dialog.outputs_groupbox.graham_model_output.setTitle("Graham Model")
dcf_dialog.outputs_groupbox.graham_model_output.ev_label = QLabel(
    dcf_dialog.outputs_groupbox.graham_model_output)
dcf_dialog.outputs_groupbox.graham_model_output.ev_label.setText(
    "Expected value implied by growth rate:")
dcf_dialog.outputs_groupbox.graham_model_output.ev_label.setGeometry(
    10, 20, 200, 50)
dcf_dialog.outputs_groupbox.graham_model_output.ev = QLabel(
    dcf_dialog.outputs_groupbox.graham_model_output)
dcf_dialog.outputs_groupbox.graham_model_output.ev.setGeometry(
    490, 20, 100, 50)
dcf_dialog.outputs_groupbox.graham_model_output.graham_growth_estimate_label = QLabel(
    dcf_dialog.outputs_groupbox.graham_model_output)
dcf_dialog.outputs_groupbox.graham_model_output.graham_growth_estimate_label.setText(
    "Growth rate implied by stock price:")
dcf_dialog.outputs_groupbox.graham_model_output.graham_growth_estimate_label.setGeometry(
    10, 80, 200, 50)
dcf_dialog.outputs_groupbox.graham_model_output.graham_growth_estimate = QLabel(
    dcf_dialog.outputs_groupbox.graham_model_output)
dcf_dialog.outputs_groupbox.graham_model_output.graham_growth_estimate.setGeometry(
    490, 80, 100, 50)
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
settings_dialog.apply_button.clicked.connect(
    lambda: applySettingsChanges())
#################
# wallet dialog #
#################
wallet_dialog = QDialog()
wallet_dialog.setStyleSheet('background-color: goldenrod')
# user's crypto wallet NAV
wallet_dialog.currentNAV = QGroupBox(wallet_dialog)
wallet_dialog.currentNAV.setTitle("Your NAV")
wallet_dialog.currentNAV.setGeometry(10, 10, 250, 250)
wallet_dialog.currentNAV.setStyleSheet(
    'background-color: black; color: white;')
# net liquidation value labels
wallet_dialog.currentNAV.netLiq = QLabel(wallet_dialog.currentNAV)
wallet_dialog.currentNAV.netLiq.setText("Net Liq: ")
wallet_dialog.currentNAV.netLiq.setGeometry(10, 20, 80, 20)
wallet_dialog.currentNAV.netLiq.setFont(QFont('genius', 10))
wallet_dialog.currentNAV.liq = QLabel(wallet_dialog.currentNAV)
wallet_dialog.currentNAV.liq.setText(
    '${:0,.2f}'.format(float(str(wallet_nav))))
wallet_dialog.currentNAV.liq.setGeometry(10, 40, 160, 40)
wallet_dialog.currentNAV.liq.setFont(QFont('genius', 20))
# positions table settings
wallet_dialog.positions_view_groupbox = QGroupBox(wallet_dialog)
wallet_dialog.positions_view_groupbox.setGeometry(10, 300, 900, 250)
wallet_dialog.positions_view_groupbox.setTitle("Your Portfolio")
wallet_dialog.positions_view_groupbox.setStyleSheet(
    'background-color: black; color: white;')
wallet_dialog.positions_view_groupbox.positions_view = QTableWidget(
    wallet_dialog.positions_view_groupbox)
wallet_dialog.positions_view_groupbox.positions_view.setEditTriggers(
    QAbstractItemView.EditTrigger.NoEditTriggers)
wallet_dialog.positions_view_groupbox.positions_view.setFont(
    QFont('arial', 10))
wallet_dialog.positions_view_groupbox.positions_view.setRowCount(
    len(wallet_amts) - 1)
wallet_dialog.positions_view_groupbox.positions_view.setColumnCount(8)
wallet_dialog.positions_view_groupbox.positions_view.setGeometry(
    10, 20, 850, 200)
wallet_dialog.positions_view_groupbox.positions_view.setStyleSheet(
    'background-color: black;')
wallet_dialog.positions_view_groupbox.positions_view.horizontalHeader(
).setStyleSheet("::section{background-color: black; color: white}")
btn = wallet_dialog.positions_view_groupbox.positions_view.cornerWidget()
wallet_dialog.positions_view_groupbox.positions_view.setHorizontalHeaderItem(
    0, QTableWidgetItem("Ticker"))
wallet_dialog.positions_view_groupbox.positions_view.setHorizontalHeaderItem(
    1, QTableWidgetItem("Today's Performance"))
wallet_dialog.positions_view_groupbox.positions_view.setHorizontalHeaderItem(
    2, QTableWidgetItem("Current Price"))
wallet_dialog.positions_view_groupbox.positions_view.setHorizontalHeaderItem(
    3, QTableWidgetItem("Gain/Loss Per Share"))
wallet_dialog.positions_view_groupbox.positions_view.setHorizontalHeaderItem(
    4, QTableWidgetItem("Purchase Price"))
wallet_dialog.positions_view_groupbox.positions_view.setHorizontalHeaderItem(
    5, QTableWidgetItem("# of Shares"))
wallet_dialog.positions_view_groupbox.positions_view.setHorizontalHeaderItem(
    6, QTableWidgetItem("Total Value"))
wallet_dialog.positions_view_groupbox.positions_view.setHorizontalHeaderItem(
    7, QTableWidgetItem("Position Gain/Loss"))
for i in range(8):
    wallet_dialog.positions_view_groupbox.positions_view.horizontalHeaderItem(
        i).setFont(QFont('arial', 10))
for i in range(portfolio_dialog.positions_view_groupbox.positions_view.rowCount()):
    wallet_dialog.positions_view_groupbox.positions_view.setVerticalHeaderItem(
        0, QTableWidgetItem("1"))
    wallet_dialog.positions_view_groupbox.positions_view.verticalHeaderItem(
        i).setFont(QFont('arial', 10))
update_wallet_table()
# cash labels
wallet_dialog.currentNAV.cashLabel = QLabel(wallet_dialog.currentNAV)
wallet_dialog.currentNAV.cashLabel.setText("Cash: ")
wallet_dialog.currentNAV.cashLabel.setGeometry(10, 90, 80, 20)
wallet_dialog.currentNAV.cash = QLabel(wallet_dialog.currentNAV)
wallet_dialog.currentNAV.cash.setText('${:0,.2f}'.format(wallet_cash))
wallet_dialog.currentNAV.cash.setGeometry(100, 90, 80, 20)
# buying power labels
wallet_dialog.currentNAV.buyingPowerLabel = QLabel(
    wallet_dialog.currentNAV)
wallet_dialog.currentNAV.buyingPowerLabel.setText("Buying Power: ")
wallet_dialog.currentNAV.buyingPowerLabel.setGeometry(10, 110, 80, 20)
wallet_dialog.currentNAV.buyingPower = QLabel(wallet_dialog.currentNAV)
wallet_dialog.currentNAV.buyingPower.setText(
    '${:0,.2f}'.format(get_wallet_bp()))
wallet_dialog.currentNAV.buyingPower.setGeometry(100, 110, 80, 20)
# assets labels
wallet_dialog.currentNAV.assetsLabel = QLabel(wallet_dialog.currentNAV)
wallet_dialog.currentNAV.assetsLabel.setText("Long Assets: ")
wallet_dialog.currentNAV.assetsLabel.setGeometry(10, 130, 80, 20)
wallet_dialog.currentNAV.assets = QLabel(wallet_dialog.currentNAV)
total_long = 0
for i in range(1, len(wallet_amts)):
    price = atof(wallet_dialog.positions_view_groupbox.positions_view.item(
        i - 1, 2).text()[1:])
    if float(wallet_amts[i].text) > 0:
        total_long += float(price) * float(wallet_amts[i].text)
wallet_dialog.currentNAV.assets.setText('${:0,.2f}'.format(total_long))
wallet_dialog.currentNAV.assets.setGeometry(100, 130, 80, 20)
# liabilities labels
wallet_dialog.currentNAV.liabilitiesLabel = QLabel(
    wallet_dialog.currentNAV)
wallet_dialog.currentNAV.liabilitiesLabel.setText("Short Assets: ")
wallet_dialog.currentNAV.liabilitiesLabel.setGeometry(10, 150, 80, 20)
wallet_dialog.currentNAV.liabilities = QLabel(wallet_dialog.currentNAV)
total_short = 0
for i in range(1, len(wallet_amts)):
    price = atof(wallet_dialog.positions_view_groupbox.positions_view.item(
        i - 1, 2).text()[1:])
    if float(wallet_amts[i].text) < 0:
        total_short -= float(price) * float(wallet_amts[i].text)
wallet_dialog.currentNAV.liabilities.setText(
    '${:0,.2f}'.format(total_short))
wallet_dialog.currentNAV.liabilities.setGeometry(100, 150, 80, 20)
# return since inception labels
wallet_dialog.currentNAV.returnSinceInceptionLabel = QLabel(
    wallet_dialog.currentNAV)
wallet_dialog.currentNAV.returnSinceInceptionLabel.setText(
    "Return Since Inception: ")
wallet_dialog.currentNAV.returnSinceInceptionLabel.setGeometry(
    10, 170, 120, 20)
wallet_dialog.currentNAV.returnSinceInception = QLabel(
    wallet_dialog.currentNAV)
wallet_dialog.currentNAV.returnSinceInception.setFont(QFont('genius', 20))
wallet_dialog.currentNAV.returnSinceInception.setText(
    '{:0.2f}'.format((wallet_nav / 10000 - 1) * 100) + "%")
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
