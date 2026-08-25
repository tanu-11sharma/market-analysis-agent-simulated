"""Synthetic market data generator.

All data in this module is SYNTHETIC (deterministically seeded random walk).
No real market data provider is called. This project is a simulation only.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass


@dataclass
class Bar:
    day: int
    close: float


def generate_synthetic_series(
    symbol: str = "SIM",
    days: int = 180,
    start_price: float = 100.0,
    seed: int | None = None,
) -> list[Bar]:
    """Generate a deterministic synthetic daily close-price series.

    Uses a seeded random walk with mild drift so results are reproducible
    for the same (symbol, days, start_price, seed) combination. This is
    NOT real market data and must never be treated as such.
    """
    if seed is None:
        # Deterministic per-symbol seed so repeated calls for the same
        # symbol always return the same synthetic history.
        seed = sum(ord(c) for c in symbol) * 1000 + days

    rng = random.Random(seed)
    price = start_price
    bars: list[Bar] = []
    drift = 0.0002
    vol = 0.012

    for day in range(days):
        shock = rng.gauss(0, 1)
        pct_change = drift + vol * shock
        price = max(0.01, price * (1 + pct_change))
        bars.append(Bar(day=day, close=round(price, 4)))

    return bars


def series_to_closes(bars: list[Bar]) -> list[float]:
    return [b.close for b in bars]
