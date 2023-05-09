from PySide6.QtWidgets import QGroupBox, QTableWidget, QTableWidgetItem, QAbstractItemView, QHBoxLayout
from PySide6.QtGui import QFont
import dependencies.perficon as perficon
import yahooquery as yq
from widgets.portfolio.portfolio import Portfolio

class PortfolioWidget(QGroupBox):
    def __init__(self, portfolio_tickers: list):
        super().__init__()
        self.setTitle("Your Portfolio")
        self.setStyleSheet('background-color: white')
        self.setLayout(QHBoxLayout())

        self.table = QTableWidget(self)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setFont(QFont('arial', 10))
        self.table.setRowCount(len(portfolio_tickers) - 1)
        self.table.setColumnCount(8)
        self.table.setStyleSheet('background-color: white')
        headers = (
            "Ticker", "Today's Performance", "Current Price", "P/L Per Share Today",
            "Purchase Price", "# of Shares", "Total Value", "Position Gain/Loss"
        )
        for idx, header in enumerate(headers):
            self.table.setHorizontalHeaderItem(idx, QTableWidgetItem(header))
            self.table.horizontalHeaderItem(idx).setFont(QFont('arial', 10))
        for row in range(self.table.rowCount()):
            for column in range(self.table.columnCount()):
                self.table.setItem(row, column, QTableWidgetItem())
        self.layout().addWidget(self.table)
        self.table.resizeColumnsToContents()

    def update(self, portfolio: Portfolio):
        tickers = [position.ticker for position in portfolio[1:]]
        bases = [position.basis for position in portfolio[1:]]
        amts = [position.amt for position in portfolio[1:]]
        types = [position.asset_type for position in portfolio[1:]]

        prices = yq.Ticker(tickers).price
        price_data = [
            (
                prices[ticker]['regularMarketPrice'],
                prices[ticker]['regularMarketOpen'],
                prices[ticker]['regularMarketPreviousClose']
            )
            for ticker in tickers
        ]

        port_zip = zip(price_data, bases, amts)
        for idx, (data, basis, amt) in enumerate(port_zip):
            # get the current price and the price it last closed at

            current_price = data[0]
            last_close = data[2]
            # calculate the return since the position was opened in dollar and percent terms
            total_return = (current_price - basis) * amt
            percent_change = round(total_return / (basis * amt) * 100, 2)
            if amt < 0:
                percent_change *= -1
            # update the table with the new information

            if self.table.item(idx, 0) is None:
                column_count = self.table.columnCount()
                for k in range(column_count):
                    self.table.setItem(idx, k, QTableWidgetItem())


            self.table.item(idx, 0).setText(tickers[idx])

            self.table.item(idx, 1).setIcon(perficon.update_ticker_icon(data))

            self.table.item(idx, 2).setText(f'${current_price:0,.2f}')

            last_close_change = current_price - last_close
            self.table.item(idx, 3).setText(
                f'${last_close_change:0,.2f} ({round(last_close_change / last_close * 100, 2)}%)'
            )

            self.table.item(idx, 4).setText(f'${basis:0,.2f}')

            self.table.item(idx, 5).setText(f"{amt}")

            option_modifier = 100 if types[idx] == 'Option' else 1

            self.table.item(idx, 6).setText(f'${(current_price * amt * option_modifier):0,.2f}')

            self.table.item(idx, 7).setText(
                f'${total_return * option_modifier:0,.2f} ({percent_change}%)')
