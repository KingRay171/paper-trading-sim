from PySide6.QtWidgets import QDialog, QTabWidget, QGroupBox, QTableWidgetItem
from PySide6.QtCharts import QLineSeries, QDateTimeAxis
from PySide6.QtCore import QDateTime, Qt
from dependencies import optionchain as oc
import yahooquery as yq
from widgets.trade_stocks.search_bar import SearchBar
from widgets.trade_stocks.basic_info import StockBasicInfo
from widgets.trade_stocks.order_view import OrderView
from widgets.trade_stocks.chart import StockTradeChart

class StocksDialog(QDialog):
    def __init__(self, string_list, orders):
        super().__init__()
        self.setStyleSheet('background-color: deepskyblue;')
        self.search = SearchBar(string_list)
        self.search.setParent(self)
        self.search.setGeometry(10, 10, 960, 70)

        self.basic_info = StockBasicInfo()
        self.basic_info.setParent(self)
        self.basic_info.setGeometry(980, 10, 300, 70)

        self.order_view = OrderView(orders)
        self.order_view.setParent(self)
        self.order_view.setGeometry(10, 90, 450, 400)

        self.chart = StockTradeChart()
        self.chart.setParent(self)
        self.chart.setGeometry(500, 90, 650, 400)




