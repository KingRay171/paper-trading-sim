from PySide6.QtWidgets import QGroupBox, QScrollArea, QWidget, QHBoxLayout

class MomentumView(QGroupBox):
    def __init__(self):
        super().__init__()
        self.setTitle("Momentum Indicators")
        self.setStyleSheet('background-color: white')
        self.setLayout(QHBoxLayout())
        self.momentum_scrollarea = QScrollArea()
        self.momentum_widget = QWidget()
        self.layout()


