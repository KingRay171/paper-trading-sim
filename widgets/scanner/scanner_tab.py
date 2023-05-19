from PySide6.QtWidgets import QTabWidget, QPushButton, QScrollArea, QVBoxLayout, QHBoxLayout, QSizePolicy, QWidget, QLabel, QGroupBox, QDialog
from PySide6.QtGui import QIcon
from widgets.scanner.scanner_dialog import ScannerDialog
from widgets.scanner.uncon_strats_tab import UnconStratsTab
from dependencies import scanner as sc
from dependencies import unconventional_stragegies as us
import os

class ScannerTab(QTabWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: deepskyblue;")

        self.scanner_dialog = ScannerDialog()
        self.uncon_strats = UnconStratsTab()

        self.uncon_strats.cramer_gb.cramer_btn.clicked.connect(self.cramer_btn_clicked)

        self.uncon_strats.wsb_gb.wsb_btn.clicked.connect(self.wsb_btn_clicked)

        self.uncon_strats.google_gb.google_btn.clicked.connect(self.google_btn_clicked)

        self.create_scanner(
            'Day Gainers',
            "Find stocks that have gained the most relative to their close yesterday",
            "day_gainers",
            0, 0,
            'regularMarketChangePercent',
        )

        self.create_scanner(
            "Day Losers",
            "Find stocks that have lost the most relative to their close yesterday",
            "day_losers",
            1, 0,
            "regularMarketChangePercent"
        )

        self.create_scanner(
            "Most Active",
            "Find stocks that have traded the most shares today",
            "most_actives",
            2, 0,
            "regularMarketVolume"
        )

        self.create_scanner(
            "Options Open Interest",
            "Find options with the highest Open Interest",
            "top_options_open_interest",
            3, 0
        )

        self.create_scanner(
            "Options Gamma",
            "Find options with the highest Implied Volatility",
            "top_options_implied_volatility",
            4, 0
        )

        self.create_scanner(
            "Undervalued Growth Stocks",
            "Find stocks with earnings growth above 25% and low PE ratios",
            "undervalued_growth_stocks",
            5, 0
        )

        self.create_scanner(
            "Undervalued Large Caps",
            "Find large cap stocks trading at low multiples",
            "undervalued_large_caps",
            6, 0
        )

        self.create_scanner(
            "Small Cap Gainers",
            "Find small cap stocks up more than 5% today",
            "small_cap_gainers",
            0, 1
        )

        self.addTab(self.scanner_dialog, "Scanner")
        self.addTab(self.uncon_strats, "Unconventional Strategies")

    def create_results_dialog(self, search_criteria=None, search_results=None, sort_field=None, results_iterable=None):
        """
        Changes the content of the "Scanner" dialog in the "Trade Ideas" tab to the
        scanner search results
        """
        new_scanner_dialog = QDialog()
        new_scanner_dialog.setStyleSheet('background-color: deepskyblue')

        new_scanner_dialog.back_button = QPushButton(new_scanner_dialog)

        new_scanner_dialog.back_button.setIcon(QIcon(f"{os.getcwd()}/icons/backarrow.png"))
        new_scanner_dialog.back_button.setGeometry(10, 20, 50, 50)

        def back_button_clicked():
            self.removeTab(0)
            self.insertTab(0, self.scanner_dialog, 'Scanner')
            self.setCurrentIndex(0)

        new_scanner_dialog.back_button.clicked.connect(back_button_clicked)

        new_scanner_dialog.results_scroll = QScrollArea(new_scanner_dialog)
        new_scanner_dialog.results_scroll.setGeometry(100, 20, 1100, 550)
        new_scanner_dialog.results_scroll.setStyleSheet('background-color: white')
        new_scanner_dialog.results_scroll.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )

        new_scanner_dialog.results_widget = QWidget(new_scanner_dialog)
        new_scanner_dialog.results_widget.setLayout(QVBoxLayout())
        new_scanner_dialog.setMinimumWidth(1000)

        if search_criteria is not None and sort_field is not None:
            for result in sc.get_results(search_criteria, sort_field):
                result_widget = QWidget()
                result_widget.setLayout(QHBoxLayout())
                for key in result.keys():
                    result_widget.layout().addWidget(QLabel(f"{result[key]}"))

                new_scanner_dialog.results_widget.layout().addWidget(result_widget)
        elif search_results is not None:
            for result in results_iterable:
                result_widget = QWidget()
                result_widget.setLayout(QHBoxLayout())
                for item in result:
                    result_widget.layout().addWidget(QLabel(f"{item}"))

                new_scanner_dialog.results_widget.layout().addWidget(result_widget)



        new_scanner_dialog.results_scroll.setWidget(new_scanner_dialog.results_widget)
        self.removeTab(0)
        self.insertTab(0, new_scanner_dialog, 'Scanner')
        self.setCurrentIndex(0)


    def create_scanner(self, title, desc, search_criteria, xpos, ypos, sort_field=None):
        """
        Creates a scanner widget and adds it to the scanner dialog
        """
        scanner_groupbox = QGroupBox(self)
        scanner_groupbox.setTitle(title)
        scanner_groupbox.setStyleSheet('background-color: white')

        scanner_groupbox.desc_label = QLabel(scanner_groupbox)
        scanner_groupbox.desc_label.setText(desc)
        scanner_groupbox.desc_label.setWordWrap(True)
        scanner_groupbox.desc_label.setGeometry(10, 15, 130, 90)

        scanner_groupbox.run_button = QPushButton(scanner_groupbox)
        scanner_groupbox.run_button.setText('Run')
        scanner_groupbox.run_button.setGeometry(25, 110, 100, 20)

        scanner_groupbox.run_button.clicked.connect(
            lambda: self.create_results_dialog(search_criteria=search_criteria, sort_field=sort_field)
        )

        self.scanner_dialog.layout().addWidget(scanner_groupbox, ypos, xpos)

    def google_btn_clicked(self):
        results = us.get_google_trends()
        results_iter = zip(results['Ticker'], results['Trend Score'])
        self.create_results_dialog(search_results=results, results_iterable=results_iter)

    def cramer_btn_clicked(self):
        results = us.get_cramer_recs()
        results_iter = zip(
            results['Stock'], results['Direction'], results['Date'], results['Return Since']
        )
        self.create_results_dialog(search_results=results, results_iterable=results_iter)

    def wsb_btn_clicked(self):
        results = us.get_wsb_tickers()
        results_iter = zip(results['Stock'], results['Mentions'], results['% Change'])
        self.create_results_dialog(search_results=results, results_iterable=results_iter)