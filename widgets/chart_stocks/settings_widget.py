from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QWidget, QHBoxLayout, QRadioButton, QComboBox, QLabel, QCheckBox, QCalendarWidget

class ChartSettingsWidget(QGroupBox):
    def __init__(self):
        super().__init__()
        periods = ["1d", "5d", "1mo", "3mo", "6mo","1y", "2y", "5y", "10y", "ytd", "max"]
        timeframes = ["1m", "2m", "5m", "15m", "30m", "60m","90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"]

        self.setTitle("Chart Settings")
        self.setStyleSheet("background-color: white;")
        self.setLayout(QVBoxLayout())

        self.buttons = QWidget()
        self.buttons.setLayout(QHBoxLayout())

        self.daterange_button_widget = QWidget()
        self.daterange_button_widget.setLayout(QHBoxLayout())

        self.calendars = QWidget()
        self.calendars.setLayout(QHBoxLayout())

        self.period_radiobutton = QRadioButton()
        self.period_radiobutton.setText("Chart by Period")
        self.period_radiobutton.setChecked(True)
        self.period_radiobutton.clicked.connect(self.period_radiobutton_clicked)
        self.buttons.layout().addWidget(self.period_radiobutton)

        self.period_combobox = QComboBox()
        self.period_combobox.addItems(periods)
        self.buttons.layout().addWidget(self.period_combobox)

        self.prepost = QCheckBox()
        self.prepost.setText("Include Pre/Post Market Data")
        self.buttons.layout().addWidget(self.prepost)

        self.split_dividend = QCheckBox()
        self.split_dividend.setText("Show Split and Dividend Actions")
        self.buttons.layout().addWidget(self.split_dividend)

        self.ohlc = QCheckBox()
        self.ohlc.setText("Adjust OHLC")
        self.buttons.layout().addWidget(self.ohlc)

        self.volume = QCheckBox()
        self.volume.setText("Include Volume Bars")
        self.buttons.layout().addWidget(self.volume)

        self.timeframe_combobox = QComboBox()
        self.timeframe_combobox.addItems(timeframes)
        self.buttons.layout().addWidget(QLabel("Chart Timeframe:"))
        self.buttons.layout().addWidget(self.timeframe_combobox)

        self.daterange_radiobutton = QRadioButton()
        self.daterange_radiobutton.setText("Chart by Date Range")
        self.daterange_radiobutton.clicked.connect(self.daterange_radiobutton_clicked)
        self.daterange_button_widget.layout().addWidget(self.daterange_radiobutton)

        self.start_date = QCalendarWidget()
        self.start_date.setStyleSheet('background-color: deepskyblue; border: 3px solid black')
        self.start_date.setEnabled(False)
        self.calendars.layout().addWidget(self.start_date)

        self.end_date = QCalendarWidget()
        self.end_date.setStyleSheet('background-color: deepskyblue; border: 3px solid black')
        self.end_date.setEnabled(False)
        self.calendars.layout().addWidget(self.end_date)

        self.layout().addWidget(self.buttons)
        self.layout().addWidget(self.daterange_button_widget)
        self.layout().addWidget(self.calendars)

    def daterange_radiobutton_clicked(self):
        self.start_date.setEnabled(True)
        self.end_date.setEnabled(True)
        self.period_radiobutton.setChecked(False)
        self.period_combobox.setEnabled(False)

    def period_radiobutton_clicked(self):
        self.start_date.setEnabled(False)
        self.end_date.setEnabled(False)
        self.period_combobox.setEnabled(True)
        self.daterange_radiobutton.setChecked(False)
