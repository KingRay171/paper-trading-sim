from typing import Optional
import PySide6.QtCore
from PySide6.QtWidgets import QDialog, QGroupBox, QLabel, QTableWidget, QTableWidgetItem, QAbstractItemView
from PySide6.QtGui import QFont
import yahooquery as yq
from dependencies.perficon import update_ticker_icon
from widgets.wallet.wallet import Wallet
from locale import atof, setlocale

class WalletTab(QDialog):
    def __init__(self, wallet: Wallet) -> None:
        super().__init__()
        self.setStyleSheet('background-color: goldenrod')
        self.font = QFont('arial', 10)
        # user's crypto wallet NAV
        self.nav_gb = QGroupBox(self)
        self.nav_gb.setTitle("Your NAV")
        self.nav_gb.setGeometry(10, 10, 250, 250)
        self.nav_gb.setStyleSheet('background-color: black; color: white;')
        # net liquidation value labels
        self.nav_gb.netLiq = QLabel(self.nav_gb)
        self.nav_gb.netLiq.setText("Net Liq: ")
        self.nav_gb.netLiq.setGeometry(10, 20, 80, 20)
        self.nav_gb.netLiq.setFont(QFont('genius', 10))
        self.nav_gb.liq = QLabel(self.nav_gb)
        self.nav_gb.liq.setGeometry(10, 40, 160, 40)
        self.nav_gb.liq.setFont(QFont('genius', 20))
        # positions table settings
        self.pos_view_gb = QGroupBox(self)
        self.pos_view_gb.setGeometry(10, 300, 900, 250)
        self.pos_view_gb.setTitle("Your Portfolio")
        self.pos_view_gb.setStyleSheet('background-color: black; color: white;')
        self.pos_view_gb.pos_view = QTableWidget(self.pos_view_gb)
        self.pos_view_gb.pos_view.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers)
        self.pos_view_gb.pos_view.setFont(self.font)
        self.pos_view_gb.pos_view.setRowCount(len(wallet.positions) - 1)
        self.pos_view_gb.pos_view.setColumnCount(8)
        self.pos_view_gb.pos_view.setGeometry(10, 20, 850, 200)
        self.pos_view_gb.pos_view.setStyleSheet('background-color: black;')
        self.pos_view_gb.pos_view.horizontalHeader().setStyleSheet(
            "::section{background-color: black; color: white}"
        )
        btn = self.pos_view_gb.pos_view.cornerWidget()
        headers = (
                    "Ticker", "Today's Performance", "Current Price", "P/L Per Share Today",
                    "Purchase Price", "# of Shares", "Total Value", "Position Gain/Loss"
                )
        for idx, header in enumerate(headers):
            self.pos_view_gb.pos_view.setHorizontalHeaderItem(idx, QTableWidgetItem(header))
            self.pos_view_gb.pos_view.horizontalHeaderItem(idx).setFont(self.font)
        for row in range(8):
            for column in range(self.pos_view_gb.pos_view.columnCount()):
                self.pos_view_gb.pos_view.setItem(row, column, QTableWidgetItem())

            self.pos_view_gb.pos_view.horizontalHeaderItem(row).setFont(self.font)


        self.update_wallet_table(wallet)
        # cash labels
        self.nav_gb.cashLabel = QLabel(self.nav_gb)
        self.nav_gb.cashLabel.setText("Cash: ")
        self.nav_gb.cashLabel.setGeometry(10, 90, 80, 20)
        self.nav_gb.cash = QLabel(self.nav_gb)
        self.nav_gb.cash.setGeometry(100, 90, 80, 20)
        # buying power labels
        self.nav_gb.bp_label = QLabel(self.nav_gb)
        self.nav_gb.bp_label.setText("Buying Power: ")
        self.nav_gb.bp_label.setGeometry(10, 110, 80, 20)
        self.nav_gb.bp = QLabel(self.nav_gb)
        self.nav_gb.bp.setGeometry(100, 110, 80, 20)
        # assets labels
        self.nav_gb.assetsLabel = QLabel(self.nav_gb)
        self.nav_gb.assetsLabel.setText("Long Assets: ")
        self.nav_gb.assetsLabel.setGeometry(10, 130, 80, 20)
        self.nav_gb.assets = QLabel(self.nav_gb)
        self.nav_gb.assets.setGeometry(100, 130, 80, 20)
        # liabilities labels
        self.nav_gb.liabilitiesLabel = QLabel(self.nav_gb)
        self.nav_gb.liabilitiesLabel.setText("Short Assets: ")
        self.nav_gb.liabilitiesLabel.setGeometry(10, 150, 80, 20)
        self.nav_gb.liabilities = QLabel(self.nav_gb)
        self.nav_gb.liabilities.setGeometry(100, 150, 80, 20)
        # return since inception labels
        self.nav_gb.returnSinceInceptionLabel = QLabel(self.nav_gb)
        self.nav_gb.returnSinceInceptionLabel.setText("Return Since Inception: ")
        self.nav_gb.returnSinceInceptionLabel.setGeometry(10, 170, 120, 20)
        self.nav_gb.returnSinceInception = QLabel(self.nav_gb)
        self.nav_gb.returnSinceInception.setFont(QFont('genius', 20))
        self.nav_gb.returnSinceInception.setGeometry(10, 190, 120, 30)
        self.pos_view_gb.pos_view.resizeColumnsToContents()
        self.update_wallet_nav(wallet)

    def update_wallet_table(self, wallet):
        """
        Updates the positions table on the crypto wallet dialog.
        """
        wallet_tickers = [position.ticker for position in wallet[1:]]
        wallet_costbases = [position.basis for position in wallet[1:]]
        wallet_amts = [position.amt for position in wallet[1:]]

        prices = yq.Ticker(wallet_tickers).price
        price_data = [
            (
                float(prices[ticker]['regularMarketPrice']),
                float(prices[ticker]['regularMarketOpen']),
                float(prices[ticker]['regularMarketPreviousClose'])
            ) for ticker in wallet_tickers
        ]
        wallet_zip = zip(price_data, wallet_costbases, wallet_amts)
        for idx, (data, basis, amt) in enumerate(wallet_zip):

            # get the current price and the price it last closed at
            current_price = data[0]
            last_close_price = data[2]

            # calculate the return since the position was opened in dollar and percent terms
            total_return = (current_price - basis) * amt
            percent_change = round(total_return / (basis * amt) * 100, 2)

            # update the table with the new information

            # first cell in the row is the coin symbol
            self.pos_view_gb.pos_view.item(idx, 0).setText(wallet_tickers[idx])

            # second cell is the coin's performance icon
            self.pos_view_gb.pos_view.item(idx, 1).setIcon(update_ticker_icon(data))

            # third cell is the coin's current price
            self.pos_view_gb.pos_view.item(idx, 2).setText(f'${current_price:0,.2f}')


            # fourth cell is the change in the coin's price from it's last close,
            # in dollar and percent terms
            last_close_change = current_price - last_close_price
            self.pos_view_gb.pos_view.item(idx, 3).setText(
                f'${last_close_change:0,.2f} ({round(last_close_change / last_close_price * 100, 2)}%)'
            )


            # fifth cell is the user's costbasis for the token
            self.pos_view_gb.pos_view.item(idx, 4).setText(f'${basis:0,.2f}')


            # sixth cell is the amount of the coin the user has (or is short)
            self.pos_view_gb.pos_view.item(idx, 5).setText(f"{amt}")


            # seventh cell is the NLV the user has in the coin
            self.pos_view_gb.pos_view.item(idx, 6).setText(
                f'${(current_price * amt):0,.2f}')


            # eighth cell is the user's net P/L on the position from when it was opened
            self.pos_view_gb.pos_view.item(idx, 7).setText(
                f'${total_return:0,.2f} ({percent_change}%)'
            )

    def update_wallet_nav(self, wallet):
        """Updates the user's NAV tab. Calculated as cash + (.5 * value of all long positions) -
        (1.5 * value of all short positions).
        """

        wallet_amts = [position.amt for position in wallet]

        # sets buying power to user's cash
        new_val = wallet_amts[0]
        liabilities = 0
        assets = 0
        for idx, amt in enumerate(wallet_amts[1:]):
            cur_val = atof(self.pos_view_gb.pos_view.item(idx, 2).text()[1:])
            if amt > 0:
                new_val += cur_val * amt
                assets += cur_val * amt
            elif amt < 0:
                new_val -= cur_val * amt
                liabilities += cur_val * amt

        buying_power = self.get_wallet_bp(wallet_amts)
        self.nav_gb.liq.setText(f'${new_val:0,.2f}')

        self.nav_gb.bp.setText(f'${buying_power:0,.2f}')

        self.nav_gb.cash.setText(f'${wallet_amts[0]:0,.2f}')

        self.nav_gb.assets.setText(f'${assets:0,.2f}')

        self.nav_gb.liabilities.setText(f'${liabilities:0,.2f}')

        self.nav_gb.returnSinceInception.setText(f'{((new_val / 10000 - 1) * 100):0,.2f}%')

    def get_wallet_bp(self, wallet_amts: list) -> float:
        """
        Returns the user's wallet buying power.
        Calculated as cash * 10
        """
        return wallet_amts[0] * 10