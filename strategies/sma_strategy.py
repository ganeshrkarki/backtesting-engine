from strategies.strategy import Strategy
import pandas as pd

class SMAStrategy(Strategy):
    """Simple Moving Average Crossover Strategy."""
    def generate_signals(self, data: pd.DataFrame):
        data = data.copy()
        data['SMA50'] = data['Close'].rolling(window=50).mean()
        data['SMA200'] = data['Close'].rolling(window=200).mean()
        data['Signal'] = 0
        crossover = (
            (data['SMA50'] > data['SMA200']) &
            (data['SMA50'].shift(1) <= data['SMA200'].shift(1))
        )
        data.loc[crossover, 'Signal'] = 1
        data['Position'] = data['Signal'].diff().fillna(0)
        return data
