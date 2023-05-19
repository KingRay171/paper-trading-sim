from datetime import datetime, timedelta
import yahooquery as yq

class WalletPosition():
    def __init__(self, ticker: str, basis: float, amt: int):
        self.ticker: str = ticker
        self.basis: float = basis
        self.amt: int = amt



class Wallet():
    def __init__(self, tickers: list, bases: list, amts: list):
        self.positions: list[WalletPosition] = [
            WalletPosition(pos[0], pos[1], pos[2]) for pos in zip(tickers, bases, amts)
        ]

    def __iter__(self) -> WalletPosition:
        for position in self.positions:
            yield position

    def __getitem__(self, item) -> WalletPosition:
        return self.positions[item]

    def get_index_by_ticker(self, ticker):
        for position in self.positions:
            if position.ticker == ticker:
                return self.positions.index(position)
        return -1
