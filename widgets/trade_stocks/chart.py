from PySide6.QtWidgets import QGroupBox, QHBoxLayout
from PySide6.QtCharts import QChart, QDateTimeAxis, QLineSeries, QValueAxis, QChartView
from PySide6.QtCore import Qt

class StockTradeChart(QGroupBox):
    def __init__(self):
        super().__init__()
        self.setTitle("Chart")
        self.setStyleSheet("background-color: white;")
        self.setLayout(QHBoxLayout())

        self.chart = QChart()
        self.chartview = QChartView()
        self.lineseries = QLineSeries()
        self.chart.addSeries(self.lineseries)
        self.lineseries.setName("Stock")

        self.xaxis = QDateTimeAxis()
        self.xaxis.setFormat('h:mm')
        self.xaxis.setTitleText("Time")
        self.xaxis.setVisible(True)
        self.chart.addAxis(self.xaxis, Qt.AlignmentFlag.AlignBottom)
        self.lineseries.attachAxis(self.xaxis)

        self.yaxis = QValueAxis()
        self.chart.addAxis(self.yaxis, Qt.AlignmentFlag.AlignLeft)
        self.lineseries.attachAxis(self.yaxis)
        self.chartview.setChart(self.chart)

        self.layout().addWidget(self.chartview)

