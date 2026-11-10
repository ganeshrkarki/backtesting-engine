import matplotlib.pyplot as plt
import pandas as pd

def plot_signals(data: pd.DataFrame, title: str = "SMA Strategy Backtest"):
    plt.figure(figsize=(14, 7))
    plt.plot(data.index, data['Close'], label='Close Price', color='blue')
    plt.plot(data.index, data['SMA50'], label='SMA 50', color='orange', alpha=0.7)
    plt.plot(data.index, data['SMA200'], label='SMA 200', color='magenta', alpha=0.7)
    # Buy signals
    buy_signals = data[data['Position'] == 1]
    plt.scatter(buy_signals.index, buy_signals['Close'], marker='^', color='green', label='Buy', s=100)
    # Sell signals
    sell_signals = data[data['Position'] == -1]
    plt.scatter(sell_signals.index, sell_signals['Close'], marker='v', color='red', label='Sell', s=100)
    plt.title(title)
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.grid(True)
    plt.show()
