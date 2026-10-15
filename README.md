# Aurum Gold Bot — demo-first XAU/USD research

**Status: research and paper signals only. No order placement is implemented. No win rate or profitability is promised.**

## What is included
- EMA(9)/EMA(21) crossover with RSI confirmation.
- ATR-based exits and a chronological holdout backtest with spread, slippage and commission modelling.
- Read-only MT5 candle export for a locally running Windows terminal.
- Responsive static dashboard for phone, tablet and desktop browsers.
- GitHub Actions test workflow and GitHub Pages deployment workflow.

The included CSV is synthetic software-test data, not gold market data. Do not use its results to infer trading profitability.

## Local setup (Python 3.11+)
```powershell
py -m venv .venv
.venv\\Scripts\\Activate.ps1
python -m pip install -r requirements.txt
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -v
```

## MT5 read-only export
Run on Windows with MT5 installed and connected to a demo account:
```powershell
python -m pip install MetaTrader5
$env:PYTHONPATH = "src"
python -m aurum_bot.mt5_export --symbol XAUUSD --timeframe M5 --bars 20000 --output data/xauusd_mt5.csv
```
Confirm your broker's exact gold symbol in Market Watch. This command only exports candles; it never submits orders.

## Backtest real data
```powershell
$env:PYTHONPATH = "src"
python -m aurum_bot.research --input data/xauusd_mt5.csv --output reports/backtest.json --test-fraction 0.25 --spread 0.30 --slippage 0.05 --commission-per-lot 0 --starting-balance 1000
```
Use observed broker costs and verify contract size, tick value, lot step, account currency and margin rules. Never tune on the holdout and then call it out-of-sample.

## Cross-platform dashboard and hosting
`site/index.html` is a responsive static dashboard. GitHub Pages can serve it to modern mobile and desktop browsers. See [PLATFORM_ARCHITECTURE.md](PLATFORM_ARCHITECTURE.md). GitHub Actions is not a persistent low-latency trading server. For future MT5 demo execution, use an always-on Windows VPS running MT5 or a supported official broker API host, plus an authenticated backend. Keep secrets out of source and browser code.

## Strategy hypothesis
Long: EMA(9) crosses above EMA(21), RSI(14) >= 52. Short: EMA(9) crosses below EMA(21), RSI(14) <= 48. Entry is next bar open; stop 1.2 ATR, target 1.5 ATR, timeout 12 bars. These are hypotheses, not a proven edge.

Before adding demo execution, implement and test idempotency, stale-data and max-spread guards, daily loss/position caps, broker-side SL/TP verification, reconnect handling and an emergency stop. Live trading must remain disabled by default.