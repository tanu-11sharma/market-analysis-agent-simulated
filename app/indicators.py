"""Technical indicator helpers used by the (simulated) market analysis agent."""
from __future__ import annotations


def sma(values: list[float], window: int) -> list[float | None]:
    """Simple moving average. Returns None for indices before the window fills."""
    out: list[float | None] = []
    running_sum = 0.0
    for i, v in enumerate(values):
        running_sum += v
        if i >= window:
            running_sum -= values[i - window]
        if i >= window - 1:
            out.append(round(running_sum / window, 4))
        else:
            out.append(None)
    return out


def daily_returns(values: list[float]) -> list[float]:
    returns = []
    for prev, cur in zip(values, values[1:]):
        if prev == 0:
            returns.append(0.0)
        else:
            returns.append((cur - prev) / prev)
    return returns


def max_drawdown(values: list[float]) -> float:
    peak = values[0] if values else 0.0
    max_dd = 0.0
    for v in values:
        peak = max(peak, v)
        if peak > 0:
            dd = (v - peak) / peak
            max_dd = min(max_dd, dd)
    return round(max_dd, 4)
