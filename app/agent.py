"""A small agentic pipeline for SIMULATED, backtest-only market analysis.

IMPORTANT: This module performs no real trading and places no real orders.
It only computes statistics over synthetic, locally-generated price data
and returns a structured, natural-language-style report. It must never be
connected to a live brokerage, exchange, or real market-data feed.

The "agent" here is a small chain of tool-like steps (a common pattern in
agentic AI applications): each step takes the previous step's structured
output and decides what to do next, similar in spirit to a LangGraph-style
node pipeline, but implemented with plain functions to keep the demo
dependency-light and fully offline.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from app.data import generate_synthetic_series, series_to_closes
from app.indicators import daily_returns, max_drawdown, sma


@dataclass
class BacktestResult:
    symbol: str
    days: int
    total_return_pct: float
    max_drawdown_pct: float
    win_rate_pct: float
    num_signals: int
    final_signal: str
    trace: list[str] = field(default_factory=list)


def step_fetch_data(symbol: str, days: int, seed: int | None = None) -> list[float]:
    bars = generate_synthetic_series(symbol=symbol, days=days, seed=seed)
    return series_to_closes(bars)


def step_compute_signals(closes: list[float], fast: int = 10, slow: int = 30) -> list[str]:
    """SMA crossover signal: 'buy' when fast SMA crosses above slow SMA,
    'sell' when it crosses below, else 'hold'. Signals only -- no orders
    are ever placed."""
    fast_sma = sma(closes, fast)
    slow_sma = sma(closes, slow)
    signals: list[str] = []
    prev_state: str | None = None
    for f, s in zip(fast_sma, slow_sma):
        if f is None or s is None:
            signals.append("hold")
            continue
        state = "above" if f >= s else "below"
        if prev_state is None:
            signals.append("hold")
        elif state == "above" and prev_state == "below":
            signals.append("buy")
        elif state == "below" and prev_state == "above":
            signals.append("sell")
        else:
            signals.append("hold")
        prev_state = state
    return signals


def step_backtest(closes: list[float], signals: list[str]) -> dict:
    """Very simple long-only backtest: hold 1 unit while in a 'buy' state,
    flat otherwise. Purely arithmetic over synthetic data -- no execution
    of any kind against a real market."""
    position = 0
    entry_price = 0.0
    trade_returns: list[float] = []

    for price, signal in zip(closes, signals):
        if signal == "buy" and position == 0:
            position = 1
            entry_price = price
        elif signal == "sell" and position == 1:
            trade_returns.append((price - entry_price) / entry_price)
            position = 0

    if position == 1:
        trade_returns.append((closes[-1] - entry_price) / entry_price)

    wins = [r for r in trade_returns if r > 0]
    win_rate = (len(wins) / len(trade_returns) * 100) if trade_returns else 0.0
    total_return = 1.0
    for r in trade_returns:
        total_return *= 1 + r
    total_return_pct = round((total_return - 1) * 100, 2)

    return {
        "num_signals": sum(1 for s in signals if s in ("buy", "sell")),
        "num_trades": len(trade_returns),
        "win_rate_pct": round(win_rate, 2),
        "total_return_pct": total_return_pct,
    }


def step_summarize(symbol: str, days: int, closes: list[float], signals: list[str], backtest: dict) -> BacktestResult:
    dd = max_drawdown(closes)
    final_signal = signals[-1] if signals else "hold"
    trace = [
        f"Fetched {days} days of SYNTHETIC price data for '{symbol}'.",
        f"Computed SMA(10)/SMA(30) crossover signals ({backtest['num_signals']} signal events).",
        f"Ran a long-only backtest: {backtest['num_trades']} trades, "
        f"{backtest['win_rate_pct']}% win rate, {backtest['total_return_pct']}% total return.",
        f"Max drawdown over the period: {round(dd * 100, 2)}%.",
        "This is a simulation over synthetic data only -- not investment advice, "
        "and no real orders were placed.",
    ]
    return BacktestResult(
        symbol=symbol,
        days=days,
        total_return_pct=backtest["total_return_pct"],
        max_drawdown_pct=round(dd * 100, 2),
        win_rate_pct=backtest["win_rate_pct"],
        num_signals=backtest["num_signals"],
        final_signal=final_signal,
        trace=trace,
    )


def run_market_analysis_agent(symbol: str = "SIM", days: int = 180, seed: int | None = None) -> BacktestResult:
    """Runs the full simulated pipeline: fetch -> signal -> backtest -> summarize."""
    closes = step_fetch_data(symbol, days, seed=seed)
    signals = step_compute_signals(closes)
    backtest = step_backtest(closes, signals)
    return step_summarize(symbol, days, closes, signals, backtest)
