import pandas as pd

from strategies.strategy import Strategy


class SMAStrategy(Strategy):
    """Long while the fast moving average is above the slow one, flat otherwise."""

    def __init__(self, fast: int = 50, slow: int = 200):
        if fast >= slow:
            raise ValueError("fast window must be shorter than slow window")
        self.fast = fast
        self.slow = slow

    def indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        return pd.DataFrame({
            f"SMA{self.fast}": data["Close"].rolling(self.fast).mean(),
            f"SMA{self.slow}": data["Close"].rolling(self.slow).mean(),
        })

    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        ind = self.indicators(data)
        fast, slow = ind.iloc[:, 0], ind.iloc[:, 1]
        # Comparisons against NaN are False, so the warm-up period stays flat.
        return (fast > slow).astype(int).rename("target")
