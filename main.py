from engine import Engine
from metrics import summarize
from strategies.buy_and_hold import BuyAndHold
from strategies.sma_strategy import SMAStrategy

PERCENT_ROWS = {"Total return", "CAGR", "Volatility", "Max drawdown", "Hit rate", "Exposure"}


def fmt(name, value):
    if name in PERCENT_ROWS:
        return f"{value:.1%}"
    if isinstance(value, int):
        return str(value)
    return f"{value:.2f}"


if __name__ == "__main__":
    symbol = "AAPL"
    start = "2015-01-01"
    end = "2025-01-01"
    initial_capital = 100_000

    engine = Engine(SMAStrategy(50, 200), symbol, start, end, initial_capital)
    results = engine.run()

    benchmark = Engine(BuyAndHold(), symbol, start, end, initial_capital, data=engine.data)
    bench_results = benchmark.run()

    strat_stats = summarize(results, engine.trades)
    bench_stats = summarize(bench_results, benchmark.trades)

    print(f"{symbol} {start} to {end}")
    print(f"{'':<15}{'SMA 50/200':>12}{'Buy & hold':>12}")
    for name in strat_stats:
        print(f"{name:<15}{fmt(name, strat_stats[name]):>12}{fmt(name, bench_stats[name]):>12}")

    print("\nTrades:")
    for t in engine.trades:
        exit_info = f"{t.exit_date.date()} @ {t.exit_price:.2f}" if t.exit_date is not None else "open"
        pnl = f"{t.pnl:+,.0f}" if t.pnl is not None else ""
        print(f"  {t.entry_date.date()} @ {t.entry_price:.2f} -> {exit_info}  {pnl}")
