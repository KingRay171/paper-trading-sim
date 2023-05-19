
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QWidget, QTableWidgetItem, QLabel, QSpinBox, QComboBox, QPushButton, QSlider
import yahooquery as yq
import math
import time
from threading import Thread
from widgets.portfolio.portfolio import Portfolio
from widgets.trade_stocks.confirm_option_trade import ConfirmOptionTradeWindow
class OptionTradeWindow(QDialog):
    def __init__(self, parent: QWidget, stock: str, wi: QTableWidgetItem, port: Portfolio, orders: list) -> None:
        super().__init__(parent)
        self.setStyleSheet("background-color: white;")
        self.stock = stock
        self.port = port
        self.wi = wi
        self.orders = orders
        self.confirm_window = None
        self.current_chain = parent.currentWidget()
        self.calls_puts_idx = self.current_chain.indexOf(self.current_chain.currentWidget())
        self.calls_puts = self.current_chain.tabText(self.calls_puts_idx)
        self.setWindowTitle(
            f"""{"Sell" if wi.column() == 2 else "Buy"} {stock} {wi.tableWidget().item(wi.row(), 0).text()}
            {"Call" if self.calls_puts == "Calls" else "Put"}"""
        )
        self.setFixedSize(400, 300)
        self.place_trade = QPushButton(self)
        self.place_trade.setText('Preview Order')
        self.place_trade.setGeometry(225, 240, 100, 50)

        self.quantity_label = QLabel(self)
        self.quantity_label.setText("Quantity")
        self.quantity_label.setGeometry(10, 50, 50, 40)

        self.quantity_spinbox = QSpinBox(self)
        self.quantity_spinbox.setValue(0)
        self.quantity_spinbox.setGeometry(100, 50, 100, 40)

        self.ordertype_label = QLabel(self)
        self.ordertype_label.setText("Order Type:")
        self.ordertype_label.setGeometry(10, 100, 60, 40)

        self.ordertype_combobox = QComboBox(self)
        self.ordertype_combobox.addItems(('Market', 'Limit', 'Stop'))
        self.ordertype_combobox.setGeometry(100, 100, 100, 40)
        self.ordertype_combobox.currentTextChanged.connect(self.on_option_ordertype_change)
        self.price_slider = QSlider(self)
        self.price_slider.setOrientation(Qt.Orientation.Horizontal)
        self.price_slider.setRange(0, 10)
        self.price_slider.setGeometry(210, 100, 160, 40)
        self.price_slider.setVisible(False)
        self.limit_stop_bid = QLabel(self)
        self.limit_stop_bid.setText("<bid>")
        self.limit_stop_bid.setGeometry(200, 150, 50, 50)
        self.limit_stop_bid.setVisible(False)
        self.limit_stop_ask = QLabel(self)
        self.limit_stop_ask.setText("<ask>")
        self.limit_stop_ask.setGeometry(350, 150, 50, 50)
        self.limit_stop_ask.setVisible(False)
        self.limit_stop_mid = QLabel(self)
        self.limit_stop_mid.setText("<mid>")
        self.limit_stop_mid.setGeometry(280, 150, 50, 50)
        self.limit_stop_mid.setVisible(False)
        self.trade_price_label = QLabel(self)
        self.trade_price_label.setText("Trade Price")
        self.trade_price_label.setGeometry(10, 150, 60, 40)
        self.trade_price = QLabel(self)
        self.trade_price.setText(wi.text())
        self.trade_price.setGeometry(100, 150, 60, 40)
        self.bpr_label = QLabel(self)
        self.bpr_label.setText('Buying Power Reduction:')
        self.bpr_label.setGeometry(10, 200, 60, 40)
        self.bpr = QLabel(self)
        self.bpr.setText(
                f"""{
                    self.get_bpr(
                        stock,
                        int(self.quantity_spinbox.value()),
                        wi.tableWidget().item(wi.row(), 0).text(),
                        "Sell" if wi.column() == 2 else "Buy",
                        wi.tableWidget().item(wi.row(), 19).text(),
                        wi.tableWidget().item(wi.row(), 2).text(),
                        port
                    )
                }"""
            )
        self.quantity_spinbox.valueChanged.connect(
            lambda: self.bpr.setText(
                f"""{
                    self.get_bpr(
                        stock,
                        int(self.quantity_spinbox.value()),
                        float(wi.tableWidget().item(wi.row(), 0).text()),
                        "Sell" if wi.column() == 2 else "Buy",
                        wi.tableWidget().item(wi.row(), 19).text(),
                        wi.tableWidget().item(wi.row(), 1).text() == 'ITM',
                        port
                    )
                }"""
            )
        )
        self.update_thread = Thread(target=self.update_option_trade_dialog, daemon=True)
        self.update_thread.start()
        self.bpr.setGeometry(100, 200, 60, 40)
        self.CURRENT_TRADE_OPTION_NAME = wi.tableWidget().item(wi.row(), 22).text()
        self.place_trade.clicked.connect(self.preview_option_trade)
        self.exec()




    def on_option_ordertype_change(self, value):
        """
        Shows or hides the price slider depending on the type of order selected
        (show for limit/stop, hide for market)
        """
        match value:
            case 'Market':
                self.price_slider.setVisible(False)
                self.limit_stop_bid.setVisible(False)
                self.limit_stop_ask.setVisible(False)
                self.limit_stop_mid.setVisible(False)
            case _:
                self.price_slider.setVisible(True)
                self.limit_stop_bid.setVisible(True)
                self.limit_stop_ask.setVisible(True)
                self.limit_stop_mid.setVisible(True)

    def num_options_on_underlying(self, ticker: str, calls_puts: str, port: Portfolio):
        """
        Finds the number of options, of any strike or expiration, that the user has positions in for a given underlying
        """
        acc = 0
        portfolio_tickers = [pos.ticker for pos in port.positions]
        portfolio_amts = [pos.amt for pos in port.positions]
        portfolio_asset_types = [pos.asset_type for pos in port.positions]
        for idx, asset_type in enumerate(portfolio_asset_types):
            if asset_type == "Option" and portfolio_amts[idx] < 0:
                if ticker in portfolio_tickers[idx]:
                    _type = yq.Ticker(portfolio_tickers[idx]).all_modules[portfolio_tickers[idx]]['price']['shortName'][:-4]
                    if calls_puts == "Calls" and _type == 'call':
                        acc += portfolio_amts[idx]
                    elif calls_puts == "Puts" and _type == ' put':
                        acc += portfolio_amts[idx]
        return acc * 100


    def get_bpr(self, ticker: str, quantity: int, strike: float, buy_sell: str, option_ticker: str, is_itm: bool, port: Portfolio):
        """
        Calculates the buying power reduction that would result from selling short a given option
        """
        if buy_sell == 'Sell':
            options_owned = 0
            option_slots_left = 0
            portfolio_tickers = [pos.ticker for pos in port.positions]
            portfolio_amts = [pos.amt for pos in port.positions]

            if option_ticker in portfolio_tickers: # user has shares of underlying
                index = portfolio_tickers.index(option_ticker)
                options_owned = portfolio_amts[index]
            shares_covered_by_options = self.num_options_on_underlying(ticker, f"{is_itm}s", port)
            num_underlying_shares = 0
            if ticker in portfolio_tickers:
                num_underlying_shares += max(0, portfolio_amts[portfolio_tickers.index(ticker)])


            option_slots_left = max(0, math.trunc((num_underlying_shares - shares_covered_by_options) / 100))
            options_owned = max(0, options_owned)

            if quantity <= options_owned:
                return 0
            elif quantity > options_owned:
                if quantity > options_owned + option_slots_left:
                    cash_covered_options = quantity - options_owned - option_slots_left
                    if is_itm:
                        return cash_covered_options * yq.Ticker(ticker).price[ticker]['regularMarketPrice'] * 100 * .2
                    else:
                        stock_price = yq.Ticker(ticker).price[ticker]['regularMarketPrice']
                        return max(
                            .1 * strike * 100,
                            .2 * (stock_price - (stock_price - strike)) * 100
                        ) * cash_covered_options
                else:
                    return 0
        else:
            return 0

    def update_option_trade_dialog(self):
        while True:
            try:
                all_modules = yq.Ticker(self.CURRENT_TRADE_OPTION_NAME).all_modules[self.CURRENT_TRADE_OPTION_NAME]
            except KeyError:
                pass
            summary = all_modules['summaryDetail']
            self.limit_stop_bid.setText(f"Bid:\n{summary['bid']}")
            self.limit_stop_ask.setText(f"Ask:\n{summary['ask']}")
            self.limit_stop_mid.setText(f"Mid:\n{(summary['bid'] + summary['ask']) / 2}")
            slider_range = (summary['ask'] - summary['bid']) * 100
            self.price_slider.setRange(0, slider_range)
            self.trade_price.setText(
                f"{self.price_slider.value() / 100 + summary['bid']}"
                if self.ordertype_combobox.currentText() != 'Market'
                else (
                    f"{summary['bid']}"
                    if self.windowTitle()[:4] == 'Sell'
                    else f"{summary['ask']}"
                )
            )
            time.sleep(.1)

    def preview_option_trade(self):
        self.confirm_window = ConfirmOptionTradeWindow(self, self.CURRENT_TRADE_OPTION_NAME, self.wi, self.port, self.orders)



