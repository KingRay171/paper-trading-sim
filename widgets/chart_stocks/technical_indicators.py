from PySide6.QtWidgets import QDialog, QGroupBox, QHBoxLayout
from widgets.chart_stocks.momentum_indicators import MomentumView
from widgets.chart_stocks.trend_indicators import TrendView

class IndicatorsWidget(QDialog):
    def __init__(self, selected_ta):
        super().__init__()
        self.setLayout(QHBoxLayout())
        combobox_items = [f"{i}" for i in range(0, 16)]

        self.momentum_gb = QGroupBox()
        self.momentum_gb.setTitle('Momentum Indicators')
        self.momentum_gb.setStyleSheet('background-color: white;')
        self.layout().addWidget(MomentumView(selected_ta))
        self.layout().addWidget(TrendView(selected_ta))





