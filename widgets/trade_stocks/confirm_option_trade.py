from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QWidget, QTableWidgetItem, QLabel, QSpinBox, QHBoxLayout, QPushButton, QVBoxLayout
from widgets.portfolio.portfolio import Portfolio

class ConfirmOptionTradeWindow(QDialog):
    def __init__(self, parent: QWidget, option: str, wi: QTableWidgetItem, port: Portfolio, orders: list) -> None:
        super().__init__(parent)
        self.setWindowTitle("Confirm Trade")
        self.setLayout(QVBoxLayout())
        self.setStyleSheet("background-color: white")

        ticker_widget = QWidget()
        ticker_widget.setLayout(QHBoxLayout())
        ticker_widget.layout().addWidget(QLabel('Ticker:'))
        ticker_label = QLabel(option)
        ticker_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        ticker_widget.layout().addWidget(ticker_label)
        self.layout().addWidget(ticker_widget)

        transaction_widget = QWidget()
        transaction_widget.setLayout(QHBoxLayout())
        transaction_widget.layout().addWidget(QLabel('Transaction:'))
        transaction_label = QLabel(parent.windowTitle()[:4])
        transaction_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        transaction_widget.layout().addWidget(transaction_label)
        self.layout().addWidget(transaction_widget)


        ordertype_widget = QWidget()
        ordertype_widget.setLayout(QHBoxLayout())
        ordertype_widget.layout().addWidget(QLabel('Order Type:'))
        ordertype_label = QLabel(parent.ordertype_combobox.currentText())
        ordertype_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        ordertype_widget.layout().addWidget(ordertype_label)
        self.layout().addWidget(ordertype_widget)

        estprice_widget = QWidget()
        estprice_widget.setLayout(QHBoxLayout())
        estprice_widget.layout().addWidget(QLabel('Estimated Price'))
        estprice_label = QLabel(parent.trade_price.text())
        estprice_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        estprice_widget.layout().addWidget(estprice_label)
        self.layout().addWidget(estprice_widget)

        qty_widget = QWidget()
        qty_widget.setLayout(QHBoxLayout())
        qty_widget.layout().addWidget(QLabel('Quantity:'))
        qty_label = QLabel(f"{parent.quantity_spinbox.value()}")
        qty_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        qty_widget.layout().addWidget(qty_label)
        self.layout().addWidget(qty_widget)

        est_cost_widget = QWidget()
        est_cost_widget.setLayout(QHBoxLayout())
        est_cost_widget.layout().addWidget(
            QLabel(
                "Estimated Net Debit"
                if parent.windowTitle()[:3] == "Buy"
                else "Estimated Net Credit"
            )
        )

        est_cost_label = QLabel(f"{int(qty_label.text()) * float(estprice_label.text())}")
        est_cost_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        est_cost_widget.layout().addWidget(est_cost_label)
        self.layout().addWidget(est_cost_widget)

        actions_widget = QWidget()
        actions_widget.setLayout(QHBoxLayout())
        cancel_button = QPushButton('Change Order')
        def cancel_button_clicked():
            self.done(0)
            parent.done(0)
        cancel_button.clicked.connect(cancel_button_clicked)
        actions_widget.layout().addWidget(cancel_button)
        ok_button = QPushButton('Confirm Order')
        def ok_button_clicked():
            orders.append(
                [
                    option,
                    'Buy' if transaction_label.text() == 'Buy ' else transaction_label.text(),
                    ordertype_label.text(),
                    estprice_label.text(),
                    float(qty_label.text())
                ]
            )
            self.done(0)
        ok_button.clicked.connect(ok_button_clicked)
        actions_widget.layout().addWidget(ok_button)
        self.layout().addWidget(actions_widget)

        self.exec()
