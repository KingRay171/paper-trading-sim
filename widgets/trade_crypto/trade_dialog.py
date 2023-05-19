from PySide6.QtWidgets import QDialog, QGroupBox, QLabel, QLineEdit, QPushButton, QComboBox, QDoubleSpinBox, QVBoxLayout, QWidget, QHBoxLayout
from PySide6.QtCharts import QChart, QChartView, QDateTimeAxis, QValueAxis, QLineSeries
from PySide6.QtCore import Qt, QDateTime
from PySide6.QtGui import QFont
import yahooquery as yq
from dependencies import autocomplete as ac

class CryptoTradeDialog(QDialog):
    def __init__(self, orders):
        super().__init__()
        self.setStyleSheet('background-color: goldenrod')

        self.orders = orders
        self.symbol = None
        self.wnd = None
        self.completer = ac.CustomQCompleter()

        self.searchbar_gb = QGroupBox(self)
        self.searchbar_gb.setStyleSheet('background-color: black; color: white;')
        self.searchbar_gb.setTitle("Find a Stock")
        self.searchbar_gb.setGeometry(10, 10, 960, 70)
        self.searchbar_gb.searchBar = QLineEdit(self.searchbar_gb)
        self.searchbar_gb.searchBar.setGeometry(10, 20, 850, 40)
        self.searchbar_gb.searchBar.textChanged.connect(self.search_text_changed)
        self.searchbar_gb.searchBar.setFont(QFont('arial', 10))
        self.searchbar_gb.searchBar.setCompleter(self.completer)
        self.searchbar_gb.search_button = QPushButton(self.searchbar_gb)
        self.searchbar_gb.search_button.setGeometry(870, 20, 80, 40)
        self.searchbar_gb.search_button.setText("Trade")

        self.basic_info_gb = QGroupBox(self)
        self.basic_info_gb.setStyleSheet('background-color: black; color: white;')
        self.basic_info_gb.setTitle("Information")
        self.basic_info_gb.setGeometry(980, 10, 300, 70)

        self.basic_info_gb.full_name_label = QLabel(self.basic_info_gb)
        self.basic_info_gb.full_name_label.setText("")
        self.basic_info_gb.full_name_label.setGeometry(10, 15, 150, 15)

        self.basic_info_gb.price_label = QLabel(self.basic_info_gb)
        self.basic_info_gb.price_label.setGeometry(160, 15, 100, 20)

        self.basic_info_gb.bid_label = QLabel(self.basic_info_gb)
        self.basic_info_gb.bid_label.setGeometry(10, 30, 140, 20)

        self.basic_info_gb.ask_label = QLabel(self.basic_info_gb)
        self.basic_info_gb.ask_label.setGeometry(160, 30, 140, 20)

        self.order_gb = QGroupBox(self)
        self.order_gb.setStyleSheet('background-color: black; color: white;')
        self.order_gb.setTitle("Create Order")
        self.order_gb.setGeometry(10, 90, 450, 400)

        self.order_gb.action_label = QLabel(self.order_gb)
        self.order_gb.action_label.setText("Action")
        self.order_gb.action_label.setGeometry(10, 50, 100, 15)

        self.order_gb.action_combobox = QComboBox(self.order_gb)
        self.order_gb.action_combobox.addItems(('Buy', 'Sell'))
        self.order_gb.action_combobox.setGeometry(10, 70, 100, 40)
        self.order_gb.action_combobox.setStyleSheet('border: 1px solid white;')

        self.order_gb.qty_label = QLabel(self.order_gb)
        self.order_gb.qty_label.setText("Quantity")
        self.order_gb.qty_label.setGeometry(10, 150, 100, 15)

        self.order_gb.qty_spinbox = QDoubleSpinBox(self.order_gb)
        self.order_gb.qty_spinbox.setGeometry(10, 170, 100, 40)

        self.order_gb.max_btn = QPushButton(self.order_gb)
        self.order_gb.max_btn.setText("Max")
        self.order_gb.max_btn.setGeometry(120, 170, 100, 40)
        self.order_gb.max_btn.setEnabled(False)
        self.order_gb.max_btn.setStyleSheet('border: 1px solid white;')

        self.order_gb.type_label = QLabel(self.order_gb)
        self.order_gb.type_label.setText("Order Type")
        self.order_gb.type_label.setGeometry(10, 230, 100, 15)

        self.order_gb.type_combobox = QComboBox(self.order_gb)
        self.order_gb.type_combobox.addItems(('Market', 'Limit', 'Stop'))
        self.order_gb.type_combobox.setGeometry(10, 250, 100, 40)
        self.order_gb.type_combobox.currentTextChanged.connect(self.on_ordertype_change)
        self.order_gb.type_combobox.setStyleSheet('border: 1px solid white;')

        self.order_gb.price_spinbox = QDoubleSpinBox(self.order_gb)
        self.order_gb.price_spinbox.setGeometry(120, 250, 100, 40)
        self.order_gb.price_spinbox.setVisible(False)


        self.order_gb.preview_order = QPushButton(self.order_gb)
        self.order_gb.preview_order.setText("Preview Order")
        self.order_gb.preview_order.setGeometry(50, 340, 360, 50)
        self.order_gb.preview_order.clicked.connect(self.on_previeworder_click)

        self.searchbar_gb.search_button.clicked.connect(self.trade_searchbar_click)

        self.chart_groupbox = QGroupBox(self)
        self.chart_groupbox.setTitle('Chart')
        self.chart_groupbox.setStyleSheet('background-color: black; color: white;')
        self.chart_groupbox.setGeometry(500, 90, 650, 400)

        self.day_chart = QChart()
        self.day_chartview = QChartView(self.chart_groupbox)
        self.day_lineseries = QLineSeries()
        self.day_chart.addSeries(self.day_lineseries)
        self.day_lineseries.setName('Stock')

        self.x_axis = QDateTimeAxis()
        self.x_axis.setFormat('h:mm')
        self.x_axis.setTitleText('Time')
        self.x_axis.setVisible(True)
        self.day_chart.addAxis(self.x_axis, Qt.AlignmentFlag.AlignBottom)
        self.day_lineseries.attachAxis(self.x_axis)

        self.y_axis = QValueAxis()
        self.day_chart.addAxis(self.y_axis, Qt.AlignmentFlag.AlignLeft)
        self.day_lineseries.attachAxis(self.y_axis)

        self.day_chartview.setGeometry(10, 15, 600, 400)
        self.day_chartview.setChart(self.day_chart)
        self.day_chartview.setStyleSheet('background-color: black; color: black;')

    def on_previeworder_click(self):
        """
        Shows dialog with preview of the user's order
        """

        self.wnd = QDialog(self)
        self.wnd.setWindowTitle("Preview Order")
        self.wnd.setLayout(QVBoxLayout())

        ticker_widget = QWidget()
        ticker_widget.setLayout(QHBoxLayout())
        ticker_widget.layout().addWidget(QLabel('Ticker:'))
        ticker_label = QLabel(self.symbol)
        ticker_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        ticker_widget.layout().addWidget(ticker_label)
        self.wnd.layout().addWidget(ticker_widget)

        transaction_widget = QWidget()
        transaction_widget.setLayout(QHBoxLayout())
        transaction_widget.layout().addWidget(QLabel('Transaction:'))
        transaction_label = QLabel(self.order_gb.action_combobox.currentText())
        transaction_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        transaction_widget.layout().addWidget(transaction_label)
        self.wnd.layout().addWidget(transaction_widget)


        ordertype_widget = QWidget()
        ordertype_widget.setLayout(QHBoxLayout())
        ordertype_widget.layout().addWidget(QLabel('Order Type:'))
        ordertype_label = QLabel(self.order_gb.type_combobox.currentText())
        ordertype_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        ordertype_widget.layout().addWidget(ordertype_label)
        self.wnd.layout().addWidget(ordertype_widget)

        estprice_widget = QWidget()
        estprice_widget.setLayout(QHBoxLayout())
        estprice_widget.layout().addWidget(QLabel('Estimated Price'))
        estprice_label = QLabel()
        if self.order_gb.type_combobox.currentText() == 'Market':
            estprice_label.setText(self.basic_info_gb.price_label.text().split('(')[0])
        else:
            # change to limit/stop price
            estprice_label.setText(self.order_gb.price_spinbox.text())
        estprice_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        estprice_widget.layout().addWidget(estprice_label)
        self.wnd.layout().addWidget(estprice_widget)

        qty_widget = QWidget()
        qty_widget.setLayout(QHBoxLayout())
        qty_widget.layout().addWidget(QLabel('Quantity:'))
        qty_label = QLabel(f"{self.order_gb.qty_spinbox.value()}")
        qty_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        qty_widget.layout().addWidget(qty_label)
        self.wnd.layout().addWidget(qty_widget)

        est_cost_widget = QWidget()
        est_cost_widget.setLayout(QHBoxLayout())
        est_cost_widget.layout().addWidget(
            QLabel(
                "Estimated Net Debit"
                if transaction_label.text() == "Buy"
                else "Estimated Net Credit"
            )
        )

        est_cost_label = QLabel(f"{float(qty_label.text()) * float(estprice_label.text())}")
        est_cost_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        est_cost_widget.layout().addWidget(est_cost_label)
        self.wnd.layout().addWidget(est_cost_widget)

        actions_widget = QWidget()
        actions_widget.setLayout(QHBoxLayout())
        cancel_button = QPushButton('Change Order')
        cancel_button.clicked.connect(self.wnd.done(0))
        actions_widget.layout().addWidget(cancel_button)
        ok_button = QPushButton('Confirm Order')
        def ok_button_clicked():
            self.orders.append(
                [
                    self.symbol,
                    transaction_label.text(),
                    ordertype_label.text(),
                    float(estprice_label.text()),
                    float(qty_label.text())
                ]
            )
            self.wnd.done(0)
        ok_button.clicked.connect(ok_button_clicked)
        actions_widget.layout().addWidget(ok_button)
        self.wnd.layout().addWidget(actions_widget)

        self.wnd.exec()

    def trade_searchbar_click(self):
        """
        Updates trade dialog when a stock is selected for trading
        """

        self.symbol = self.searchbar_gb.searchBar.text().split(' ')[0]
        ticker = yq.Ticker(self.symbol)
        self.order_gb.max_btn.setEnabled(True)
        prices = ticker.history('1d', '1m')
        self.day_chart.removeAllSeries()
        self.day_chart_series = QLineSeries()
        for idx, close in enumerate(prices.loc[:, 'close']):
            price_dt = QDateTime().fromString(f"{prices.index[idx][1]}"[0:19], "yyyy-MM-dd hh:mm:ss")
            epoch_dt = float(price_dt.toMSecsSinceEpoch())
            self.day_chart_series.append(epoch_dt, close)

        self.day_chart.addSeries(self.day_chart_series)

        self.day_chart.createDefaultAxes()
        self.day_chart.axes(Qt.Orientation.Horizontal)[0].hide()

        self.day_chart_x_axis = QDateTimeAxis()
        self.day_chart_x_axis.setTickCount(7)
        self.day_chart_x_axis.setFormat("h:mm")
        self.day_chart_x_axis.setTitleText("Date")
        self.day_chart_x_axis.setVisible(True)

        self.day_chart.addAxis(self.day_chart_x_axis, Qt.AlignmentFlag.AlignBottom)
        self.day_chart_series.attachAxis(self.day_chart_x_axis)

    def search_text_changed(self, txt: str):
        self.searchbar_gb.searchBar.setText(txt.upper())

    def on_ordertype_change(self, value):
        """
        Shows or hides the price slider depending on the type of order selected
        (show for limit/stop, hide for market)
        """
        match value:
            case 'Market':
                self.order_gb.price_spinbox.setVisible(False)
            case _:
                self.order_gb.price_spinbox.setVisible(True)
                self.order_gb.price_spinbox.setValue(float(self.basic_info_gb.price_label.text().split('(')[0]))

    def update_crypto_dialog(self):
        """
        Updates the trade dialog UI with current bid, ask, and last trade price information
        """
        try:
            all_modules = yq.Ticker(self.symbol).all_modules[self.symbol]

            quote_type = all_modules['quoteType']
            prices = all_modules['price']

            self.basic_info_gb.full_name_label.setText(quote_type['shortName'])
            self.basic_info_gb.price_label.setText(
                f"{prices['regularMarketPrice']} ({prices['regularMarketChange']})"
            )
        except KeyError:
            pass


