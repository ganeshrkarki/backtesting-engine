import argparse

from engine import Engine
from metrics import summarize
from plotting import plot_results
from strategies.buy_and_hold import BuyAndHold
from strategies.sma_strategy import SMAStrategy

PERCENT_ROWS = {"Total return", "CAGR", "Volatility", "Max drawdown", "Hit rate", "Exposure"}


def fmt(name, value):
    if value != value:  # NaN, e.g. hit rate with no closed trades
        return "n/a"
    if name in PERCENT_ROWS:
        return f"{value:.1%}"
    if isinstance(value, int):
        return str(value)
    return f"{value:.2f}"


def parse_args():
    p = argparse.ArgumentParser(description="Backtest an SMA crossover against buy and hold.")
    p.add_argument("--symbol", default="AAPL")
    p.add_argument("--start", default="2015-01-01")
    p.add_argument("--end", default="2025-01-01")
    p.add_argument("--fast", type=int, default=50)
    p.add_argument("--slow", type=int, default=200)
    p.add_argument("--capital", type=float, default=100_000)
    p.add_argument("--commission-bps", type=float, default=1.0)
    p.add_argument("--slippage-bps", type=float, default=5.0)
    p.add_argument("--risk-free", type=float, default=0.0, help="annual rate for Sharpe/Sortino")
    p.add_argument("--plot", default=None, help="save a chart to this path")
    return p.parse_args()


def main():
    args = parse_args()
    costs = dict(commission_bps=args.commission_bps, slippage_bps=args.slippage_bps)

    strategy = SMAStrategy(args.fast, args.slow)
    engine = Engine(strategy, args.symbol, args.start, args.end, args.capital, **costs)
    results = engine.run()

    benchmark = Engine(BuyAndHold(), args.symbol, args.start, args.end, args.capital,
                       data=engine.data, **costs)
    bench_results = benchmark.run()

    strat_stats = summarize(results, engine.trades, args.risk_free)
    bench_stats = summarize(bench_results, benchmark.trades, args.risk_free)

    label = f"SMA {args.fast}/{args.slow}"
    print(f"{args.symbol} {args.start} to {args.end}, "
          f"costs {args.commission_bps:g} bps commission + {args.slippage_bps:g} bps slippage")
    print(f"{'':<15}{label:>12}{'Buy & hold':>12}")
    for name in strat_stats:
        print(f"{name:<15}{fmt(name, strat_stats[name]):>12}{fmt(name, bench_stats[name]):>12}")

    print("\nTrades:")
    for t in engine.trades:
        exit_info = f"{t.exit_date.date()} @ {t.exit_price:.2f}" if t.exit_date is not None else "still open"
        pnl = f"{t.pnl:+,.0f}" if t.pnl is not None else ""
        print(f"  {t.entry_date.date()} @ {t.entry_price:.2f} -> {exit_info}  {pnl}")

    if args.plot:
        plot_results(results, engine.trades, strategy.indicators(engine.data), bench_results,
                     f"{args.symbol} {label} crossover", args.plot)
        print(f"\nChart saved to {args.plot}")


if __name__ == "__main__":
    main()
