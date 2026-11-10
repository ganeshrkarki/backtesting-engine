from engine import Engine
from strategies.sma_strategy import SMAStrategy
from plotting import plot_signals

if __name__ == "__main__":
    symbol = "AAPL"
    start = "2020-01-01"
    end = "2023-01-01"
    initial_capital = 100000

    strategy = SMAStrategy()
    engine = Engine(strategy, symbol, start, end, initial_capital)
    results = engine.run()

    print("Trades executed:")
    for trade in engine.trades:
        print(trade)

    plot_signals(results, title=f"{symbol} SMA Strategy Backtest")
