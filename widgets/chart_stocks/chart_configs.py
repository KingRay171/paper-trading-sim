from PySide6.QtWidgets import QDialog
from widgets.chart_stocks.broad_market import BroadMarketWidget
from widgets.chart_stocks.search_bar import SearchBar
from widgets.chart_stocks.settings_widget import ChartSettingsWidget
from dependencies import stockchart as sc
import multiprocessing as mp
import os
class ChartConfigs(QDialog):
    def __init__(self, string_list, selected_ta) -> None:
        super().__init__()
        self.cwd = os.getcwd() + '\\'
        self.broad_market = BroadMarketWidget()
        self.broad_market.setParent(self)
        self.broad_market.setGeometry(10, 10, 700, 50)

        self.search_bar = SearchBar(string_list)
        self.search_bar.setParent(self)
        self.search_bar.setGeometry(10, 70, 960, 70)
        self.search_bar.button.clicked.connect(lambda: self.search_button_clicked(selected_ta))

        self.settings = ChartSettingsWidget()
        self.settings.setParent(self)
        self.settings.setGeometry(10, 150, 1270, 460)

        self.broad_market.spy.clicked.connect(lambda: self.spy_button_clicked(selected_ta))
        self.broad_market.qqq.clicked.connect(lambda: self.qqq_button_clicked(selected_ta))
        self.broad_market.dia.clicked.connect(lambda: self.dia_button_clicked(selected_ta))
        self.broad_market.vix.clicked.connect(lambda: self.vix_button_clicked(selected_ta))


    def spy_button_clicked(self, selected_ta):
        self.search_bar.search.setText("SPY - SPDR S&P 500 ETF Trust")
        self.search_button_clicked(selected_ta)

    def qqq_button_clicked(self, selected_ta):
        self.search_bar.search.setText("QQQ - Invesco QQQ Trust")
        self.search_button_clicked(selected_ta)

    def dia_button_clicked(self, selected_ta):
        self.search_bar.search.setText("DIA - SPDR Dow Jones Industrial Average ETF Trust")
        self.search_button_clicked(selected_ta)

    def vix_button_clicked(self, selected_ta):
        self.search_bar.search.setText("^VIX ")
        self.search_button_clicked(selected_ta)

    def search_button_clicked(self, selected_ta):
        ticker = self.search_bar.search.text().split(' ')[0]
        interval = self.settings.timeframe_combobox.currentText()
        prepost = self.settings.prepost.isChecked()
        ohlc = self.settings.ohlc.isChecked()
        split_dividend = self.settings.split_dividend.isChecked()
        volume = self.settings.volume.isChecked()

        if self.settings.daterange_radiobutton.isChecked():

            self.chart_by_dates(ticker, interval, prepost, ohlc, split_dividend, volume, selected_ta)
        else:
            # only get period if user chose to chart by period
            self.chart_by_period(ticker, interval, prepost, ohlc, split_dividend, volume, selected_ta)

    def chart_by_dates(self, ticker, interval, prepost, ohlc, split_dividend, volume, selected_ta):
        start = self.settings.start_date.selectedDate().toString("yyyy-MM-dd")
        end = self.settings.end_date.selectedDate().toString("yyyy-MM-dd")
        queue = mp.Queue()

        mp.Process(target=sc.startChart, daemon=True, args=(ticker, interval, selected_ta, prepost, ohlc, split_dividend, volume, queue, None, start, end)).start()

    def chart_by_period(self, ticker: str, interval: str, prepost: str, ohlc: str, split_div: str, vol: str, selected_ta):
        """
        Starts chart UI, passes a period as a command line argument
        """

        period = self.settings.period_combobox.currentText()
        queue = mp.Queue()

        mp.Process(target=sc.startChart, daemon=True, args=(ticker, interval, selected_ta, prepost, ohlc, split_div, vol, queue, period, None, None)).start()

