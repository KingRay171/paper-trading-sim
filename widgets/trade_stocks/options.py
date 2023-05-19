from PySide6.QtWidgets import QTabWidget, QTableWidgetItem, QTableWidget
from PySide6.QtCore import Qt
from widgets.trade_stocks.option_trade_window import OptionTradeWindow
import yahooquery as yq
from datetime import datetime
from dependencies import optionchain as oc
from dependencies import greekscalc as gc

class OptionsDialog(QTabWidget):
    def __init__(self, string_list, port):
        super().__init__()
        self.window = None
        self.port = port

    def init_option_trade(self, wi: QTableWidgetItem, parent, stock, orders):
        self.window = OptionTradeWindow(parent, stock, wi, self.port, orders)

    def update(self, stock: str):
        ticker = yq.Ticker(stock)
        new_option_chain = oc.split_option_chain(ticker.option_chain)
        current_chain = self.currentWidget()
        index = self.indexOf(current_chain)
        date = self.tabText(index)
        table: QTableWidget = current_chain.currentWidget().children()[0].children()[0]
        calls_puts = current_chain.tabText(current_chain.indexOf(current_chain.currentWidget()))
        r = yq.Ticker('^FVX').price['^FVX']['regularMarketPrice'] / 100
        s = ticker.price[stock]['regularMarketPrice']
        t = (datetime.strptime(f"{date} 16:00:00", "%Y-%m-%d %H:%M:%S") - datetime.now()).total_seconds() / 31536000
        for chain in new_option_chain:
            if f"{chain.index[0][1]}"[:10] == date:
                chain_tuple_idx = 0 if calls_puts == 'Calls' else 1
                chain = oc.split_calls_puts(chain)[chain_tuple_idx]
                if table.item(0, 0) is None:
                    table.setRowCount(len(chain.index))
                    for i in range(table.rowCount()):
                        chain_row = chain.iloc[i]
                        greeks = gc.get_call_greeks(
                            s, chain_row.at['strike'], chain_row.at['impliedVolatility'],
                            t, r, "Call" if chain_tuple_idx == 0 else "Put"
                        )
                        table_values = [
                            chain_row.at['strike'], "ITM" if chain_row.at['inTheMoney'] else "OTM", chain_row.at['bid'],
                            chain_row.at['ask'], chain_row.at['lastPrice'], f"{chain_row.at['change']:0,.2f}",
                            round(chain_row.at['percentChange'], 2), chain_row.at['volume'],
                            round(100 * chain_row.at['impliedVolatility'], 2), f"{chain_row.at['openInterest']}"[:-2]
                        ]
                        table_values.extend(greeks)
                        table_values.append(chain.iat[i, 0])
                        for idx, value in enumerate(table_values):
                            table.setItem(i, idx, QTableWidgetItem(f"{value}"))
                            table.item(i, idx).setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    table.resizeColumnsToContents()
                else:
                    for i in range(table.rowCount()):
                        chain_row = chain.iloc[i]
                        greeks = gc.get_call_greeks(
                            s, chain_row.at['strike'], chain_row.at['impliedVolatility'],
                            t, r, "Call" if chain_tuple_idx == 0 else "Put"
                        )
                        table_values = [
                            chain_row.at['strike'], "ITM" if chain_row.at['inTheMoney'] else "OTM", chain_row.at['bid'],
                            chain_row.at['ask'], chain_row.at['lastPrice'], f"{chain_row.at['change']:0,.2f}",
                            round(chain_row.at['percentChange'], 2), chain_row.at['volume'],
                            round(100 * chain_row.at['impliedVolatility'], 2), f"{chain_row.at['openInterest']}"[:-2]
                        ]
                        table_values.extend(greeks)
                        table_values.append(chain.iat[i, 0])
                        for idx, value in enumerate(table_values):
                            table.item(i, idx).setText(f"{value}")
