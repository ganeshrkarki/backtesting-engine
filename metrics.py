import numpy as np
import pandas as pd

TRADING_DAYS = 252


def total_return(equity: pd.Series) -> float:
    return float(equity.iloc[-1] / equity.iloc[0] - 1)


def cagr(equity: pd.Series) -> float:
    years = (equity.index[-1] - equity.index[0]).days / 365.25
    if years <= 0:
        return 0.0
    return float((equity.iloc[-1] / equity.iloc[0]) ** (1 / years) - 1)


def annual_volatility(returns: pd.Series) -> float:
    return float(returns.std() * np.sqrt(TRADING_DAYS))


def sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.0) -> float:
    """Annualized Sharpe from daily returns. risk_free_rate is annual."""
    excess = returns - risk_free_rate / TRADING_DAYS
    std = excess.std()
    if std == 0 or np.isnan(std):
        return 0.0
    return float(excess.mean() / std * np.sqrt(TRADING_DAYS))


def sortino_ratio(returns: pd.Series, risk_free_rate: float = 0.0) -> float:
    excess = returns - risk_free_rate / TRADING_DAYS
    downside = np.sqrt((np.minimum(excess, 0) ** 2).mean())
    if downside == 0 or np.isnan(downside):
        return 0.0
    return float(excess.mean() / downside * np.sqrt(TRADING_DAYS))


def drawdown(equity: pd.Series) -> pd.Series:
    return equity / equity.cummax() - 1


def max_drawdown(equity: pd.Series) -> float:
    return float(drawdown(equity).min())


def hit_rate(trades) -> float:
    closed = [t.pnl for t in trades if t.pnl is not None]
    if not closed:
        return float("nan")
    return sum(p > 0 for p in closed) / len(closed)


def exposure(shares: pd.Series) -> float:
    """Fraction of days with an open position."""
    return float((shares > 0).mean())


def summarize(results: pd.DataFrame, trades, risk_free_rate: float = 0.0) -> dict:
    equity, returns = results["equity"], results["returns"]
    closed = [t for t in trades if t.pnl is not None]
    return {
        "Total return": total_return(equity),
        "CAGR": cagr(equity),
        "Volatility": annual_volatility(returns),
        "Sharpe": sharpe_ratio(returns, risk_free_rate),
        "Sortino": sortino_ratio(returns, risk_free_rate),
        "Max drawdown": max_drawdown(equity),
        "Hit rate": hit_rate(trades),
        "Closed trades": len(closed),
        "Exposure": exposure(results["shares"]),
    }
