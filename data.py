import yfinance as yf
import pandas as pd

class DataFetcher:
    """Fetches historical stock data using yfinance."""
    @staticmethod
    def fetch(symbol: str, start: str, end: str) -> pd.DataFrame:
        data = yf.download(symbol, start=start, end=end)
        return data
