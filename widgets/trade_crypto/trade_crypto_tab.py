from PySide6.QtWidgets import QTabWidget
from widgets.trade_crypto.trade_dialog import CryptoTradeDialog

class CryptoTradeTab(QTabWidget):
    def __init__(self, orders):
        super().__init__()
        self.setStyleSheet('background-color: goldenrod;')
        self.trade = CryptoTradeDialog(orders)
        self.addTab(self.trade, "Crypto")

