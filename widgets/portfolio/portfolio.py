
from datetime import datetime, timedelta
import yahooquery as yq
class PortfolioPosition():
    def __init__(self, ticker: str, basis: float, amt: int, asset_type: str):
        self.ticker: str = ticker
        self.basis: float = basis
        self.amt: int = amt
        self.asset_type: str = asset_type



class Portfolio():
    def __init__(self, tickers: list, bases: list, amts: list, types: list):
        self.positions: list[PortfolioPosition] = [
            PortfolioPosition(pos[0], pos[1], pos[2], pos[3]) for pos in zip(tickers, bases, amts, types)
        ]

    def __iter__(self) -> PortfolioPosition:
        for position in self.positions:
            yield position

    def __getitem__(self, item) -> PortfolioPosition:
        return self.positions[item]

    def _option_has_expired(self, option: PortfolioPosition):
        exp = yq.Ticker(option.ticker).summary_detail[option.ticker]['expireDate']
        exp_date = datetime.strptime(exp, "%Y-%m-%d %H:%M:%S") + timedelta(hours=20)
        cur_date = datetime.now()
        return exp_date > cur_date

    def update_options(self):
        expired_options = list(filter(self._option_has_expired, list(filter(lambda e: e.asset_type == "Option", self))))
        for exp_option in expired_options:
            self.positions.remove(exp_option)
