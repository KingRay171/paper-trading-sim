from typing import Optional
from PySide6.QtWidgets import QDialog, QScrollArea, QWidget, QVBoxLayout, QGroupBox, QTableWidget, QAbstractItemView
from PySide6.QtCharts import QChart, QBarSeries, QChartView
from PySide6.QtGui import QFont

class StockInfoFinancials(QDialog):
    def __init__(self):
        super().__init__()
        self.setStyleSheet('background-color: deepskyblue')
        self.content_container = QScrollArea(self)
        self.financials_chart_widget = QWidget()
        self.financials_chart_widget.resize(1300, 2000)
        self.financials_chart_widget.setLayout(QVBoxLayout())
        self.content_container.setWidget(self.financials_chart_widget)
        self.content_container.setGeometry(5, 15, 1290, 650)
        self.financials_chart = QChart()
        self.financials_chart.setTitle("Financial Statements")
        self.financials_barseries = QBarSeries()
        self.financials_chart.addSeries(self.financials_barseries)
        self.financials_groupbox = QGroupBox(self.financials_chart_widget)
        self.financials_groupbox.setTitle("Fundamentals")
        self.financials_groupbox.setGeometry(10, 10, 1250, 1950)
        self.financials_chartview = QChartView(self.financials_chart)
        self.financials_chartview.setParent(self.financials_groupbox)
        self.financials_chartview.setVisible(True)
        self.financials_chartview.setGeometry(10, 15, 1200, 300)
        self.financials_table = QTableWidget(self.financials_groupbox)
        self.financials_table.setGeometry(10, 325, 1200, 1500)
        self.financials_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.financials_table.setFont(QFont('arial', 10))
        self.financials_table.setStyleSheet('background-color: white;')
