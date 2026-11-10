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
    entry_fee: float = 0.0
    exit_date: Optional[pd.Timestamp] = None
    exit_price: Optional[float] = None
    exit_fee: float = 0.0

    @property
    def pnl(self) -> Optional[float]:
        """Net P&L after slippage (already in the fill prices) and commissions."""
        if self.exit_price is None:
            return None
        gross = (self.exit_price - self.entry_price) * self.shares
        return gross - self.entry_fee - self.exit_fee


class Engine:
    """Runs a long/flat strategy on daily bars.

    The target position decided at day t's close is filled at day t+1's open,
    so a signal can never trade on the price that produced it.

    Costs are in basis points of traded notional. Slippage moves the fill
    price against us (buy higher, sell lower); commission is charged on top.
    """

    def __init__(
        self,
        strategy: Strategy,
        symbol: str,
        start: str,
        end: str,
        initial_capital: float = 100_000,
        allocation: float = 1.0,
        commission_bps: float = 1.0,
        slippage_bps: float = 5.0,
        data: Optional[pd.DataFrame] = None,
    ):
        if not 0 < allocation <= 1:
            raise ValueError("allocation must be in (0, 1]")
        if commission_bps < 0 or slippage_bps < 0:
            raise ValueError("costs cannot be negative")
        self.commission = commission_bps / 10_000
        self.slippage = slippage_bps / 10_000
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
                fill = bar.Open * (1 + self.slippage)
                qty = int(cash * self.allocation // (fill * (1 + self.commission)))
                if qty > 0:
                    fee = qty * fill * self.commission
                    cash -= qty * fill + fee
                    shares = qty
                    open_trade = Trade(date, fill, qty, entry_fee=fee)
            elif order == 0 and shares > 0:
                fill = bar.Open * (1 - self.slippage)
                fee = shares * fill * self.commission
                cash += shares * fill - fee
                open_trade.exit_date = date
                open_trade.exit_price = fill
                open_trade.exit_fee = fee
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
