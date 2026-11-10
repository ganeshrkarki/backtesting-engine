from dataclasses import dataclass
from typing import Optional

import pandas as pd

from data import DataFetcher
from strategies.strategy import Strategy


@dataclass
class Trade:
    entry_date: pd.Timestamp
    entry_price: float
    shares: int
    exit_date: Optional[pd.Timestamp] = None
    exit_price: Optional[float] = None

    @property
    def pnl(self) -> Optional[float]:
        if self.exit_price is None:
            return None
        return (self.exit_price - self.entry_price) * self.shares


class Engine:
    """Runs a long/flat strategy on daily bars.

    The target position decided at day t's close is filled at day t+1's open,
    so a signal can never trade on the price that produced it.
    """

    def __init__(
        self,
        strategy: Strategy,
        symbol: str,
        start: str,
        end: str,
        initial_capital: float = 100_000,
        allocation: float = 1.0,
        data: Optional[pd.DataFrame] = None,
    ):
        if not 0 < allocation <= 1:
            raise ValueError("allocation must be in (0, 1]")
        self.strategy = strategy
        self.symbol = symbol
        self.start = start
        self.end = end
        self.initial_capital = initial_capital
        self.allocation = allocation
        self.data = data
        self.trades: list[Trade] = []

    def run(self) -> pd.DataFrame:
        if self.data is None:
            self.data = DataFetcher.fetch(self.symbol, self.start, self.end)
        data = self.data

        target = self.strategy.generate_signals(data).reindex(data.index).fillna(0)
        orders = target.shift(1).fillna(0).astype(int)

        cash = float(self.initial_capital)
        shares = 0
        open_trade: Optional[Trade] = None
        self.trades = []
        rows = []

        for date, bar, order in zip(data.index, data.itertuples(), orders):
            if order == 1 and shares == 0:
                qty = int(cash * self.allocation // bar.Open)
                if qty > 0:
                    cash -= qty * bar.Open
                    shares = qty
                    open_trade = Trade(date, bar.Open, qty)
            elif order == 0 and shares > 0:
                cash += shares * bar.Open
                open_trade.exit_date = date
                open_trade.exit_price = bar.Open
                self.trades.append(open_trade)
                open_trade = None
                shares = 0

            rows.append({
                "Date": date,
                "Close": bar.Close,
                "target": target.loc[date],
                "shares": shares,
                "cash": cash,
                "equity": cash + shares * bar.Close,
            })

        if open_trade is not None:
            self.trades.append(open_trade)

        results = pd.DataFrame(rows).set_index("Date")
        results["returns"] = results["equity"].pct_change().fillna(0.0)
        return results
