from engine import Engine
from strategies.sma_strategy import SMAStrategy

if __name__ == "__main__":
    symbol = "AAPL"
    start = "2015-01-01"
    end = "2025-01-01"
    initial_capital = 100_000

    strategy = SMAStrategy(fast=50, slow=200)
    engine = Engine(strategy, symbol, start, end, initial_capital)
    results = engine.run()

    print(f"Final equity: ${results['equity'].iloc[-1]:,.2f}")
    print("Trades:")
    for t in engine.trades:
        exit_info = f"{t.exit_date.date()} @ {t.exit_price:.2f}" if t.exit_date is not None else "open"
        print(f"  {t.entry_date.date()} @ {t.entry_price:.2f} -> {exit_info}  shares={t.shares}")
