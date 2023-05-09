from PySide6.QtWidgets import QGroupBox, QLabel, QVBoxLayout, QTableWidget, QWidget, QHBoxLayout
from PySide6.QtGui import QFont
from functools import reduce
import yahooquery as yq
from widgets.portfolio.portfolio import Portfolio

class PortfolioOverview(QGroupBox):
    def __init__(self):
        super().__init__()
        self.setLayout(QVBoxLayout())
        self.setStyleSheet('background-color: white;')
        self.setTitle("Your NAV")

        self.label = QLabel("Net Liq:", self)
        self.label.setFont(QFont('genius', 10))
        self.layout().addWidget(self.label)

        self.net_liq = QLabel(self)
        self.net_liq.setFont(QFont('genius', 20))
        self.layout().addWidget(self.net_liq)

        self.cash_widget = QWidget(self)
        self.cash_widget.setLayout(QHBoxLayout())
        self.cash_widget.layout().setContentsMargins(1, 1, 1, 1)
        self.cash_widget.layout().addWidget(QLabel("Cash:", self.cash_widget))

        self.cash = QLabel(self)
        self.cash_widget.layout().addWidget(self.cash)

        self.layout().addWidget(self.cash_widget)

        self.bp_widget = QWidget(self)
        self.bp_widget.setLayout(QHBoxLayout())
        self.bp_widget.layout().setContentsMargins(1, 0, 1, 0)
        w = QLabel("Buying Power:", self.bp_widget)
        self.bp_widget.layout().addWidget(w)

        self.bp = QLabel(self)
        self.bp_widget.layout().addWidget(self.bp)
        self.bp.adjustSize()
        self.bp_widget.adjustSize()
        self.layout().addWidget(self.bp_widget)

        self.long_assets_widget = QWidget(self)
        self.long_assets_widget.setLayout(QHBoxLayout())
        self.long_assets_widget.layout().setContentsMargins(1, 0, 1, 0)
        self.long_assets_widget.layout().addWidget(QLabel("Long Assets:", self.long_assets_widget))

        self.long_assets = QLabel(self)
        self.long_assets_widget.layout().addWidget(self.long_assets)
        self.layout().addWidget(self.long_assets_widget)

        self.short_assets_widget = QWidget(self)
        self.short_assets_widget.setLayout(QHBoxLayout())
        self.short_assets_widget.layout().setContentsMargins(1, 1, 1, 1)
        self.short_assets_widget.layout().addWidget(QLabel("Short Assets:", self.short_assets_widget))

        self.short_assets = QLabel(self)
        self.short_assets.adjustSize()
        self.short_assets_widget.layout().addWidget(self.short_assets)
        self.layout().addWidget(self.short_assets_widget)

        self.option_req_widget = QWidget(self)
        self.option_req_widget.setLayout(QHBoxLayout())
        self.option_req_widget.layout().setContentsMargins(1, 0, 1, 0)
        self.option_req_widget.layout().addWidget(QLabel("Option Req:", self.option_req_widget))

        self.option_req = QLabel(self)
        self.option_req_widget.layout().addWidget(self.option_req)
        self.layout().addWidget(self.option_req_widget)
        self.layout().setSpacing(0)

        self.inc_return_label = QLabel("Return Since Inception:", self)
        self.layout().addWidget(self.inc_return_label)

        self.inc_return = QLabel(self)
        self.inc_return.setFont(QFont('genius', 20))
        self.layout().addWidget(self.inc_return)


    def update(self, pos_view_table: QTableWidget, portfolio: Portfolio):
        portfolio_amts = [position.amt for position in portfolio]
        portfolio_tickers = [position.ticker for position in portfolio]
        portfolio_asset_types = [position.asset_type for position in portfolio]
        values = [
            float(pos_view_table.item(i, 2).text()[1:]) * portfolio_amts[i + 1]
            for i in range(pos_view_table.rowCount())
        ]

        long_assets = reduce(lambda x, y: x + y, filter(lambda e: e > 0, values), 0)
        short_assets = reduce(lambda x, y: x + y, filter(lambda e: e < 0, values), 0)

        values.append(portfolio_amts[0])

        new_val = reduce(lambda x, y: x + y, values)


        self.net_liq.setText(f"${new_val:0,.2f}")
        self.cash.setText(f"${portfolio_amts[0]:0,.2f}")
        self.bp.setText(f"${self._get_portfolio_bp(values):0,.2f}")
        self.long_assets.setText(f"${long_assets:0,.2f}")
        self.short_assets.setText(f"${short_assets:0,.2f}")
        self.option_req.setText(f"${self._get_option_req(portfolio_tickers, portfolio_amts, portfolio_asset_types):0,.2f}")
        self.inc_return.setText(f'{((new_val / 10000 - 1) * 100):0,.2f}%')

    def _get_portfolio_bp(self, values: list):
        return values[-1] + reduce(lambda x, y: x + (y * 2 if y < 0 else y * .5), values[:-1], 0)

    def _get_option_req(self, portfolio_tickers: list, portfolio_amts: list, portfolio_asset_types: list):
        portfolio_zip = zip(portfolio_tickers[1:], portfolio_asset_types[1:], portfolio_amts[1:])
        options = filter(lambda e: e[1] == 'Option' and e[2] < 0, portfolio_zip)
        if len(list(options)) == 0:
            return 0

        option_collateral = 0

        for option in options:
            option_obj = yq.Ticker(option[0]).all_modules[option[0]]
            shortname_list = option_obj['price']['shortName'].split(' ')
            underlying_price = yq.Ticker(shortname_list[0]).price[shortname_list[0]]['regularMarketPrice']
            is_itm = float(shortname_list[-2]) > underlying_price
            strike = float(shortname_list[-2])
            option_collateral += (
                .2 * underlying_price * 100 * option[1]
            ) if is_itm else max(
                .1 * strike * 100, .2 * (underlying_price - (underlying_price - strike)) * 100
            ) * option[1]
        return option_collateral
