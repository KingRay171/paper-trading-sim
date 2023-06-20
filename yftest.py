# Started by Ray Ikome on 11/16/22
if __name__ == "__main__":
    import sys
    import os
    from locale import setlocale, LC_NUMERIC
    from threading import Thread
    import time

    from datetime import datetime
    import pandas as pd
    from functools import reduce
    # pylint: disable-msg=E0611
    # pylint: disable-msg=W0603
    # pylint: disable-msg=C0103
    from PySide6.QtWidgets import QTabWidget, QTableWidgetItem, QSplashScreen, QApplication, QProgressBar
    from PySide6.QtGui import QFont, QFontDatabase, QPixmap, QIcon
    import yahooquery as yq

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('wsb.jpg'))

    CWD = os.getcwd() + '\\'
    splash = QSplashScreen(QPixmap(f"{CWD}splashscreen-images/splash.jpg"))
    progressBar = QProgressBar(splash)
    progressBar.setGeometry(620, 690, 400, 50)
    splash.show()

    from dependencies import autocomplete as ac
    from dependencies import IsMarketOpen as mktopen
    from dependencies import readassets as ra
    from dependencies import savetrades as st
    from dependencies import saveport as sp
    from dependencies import savewallet as sw

    progressBar.setValue(10)

    from widgets.portfolio import portfolio
    from widgets.portfolio import portfolio_tab

    progressBar.setValue(20)

    from widgets.chart_stocks import stock_chart_tab
    from widgets.trade_stocks import trade_tab
    from widgets.stock_info import stockinfo_tab

    progressBar.setValue(30)

    from widgets.scanner import scanner_tab
    from widgets.dcf import dcf_tab

    progressBar.setValue(40)

    from widgets.wallet import wallet, wallet_tab
    from widgets.trade_crypto import trade_crypto_tab
    from widgets.minigame import minigame_tab
    from widgets.settings import settings_tab

    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

    CURRENT_TICKER = ''

    selected_ta = []

    OPEN_PORT_ORDERS = []
    OPEN_WALLET_ORDERS = []

    ARIAL_10 = QFont('arial', 10)



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
            try:
                if widget.currentWidget() == wallet_dialog:
                    wallet_dialog.update_wallet_table(wall)
                    wallet_dialog.update_wallet_nav(wall)

                    time.sleep(5)
                if widget.currentWidget() == trade_dialog and trade_dialog.symbol is not None:
                    trade_dialog.update_stock_trade_dialog(trade_dialog.symbol)
                if widget.currentWidget() == trade_dialog:
                    if widget.currentWidget().currentWidget() == trade_dialog.options:
                        try:
                            trade_dialog.update_options()
                        except AttributeError:
                            pass
                if widget.currentWidget() == trade_crypto_dialog and trade_crypto_dialog.trade.symbol is not None:
                    trade_crypto_dialog.trade.update_crypto_dialog()
                if mktopen.market_is_open():
                    if widget.currentWidget() == port_dialog:
                        port.update_options()
                        port_dialog.port.update(port)
                        port_dialog.watchlist.update(watchlist_tickers)
                        port_dialog.port_overview.update(port_dialog.port.table, port)
                        port_dialog.chart.update(port_dialog.port, port, port_dialog.port_overview)

                    update_port_trades()

                else:
                    time.sleep(.1)
                port_dialog.trades.update(OPEN_PORT_ORDERS)
                update_wallet_trades()
            except RuntimeError:
                pass


    def update_wallet_trades():
        """
        Checks if any open crypto trades can be executed and executes them
        """
        for order in OPEN_WALLET_ORDERS:

            cash = wall.positions[0].amt
            ticker = yq.Ticker(order[0])
            cur_price = ticker.price[order[0]]['regularMarketPrice']

            if order[2] == 'Market' and order[1] == 'Buy':
                execute_crypto_buy(order, cash, cur_price)

            elif order[2] == 'Market' and order[1] == 'Sell':
                execute_crypto_sell(order, cash, cur_price)

            elif order[2] == 'Limit' and order[1] == 'Buy':
                if cur_price < float(order[3]):
                    execute_crypto_buy(order, cash, cur_price)

            elif order[2] == 'Limit' and order[1] == 'Sell':
                if cur_price > float(order[3]):
                    execute_crypto_sell(order, cash, cur_price)

            elif order[2] == 'Stop' and order[1] == 'Buy':
                if cur_price > float(order[3]):
                    execute_crypto_buy(order, cash, cur_price)

            elif order[2] == 'Stop' and order[1] == 'Sell':
                if cur_price < float(order[3]):
                    execute_crypto_sell(order, cash, cur_price)


    def execute_crypto_buy(order, cash, trade_price):

        order[0] = order[0].upper()

        trade_qty = float(order[4])
        cash -= trade_qty * float(trade_price)
        wall.positions[0].amt = cash

        index = wall.get_index_by_ticker(order[0])

        if index != -1:
            position = wall[index]
            pos_size = position.amt
            old_basis = position.basis

            if -1 * trade_qty == pos_size:
                wall.positions = list(filter(lambda e: e.ticker != order[0], wall.positions))
                wallet_dialog.pos_view_gb.pos_view.setRowCount(len(wall.positions) - 1)

            elif trade_qty < pos_size:
                token_amt = pos_size + trade_qty
                position.amt = token_amt

                new_cb = 0
                if pos_size <= 0:
                    new_cb = round(
                        (old_basis * (token_amt - trade_qty) + trade_price * trade_qty) / token_amt, 2
                    )
                    position.basis = new_cb

            elif trade_qty >= pos_size:
                token_amt = pos_size + trade_qty
                position.amt = token_amt

                new_cb = 0
                if pos_size >= 0:
                    new_cb = round(
                        (old_basis * (token_amt - trade_qty) + trade_price * trade_qty) / token_amt, 2
                    )
                    position.basis = new_cb
                else:
                    if trade_qty > abs(pos_size):
                        position.basis = trade_price

        else:
            wall.positions.append(wallet.WalletPosition(order[0], trade_price, order[4]))

            wallet_dialog.pos_view_gb.pos_view.setRowCount(len(wall.positions) - 1)
            row_count = wallet_dialog.pos_view_gb.pos_view.rowCount()
            column_count = wallet_dialog.pos_view_gb.pos_view.columnCount()
            for k in range(column_count):
                wallet_dialog.pos_view_gb.pos_view.setItem(row_count - 1, k, QTableWidgetItem())


        OPEN_WALLET_ORDERS.remove(order)


    def execute_crypto_sell(order, cash, trade_price):
        order[0] = order[0].upper()

        trade_qty = float(order[4])

        cash += trade_qty * float(trade_price)
        wall.positions[0].amt = cash

        index = wall.get_index_by_ticker(order[0])

        if index != -1:
            position = wall[index]
            pos_size = position.amt
            old_basis = position.basis

            if trade_qty < pos_size:
                token_amt = pos_size - trade_qty
                position.amt = token_amt

            elif trade_qty == pos_size:
                wall.positions = list(filter(lambda e: e.ticker != order[0], wall.positions))
                wallet_dialog.pos_view_gb.pos_view.setRowCount(len(wall.positions) - 1)

            else:
                token_amt = pos_size - trade_qty
                position.amt = token_amt

                new_cb = 0
                if pos_size <= 0:
                    new_cb = round(
                        (old_basis * (token_amt + trade_qty) + trade_price * -trade_qty) / token_amt, 2
                    )
                    position.basis = new_cb
                else:
                    position.basis = trade_price

        else:
            wall.positions.append(wallet.WalletPosition(order[0], trade_price, order[4]))

            wallet_dialog.pos_view_gb.pos_view.setRowCount(len(wall.positions) - 1)
            row_count = wallet_dialog.pos_view_gb.pos_view.rowCount()
            column_count = wallet_dialog.pos_view_gb.pos_view.columnCount()
            for j in range(column_count):
                wallet_dialog.pos_view_gb.pos_view.setItem(row_count - 1, j, QTableWidgetItem())
        OPEN_WALLET_ORDERS.remove(order)


    def update_port_trades():
        """
        Checks if any open stock/option trades can be executed and executes them
        """
        for order in OPEN_PORT_ORDERS:

            cash = port.positions[0].amt
            ticker = yq.Ticker(order[0])
            asset_type = ""
            match ticker.quote_type[order[0]]['quoteType']:
                case 'EQUITY':
                    asset_type = 'Stock'
                case 'ETF':
                    asset_type = 'ETF'
                case 'OPTION':
                    asset_type = 'Option'

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
        if trade_price is None:
            trade_price = ticker.summary_detail[order[0]]['ask']

        cash -= float(order[4]) * float(trade_price)
        port.positions[0].amt = cash
        trade_qty = float(order[4])

        index = port.get_index_by_ticker(order[0])

        if index != -1:
            position = port[index]
            pos_size = position.amt
            old_basis = position.basis

            if -1 * trade_qty == pos_size:
                port.positions = list(filter(lambda e: e.ticker != order[0]))

                port_dialog.port.table.setRowCount(len(port.positions) - 1)

            elif trade_qty < pos_size:
                stock_amt = pos_size + trade_qty
                position.amt = stock_amt

                new_cb = 0
                if pos_size >= 0:
                    new_cb = round(
                        (old_basis * (stock_amt - trade_qty) + trade_price * trade_qty) / stock_amt, 2
                    )
                    position.basis = new_cb

            elif trade_qty >= pos_size:
                stock_amt = pos_size + trade_qty
                position.amt = stock_amt

                new_cb = 0
                if pos_size >= 0:
                    new_cb = round(
                        (old_basis * (stock_amt - trade_qty) + trade_price * trade_qty) / stock_amt, 2
                    )
                    position.basis = new_cb
                else:
                    if trade_qty > abs(pos_size):
                        position.basis = trade_price

        else:
            port.positions.append(portfolio.PortfolioPosition(order[0], trade_price, order[4], asset_type))

            port_dialog.port.table.setRowCount(len(port.positions) - 1)
            column_count = port_dialog.port.table.columnCount()
            row_count = port_dialog.port.table.rowCount()
            for j in range(column_count):
                port_dialog.port.table.setItem(row_count - 1, j, QTableWidgetItem())


        OPEN_PORT_ORDERS.remove(order)
        port_dialog.trades.update(OPEN_PORT_ORDERS)


    def execute_sell(order: list, ticker: yq.Ticker, asset_type: str, cash: float, trade_price=None):
        if trade_price is None:
            trade_price = ticker.summary_detail[order[0]]['bid']
        cash += float(order[4]) * float(trade_price)
        port.positions[0].amt = cash

        trade_qty = float(order[4])

        index = port.get_index_by_ticker(order[0])

        if index != -1:
            position = port[index]
            pos_size = position.amt
            old_basis = position.basis

            if trade_qty < pos_size:
                stock_amt = pos_size - trade_qty
                position.amt = stock_amt

            elif trade_qty == pos_size:
                port.positions = list(filter(lambda e: e.ticker != order[0]))
                port_dialog.port.table.setRowCount(len(port.positions) - 1)

            else:
                stock_amt = pos_size - trade_qty
                position.amt = stock_amt
                new_cb = 0

                if pos_size <= 0:
                    new_cb = round(
                        (old_basis * (stock_amt + trade_qty) + trade_price * -trade_qty) / stock_amt, 2
                    )
                    position.basis = new_cb
                else:
                    position.basis = trade_price

        else:
            port.positions.append(portfolio.PortfolioPosition(order[0], trade_price, order[4], asset_type))

            port_dialog.port.table.setRowCount(len(port.positions) - 1)
            row_count = port_dialog.port.table.rowCount()
            column_count = port_dialog.port.tablecolumnCount()
            for j in range(column_count):
                port_dialog.port.table.setItem(row_count - 1, j, QTableWidgetItem())

        OPEN_PORT_ORDERS.remove(order)
        port_dialog.trades.update(OPEN_PORT_ORDERS)


    def close_event():
        """
        Saves currently open trades and the state of the portfolio to trades.xml and portfolio.xml
        """
        st.save(OPEN_PORT_ORDERS)
        sp.save_port(port)
        sw.save_wallet(wall)


    app.aboutToQuit.connect(close_event)
    widget = QTabWidget()
    widget.setWindowTitle("Paper Trading Game")

    setlocale(LC_NUMERIC, '')


    #####################################################
    # parse XML file data relating to user's portfolio, #
    # watchlist, and settings                           #
    #####################################################

    watchlist_tickers = [ticker.text for ticker in ra.get_xml_data(r'assets\watchlist.xml', 'name')]

    port = portfolio.Portfolio(
        [ticker.text for ticker in ra.get_xml_data(r'assets\portfolio.xml', 'name')],
        [None] + [float(price.text) for price in ra.get_xml_data(r'assets\portfolio.xml', 'costbasis')],
        [float(amt.text) for amt in ra.get_xml_data(r'assets\portfolio.xml', 'amount')],
        [type.text for type in ra.get_xml_data(r'assets\portfolio.xml', 'type')]
    )

    wall = wallet.Wallet(
        [ticker.text for ticker in ra.get_xml_data(r'assets\wallet.xml', 'name')],
        [None] + [float(basis.text) for basis in ra.get_xml_data(r'assets\wallet.xml', 'costbasis')],
        [float(amt.text) for amt in ra.get_xml_data(r'assets\wallet.xml', 'amount')])

    trades = ra.get_xml_data(r'assets\trades.xml', 'trade')

    all_tickers_list = pd.read_csv(CWD + r"assets\stock_list.csv")['Symbol'].tolist()
    all_names_list = pd.read_csv(CWD + r"assets\stock_list.csv")['Name'].tolist()

    all_tickers_list[5023] = 'NAN'
    all_tickers_list = [f"{ticker} - {name}" for (ticker, name) in zip(all_tickers_list, all_names_list)]

    # set user's NAV equal to cash first, then iterate through stocks,
    # find their current price, and add their values to user's NAV

    portfolio_nav = reduce(lambda x, y: x + y, map(
        lambda e: e.amt * (
            yq.Ticker(e.ticker).history('5d').iat[-1, 5] if e.ticker != 'US Dollars' else 1
            ), port.positions
    ))

    wallet_nav = reduce(lambda x, y: x + y, map(
        lambda e: e.amt * (
            yq.Ticker(e.ticker).history('5d').iat[-1, 5] if e.ticker != 'US Dollars' else 1
            ), wall.positions
        )
    )


    # add genius font to database
    QFontDatabase.addApplicationFont('fonts/genius.ttf')
    progressBar.setValue(50)

    ####################
    # portfolio dialog #
    ####################

    port_dialog = portfolio_tab.PortfolioTab(port, watchlist_tickers, OPEN_PORT_ORDERS)
    chart_dialog = stock_chart_tab.StockChartTab(all_tickers_list, selected_ta)
    trade_dialog = trade_tab.StockTradeTab(all_tickers_list, port, OPEN_PORT_ORDERS)
    stockinfo_dialog = stockinfo_tab.StockInfoTab(all_tickers_list)
    dcf_dialog = dcf_tab.DCFTab(all_tickers_list)
    ideas_dialog = scanner_tab.ScannerTab()
    wallet_dialog = wallet_tab.WalletTab(wall)
    trade_crypto_dialog = trade_crypto_tab.CryptoTradeTab(OPEN_WALLET_ORDERS)
    minigame_dialog = minigame_tab.MinigameTab()
    settings_dialog = settings_tab.SettingsTab()

    completer = ac.CustomQCompleter()

    # handle trades
    for trade in trades:
        trade_list_item = [trade.contents[1].text, trade.contents[3].text, trade.contents[5].text,
                           trade.contents[7].text, trade.contents[9].text]

        OPEN_PORT_ORDERS.append(trade_list_item)

        ticker_obj = yq.Ticker(trade.contents[1].text)
        prices_frame = ticker_obj.history(
            interval='1m',
            start=datetime.strptime(trade.contents[11].text, '%Y-%m-%d %H:%M:%S.%f'),
            end=datetime.now()
        )


        asset_class = ""
        match ticker_obj.quote_type[trade.contents[1].text]['quoteType']:
            case 'EQUITY':
                asset_class = 'Stock'
            case 'ETF':
                asset_class = 'ETF'
            case 'OPTION':
                asset_class = "Option"

        execution_price = float(trade.contents[7].text)
        if trade.contents[3].text == 'Buy' and trade.contents[5].text == 'Limit':
            for row in prices_frame.iterrows():
                if row[1].iloc[3] < execution_price:
                    execute_buy(trade_list_item, ticker_obj, asset_class, port.postions[0].amt, execution_price)
                    break
        elif trade.contents[3].text == 'Sell' and trade.contents[5].text == 'Limit':
            for row in prices_frame.iterrows():
                if row[1].iloc[2] > execution_price:
                    execute_sell(trade_list_item, ticker_obj, asset_class, port.postions[0].amt, execution_price)
                    break
        elif trade.contents[3].text == 'Buy' and trade.contents[5].text == 'Stop':
            for row in prices_frame.iterrows():
                if row[1].iloc[2] > execution_price:
                    execute_buy(trade_list_item, ticker_obj, asset_class, port.postions[0].amt, execution_price)
                    break
        elif trade.contents[3].text == 'Sell' and trade.contents[5].text == 'Stop':
            for row in prices_frame.iterrows():
                if row[1].iloc[3] < execution_price:
                    execute_sell(trade_list_item, ticker_obj, asset_class, port.postions[0].amt, execution_price)
                    break
        elif trade.contents[3].text == 'Buy' and trade.contents[5].text == 'Market':
            if prices_frame.size > 1:
                execute_buy(trade_list_item, ticker_obj, asset_class, port.postions[0].amt, execution_price)
                break
        elif trade.contents[3].text == 'Sell' and trade.contents[5].text == 'Market':
            if prices_frame.size > 1:
                execute_sell(trade_list_item, ticker_obj, asset_class, port.postions[0].amt, execution_price)
                break

    progressBar.setValue(90)


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
    widget.addTab(trade_crypto_dialog, "Trade Crypto")
    widget.addTab(minigame_dialog, "Minigame")
    widget.addTab(settings_dialog, "Settings")
    widget.resize(1300, 700)
    widget.show()
    splash.close()

    # instantiate thread which runs the updateNav function in an infinite loop
    Thread(target=update_ui, daemon=True).start()
    sys.exit(app.exec())
