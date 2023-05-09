from PySide6.QtWidgets import QDialog
from widgets.portfolio.portfolio import Portfolio
from widgets.portfolio.port_overview_widget import PortfolioOverview
from widgets.portfolio.portfolio_widget import PortfolioWidget
from widgets.portfolio.watchlist import Watchlist
from widgets.portfolio.pie_chart_widget import PortfolioPieChart
from widgets.portfolio.trades_widget import TradesWidget

class PortfolioTab(QDialog):
    def __init__(self, portfolio: Portfolio, watchlist_tickers: list, orders: list):
        super().__init__()
        self.setStyleSheet('background-color: deepskyblue;')
        self.setAutoFillBackground(True)

        tickers = [position.ticker for position in portfolio]

        self.port = PortfolioWidget(tickers)

        self.port.setParent(self)
        self.port.parent().setStyleSheet('background-color: deepskyblue;')
        self.port.setGeometry(10, 270, 870, 390)
        self.port.update(portfolio)

        self.port_overview = PortfolioOverview()
        self.port_overview.setParent(self)
        self.port_overview.setGeometry(10, 10, 250, 250)
        self.port_overview.update(self.port.table, portfolio)

        self.watchlist = Watchlist(watchlist_tickers)
        self.watchlist.setParent(self)
        self.watchlist.setGeometry(270, 10, 500, 250)
        self.watchlist.update(watchlist_tickers)

        self.chart = PortfolioPieChart(self.port, portfolio, self.port_overview)
        self.chart.setParent(self)
        self.chart.setGeometry(780, 1, 500, 265)
        self.chart.update(self.port, portfolio, self.port_overview)

        self.trades = TradesWidget(orders)
        self.trades.setParent(self)
        self.trades.setGeometry(890, 270, 385, 390)
        self.trades.update(orders)
