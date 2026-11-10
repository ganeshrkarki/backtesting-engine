import unittest

import numpy as np
import pandas as pd

from engine import Engine
from strategies.sma_strategy import SMAStrategy
from strategies.strategy import Strategy


def make_bars(closes, opens=None):
    idx = pd.bdate_range("2020-01-01", periods=len(closes))
    closes = np.asarray(closes, dtype=float)
    opens = closes if opens is None else np.asarray(opens, dtype=float)
    return pd.DataFrame({
        "Open": opens, "High": np.maximum(opens, closes), "Low": np.minimum(opens, closes),
        "Close": closes, "Volume": 1_000,
    }, index=idx)


class FixedTargets(Strategy):
    def __init__(self, targets):
        self.targets = targets

    def generate_signals(self, data):
        return pd.Series(self.targets, index=data.index)


def run(data, targets, **kwargs):
    kwargs.setdefault("commission_bps", 0)
    kwargs.setdefault("slippage_bps", 0)
    engine = Engine(FixedTargets(targets), "TEST", "", "", 10_000, data=data, **kwargs)
    return engine, engine.run()


class EngineTests(unittest.TestCase):
    def test_signal_fills_at_next_open(self):
        data = make_bars(closes=[10, 10, 10, 10], opens=[10, 11, 12, 13])
        engine, _ = run(data, [1, 0, 0, 0])
        trade = engine.trades[0]
        self.assertEqual(trade.entry_date, data.index[1])
        self.assertEqual(trade.entry_price, 11)
        self.assertEqual(trade.exit_date, data.index[2])
        self.assertEqual(trade.exit_price, 12)

    def test_position_is_held_while_target_stays_on(self):
        data = make_bars([10] * 6)
        engine, results = run(data, [1, 1, 1, 1, 0, 0])
        self.assertEqual(len(engine.trades), 1)
        self.assertEqual(results["shares"].tolist(), [0, 1000, 1000, 1000, 1000, 0])

    def test_equity_is_marked_to_market_daily(self):
        data = make_bars([10, 10, 12, 15])
        _, results = run(data, [1, 1, 1, 1])
        self.assertEqual(results["equity"].tolist(), [10_000, 10_000, 12_000, 15_000])

    def test_costs_reduce_pnl(self):
        data = make_bars([10, 10, 11, 11])
        free, _ = run(data, [1, 1, 0, 0])
        costly, _ = run(data, [1, 1, 0, 0], commission_bps=10, slippage_bps=10)
        self.assertLess(costly.trades[0].pnl, free.trades[0].pnl)
        self.assertGreater(costly.trades[0].entry_price, 10)
        self.assertLess(costly.trades[0].exit_price, 11)

    def test_open_position_is_reported_without_pnl(self):
        data = make_bars([10, 10, 10])
        engine, _ = run(data, [1, 1, 1])
        self.assertIsNone(engine.trades[-1].exit_date)
        self.assertIsNone(engine.trades[-1].pnl)


class SMAStrategyTests(unittest.TestCase):
    def test_no_lookahead(self):
        rng = np.random.default_rng(0)
        closes = 100 + rng.normal(0, 1, 300).cumsum()
        data = make_bars(closes)
        strategy = SMAStrategy(5, 20)
        full = strategy.generate_signals(data)

        changed = data.copy()
        changed.iloc[200:, changed.columns.get_loc("Close")] *= 3
        partial = strategy.generate_signals(changed)
        pd.testing.assert_series_equal(full.iloc[:200], partial.iloc[:200])

    def test_flat_during_warmup(self):
        data = make_bars(np.linspace(10, 20, 30))
        signals = SMAStrategy(5, 20).generate_signals(data)
        self.assertTrue((signals.iloc[:19] == 0).all())
        self.assertEqual(signals.iloc[-1], 1)

    def test_rejects_bad_windows(self):
        with self.assertRaises(ValueError):
            SMAStrategy(50, 20)


if __name__ == "__main__":
    unittest.main()
