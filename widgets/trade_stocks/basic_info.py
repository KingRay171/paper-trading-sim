from PySide6.QtWidgets import QGroupBox, QLabel

class StockBasicInfo(QGroupBox):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: white;")
        self.setTitle("Information")

        self.full_name_label = QLabel(self)
        self.full_name_label.setText("")
        self.full_name_label.setGeometry(10, 15, 150, 15)

        self.price_label = QLabel(self)
        self.price_label.setGeometry(160, 15, 100, 20)

        self.bid_label = QLabel(self)
        self.bid_label.setGeometry(10, 30, 140, 20)

        self.ask_label = QLabel(self)
        self.ask_label.setGeometry(160, 30, 140, 20)
