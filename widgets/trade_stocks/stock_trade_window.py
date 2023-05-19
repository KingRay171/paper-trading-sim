from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QWidget, QTableWidgetItem, QLabel, QSpinBox, QHBoxLayout, QPushButton, QVBoxLayout
import yahooquery as yq
import math
import time
from threading import Thread
from widgets.portfolio.portfolio import Portfolio

class StockTradeWindow(QDialog):
    def __init__(self, parent: QWidget, orders: list):
        super().__init__(parent=parent)
        self.setWindowTitle("Preview Order")
        self.orders = orders
        self.setLayout(QVBoxLayout())
        self.CURRENT_TRADE_STOCK_NAME = parent.parent().search.search.text().split(' ')[0]
        self.ticker_widget = QWidget()
        self.ticker_widget.setLayout(QHBoxLayout())
        self.ticker_widget.layout().addWidget(QLabel('Ticker:'))
        self.ticker_label = QLabel(self.CURRENT_TRADE_STOCK_NAME)
        self.ticker_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.ticker_widget.layout().addWidget(self.ticker_label)
        self.layout().addWidget(self.ticker_widget)
        self.transaction_widget = QWidget()
        self.transaction_widget.setLayout(QHBoxLayout())
        self.transaction_widget.layout().addWidget(QLabel('Transaction:'))
        self.transaction_label = QLabel(parent.action_combobox.currentText())
        self.transaction_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.transaction_widget.layout().addWidget(self.transaction_label)
        self.layout().addWidget(self.transaction_widget)
        self.ordertype_widget = QWidget()
        self.ordertype_widget.setLayout(QHBoxLayout())
        self.ordertype_widget.layout().addWidget(QLabel('Order Type:'))
        self.ordertype_label = QLabel(parent.type_combobox.currentText())
        self.ordertype_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.ordertype_widget.layout().addWidget(self.ordertype_label)
        self.layout().addWidget(self.ordertype_widget)
        self.estprice_widget = QWidget()
        self.estprice_widget.setLayout(QHBoxLayout())
        self.estprice_widget.layout().addWidget(QLabel('Estimated Price'))
        self.estprice_label = QLabel()
        if parent.type_combobox.currentText() == 'Market':
            if parent.action_combobox.currentText() == 'Buy':
                self.estprice_label.setText(parent.limit_stop_ask.text().split('\n')[1])
            else:
                self.estprice_label.setText(parent.limit_stop_bid.text().split('\n')[1])
        else:
            # change to limit/stop price
            self.estprice_label.setText(parent.limit_stop_bid.text())
        self.estprice_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.estprice_widget.layout().addWidget(self.estprice_label)
        self.layout().addWidget(self.estprice_widget)
        self.qty_widget = QWidget()
        self.qty_widget.setLayout(QHBoxLayout())
        self.qty_widget.layout().addWidget(QLabel('Quantity:'))
        self.qty_label = QLabel(f"{parent.qty_spinbox.value()}")
        self.qty_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.qty_widget.layout().addWidget(self.qty_label)
        self.layout().addWidget(self.qty_widget)
        self.est_cost_widget = QWidget()
        self.est_cost_widget.setLayout(QHBoxLayout())
        self.est_cost_widget.layout().addWidget(
            QLabel(
                "Estimated Net Debit"
                if self.transaction_label.text() == "Buy"
                else "Estimated Net Credit"
            )
        )
        self.est_cost_label = QLabel(f"{int(self.qty_label.text()) * float(self.estprice_label.text())}")
        self.est_cost_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.est_cost_widget.layout().addWidget(self.est_cost_label)
        self.layout().addWidget(self.est_cost_widget)
        self.actions_widget = QWidget()
        self.actions_widget.setLayout(QHBoxLayout())
        self.cancel_button = QPushButton('Change Order')
        self.cancel_button.clicked.connect(self.done(0))
        self.actions_widget.layout().addWidget(self.cancel_button)
        self.ok_button = QPushButton('Confirm Order')

        self.ok_button.clicked.connect(self.ok_button_clicked)
        self.actions_widget.layout().addWidget(self.ok_button)
        self.layout().addWidget(self.actions_widget)

    def ok_button_clicked(self):
        self.orders.append(
            [
                self.CURRENT_TRADE_STOCK_NAME,
                self.transaction_label.text(),
                self.ordertype_label.text(),
                self.estprice_label.text(),
                float(self.qty_label.text())
            ]
        )
        self.done(0)