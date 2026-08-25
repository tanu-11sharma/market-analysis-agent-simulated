"""FastAPI app exposing the SIMULATED market analysis agent.

DISCLAIMER: This service is a demo/simulation only. It uses synthetic,
locally-generated price data, performs no real trading, and must never be
treated as financial advice or connected to a live brokerage or exchange.
"""
from __future__ import annotations

from dataclasses import asdict

from fastapi import FastAPI, Query
from pydantic import BaseModel

from app.agent import run_market_analysis_agent

app = FastAPI(
    title="Market Analysis Agent (Simulated)",
    description=(
        "Backtest-only market analysis agent over synthetic sample data. "
        "This is a demo/simulation, NOT financial advice, and never executes "
        "real trades."
    ),
    version="0.1.0",
)


class AnalysisResponse(BaseModel):
    symbol: str
    days: int
    total_return_pct: float
    max_drawdown_pct: float
    win_rate_pct: float
    num_signals: int
    final_signal: str
    trace: list[str]
    disclaimer: str = (
        "Simulation only. Synthetic data. Not financial advice. "
        "No real trades were executed."
    )


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/analyze", response_model=AnalysisResponse)
def analyze(
    symbol: str = Query("SIM", description="Synthetic ticker symbol, any string"),
    days: int = Query(180, ge=30, le=2000, description="Number of synthetic trading days to simulate"),
    seed: int | None = Query(None, description="Optional RNG seed for reproducibility"),
) -> AnalysisResponse:
    result = run_market_analysis_agent(symbol=symbol, days=days, seed=seed)
    return AnalysisResponse(**asdict(result))
