import pandas as pd

from strategies.strategy import Strategy


class BuyAndHold(Strategy):
    """Always long. Used as the benchmark."""

    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        return pd.Series(1, index=data.index, name="target")
