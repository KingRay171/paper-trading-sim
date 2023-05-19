from typing import Optional
from PySide6.QtWidgets import QTabWidget, QLabel, QPushButton, QButtonGroup, QTableWidgetItem, QCheckBox
from PySide6.QtGui import QColor, QFont
from PySide6.QtCharts import QChart, QPieSeries, QChartView, QBarSeries, QLineSeries, QDateTimeAxis, QBarSet
from PySide6.QtCore import Qt, QDateTime, SIGNAL
from dependencies import predictionRunnerExample as spred
from widgets.stock_info.main_dialog import StockInfoMain
from widgets.stock_info.recs_dialog import StockInfoRecs
from widgets.stock_info.forecasts_dialog import StockInfoForecasts
from widgets.stock_info.financials_dialog import StockInfoFinancials
import yahooquery as yq
from dependencies import finviznews as fn
from dependencies.clearlayout import clear_layout
from dependencies import numberformat as nf
import pandas as pd


class StockInfoTab(QTabWidget):
    def __init__(self, string_list) -> None:
        super().__init__()
        self.setStyleSheet("background-color: deepskyblue;")
        self.main_tab = StockInfoMain(string_list)
        self.main_tab.searchbar_gb.search_button.clicked.connect(self.stockinfo_searchbar_click)

        self.recs_tab = StockInfoRecs()
        self.forecasts_tab = StockInfoForecasts()
        self.financials_tab = StockInfoFinancials()


        self.addTab(self.main_tab, "Overview")
        self.addTab(self.recs_tab, "Insiders and Institutions")
        self.addTab(self.forecasts_tab, "Forecasts")
        self.addTab(self.financials_tab, "Financials")

        self.connect(self, SIGNAL('currentChanged(int)'), lambda: self.stockinfo_dialog_changed(self.currentIndex()))

        self.TAB2_ISLOADED = False
        self.TAB3_ISLOADED = False
        self.TAB4_ISLOADED = False

    def stockinfo_searchbar_click(self):
        """
        Initiates the retrieval and display of stock information when the searchbar button
        is pressed
        """
        self.TAB2_ISLOADED = False
        self.TAB3_ISLOADED = False
        self.TAB4_ISLOADED = False

        ticker = self.main_tab.searchbar_gb.searchBar.text().split(' ')[0]
        yq_ticker = yq.Ticker(ticker)

        if yq_ticker.quote_type[ticker]['quoteType'] == 'ETF':
            self.setTabEnabled(1, False)
            self.setTabEnabled(2, False)
            self.setTabEnabled(3, False)
            self.setup_etf_info(yq_ticker, ticker)
        elif yq_ticker.quote_type[ticker]['quoteType'] == 'EQUITY':
            self.setTabEnabled(1, True)
            self.setTabEnabled(2, True)
            self.setTabEnabled(3, True)
            self.setup_stock_info(yq_ticker, ticker)

    def get_etf_weights(self, ticker_info: pd.DataFrame) -> dict:
        """
        Creates a dictionary with sector names as keys and sector
        weights as values from the given ticker information dataframe,
        obtained from a call to yq.Ticker('name').fund_sector_weightings
        """

        return {
            "Real Estate" : ticker_info.iat[0, 0],
            "Consumer Cyclicals" : ticker_info.iat[1, 0],
            "Basic Materials" : ticker_info.iat[2, 0],
            "Consumer Defensives" : ticker_info.iat[3, 0],
            "Technology" : ticker_info.iat[4, 0],
            "Communication Services" : ticker_info.iat[5, 0],
            "Financial Services" : ticker_info.iat[6, 0],
            "Utilities" : ticker_info.iat[7, 0],
            "Industrials" : ticker_info.iat[8, 0],
            "Energy" : ticker_info.iat[9, 0],
            "Healthcare" : ticker_info.iat[10, 0]
        }


    def setup_etf_info(self, ticker: yq.Ticker, name: str):
        """
        Populates the stock information dialog with the given ETF's info
        """
        ticker_data = ticker.all_modules

        price_data = ticker_data[name]['price']
        fund_profile = ticker_data[name]['fundProfile']
        quote_type = ticker_data[name]['quoteType']
        summary_detail = ticker_data[name]['summaryDetail']
        asset_profile = ticker_data[name]['assetProfile']
        key_stats = ticker_data[name]['defaultKeyStatistics']
        fund_performance = ticker.fund_performance[name]['trailingReturns']
        etf_weights = self.get_etf_weights(ticker.fund_sector_weightings)
        ticker_news = fn.get_finviz_news(name)


        self.main_tab.about_groupbox.setVisible(True)
        self.main_tab.asset_info_gb.setVisible(True)
        self.main_tab.news_groupbox.setVisible(True)


        full_name_label = QLabel(f"Full Name: {price_data['longName']}")

        category_label = QLabel(f"Category: {fund_profile['categoryName']}")

        exchange_label = QLabel(f"Exchange: {quote_type['exchange']}")

        total_assets_label = QLabel(f"Total Assets: {summary_detail['totalAssets']}")


        description_label = QLabel("Description: " + asset_profile['longBusinessSummary'])
        description_label.setWordWrap(True)

        inception_label = QLabel(f"Date of Inception: {key_stats['fundInceptionDate']}")

        more_info_label = QLabel("Hover over a slice of the pie chart for more information")
        more_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        ai_button = QPushButton('Get AI Prediction')
        ai_button.clicked.connect(lambda: spred.run(name))

        weights_piechart = QPieSeries()

        for index, (sector, weight) in enumerate(etf_weights.items()):
            weights_piechart.append(sector, index + 1)
            weights_piechart.slices()[index].setValue(weight * 100)
            weights_piechart.slices()[index].setLabelVisible(True)
            weights_piechart.slices()[index].setLabelFont(QFont('arial', 8))

        def on_slice_hover(idx, state):
            _slice = weights_piechart.slices()[idx]
            _slice.setExploded(state)
            border_width = 2 if state else 0
            _slice.setBorderWidth(border_width)
            _slice.setBorderColor(QColor('black'))
            more_info_label.setText(f'{_slice.label()} - {_slice.value()}%')

        weights_chart = QChart()
        weights_chart.addSeries(weights_piechart)
        weights_chart.setTitle(f"{name} Holdings by Sector")
        weights_chart.setVisible(True)

        weights_chartview = QChartView(weights_chart)
        weights_piechart.slices()[0].hovered.connect(lambda state: on_slice_hover(0, state))
        weights_piechart.slices()[1].hovered.connect(lambda state: on_slice_hover(1, state))
        weights_piechart.slices()[2].hovered.connect(lambda state: on_slice_hover(2, state))
        weights_piechart.slices()[3].hovered.connect(lambda state: on_slice_hover(3, state))
        weights_piechart.slices()[4].hovered.connect(lambda state: on_slice_hover(4, state))
        weights_piechart.slices()[5].hovered.connect(lambda state: on_slice_hover(5, state))
        weights_piechart.slices()[6].hovered.connect(lambda state: on_slice_hover(6, state))
        weights_piechart.slices()[7].hovered.connect(lambda state: on_slice_hover(7, state))
        weights_piechart.slices()[8].hovered.connect(lambda state: on_slice_hover(8, state))
        weights_piechart.slices()[9].hovered.connect(lambda state: on_slice_hover(9, state))
        weights_piechart.slices()[10].hovered.connect(lambda state: on_slice_hover(10, state))


        current_price_label = QLabel(f"Current Price: {price_data['regularMarketPrice']}")
        open_price_label = QLabel(f"\tOpen: {price_data['regularMarketOpen']}")
        high_price_label = QLabel(f"\tHigh: {price_data['regularMarketDayHigh']}")
        low_price_label = QLabel(f"\tLow: {price_data['regularMarketDayLow']}")
        close_price_label = QLabel(f"\tLast Close: {summary_detail['regularMarketPreviousClose']}")
        nav_price_label = QLabel(f"NAV Price: {summary_detail['navPrice']}")

        bid_label = QLabel(f"Bid: {summary_detail['bid']} ({summary_detail['bidSize']})")
        ask_label = QLabel(f"Ask: {summary_detail['ask']} ({summary_detail['askSize']})")

        volume_label = QLabel(f"Volume: {summary_detail['regularMarketVolume']}")
        avg_volume_label = QLabel(f"Average Volume (10d): {summary_detail['averageVolume10days']}")
        long_avg_volume_label = QLabel(f"Average Volume (1M): {summary_detail['averageVolume']} ")

        year_high_label = QLabel(f"52 Week High: {summary_detail['fiftyTwoWeekHigh']}")
        year_low_label = QLabel(f"52 Week Low: {summary_detail['fiftyTwoWeekLow']}")

        averages_label = QLabel("Price Averages: ")
        fifty_avg_label = QLabel(f"\t50d MA: {summary_detail['fiftyDayAverage']}")
        twohundred_avg_label = QLabel(f"\t200d MA: {summary_detail['twoHundredDayAverage']}")

        threeyr_cagr_label = QLabel(
            f"Three-Year CAGR: {fund_performance['threeYear'] * 100}% per annum")
        fiveyr_cagr_label = QLabel(f"Five-Year CAGR: {fund_performance['fiveYear'] * 100}% per annum")

        try:
            dividend_label = QLabel(
                f"Trailing Dividend Yield: {summary_detail['trailingAnnualDividendYield'] * 100}%"
            )
        except KeyError:  # ETF does not pay a dividend
            dividend_label = QLabel("Trailing Annual Dividend Yield: 0% per annum")

        try:
            dividend_rate_label = QLabel(
                f"Trailing Dividend Rate: ${summary_detail['trailingAnnualDividendRate']}"
            )
        except KeyError:
            dividend_rate_label = QLabel("Trailing Annual Dividend Rate: $0.00")

        beta_3y_label = QLabel(f"3-Year Beta (Relative to SPY): {key_stats['beta3Year']}")


        clear_layout(self.main_tab.about_scrollarea_widget.layout())
        clear_layout(self.main_tab.assetinfo_scrollarea_widget.layout())
        clear_layout(self.main_tab.news_groupbox.layout())

        for news_item in ticker_news:
            news_label = QLabel(f"""
                <a href=\"{news_item['link']}\">
                    <font face=verdana size=1 color=black> {news_item['title']}</font>
                </a>
                <br>
                <a>{news_item['source']}
                <br> {news_item['dateTime']}
                </a>
            """)
            news_label.setOpenExternalLinks(True)
            news_label.setStyleSheet("""QToolTip {
                               font-size: 12px
                               }""")
            news_label.setToolTip(news_item['link'])
            self.main_tab.news_groupbox.layout().addWidget(news_label)

        self.main_tab.about_scrollarea_widget.layout().addWidget(full_name_label)
        self.main_tab.about_scrollarea_widget.layout().addWidget(category_label)
        self.main_tab.about_scrollarea_widget.layout().addWidget(exchange_label)
        self.main_tab.about_scrollarea_widget.layout().addWidget(total_assets_label)
        self.main_tab.about_scrollarea_widget.layout().addWidget(inception_label)
        self.main_tab.about_scrollarea_widget.layout().addWidget(description_label)
        self.main_tab.about_scrollarea_widget.layout().addWidget(weights_chartview)
        self.main_tab.about_scrollarea_widget.layout().addWidget(more_info_label)
        self.main_tab.about_scrollarea_widget.layout().addWidget(ai_button)


        self.main_tab.assetinfo_scrollarea_widget.layout().addWidget(current_price_label)
        self.main_tab.assetinfo_scrollarea_widget.layout().addWidget(open_price_label)
        self.main_tab.assetinfo_scrollarea_widget.layout().addWidget(high_price_label)
        self.main_tab.assetinfo_scrollarea_widget.layout().addWidget(low_price_label)
        self.main_tab.assetinfo_scrollarea_widget.layout().addWidget(close_price_label)
        self.main_tab.assetinfo_scrollarea_widget.layout().addWidget(nav_price_label)
        self.main_tab.assetinfo_scrollarea_widget.layout().addWidget(bid_label)
        self.main_tab.assetinfo_scrollarea_widget.layout().addWidget(ask_label)
        self.main_tab.assetinfo_scrollarea_widget.layout().addWidget(volume_label)
        self.main_tab.assetinfo_scrollarea_widget.layout().addWidget(avg_volume_label)
        self.main_tab.assetinfo_scrollarea_widget.layout().addWidget(long_avg_volume_label)
        self.main_tab.assetinfo_scrollarea_widget.layout().addWidget(year_high_label)
        self.main_tab.assetinfo_scrollarea_widget.layout().addWidget(year_low_label)
        self.main_tab.assetinfo_scrollarea_widget.layout().addWidget(averages_label)
        self.main_tab.assetinfo_scrollarea_widget.layout().addWidget(fifty_avg_label)
        self.main_tab.assetinfo_scrollarea_widget.layout().addWidget(twohundred_avg_label)
        self.main_tab.assetinfo_scrollarea_widget.layout().addWidget(threeyr_cagr_label)
        self.main_tab.assetinfo_scrollarea_widget.layout().addWidget(fiveyr_cagr_label)
        self.main_tab.assetinfo_scrollarea_widget.layout().addWidget(dividend_label)
        self.main_tab.assetinfo_scrollarea_widget.layout().addWidget(dividend_rate_label)
        self.main_tab.assetinfo_scrollarea_widget.layout().addWidget(beta_3y_label)


    def setup_stock_info(self, ticker: yq.Ticker, name: str):
        """
        Populates the stock information dialog with the given stock's info
        """
        ticker_data = ticker.all_modules
        ticker_news = fn.get_finviz_news(name)

        price_data = ticker_data[name]['price']
        asset_profile = ticker_data[name]['assetProfile']
        summary_detail = ticker_data[name]['summaryDetail']

        self.main_tab.about_groupbox.setVisible(True)
        self.main_tab.asset_info_gb.setVisible(True)
        self.main_tab.news_groupbox.setVisible(True)
        self.recs_tab.analyst_rec_groupbox.setVisible(True)
        self.recs_tab.iandi_groupbox.setVisible(True)
        self.recs_tab.mutfund_groupbox.setVisible(True)

        full_name_label = QLabel(f"Full Name: {price_data['longName']}")

        sector_label = QLabel(f"Sector: {asset_profile['sector']}: {asset_profile['industry']}")

        country_label = QLabel(f"Country: {asset_profile['country']}")

        description_label = QLabel("Description: " + asset_profile['longBusinessSummary'])

        description_label.setWordWrap(True)

        location_label = QLabel(f"Location: {asset_profile['city']}, {asset_profile['state']}")

        website_label = QLabel(
            f"Website: <a href=\"{asset_profile['website']}\"> {asset_profile['website']} </a>")

        ai_button = QPushButton('Get AI Prediction')
        ai_button.clicked.connect(lambda: spred.run(name))

        current_price_label = QLabel(f"Current Price: {price_data['regularMarketPrice']}")
        open_price_label = QLabel(f"\tOpen: {price_data['regularMarketOpen']}")
        high_price_label = QLabel(f"\tHigh: {price_data['regularMarketDayHigh']}")
        low_price_label = QLabel(f"\tLow: {price_data['regularMarketDayLow']}")
        close_price_label = QLabel(f"\tLast Close: {price_data['regularMarketPreviousClose']}")

        bid_label = QLabel(f"Bid: {summary_detail['bid']} ({summary_detail['bidSize']})")
        ask_label = QLabel(f"Ask: {summary_detail['ask']} ({summary_detail['askSize']})")

        volume_label = QLabel(f"Volume: {price_data['regularMarketVolume']}")
        avg_volume_label = QLabel(f"Average Volume (10d): {summary_detail['averageVolume10days']}")
        long_avg_volume_label = QLabel(f"Average Volume (3M): {summary_detail['averageVolume']} ")

        year_high_label = QLabel(f"52 Week High: {summary_detail['fiftyTwoWeekHigh']}")
        year_low_label = QLabel(f"52 Week Low: {summary_detail['fiftyTwoWeekLow']}")

        averages_label = QLabel("Price Averages: ")
        fifty_avg_label = QLabel(f"\t50d MA: {summary_detail['fiftyDayAverage']}")
        twohundred_avg_label = QLabel(f"\t200d MA: {summary_detail['twoHundredDayAverage']}")


        clear_layout(self.main_tab.about_scrollarea_widget.layout())
        clear_layout(self.main_tab.assetinfo_scrollarea_widget.layout())
        clear_layout(self.main_tab.news_groupbox.layout())
        clear_layout(self.recs_tab.analyst_rec_groupbox.layout())
        clear_layout(self.recs_tab.iandi_groupbox.layout())
        clear_layout(self.recs_tab.mutfund_groupbox.layout())

        for news_item in ticker_news:
            news_label = QLabel(f"""
                <a href=\"{news_item['link']}\">
                    <font face=verdana size=1 color=black> {news_item['title']}</font>
                </a>
                <br>
                <a>{news_item['source']}
                <br> {news_item['dateTime']}
                </a>
            """)
            news_label.setOpenExternalLinks(True)
            news_label.setStyleSheet("""QToolTip {
                               font-size: 12px
                               }""")
            news_label.setToolTip(news_item['link'])
            self.main_tab.news_groupbox.layout().addWidget(news_label)



        self.main_tab.about_scrollarea_widget.layout().addWidget(full_name_label)
        self.main_tab.about_scrollarea_widget.layout().addWidget(sector_label)
        self.main_tab.about_scrollarea_widget.layout().addWidget(country_label)
        self.main_tab.about_scrollarea_widget.layout().addWidget(description_label)
        self.main_tab.about_scrollarea_widget.layout().addWidget(location_label)
        self.main_tab.about_scrollarea_widget.layout().addWidget(website_label)
        self.main_tab.about_scrollarea_widget.layout().addWidget(ai_button)


        self.main_tab.assetinfo_scrollarea_widget.layout().addWidget(current_price_label)
        self.main_tab.assetinfo_scrollarea_widget.layout().addWidget(open_price_label)
        self.main_tab.assetinfo_scrollarea_widget.layout().addWidget(high_price_label)
        self.main_tab.assetinfo_scrollarea_widget.layout().addWidget(low_price_label)
        self.main_tab.assetinfo_scrollarea_widget.layout().addWidget(close_price_label)
        self.main_tab.assetinfo_scrollarea_widget.layout().addWidget(bid_label)
        self.main_tab.assetinfo_scrollarea_widget.layout().addWidget(ask_label)
        self.main_tab.assetinfo_scrollarea_widget.layout().addWidget(volume_label)
        self.main_tab.assetinfo_scrollarea_widget.layout().addWidget(avg_volume_label)
        self.main_tab.assetinfo_scrollarea_widget.layout().addWidget(long_avg_volume_label)
        self.main_tab.assetinfo_scrollarea_widget.layout().addWidget(year_high_label)
        self.main_tab.assetinfo_scrollarea_widget.layout().addWidget(year_low_label)
        self.main_tab.assetinfo_scrollarea_widget.layout().addWidget(averages_label)
        self.main_tab.assetinfo_scrollarea_widget.layout().addWidget(fifty_avg_label)
        self.main_tab.assetinfo_scrollarea_widget.layout().addWidget(twohundred_avg_label)


    def stockinfo_dialog_changed(self, tab_id: int):
        """
        Populates each tab in the stock information dialog when the user clicks on it
        """

        name = self.main_tab.searchbar_gb.searchBar.text().split(' ')[0]
        ticker = yq.Ticker(name)
        ticker_data = ticker.all_modules

        if (tab_id == 1 and not self.TAB2_ISLOADED):
            ticker_recommendations = ticker_data[name]['upgradeDowngradeHistory']['history'][:9]
            ticker_instholders = ticker_data[name]['institutionOwnership']['ownershipList'][:9]
            ticker_mutfundholders = ticker_data[name]['fundOwnership']['ownershipList'][:9]

            for recommendation in ticker_recommendations:
                txt = f"""
                {recommendation['firm']}: {recommendation['toGrade']} <br>
                {recommendation['epochGradeDate']}
                """
                self.recs_tab.analyst_rec_groupbox.layout().addWidget(QLabel(txt))

            for instholder in ticker_instholders:
                txt = f"""
                {instholder['organization']}: {instholder['position']} shares ({instholder['pctHeld'] * 100}%) <br>
                {instholder['reportDate']}
                """
                self.recs_tab.iandi_groupbox.layout().addWidget(QLabel(txt))

            for mutfund in ticker_mutfundholders:
                txt = f"""
                {mutfund['organization']}: {mutfund['position']} shares ({mutfund['pctHeld'] * 100}%) <br>
                {mutfund['reportDate']}
                """
                self.recs_tab.mutfund_groupbox.layout().addWidget(QLabel(txt))

            self.TAB2_ISLOADED = True

        elif (tab_id == 2 and not self.TAB3_ISLOADED):
            ticker_pts = ticker_data[name]['financialData']
            ticker_hist = ticker.history(period="2y", interval="1wk")
            ticker_qtr_earnings = ticker_data[name]['earningsHistory']['history']
            ticker_qtr_rev = ticker_data[name]['earnings']['financialsChart']['quarterly']
            ticker_yr_earnings_rev = ticker_data[name]['earnings']['financialsChart']['yearly']

            self.forecasts_tab.ptchart.removeAxis(self.forecasts_tab.ptchart.axes(Qt.Orientation.Horizontal)[0])
            self.forecasts_tab.ptchart.removeAxis(self.forecasts_tab.ptchart.axes(Qt.Orientation.Vertical)[0])

            self.forecasts_tab.ptchart.removeAllSeries()

            series = QLineSeries()

            series2 = QLineSeries()

            series3 = QLineSeries()

            series4 = QLineSeries()

            current_dt = float(QDateTime().currentDateTime().toMSecsSinceEpoch())
            prediction_date = QDateTime().currentDateTime().addYears(1).toMSecsSinceEpoch()
            date_format = "yyyy-MM-dd hh:mm:ss"
            for idx, close in enumerate(ticker_hist.loc[:, 'adjclose']):
                price_dt = QDateTime().fromString(f"{ticker_hist.index[idx][1]}"[0:19], date_format)

                series.append(float(price_dt.toMSecsSinceEpoch()), close)

            series.append(float(prediction_date), ticker_pts['currentPrice'])
            series.setName("Current Price")
            series.setColor(QColor("blue"))

            series2.setName("Worst Case")
            series2.setColor(QColor("red"))

            series3.setName("Mean Target Price")
            series3.setColor(QColor("black"))

            series4.setName("Best Case")
            series4.setColor(QColor("green"))

            current_price = ticker_hist.iat[-1, 3]
            series2.append(current_dt, current_price)
            series2.append(float(prediction_date), ticker_pts['targetLowPrice'])

            series3.append(current_dt, current_price)
            series3.append(float(prediction_date), ticker_pts['targetMeanPrice'])

            series4.append(current_dt, current_price)
            series4.append(float(prediction_date), ticker_pts['targetHighPrice'])

            self.forecasts_tab.ptchart.addSeries(series)
            self.forecasts_tab.ptchart.addSeries(series2)
            self.forecasts_tab.ptchart.addSeries(series3)
            self.forecasts_tab.ptchart.addSeries(series4)

            self.forecasts_tab.ptchart.createDefaultAxes()
            self.forecasts_tab.ptchart.axes(Qt.Orientation.Horizontal)[0].hide()

            self.forecasts_tab.ptchart_x_axis = QDateTimeAxis()
            self.forecasts_tab.ptchart_x_axis.setTickCount(7)
            self.forecasts_tab.ptchart_x_axis.setFormat("MM-dd-yyyy")
            self.forecasts_tab.ptchart_x_axis.setTitleText("Date")
            self.forecasts_tab.ptchart_x_axis.setVisible(True)

            self.forecasts_tab.ptchart.addAxis(self.forecasts_tab.ptchart_x_axis, Qt.AlignmentFlag.AlignBottom)
            series.attachAxis(self.forecasts_tab.ptchart_x_axis)

            clear_layout(self.forecasts_tab.pt_label_container.layout())
            self.forecasts_tab.pt_label_container.layout().addWidget(
                QLabel(f"Current Price: {ticker_pts['currentPrice']}")
            )
            self.forecasts_tab.pt_label_container.layout().addWidget(
                QLabel(f"Target Low Price: {ticker_pts['targetLowPrice']}")
            )
            self.forecasts_tab.pt_label_container.layout().addWidget(
                QLabel(f"Target Mean Price: {ticker_pts['targetMeanPrice']}")
            )
            self.forecasts_tab.pt_label_container.layout().addWidget(
                QLabel(f"Target High Price: {ticker_pts['targetHighPrice']}")
            )
            self.forecasts_tab.pt_label_container.layout().addWidget(
                QLabel(f"Number of Analyst Opinions: {ticker_pts['numberOfAnalystOpinions']}")
            )


            self.forecasts_tab.qtr_earnings_chart.removeAllSeries()
            series = QBarSeries()

            actual_qtr_earnings_set = QBarSet("Actual")
            estimate_qtr_earnings_set = QBarSet("Estimate")
            earnings_trend_max = 0
            earnings_trend_min = 0

            self.forecasts_tab.qtr_earnings_table.setRowCount(5)
            self.forecasts_tab.qtr_earnings_table.setColumnCount(3)
            self.forecasts_tab.qtr_earnings_table.setHorizontalHeaderItem(0, QTableWidgetItem("Actual"))
            self.forecasts_tab.qtr_earnings_table.setHorizontalHeaderItem(1, QTableWidgetItem("Expected"))
            self.forecasts_tab.qtr_earnings_table.setHorizontalHeaderItem(2, QTableWidgetItem("Surprise"))

            for idx in range(self.forecasts_tab.qtr_earnings_table.columnCount()):
                self.forecasts_tab.qtr_earnings_table.horizontalHeaderItem(idx).setFont(QFont('arial', 10))

            for idx in range(self.forecasts_tab.qtr_earnings_table.rowCount()):
                self.forecasts_tab.qtr_earnings_table.setVerticalHeaderItem(idx, QTableWidgetItem(f"{idx + 1}"))
                self.forecasts_tab.qtr_earnings_table.verticalHeaderItem(idx).setFont(QFont('arial', 10))

            for idx, report in enumerate(ticker_qtr_earnings):
                reported = report['epsActual']
                actual_qtr_earnings_set.append(reported)
                if reported > earnings_trend_max:
                    earnings_trend_max = reported
                if reported < earnings_trend_min:
                    earnings_trend_min = reported

                estimate = report['epsEstimate']
                if estimate > earnings_trend_max:
                    earnings_trend_max = estimate
                if estimate < earnings_trend_min:
                    earnings_trend_min = estimate
                estimate_qtr_earnings_set.append(estimate)

                self.forecasts_tab.qtr_earnings_table.setItem(idx, 0, QTableWidgetItem(f"{reported}"))
                self.forecasts_tab.qtr_earnings_table.setItem(idx, 1, QTableWidgetItem(f"{estimate}"))
                self.forecasts_tab.qtr_earnings_table.setItem(idx, 2, QTableWidgetItem(f"{reported - estimate}"))

            series.append(actual_qtr_earnings_set)
            series.append(estimate_qtr_earnings_set)
            self.forecasts_tab.qtr_earnings_chart.addSeries(series)
            self.forecasts_tab.qtr_earnings_chart.createDefaultAxes()
            self.forecasts_tab.qtr_earnings_chart.axes(Qt.Orientation.Vertical)[0].setRange(
                earnings_trend_min * 1.1, earnings_trend_max * 1.1)

            self.forecasts_tab.qtr_revtrend_chart.removeAllSeries()
            qtr_rev_barseries = QBarSeries()
            qtr_rev_barset = QBarSet("Revenue")
            qtr_revtrend_max = 0
            qtr_revtrend_min = 0
            for rev in ticker_qtr_rev:
                revenue = rev['revenue']
                qtr_rev_barset.append(float(revenue))
                if revenue > qtr_revtrend_max:
                    qtr_revtrend_max = revenue
                if revenue < qtr_revtrend_min:
                    qtr_revtrend_min = revenue
                self.forecasts_tab.qtr_revtrend_label_container.layout().addWidget(QLabel(f"{rev['date']}: {revenue}"))

            qtr_rev_barseries.append(qtr_rev_barset)

            self.forecasts_tab.qtr_revtrend_chart.addSeries(qtr_rev_barseries)
            self.forecasts_tab.qtr_revtrend_chart.createDefaultAxes()
            self.forecasts_tab.qtr_revtrend_chart.axes(Qt.Orientation.Vertical)[0].setRange(
                qtr_revtrend_min * 1.1, qtr_revtrend_max * 1.1)

            self.forecasts_tab.yr_earnings_chart.removeAllSeries()
            clear_layout(self.forecasts_tab.yr_earnings_label_container.layout())
            yr_er_barseries = QBarSeries()
            yr_er_barset = QBarSet("Earnings")
            yr_eps_max = 0
            yr_eps_min = 0

            for report in ticker_yr_earnings_rev:
                earnings = float(report['earnings'])
                if earnings > yr_eps_max:
                    yr_eps_max = earnings
                if earnings < yr_eps_min:
                    yr_eps_min = earnings
                yr_er_barset.append(earnings)
                self.forecasts_tab.yr_earnings_label_container.layout().addWidget(
                    QLabel(f"{report['date']}: {earnings}"))

            yr_er_barseries.append(yr_er_barset)
            self.forecasts_tab.yr_earnings_chart.addSeries(yr_er_barseries)
            self.forecasts_tab.yr_earnings_chart.createDefaultAxes()
            self.forecasts_tab.yr_earnings_chart.axes(Qt.Orientation.Vertical)[0].setRange(
                yr_eps_min * 1.1, yr_eps_max * 1.1)

            self.forecasts_tab.yr_revtrend_chart.removeAllSeries()
            clear_layout(self.forecasts_tab.yr_revtrend_label_container.layout())
            year_rev_series = QBarSeries()
            year_rev_set = QBarSet("Revenue")

            yr_revtrend_max = 0
            yr_revtrend_min = 0
            for report in ticker_yr_earnings_rev:
                rev = float(report['revenue'])
                year_rev_set.append(rev)
                yr_revtrend_max = rev if rev > yr_revtrend_max else yr_revtrend_max
                yr_revtrend_min = rev if rev < yr_revtrend_min else yr_revtrend_min
                self.forecasts_tab.yr_revtrend_label_container.layout().addWidget(
                    QLabel(f"{report['date']}: {rev}"))

            year_rev_set.setPen(QColor("green"))

            year_rev_series.append(year_rev_set)

            self.forecasts_tab.yr_revtrend_chart.addSeries(year_rev_series)
            self.forecasts_tab.yr_revtrend_chart.createDefaultAxes()
            self.forecasts_tab.yr_revtrend_chart.axes(Qt.Orientation.Vertical)[0].setRange(
                yr_revtrend_min * 1.1, yr_revtrend_max * 1.1)
            self.TAB3_ISLOADED = True

        elif (tab_id == 3 and not self.TAB4_ISLOADED):
            ticker_financials = ticker.all_financial_data()
            self.financials_tab.financials_table.setRowCount(ticker_financials.columns.size)
            self.financials_tab.financials_table.setColumnCount(5)

            for idx in range(4):
                tw_item = QTableWidgetItem(f"{ticker_financials.iat[idx, 0]}"[:10])
                self.financials_tab.financials_table.setHorizontalHeaderItem(idx, tw_item)
                self.financials_tab.financials_table.horizontalHeaderItem(idx).setFont(QFont('arial', 10))

            for idx in range(4):
                for j in range(3, ticker_financials.iloc[0].size):
                    current_data = float(ticker_financials.iat[idx, j])
                    if current_data > 1000:
                        formatted_data = nf.simplify(current_data, True)
                        self.financials_tab.financials_table.setItem(j, idx, QTableWidgetItem(formatted_data))
                    elif current_data < -1000:
                        formatted_data = nf.simplify(abs(current_data), True)
                        self.financials_tab.financials_table.setItem(j, idx, QTableWidgetItem(f"-{formatted_data}"))
                    else:
                        self.financials_tab.financials_table.setItem(j, idx, QTableWidgetItem(f"{current_data}"))

            checkboxes = QButtonGroup()

            for idx in range(ticker_financials.iloc[0].size):

                checkbox = QCheckBox()
                checkboxes.addButton(checkbox)
                item = QTableWidgetItem(ticker_financials.columns[idx])
                self.financials_tab.financials_table.setVerticalHeaderItem(idx, item)
                self.financials_tab.financials_table.verticalHeaderItem(idx).setFont(QFont("arial", 10))
                checkbox.clicked.connect(self.on_financials_checkbox_click)

                self.financials_tab.financials_table.setCellWidget(idx, 4, checkbox)
            self.TAB4_ISLOADED = True

    def on_financials_checkbox_click(self):
        """
        Adds the financial data from the checkbox's row to the chart in the financials
        tab of the stockinfo dialog when selected
        """

        self.financials_tab.financials_chart.removeAllSeries()
        series = QBarSeries()
        for outer in range(self.financials_tab.financials_table.rowCount()):
            box = self.financials_tab.financials_table.cellWidget(outer, 4)
            if box.isChecked():
                financials_set = QBarSet(self.financials_tab.financials_table.verticalHeaderItem(outer).text())
                for inner in range(4):
                    val = self.financials_tab.financials_table.item(outer, inner).text()
                    last_char = val[-1]
                    match last_char:
                        case 'k':
                            financials_set.append(float(val[:-1]) * 10**3)
                        case 'M':
                            financials_set.append(float(val[:-1]) * 10**6)
                        case 'B':
                            financials_set.append(float(val[:-1]) * 10**9)
                        case 'T':
                            financials_set.append(float(val[:-1]) * 10**12)
                        case _:
                            financials_set.append(float(val))
                series.append(financials_set)

        self.financials_tab.financials_chart.addSeries(series)
        self.financials_tab.financials_chart.createDefaultAxes()