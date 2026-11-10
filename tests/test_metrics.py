import unittest

import pandas as pd

import metrics
from engine import Trade


def series(values, start="2020-01-01"):
    return pd.Series(values, index=pd.bdate_range(start, periods=len(values)), dtype=float)


class MetricsTests(unittest.TestCase):
    def test_max_drawdown(self):
        equity = series([100, 120, 90, 130, 117])
        self.assertAlmostEqual(metrics.max_drawdown(equity), -0.25)

    def test_cagr_doubling_over_one_year(self):
        idx = pd.to_datetime(["2020-01-01", "2020-12-31"])
        equity = pd.Series([100.0, 200.0], index=idx)
        self.assertAlmostEqual(metrics.cagr(equity), 1.0, places=2)

    def test_sharpe_is_zero_without_volatility(self):
        self.assertEqual(metrics.sharpe_ratio(series([0.0] * 10)), 0.0)

    def test_sharpe_sign_follows_mean_return(self):
        self.assertGreater(metrics.sharpe_ratio(series([0.01, -0.005] * 50)), 0)
        self.assertLess(metrics.sharpe_ratio(series([-0.01, 0.005] * 50)), 0)

    def test_hit_rate_ignores_open_trades(self):
        day = pd.Timestamp("2020-01-01")
        trades = [
            Trade(day, 10, 1, exit_date=day, exit_price=12),
            Trade(day, 10, 1, exit_date=day, exit_price=9),
            Trade(day, 10, 1, exit_date=day, exit_price=11),
            Trade(day, 10, 1),
        ]
        self.assertAlmostEqual(metrics.hit_rate(trades), 2 / 3)


if __name__ == "__main__":
    unittest.main()
