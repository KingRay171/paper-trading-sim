from PySide6.QtWidgets import QGroupBox, QLabel, QComboBox, QSpinBox, QPushButton, QSlider
from PySide6.QtCore import Qt
from widgets.trade_stocks.stock_trade_window import StockTradeWindow

class OrderView(QGroupBox):
    def __init__(self, orders):
        super().__init__()
        self.setStyleSheet("background-color: white;")
        self.setTitle("Create Order")

        self.orders = orders

        self.action_label = QLabel(self)
        self.action_label.setText("Action")
        self.action_label.setGeometry(10, 50, 100, 15)

        self.action_combobox = QComboBox(self)
        self.action_combobox.addItems(('Buy', 'Sell'))
        self.action_combobox.setGeometry(10, 70, 100, 40)

        self.qty_label = QLabel(self)
        self.qty_label.setText("Quantity")
        self.qty_label.setGeometry(10, 150, 100, 15)

        self.qty_spinbox = QSpinBox(self)
        self.qty_spinbox.setGeometry(10, 170, 100, 40)

        self.max_btn = QPushButton(self)
        self.max_btn.setText("Max")
        self.max_btn.setGeometry(120, 170, 100, 40)
        self.max_btn.setEnabled(False)

        self.type_label = QLabel(self)
        self.type_label.setText("Order Type")
        self.type_label.setGeometry(10, 230, 100, 15)

        self.type_combobox = QComboBox(self)
        self.type_combobox.addItems(('Market', 'Limit', 'Stop'))
        self.type_combobox.setGeometry(10, 250, 100, 40)
        self.type_combobox.currentTextChanged.connect(self.on_ordertype_change)

        self.price_slider = QSlider(self)
        self.price_slider.setOrientation(Qt.Orientation.Horizontal)
        self.price_slider.setRange(0, 10)
        self.price_slider.setGeometry(120, 250, 250, 40)
        self.price_slider.setVisible(False)

        self.limit_stop_bid = QLabel(self)
        self.limit_stop_bid.setGeometry(120, 300, 50, 50)
        self.limit_stop_bid.setVisible(False)

        self.limit_stop_ask = QLabel(self)
        self.limit_stop_ask.setGeometry(350, 300, 50, 50)
        self.limit_stop_ask.setVisible(False)

        self.limit_stop_mid = QLabel(self)
        self.limit_stop_mid.setGeometry(240, 300, 50, 50)
        self.limit_stop_mid.setVisible(False)

        self.preview_order = QPushButton(self)
        self.preview_order.setText("Preview Order")
        self.preview_order.setGeometry(50, 340, 360, 50)
        self.preview_order.clicked.connect(self.on_previeworder_click)

        self.wnd = None

    def on_ordertype_change(self, value):
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

    def on_previeworder_click(self):
        self.wnd = StockTradeWindow(self, self.orders)
        self.wnd.exec()
