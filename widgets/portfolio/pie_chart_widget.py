from PySide6.QtCharts import QPieSeries, QChart, QChartView
from PySide6.QtWidgets import QSizePolicy
from widgets.portfolio.portfolio_widget import PortfolioWidget
from widgets.portfolio.portfolio import Portfolio
from widgets.portfolio.port_overview_widget import PortfolioOverview
from functools import reduce

class PortfolioPieChart(QChartView):
    def __init__(self, table: PortfolioWidget, portfolio: Portfolio, port_overview: PortfolioOverview):
        super().__init__()
        self.pie_series = QPieSeries()
        self.pie_series.append("Long ETFs", 1)
        self.pie_series.append("Short ETFs", 2)
        self.pie_series.append("Long Stocks", 3)
        self.pie_series.append("Short Stocks", 4)
        self.pie_series.append("Long Options", 5)
        self.pie_series.append("Short Options", 6)
        self.pie_series.append("Cash", 7)
        self._chart = QChart()
        self._chart.addSeries(self.pie_series)
        self._chart.setTitle("Positions by Asset Class")
        self._chart.setVisible(True)
        self.setChart(self._chart)
        self.update(table, portfolio, port_overview)


    def update(self, table: PortfolioWidget, portfolio: Portfolio, port_overview: PortfolioOverview):
        long_etfs = 0
        short_etfs = 0
        long_stocks = 0
        short_stocks = 0
        long_options = 0
        short_options = 0
        cash_amount = 0

        portfolio_amts = [position.amt for position in portfolio]
        portfolio_asset_types = [position.asset_type for position in portfolio]


        for idx, amount in enumerate(portfolio_amts):
            if portfolio_asset_types[idx] != 'Liquidity':
                asset_price = float(table.table.item(idx - 1, 2).text()[1:])

            match portfolio_asset_types[idx]:
                case "ETF":
                    if amount > 0:
                        long_etfs += amount * asset_price
                    else:
                        short_etfs -= amount * asset_price
                case "Liquidity":
                    cash_amount += amount
                case "Stock":
                    if amount > 0:
                        long_stocks += amount * asset_price
                    else:
                        short_stocks -= amount * asset_price
                case "Option":
                    if amount > 0:
                        long_options += amount * asset_price * 100
                    else:
                        short_options -= amount * asset_price * 100

        cash_amount -= 2 * float(port_overview.short_assets.text()[2:].replace(",", ""))
        values = [
            float(table.table.item(i, 2).text()[1:]) * portfolio_amts[i + 1]
            for i in range(table.table.rowCount())
        ]
        values.append(portfolio_amts[0])

        new_val = reduce(lambda x, y: x + y, values)
        portfolio_nav = new_val

        # loads values into pie chart and displays them


        self.pie_series.slices()[0].setValue(round(long_etfs / portfolio_nav * 100, 2))
        if long_etfs != 0:
            self.pie_series.slices()[0].setLabel(
                f"Long ETFs: {round(long_etfs / portfolio_nav * 100, 2)}%"
            )
            self.pie_series.slices()[0].setLabelVisible(True)

        self.pie_series.slices()[1].setValue(round(short_etfs / portfolio_nav * 100, 2))
        if short_etfs != 0:
            self.pie_series.slices()[1].setLabel(
                f"Short ETFs: {round(short_etfs / portfolio_nav * 100, 2)}%"
            )
            self.pie_series.slices()[1].setLabelVisible(True)

        self.pie_series.slices()[2].setValue(round(long_stocks / portfolio_nav * 100, 2))
        if long_stocks != 0:
            self.pie_series.slices()[2].setLabel(
                f"Long Stocks: {round(long_stocks / portfolio_nav * 100, 2)}%"
            )
            self.pie_series.slices()[2].setLabelVisible(True)

        self.pie_series.slices()[3].setValue(round(short_stocks / portfolio_nav * 100, 2))
        if short_stocks != 0:
            self.pie_series.slices()[3].setLabel(
                f"Short Stocks: {round(short_stocks / portfolio_nav * 100, 2)}%"
            )
            self.pie_series.slices()[3].setLabelVisible(True)

        self.pie_series.slices()[4].setValue(long_options / portfolio_nav * 100)
        if long_options != 0:
            self.pie_series.slices()[4].setLabel(
                f"Long Options: {round(long_options / portfolio_nav * 100, 2)}%"
            )
            self.pie_series.slices()[4].setLabelVisible(True)

        self.pie_series.slices()[5].setValue(short_options / portfolio_nav * 100)
        if short_options != 0:
            self.pie_series.slices()[5].setLabel(
                f"Short Options: {round(short_options / portfolio_nav * 100, 2)}%"
            )
            self.pie_series.slices()[5].setLabelVisible(True)

        self.pie_series.slices()[6].setValue(cash_amount / portfolio_nav * 100)
        if cash_amount != 0:
            self.pie_series.slices()[6].setLabel(
                f"Cash: {round(cash_amount / portfolio_nav * 100, 2)}%"
            )
            self.pie_series.slices()[6].setLabelVisible(True)
