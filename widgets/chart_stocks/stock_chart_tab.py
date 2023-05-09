from typing import Optional
from PySide6.QtWidgets import QTabWidget
from widgets.chart_stocks.chart_configs import ChartConfigs
from widgets.chart_stocks.technical_indicators import IndicatorsWidget

class StockChartTab(QTabWidget):
    def __init__(self, string_list, selected_ta) -> None:
        super().__init__()
        self.setStyleSheet('background-color: deepskyblue;')
        self.addTab(ChartConfigs(string_list, selected_ta), "Chart Configurations")
        self.addTab(IndicatorsWidget(), "Technical Indicators")