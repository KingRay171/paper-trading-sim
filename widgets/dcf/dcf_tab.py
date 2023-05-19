from PySide6.QtWidgets import QDialog, QGroupBox, QLineEdit, QPushButton, QLabel, QSlider, QCheckBox
from PySide6.QtCharts import QChart, QChartView, QLineSeries
from PySide6.QtCore import Qt, QDateTime, QStringListModel
from PySide6.QtGui import QFont
from dependencies import autocomplete as ac, dcfmodel as dcf, numberformat as nf

class DCFTab(QDialog):
    def __init__(self, string_list):
        super().__init__()
        self.setStyleSheet('background-color: deepskyblue;')
        self.completer = ac.CustomQCompleter()
        self.model = QStringListModel()
        self.model.setStringList(string_list)
        self.completer.setModel(self.model)

        # searchbar init
        self.searchbar_gb = QGroupBox(self)
        self.searchbar_gb.setStyleSheet('background-color: white;')
        self.searchbar_gb.setTitle("Find a Stock")
        self.searchbar_gb.setGeometry(10, 10, 960, 70)
        self.searchbar_gb.searchBar = QLineEdit(self.searchbar_gb)
        self.searchbar_gb.searchBar.setGeometry(10, 20, 850, 40)
        self.searchbar_gb.searchBar.textChanged.connect(lambda txt: self.searchbar_gb.searchBar.setText(txt.upper()))
        self.searchbar_gb.searchBar.setFont(QFont('arial', 10))
        self.searchbar_gb.searchBar.setCompleter(self.completer)
        self.searchbar_gb.search_button = QPushButton(self.searchbar_gb)
        self.searchbar_gb.search_button.setGeometry(870, 20, 80, 40)
        self.searchbar_gb.search_button.setText("Show Model")
        self.searchbar_gb.search_button.clicked.connect(self.dcf_findstock_button_click)

        # inputs init
        self.inputs_gb = QGroupBox(self)
        self.inputs_gb.setStyleSheet('background-color: white;')
        self.inputs_gb.setTitle("Model Inputs")
        self.inputs_gb.setGeometry(10, 90, 630, 570)
        self.inputs_gb.company_label = QLabel(self.inputs_gb)
        self.inputs_gb.company_label.setText("Company:")
        self.inputs_gb.company_label.setGeometry(10, 20, 100, 50)
        self.inputs_gb.mkt_price_label = QLabel(self.inputs_gb)
        self.inputs_gb.mkt_price_label.setText("Market Price:")
        self.inputs_gb.mkt_price_label.setGeometry(10, 70, 100, 50)
        self.inputs_gb.mkt_price = QLabel(self.inputs_gb)
        self.inputs_gb.mkt_price.setGeometry(570, 70, 100, 50)
        self.inputs_gb.eps_label = QLabel(self.inputs_gb)
        self.inputs_gb.eps_label.setText("Earnings per Share:")
        self.inputs_gb.eps_label.setGeometry(10, 120, 100, 50)
        self.inputs_gb.eps = QLabel(self.inputs_gb)
        self.inputs_gb.eps.setGeometry(570, 120, 100, 50)
        self.inputs_gb.growth_label = QLabel(self.inputs_gb)
        self.inputs_gb.growth_label.setText("Growth Estimate:")
        self.inputs_gb.growth_label.setGeometry(10, 170, 100, 50)
        self.inputs_gb.growth_slider = QSlider(self.inputs_gb)
        self.inputs_gb.growth_slider.setOrientation(Qt.Orientation.Horizontal)
        self.inputs_gb.growth_slider.setTickPosition(QSlider.TickPosition.TicksBothSides)
        self.inputs_gb.growth_slider.setGeometry(110, 170, 450, 50)
        self.inputs_gb.growth_slider.setTickInterval(10)
        self.inputs_gb.growth_slider.setRange(-500, 4000)
        self.inputs_gb.growth_slider.setSliderPosition(0)
        self.inputs_gb.growth_slider.valueChanged.connect(
            lambda: self.inputs_gb.growth.setText(f"{self.inputs_gb.growth_slider.value() / 100.0}%")
        )
        self.inputs_gb.growth = QLabel(self.inputs_gb)
        self.inputs_gb.growth.setGeometry(570, 170, 100, 50)
        self.inputs_gb.def_growth_button = QCheckBox(self.inputs_gb)
        self.inputs_gb.def_growth_button.setText("Use Analyst 5-Year Growth Estimate")
        self.inputs_gb.def_growth_button.setGeometry(1100, 170, 100, 50)
        self.inputs_gb.term_label = QLabel(self.inputs_gb)
        self.inputs_gb.term_label.setText("Term:")
        self.inputs_gb.term_label.setGeometry(10, 220, 100, 50)
        self.inputs_gb.term_slider = QSlider(self.inputs_gb)
        self.inputs_gb.term_slider.setOrientation(Qt.Orientation.Horizontal)
        self.inputs_gb.term_slider.setTickPosition(QSlider.TickPosition.TicksBothSides)
        self.inputs_gb.term_slider.setGeometry(110, 220, 450, 50)
        self.inputs_gb.term_slider.setTickInterval(1)
        self.inputs_gb.term_slider.setRange(1, 10)
        self.inputs_gb.term_slider.setSliderPosition(5)
        self.inputs_gb.term_slider.valueChanged.connect(
            lambda: self.inputs_gb.term.setText(f"{self.inputs_gb.term_slider.value()} years")
        )
        self.inputs_gb.term = QLabel(self.inputs_gb)
        self.inputs_gb.term.setText("5 years")
        self.inputs_gb.term.setGeometry(570, 220, 100, 50)
        self.inputs_gb.discount_rate_label = QLabel(self.inputs_gb)
        self.inputs_gb.discount_rate_label.setText("Discount Rate: ")
        self.inputs_gb.discount_rate_label.setGeometry(10, 270, 100, 50)
        self.inputs_gb.discount_rate_slider = QSlider(self.inputs_gb)
        self.inputs_gb.discount_rate_slider.setOrientation(Qt.Orientation.Horizontal)
        self.inputs_gb.discount_rate_slider.setTickPosition(QSlider.TickPosition.TicksBothSides)
        self.inputs_gb.discount_rate_slider.setGeometry(110, 270, 450, 50)
        self.inputs_gb.discount_rate_slider.setTickInterval(10)
        self.inputs_gb.discount_rate_slider.setRange(-500, 2000)
        self.inputs_gb.discount_rate_slider.setSliderPosition(1000)
        self.inputs_gb.discount_rate_slider.valueChanged.connect(
            lambda: self.inputs_gb.discount_rate.setText(f"{self.inputs_gb.discount_rate_slider.value() / 100.0}%")
        )
        self.inputs_gb.discount_rate = QLabel(self.inputs_gb)
        self.inputs_gb.discount_rate.setGeometry(570, 270, 100, 50)
        self.inputs_gb.perpetual_rate_label = QLabel(self.inputs_gb)
        self.inputs_gb.perpetual_rate_label.setText("Perpetual Rate:")
        self.inputs_gb.perpetual_rate_label.setGeometry(10, 320, 100, 50)
        self.inputs_gb.perpetual_rate_slider = QSlider(self.inputs_gb)
        self.inputs_gb.perpetual_rate_slider.setOrientation(Qt.Orientation.Horizontal)
        self.inputs_gb.perpetual_rate_slider.setGeometry(110, 320, 450, 50)
        self.inputs_gb.perpetual_rate_slider.setTickInterval(10)
        self.inputs_gb.perpetual_rate_slider.setTickPosition(QSlider.TickPosition.TicksBothSides)
        self.inputs_gb.perpetual_rate_slider.setRange(-500, 1000)
        self.inputs_gb.perpetual_rate_slider.setSliderPosition(250)
        self.inputs_gb.perpetual_rate_slider.valueChanged.connect(
            lambda: self.inputs_gb.perpetual_rate.setText(f"{self.inputs_gb.perpetual_rate_slider.value() / 100.0}%")
        )
        self.inputs_gb.perpetual_rate = QLabel(self.inputs_gb)
        self.inputs_gb.perpetual_rate.setGeometry(570, 320, 100, 50)
        self.inputs_gb.last_fcf_label = QLabel(self.inputs_gb)
        self.inputs_gb.last_fcf_label.setText("Last Free Cash Flow:")
        self.inputs_gb.last_fcf_label.setGeometry(10, 370, 110, 50)
        self.inputs_gb.last_fcf = QLabel(self.inputs_gb)
        self.inputs_gb.last_fcf.setGeometry(570, 370, 100, 50)
        self.inputs_gb.shares_label = QLabel(self.inputs_gb)
        self.inputs_gb.shares_label.setText("Shares in Circulation:")
        self.inputs_gb.shares_label.setGeometry(10, 420, 110, 50)
        self.inputs_gb.shares = QLabel(self.inputs_gb)
        self.inputs_gb.shares.setGeometry(570, 420, 100, 50)
        self.inputs_gb.get_analysis_button = QPushButton(self.inputs_gb)
        self.inputs_gb.get_analysis_button.setGeometry(210, 480, 200, 100)
        self.inputs_gb.get_analysis_button.setText("Get Fair Value")
        self.inputs_gb.get_analysis_button.clicked.connect(self.dcf_getanalysis_button_click)

        # outputs init
        self.outputs_gb = QGroupBox(self)
        self.outputs_gb.setStyleSheet('background-color: white;')
        self.outputs_gb.setTitle("Model Outputs")
        self.outputs_gb.setGeometry(650, 90, 630, 570)
        self.outputs_gb.verdict_label = QLabel(self.outputs_gb)
        self.outputs_gb.verdict_label.setGeometry(200, 10, 200, 50)
        self.outputs_gb.basic_gb = QGroupBox(self.outputs_gb)
        self.outputs_gb.basic_gb.setGeometry(10, 20, 610, 350)
        self.outputs_gb.basic_gb.setTitle("Basic Model")

        # chart for future cashflows init
        self.future_cashflows_chart = QChart()
        self.future_cashflows_lineseries = QLineSeries()
        self.future_cashflows_lineseries.setName("Future Cashflows")
        self.future_cashflows_chart.addSeries(self.future_cashflows_lineseries)
        self.future_cashflows_chartview = QChartView(self.future_cashflows_chart)
        self.future_cashflows_chartview.setParent(self.outputs_gb.basic_gb)
        self.future_cashflows_chartview.setGeometry(10, 20, 590, 200)

        # basic DCF model output
        self.outputs_gb.basic_gb.fair_value_label = QLabel(self.outputs_gb.basic_gb)
        self.outputs_gb.basic_gb.fair_value_label.setText("Fair Value:")
        self.outputs_gb.basic_gb.fair_value_label.setGeometry(250, 230, 100, 50)
        self.outputs_gb.basic_gb.fair_value = QLabel(self.outputs_gb.basic_gb)
        self.outputs_gb.basic_gb.fair_value.setGeometry(200, 280, 100, 50)

        # graham model output
        self.outputs_gb.graham_gb = QGroupBox(self.outputs_gb)
        self.outputs_gb.graham_gb.setGeometry(10, 380, 610, 150)
        self.outputs_gb.graham_gb.setTitle("Graham Model")
        self.outputs_gb.graham_gb.ev_label = QLabel(self.outputs_gb.graham_gb)
        self.outputs_gb.graham_gb.ev_label.setText("Expected value implied by growth rate:")
        self.outputs_gb.graham_gb.ev_label.setGeometry(10, 20, 210, 50)
        self.outputs_gb.graham_gb.ev = QLabel(self.outputs_gb.graham_gb)
        self.outputs_gb.graham_gb.ev.setGeometry(490, 20, 100, 50)
        self.outputs_gb.graham_gb.graham_ge_label = QLabel(self.outputs_gb.graham_gb)
        self.outputs_gb.graham_gb.graham_ge_label.setText("Growth rate implied by stock price:")
        self.outputs_gb.graham_gb.graham_ge_label.setGeometry(10, 80, 200, 50)
        self.outputs_gb.graham_gb.graham_growth_estimate = QLabel(self.outputs_gb.graham_gb)
        self.outputs_gb.graham_gb.graham_growth_estimate.setGeometry(490, 80, 100, 50)

        self.cur_ticker = None

    def dcf_findstock_button_click(self):
        """
        Populates the DCF dialog with default settings for the stock the user
        searched for
        """

        ticker = self.searchbar_gb.searchBar.text().split(' ')[0]
        self.cur_ticker = ticker

        input_info = dcf.parse(ticker)
        self.inputs_gb.setVisible(True)
        self.inputs_gb.company_label.setText(f"Company: {input_info['company_name']}")
        mkt_price = input_info['mp']
        self.inputs_gb.mkt_price.setText(f"${mkt_price:0,.2f}")

        self.inputs_gb.eps.setText(f"{input_info['eps']}")

        self.inputs_gb.growth.setText(f"{input_info['ge']}")

        self.inputs_gb.growth_slider.setValue(input_info['ge'] * 100)

        self.inputs_gb.discount_rate.setText(
            f"{self.inputs_gb.discount_rate_slider.value() / 100.0}%"
        )


        self.inputs_gb.perpetual_rate.setText(
            f"{self.inputs_gb.perpetual_rate_slider.value() / 100.0}%"
        )

        self.inputs_gb.last_fcf.setText(nf.simplify(input_info['fcf'], True))

        self.inputs_gb.shares.setText(nf.simplify(input_info['shares'], True))

    def dcf_getanalysis_button_click(self):
        """
        Populates the right side of the DCF dialog with the report from the DCF module when
        the "Get Analysis" button is pressed.
        """

        discount_rate = self.inputs_gb.discount_rate_slider.value() / 100.0
        perp_rate = self.inputs_gb.perpetual_rate_slider.value() / 100.0
        growth_estimate = self.inputs_gb.growth_slider.value() / 100.0
        term = self.inputs_gb.term_slider.value()
        eps = float(self.inputs_gb.eps.text())
        dcf_analysis = dcf.get_fairval(
            self.cur_ticker, discount_rate, perp_rate, growth_estimate, term, eps
        )

        self.future_cashflows_chartview.setVisible(True)

        self.future_cashflows_chart.removeAllSeries()
        future_cashflows_series = QLineSeries()
        future_cashflows_series.setName("Forecasted Cash Flows")
        future_cashflows_pv_lineseries = QLineSeries()
        future_cashflows_pv_lineseries.setName(
            "Present Value of Forecasted Cash Flows")
        current_year = QDateTime().currentDateTime().date().year()


        dcf_zip = zip(
            dcf_analysis['forecasted_cash_flows'][:-1], dcf_analysis['cashflow_present_values'][:-1]
        )

        for idx, (fcf, present_val) in enumerate(dcf_zip):
            future_cashflows_series.append(current_year + idx, fcf)
            future_cashflows_pv_lineseries.append(current_year + idx, present_val)

        self.future_cashflows_chart.addSeries(future_cashflows_series)
        self.future_cashflows_chart.addSeries(future_cashflows_pv_lineseries)

        self.future_cashflows_chart.createDefaultAxes()
        self.future_cashflows_chart.axes(Qt.Orientation.Horizontal)[
            0].setTickCount(term)

        upside = round((dcf_analysis['fair_value'] / dcf_analysis['mp'] - 1) * 100, 2)
        self.outputs_gb.basic_gb.fair_value.setText(
            f"${round(dcf_analysis['fair_value'], 2)} ({upside}%)"
        )

        upside = round(
            (dcf_analysis['graham_expected_value'] / dcf_analysis['mp'] - 1) * 100, 2)
        self.outputs_gb.graham_gb.ev.setText(
            f"${round(dcf_analysis['graham_expected_value'], 2)} ({upside}%)"
        )

        self.outputs_gb.graham_gb.graham_growth_estimate.setText(
            f"{round(dcf_analysis['graham_growth_estimate'], 2)}% per annum"
        )

