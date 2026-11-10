from data import DataFetcher
from strategies.strategy import Strategy
import pandas as pd

class Engine:
    """Runs a strategy against historical data."""
    def __init__(self, strategy: Strategy, symbol: str, start: str, end: str, initial_capital: float = 100000):
        self.strategy = strategy
        self.symbol = symbol
        self.start = start
        self.end = end
        self.data = None
        self.signals = None
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.position = 0
        self.portfolio_value = initial_capital
        self.trades = []

    def run(self):
        self.data = DataFetcher.fetch(self.symbol, self.start, self.end)
        self.signals = self.strategy.generate_signals(self.data)
        df = self.signals.copy()
        for idx, row in df.iterrows():
            price = row['Close']
            # Ensure price is a scalar (float)
            if hasattr(price, 'item'):
                try:
                    price = price.item()
                except Exception:
                    price = 0.0
            if pd.isna(price):
                price = 0.0
            position_signal = row['Position']
            if hasattr(position_signal, 'item'):
                try:
                    position_signal = position_signal.item()
                except Exception:
                    position_signal = 0
            if pd.isna(position_signal):
                position_signal = 0
            if position_signal == 1:  # Buy signal
                risk_per_trade = 0.02 * self.portfolio_value
                shares = int(risk_per_trade // price) if price > 0 else 0
                if shares > 0 and self.cash >= shares * price:
                    self.cash -= shares * price
                    self.position += shares
                    self.trades.append({'type': 'buy', 'date': idx, 'price': price, 'shares': shares})
            elif position_signal == -1 and self.position > 0:  # Sell signal
                self.cash += self.position * price
                self.trades.append({'type': 'sell', 'date': idx, 'price': price, 'shares': self.position})
                self.position = 0
            self.portfolio_value = self.cash + self.position * price
        df['PortfolioValue'] = self.portfolio_value
        return df
