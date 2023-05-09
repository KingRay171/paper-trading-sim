from PySide6.QtWidgets import QGroupBox, QHBoxLayout, QPushButton

class BroadMarketWidget(QGroupBox):
    def __init__(self):
        super().__init__()
        self.setTitle('Broad Market Indicies')
        self.setStyleSheet('background-color: white')
        self.setLayout(QHBoxLayout())

        self.spy = QPushButton("Chart SPY")
        self.layout().addWidget(self.spy)
        self.qqq = QPushButton("Chart QQQ")
        self.layout().addWidget(self.qqq)
        self.dia = QPushButton("Chart DIA")
        self.layout().addWidget(self.dia)
        self.vix = QPushButton("Chart VIX")
        self.layout().addWidget(self.vix)