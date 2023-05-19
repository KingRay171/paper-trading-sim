from PySide6.QtWidgets import QTabWidget, QDialog, QGroupBox, QTableWidget, QTableWidgetItem
from PySide6.QtCharts import QLineSeries, QDateTimeAxis
from PySide6.QtCore import QDateTime, Qt
from PySide6.QtGui import QFont
import yahooquery as yq
from dependencies import optionchain as oc
from widgets.trade_stocks.stocks import StocksDialog
from widgets.trade_stocks.options import OptionsDialog

class StockTradeTab(QTabWidget):
    def __init__(self, string_list, port, orders):
        super().__init__()
        self.setStyleSheet('background-color: deepskyblue;')
        self.stocks = StocksDialog(string_list, orders)

        self.options = OptionsDialog(string_list, port)
        self.addTab(self.stocks, "Stocks")
        self.addTab(self.options, "Options")
        self.stocks.search.button.clicked.connect(self.search_button_clicked)
        self.arial_10 = QFont('arial', 10)
        self.symbol = None
        self.orders = orders
        self.update_thread = None

    def search_button_clicked(self):

        self.symbol = self.stocks.search.search.text().split(' ')[0]
        ticker = yq.Ticker(self.symbol)
        self.stocks.order_view.max_btn.setEnabled(True)
        prices = ticker.history('1d', '1m')
        self.stocks.chart.chart.removeAllSeries()
        self.stocks.chart.lineseries = QLineSeries()
        for idx, close in enumerate(prices.loc[:, 'close']):
            price_dt = QDateTime().fromString(f"{prices.index[idx][1]}"[0:19], "yyyy-MM-dd hh:mm:ss")
            epoch_dt = float(price_dt.toMSecsSinceEpoch())
            self.stocks.chart.lineseries.append(epoch_dt, close)

        self.stocks.chart.chart.addSeries(self.stocks.chart.lineseries)

        self.stocks.chart.chart.createDefaultAxes()
        self.stocks.chart.chart.axes(Qt.Orientation.Horizontal)[0].hide()

        self.stocks.chart.xaxis = QDateTimeAxis()
        self.stocks.chart.xaxis.setTickCount(7)
        self.stocks.chart.xaxis.setFormat("h:mm")
        self.stocks.chart.xaxis.setTitleText("Date")
        self.stocks.chart.xaxis.setVisible(True)

        self.stocks.chart.chart.addAxis(self.stocks.chart.xaxis, Qt.AlignmentFlag.AlignBottom)
        self.stocks.chart.lineseries.attachAxis(self.stocks.chart.xaxis)


        option_chain_list = oc.split_option_chain(ticker.option_chain)
        self.options.clear()
        for chain in option_chain_list:
            chain_dialog = QTabWidget(self.options)
            chain_dialog.setStyleSheet('background-color: deepskyblue')

            chain_dialog.calls = QDialog(chain_dialog)
            chain_dialog.calls.setStyleSheet('background-color: deepskyblue')

            chain_dialog.puts = QDialog(chain_dialog)
            chain_dialog.puts.setStyleSheet('background-color: deepskyblue')


            chain_dialog.calls.gb = QGroupBox(chain_dialog.calls)
            chain_dialog.calls.gb.setTitle(f'Option Chain for {str(chain.index[0][1])[:10]}')
            chain_dialog.calls.gb.setGeometry(10, 110, 1260, 500)
            chain_dialog.calls.gb.setStyleSheet('background-color: white;')

            chain_dialog.calls.gb.chain = QTableWidget(chain_dialog.calls.gb)
            chain_dialog.calls.gb.chain.setGeometry(10, 20, 1250, 450)
            chain_dialog.calls.gb.chain.setColumnCount(23)
            chain_dialog.calls.gb.chain.setHorizontalHeaderItem(0, QTableWidgetItem('Strike'))
            chain_dialog.calls.gb.chain.setHorizontalHeaderItem(1, QTableWidgetItem('Moneyness'))
            chain_dialog.calls.gb.chain.setHorizontalHeaderItem(2, QTableWidgetItem('Bid'))
            chain_dialog.calls.gb.chain.setHorizontalHeaderItem(3, QTableWidgetItem('Ask'))
            chain_dialog.calls.gb.chain.setHorizontalHeaderItem(4, QTableWidgetItem('Mark'))
            chain_dialog.calls.gb.chain.setHorizontalHeaderItem(5, QTableWidgetItem('Chg'))
            chain_dialog.calls.gb.chain.setHorizontalHeaderItem(6, QTableWidgetItem('% Chg'))
            chain_dialog.calls.gb.chain.setHorizontalHeaderItem(7, QTableWidgetItem('Volume'))
            chain_dialog.calls.gb.chain.setHorizontalHeaderItem(8, QTableWidgetItem('Imp Vol'))
            chain_dialog.calls.gb.chain.setHorizontalHeaderItem(9, QTableWidgetItem('Open Int'))
            chain_dialog.calls.gb.chain.setHorizontalHeaderItem(10, QTableWidgetItem('Delta'))
            chain_dialog.calls.gb.chain.setHorizontalHeaderItem(11, QTableWidgetItem('Gamma'))
            chain_dialog.calls.gb.chain.setHorizontalHeaderItem(12, QTableWidgetItem('Theta'))
            chain_dialog.calls.gb.chain.setHorizontalHeaderItem(13, QTableWidgetItem('Vega'))
            chain_dialog.calls.gb.chain.setHorizontalHeaderItem(14, QTableWidgetItem('Rho'))
            chain_dialog.calls.gb.chain.setHorizontalHeaderItem(15, QTableWidgetItem('Vanna'))
            chain_dialog.calls.gb.chain.setHorizontalHeaderItem(16, QTableWidgetItem('Charm'))
            chain_dialog.calls.gb.chain.setHorizontalHeaderItem(17, QTableWidgetItem('Vomma'))
            chain_dialog.calls.gb.chain.setHorizontalHeaderItem(18, QTableWidgetItem('Veta'))
            chain_dialog.calls.gb.chain.setHorizontalHeaderItem(19, QTableWidgetItem('Speed'))
            chain_dialog.calls.gb.chain.setHorizontalHeaderItem(20, QTableWidgetItem('Zomma'))
            chain_dialog.calls.gb.chain.setHorizontalHeaderItem(21, QTableWidgetItem('Color'))
            chain_dialog.calls.gb.chain.itemClicked.connect(
                lambda wi: self.options.init_option_trade(wi, self.options, self.symbol, self.orders)
            )

            chain_dialog.calls.gb.chain.horizontalHeader().setFont(self.arial_10)
            chain_dialog.calls.gb.chain.resizeColumnsToContents()
            chain_dialog.calls.gb.chain.setFont(self.arial_10)

            chain_dialog.puts.gb = QGroupBox(chain_dialog.puts)
            chain_dialog.puts.gb.setTitle(f'Option Chain for {str(chain.index[0][1])[:10]}')
            chain_dialog.puts.gb.setGeometry(10, 110, 1260, 500)
            chain_dialog.puts.gb.setStyleSheet('background-color: white;')

            chain_dialog.puts.gb.chain = QTableWidget(chain_dialog.puts.gb)
            chain_dialog.puts.gb.chain.setGeometry(10, 20, 1250, 450)
            chain_dialog.puts.gb.chain.setColumnCount(23)
            chain_dialog.puts.gb.chain.setHorizontalHeaderItem(0, QTableWidgetItem('Strike'))
            chain_dialog.puts.gb.chain.setHorizontalHeaderItem(1, QTableWidgetItem('Moneyness'))
            chain_dialog.puts.gb.chain.setHorizontalHeaderItem(2, QTableWidgetItem('Bid'))
            chain_dialog.puts.gb.chain.setHorizontalHeaderItem(3, QTableWidgetItem('Ask'))
            chain_dialog.puts.gb.chain.setHorizontalHeaderItem(4, QTableWidgetItem('Mark'))
            chain_dialog.puts.gb.chain.setHorizontalHeaderItem(5, QTableWidgetItem('Chg'))
            chain_dialog.puts.gb.chain.setHorizontalHeaderItem(6, QTableWidgetItem('% Chg'))
            chain_dialog.puts.gb.chain.setHorizontalHeaderItem(7, QTableWidgetItem('Volume'))
            chain_dialog.puts.gb.chain.setHorizontalHeaderItem(8, QTableWidgetItem('Imp Vol'))
            chain_dialog.puts.gb.chain.setHorizontalHeaderItem(9, QTableWidgetItem('Open Int'))
            chain_dialog.puts.gb.chain.setHorizontalHeaderItem(10, QTableWidgetItem('Delta'))
            chain_dialog.puts.gb.chain.setHorizontalHeaderItem(11, QTableWidgetItem('Gamma'))
            chain_dialog.puts.gb.chain.setHorizontalHeaderItem(12, QTableWidgetItem('Theta'))
            chain_dialog.puts.gb.chain.setHorizontalHeaderItem(13, QTableWidgetItem('Vega'))
            chain_dialog.puts.gb.chain.setHorizontalHeaderItem(14, QTableWidgetItem('Rho'))
            chain_dialog.puts.gb.chain.setHorizontalHeaderItem(15, QTableWidgetItem('Vanna'))
            chain_dialog.puts.gb.chain.setHorizontalHeaderItem(16, QTableWidgetItem('Charm'))
            chain_dialog.puts.gb.chain.setHorizontalHeaderItem(17, QTableWidgetItem('Vomma'))
            chain_dialog.puts.gb.chain.setHorizontalHeaderItem(18, QTableWidgetItem('Veta'))
            chain_dialog.puts.gb.chain.setHorizontalHeaderItem(19, QTableWidgetItem('Speed'))
            chain_dialog.puts.gb.chain.setHorizontalHeaderItem(20, QTableWidgetItem('Zomma'))
            chain_dialog.puts.gb.chain.setHorizontalHeaderItem(21, QTableWidgetItem('Color'))
            chain_dialog.puts.gb.chain.itemClicked.connect(
                lambda wi: self.options.init_option_trade(wi, self.options, self.symbol, self.orders)
            )


            chain_dialog.puts.gb.chain.horizontalHeader().setFont(self.arial_10)
            chain_dialog.puts.gb.chain.resizeColumnsToContents()
            chain_dialog.puts.gb.chain.setFont(self.arial_10)

            chain_dialog.addTab(chain_dialog.calls, "Calls")
            chain_dialog.addTab(chain_dialog.puts, "Puts")

            self.options.addTab(chain_dialog, f"{chain.index[0][1]}"[:10])


    def update_stock_trade_dialog(self, ticker: str):
        try:
            all_modules = yq.Ticker(ticker).all_modules[ticker]

            quote_type = all_modules['quoteType']
            prices = all_modules['price']
            summary = all_modules['summaryDetail']

            self.stocks.basic_info.full_name_label.setText(quote_type['shortName'])
            self.stocks.basic_info.price_label.setText(
                f"{prices['regularMarketPrice']} ({prices['regularMarketChange']})"
            )
            self.stocks.basic_info.bid_label.setText(f"Bid: {summary['bid']} ({summary['bidSize']})")
            self.stocks.basic_info.ask_label.setText(f"Ask: {summary['ask']} ({summary['askSize']})")

            self.stocks.order_view.limit_stop_bid.setText(f"Bid:\n{summary['bid']}\n({summary['bidSize']})")
            self.stocks.order_view.limit_stop_ask.setText(f"Ask:\n{summary['ask']}\n({summary['askSize']})")
            self.stocks.order_view.limit_stop_mid.setText(f"Mid:\n{(summary['bid'] + summary['ask']) / 2}")
            slider_range = (summary['ask'] - summary['bid']) * 100
            self.stocks.order_view.price_slider.setRange(0, slider_range)
        except KeyError:
            pass

    def update_options(self):
        self.options.update(self.symbol)
