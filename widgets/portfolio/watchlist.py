from PySide6.QtWidgets import QGroupBox, QTableWidget, QTableWidgetItem, QAbstractItemView, QHBoxLayout
from PySide6.QtGui import QFont
import dependencies.perficon as perficon
import yahooquery as yq

class Watchlist(QGroupBox):
    def __init__(self, watchlist_tickers: list):
        super().__init__()
        self.setTitle("Your Watchlist")
        self.setStyleSheet('background-color: white;')
        self.setLayout(QHBoxLayout())

        self.table = QTableWidget(self)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setRowCount(len(watchlist_tickers))
        self.table.setColumnCount(4)

        headers = ("Ticker", "Today's Performance", "Current Price", "Gain/Loss Per Share")
        for idx, header in enumerate(headers):
            self.table.setHorizontalHeaderItem(idx, QTableWidgetItem(header))
            self.table.horizontalHeaderItem(idx).setFont(QFont('arial', 10))
        for row in range(self.table.rowCount()):
            for column in range(self.table.columnCount()):
                self.table.setItem(row, column, QTableWidgetItem())
        self.table.setFont(QFont('arial', 10))
        self.layout().addWidget(self.table)
        self.table.resizeColumnsToContents()

    def update(self, watchlist_tickers: list[str]):
        prices = yq.Ticker(watchlist_tickers).price
        price_data = [
            (
                prices[ticker]['regularMarketPrice'],
                prices[ticker]['regularMarketOpen'],
                prices[ticker]['regularMarketPreviousClose']
            ) for ticker in watchlist_tickers
        ]
        for idx, data in enumerate(price_data):

            ticker_current = data[0]
            last_close = data[2]

            self.table.item(idx, 0).setText(watchlist_tickers[idx])

            self.table.item(idx, 1).setIcon(perficon.update_ticker_icon(data))

            self.table.item(idx, 2).setText(f'${ticker_current:0,.2f}')

            last_close_change = ticker_current - last_close
            self.table.item(idx, 3).setText(
                f'${last_close_change:0,.2f} ({round(last_close_change / last_close * 100, 2)}%)'
            )
