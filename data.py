import pandas as pd
import yfinance as yf

COLUMNS = ["Open", "High", "Low", "Close", "Volume"]


class DataFetcher:
    """Loads daily OHLCV bars, split- and dividend-adjusted."""

    @staticmethod
    def fetch(symbol: str, start: str, end: str) -> pd.DataFrame:
        raw = yf.download(symbol, start=start, end=end, auto_adjust=True, progress=False)
        if raw.empty:
            raise ValueError(f"no data returned for {symbol} between {start} and {end}")
        if isinstance(raw.columns, pd.MultiIndex):
            # yfinance returns (field, ticker) columns even for one ticker
            raw.columns = raw.columns.get_level_values(0)
        return DataFetcher.clean(raw, symbol)

    @staticmethod
    def from_csv(path: str, symbol: str = "") -> pd.DataFrame:
        raw = pd.read_csv(path, index_col=0, parse_dates=True)
        return DataFetcher.clean(raw, symbol or path)

    @staticmethod
    def clean(raw: pd.DataFrame, symbol: str) -> pd.DataFrame:
        missing = [c for c in COLUMNS if c not in raw.columns]
        if missing:
            raise ValueError(f"{symbol}: missing columns {missing}")
        data = raw[COLUMNS].astype(float).sort_index()
        data = data[~data.index.duplicated(keep="first")]

        dropped = int(data[["Open", "Close"]].isna().any(axis=1).sum())
        if dropped:
            print(f"{symbol}: dropping {dropped} bars with missing prices")
        data = data.dropna(subset=["Open", "Close"])

        if (data[["Open", "High", "Low", "Close"]] <= 0).any().any():
            raise ValueError(f"{symbol}: non-positive prices in data")
        return data
