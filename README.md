# market-analysis-agent-simulated

A small **agentic** market-analysis pipeline that fetches synthetic price
data, computes a moving-average crossover signal, runs a backtest, and
produces a plain-language summary report — all in a chain of tool-like
steps (fetch → signal → backtest → summarize), the same pattern used by
larger multi-step agentic AI systems.

> **This is a simulation/demo only.** All price data is synthetically
> generated (a seeded random walk) inside this repo. The agent never
> connects to a real market-data feed, brokerage, or exchange, and it
> never places real trades. Nothing here is financial advice.

## Why this project

"Agentic AI" usually means chaining several reasoning/tool-call steps
together, where each step's structured output feeds the next step's
decision. This project demonstrates that pattern in a minimal, dependency
-light way that still runs and tests completely offline: no API keys, no
external services, fully reproducible given a seed.

## What it does

1. **Fetch** — generates a deterministic synthetic daily close-price series for a symbol.
2. **Signal** — computes SMA(10)/SMA(30) crossover buy/sell/hold signals.
3. **Backtest** — simulates a simple long-only strategy following those signals.
4. **Summarize** — returns a structured result plus a short natural-language trace of what the agent did at each step.

Exposed both as a small FastAPI service and as a plain Python function you
can call directly.

## Project structure

```
app/
  data.py        # synthetic price series generator
  indicators.py   # SMA, returns, drawdown helpers
  agent.py        # the 4-step agent pipeline
  main.py         # FastAPI app (/analyze, /health)
tests/
  test_agent.py   # unit + end-to-end tests
```

## Setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
uvicorn app.main:app --reload
```

Then:

```bash
curl "http://127.0.0.1:8000/analyze?symbol=SIM&days=180&seed=7"
```

Example response:

```json
{
  "symbol": "SIM",
  "days": 180,
  "total_return_pct": 4.12,
  "max_drawdown_pct": -14.13,
  "win_rate_pct": 33.33,
  "num_signals": 6,
  "final_signal": "hold",
  "trace": [
    "Fetched 180 days of SYNTHETIC price data for 'SIM'.",
    "Computed SMA(10)/SMA(30) crossover signals (6 signal events).",
    "Ran a long-only backtest: 3 trades, 33.33% win rate, 4.12% total return.",
    "Max drawdown over the period: -14.13%.",
    "This is a simulation over synthetic data only -- not investment advice, and no real orders were placed."
  ],
  "disclaimer": "Simulation only. Synthetic data. Not financial advice. No real trades were executed."
}
```

Or call the pipeline directly in Python:

```python
from app.agent import run_market_analysis_agent
result = run_market_analysis_agent(symbol="SIM", days=180, seed=7)
print(result.trace)
```

## Test

```bash
pip install -r requirements.txt
pytest -q
```

8 tests cover determinism of the synthetic data generator, the indicator
math, signal generation, the backtest, and a full end-to-end run of the
pipeline.

## Disclaimer

This is a portfolio/demo project. It uses synthetic sample data only, is
not connected to any real market-data provider or brokerage, executes no
real trades, and is not financial advice.
