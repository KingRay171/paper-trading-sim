from PySide6.QtWidgets import QGroupBox, QTableWidget, QTableWidgetItem, QAbstractItemView, QHBoxLayout
from PySide6.QtGui import QFont
import dependencies.perficon as perficon
import yahooquery as yq

class TradesWidget(QGroupBox):
    def __init__(self, orders: list):
        super().__init__()
        self.setTitle("Open Trades")
        self.setStyleSheet('background-color: white')
        self.setLayout(QHBoxLayout())

        self.table = QTableWidget(self)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setFont(QFont('arial', 10))
        self.table.setRowCount(len(orders))
        self.table.setColumnCount(5)
        self.table.setStyleSheet('background-color: white')

        headers = ("Ticker", "Transaction", "Order Type", "Est. Price", "Quantity")
        for idx, header in enumerate(headers):
            self.table.setHorizontalHeaderItem(idx, QTableWidgetItem(header))
            self.table.horizontalHeaderItem(idx).setFont(QFont('arial', 10))
        for row in range(self.table.rowCount()):
            for column in range(self.table.columnCount()):
                self.table.setItem(row, column, QTableWidgetItem())
        self.layout().addWidget(self.table)
        self.table.resizeColumnsToContents()

    def update(self, orders: list):
        self.table.setRowCount(len(orders))
        for row in range(self.table.rowCount()):
            for column in range(self.table.columnCount()):
                self.table.setItem(row, column, QTableWidgetItem(f"{orders[row][column]}"))




