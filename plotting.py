import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from metrics import drawdown


def plot_results(
    results: pd.DataFrame,
    trades,
    indicators: pd.DataFrame,
    benchmark: pd.DataFrame,
    title: str,
    path: str,
) -> None:
    fig, (ax_price, ax_eq, ax_dd) = plt.subplots(
        3, 1, figsize=(12, 9), sharex=True, gridspec_kw={"height_ratios": [3, 2, 1]}
    )

    ax_price.plot(results.index, results["Close"], color="black", lw=1, label="Close")
    for col in indicators.columns:
        ax_price.plot(indicators.index, indicators[col], lw=1, label=col)
    exits = [t for t in trades if t.exit_date is not None]
    ax_price.scatter([t.entry_date for t in trades], [t.entry_price for t in trades],
                     marker="^", color="green", s=60, zorder=3, label="Buy")
    ax_price.scatter([t.exit_date for t in exits], [t.exit_price for t in exits],
                     marker="v", color="red", s=60, zorder=3, label="Sell")
    ax_price.set_title(title)
    ax_price.set_ylabel("Price")
    ax_price.legend(loc="upper left")

    ax_eq.plot(results.index, results["equity"], label="Strategy")
    ax_eq.plot(benchmark.index, benchmark["equity"], label="Buy & hold", alpha=0.7)
    ax_eq.set_ylabel("Equity")
    ax_eq.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"${v / 1000:,.0f}k"))
    ax_eq.legend(loc="upper left")

    ax_dd.fill_between(results.index, drawdown(results["equity"]), 0, color="tab:red", alpha=0.4)
    ax_dd.set_ylabel("Drawdown")
    ax_dd.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0%}"))

    for ax in (ax_price, ax_eq, ax_dd):
        ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)
