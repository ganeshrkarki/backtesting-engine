import pandas as pd


class Strategy:
    """Base class for trading strategies.

    A strategy returns a target position for every bar: 1 to hold the asset,
    0 to stay in cash. The value for day t may only use data up to and
    including day t's close. The engine executes it on the next bar.
    """

    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        raise NotImplementedError
