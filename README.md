# Aurum Gold Bot — demo-first XAU/USD research

**Status: research and paper signals only. No order placement is implemented. No win rate or profitability is promised.**

## Included
- EMA(9)/EMA(21) crossover with RSI(14) confirmation.
- ATR-based assumptions in a chronological holdout backtest.
- Spread, slippage and commission assumptions; net P&L, return and drawdown reporting.
- Read-only MT5 candle export for a locally running Windows terminal.
- Reusable fail-closed market-data validators for stale/malformed candles and excessive/crossed quotes.
- Responsive dashboard for phones, tablets and desktop browsers.
- GitHub Actions CI and GitHub Pages deployment workflow.

The candles used in automated tests are synthetic software fixtures, not real gold prices. Never infer profitability from them.

## Install (Python 3.11+)
```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -v
```

## Export closed MT5 candles (Windows)
Install MetaTrader 5 desktop and connect to a demo account:
```powershell
python -m pip install MetaTrader5
$env:PYTHONPATH = "src"
python -m aurum_bot.mt5_export --symbol XAUUSD --timeframe M5 --bars 20000 --output data/xauusd_mt5.csv
```
Confirm the exact gold symbol in Market Watch; some brokers use a suffix or `GOLD`. This exports closed candles only and does not submit orders.

## Market-data guardrails (new)
The reusable checks are in `src/aurum_bot/feed_guard.py`. They reject stale or future-dated candles, timezone-naive timestamps, invalid/inconsistent OHLC values, invalid/crossed quotes, and spreads above a configured price-unit limit. Example:
```python
from aurum_bot.feed_guard import validate_candle, validate_spread

candle_check = validate_candle(candle, max_age_seconds=180)
quote_check = validate_spread(bid=bid, ask=ask, max_spread=0.50)
if not candle_check.ok or not quote_check.ok:
    # Fail closed: mark feed unhealthy and do not act on the signal.
    print(candle_check.reasons, quote_check.reasons)
```
**Integration boundary:** these are tested utility functions, not yet wired into a continuously running MT5-to-dashboard service. The current exporter remains a one-shot CSV export. Do not treat the dashboard as a live feed until an authenticated bridge calls these checks and exposes health/last-update status.

## Run holdout research
```powershell
$env:PYTHONPATH = "src"
python -m aurum_bot.research --input data/xauusd_mt5.csv --output reports/backtest.json --test-fraction 0.25 --spread 0.30 --slippage 0.05 --commission-per-lot 0 --starting-balance 1000
```
The last chronological fraction is held out for evaluation; parameters are not tuned by the script. This is an approximate bar-based model, not a forecast. Its sizing is illustrative and **not broker-lot sizing**. Before interpreting results, validate contract size, tick size/value, lot minimum/step, margin, account currency and actual commission units. If stop and target are both inside a candle, the model assumes the stop was hit first.

## Hosting
`site/index.html` is a responsive static dashboard. In repository Settings → Pages, choose GitHub Actions as the deployment source. GitHub Actions is not a persistent low-latency trading server. A future MT5 demo feed needs an always-on Windows host and an authenticated backend. Never put broker credentials in browser code, Pages or the repository.

## Safety
No order adapter is present. Keep development demo-first. Before any execution is developed, add idempotency, enforced stale-data and max-spread checks, daily loss/position caps, broker-side SL/TP verification, reconnect handling, authenticated controls and an emergency stop. Live trading must remain disabled by default.
