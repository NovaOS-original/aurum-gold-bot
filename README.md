# Aurum Gold Bot — demo-first XAU/USD research

**Status: research and paper signals only. No order placement is implemented. No win rate or profitability is promised.**

## Included
- EMA(9)/EMA(21) crossover with RSI(14) confirmation.
- ATR-based assumptions in a chronological holdout backtest.
- Spread, slippage and commission assumptions; net P&L, return and drawdown reporting.
- Built-in history setup: fetch daily XAU/USD history when online, or generate a labelled offline test fixture.
- Read-only MT5 candle export for a locally running Windows terminal.
- Reusable fail-closed market-data validators for stale/malformed candles and excessive/crossed quotes.
- Responsive dashboard for phones, tablets and desktop browsers.
- GitHub Actions CI and GitHub Pages deployment workflow.

## Install (Python 3.11+)
```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -v
```

## Built-in market history for demo/testing (new)
You no longer need to locate and manually provide a CSV to try the research pipeline.

```powershell
$env:PYTHONPATH = "src"
python -m aurum_bot.demo_history
```

By default, this attempts to download up to five years of **daily historical XAU/USD** from Yahoo Finance and writes:
- `data/demo_xauusd.csv` — normalized OHLCV candles
- `data/demo_xauusd.meta.json` — data source, row count, date range and warnings

Choose a period and output path:
```powershell
python -m aurum_bot.demo_history --source yahoo --period 5y --output data/demo_xauusd.csv
```

For an offline software-only test fixture:
```powershell
python -m aurum_bot.demo_history --source sample --rows 1200
```

**Important:** the offline fixture is synthetic, not real market history, and must not be used to assess strategy profitability. In default `auto` mode, if the online download fails, the script falls back to that synthetic fixture and records this clearly in the metadata file. Check `source` in the metadata before every backtest. Yahoo daily candles may differ from your broker's XAUUSD feed and do not substitute for M1/M5 scalping validation. For broker-specific intraday testing, use the MT5 export below.

## Export closed MT5 candles (Windows)
Install MetaTrader 5 desktop and connect to a demo account:
```powershell
python -m pip install MetaTrader5
$env:PYTHONPATH = "src"
python -m aurum_bot.mt5_export --symbol XAUUSD --timeframe M5 --bars 20000 --output data/xauusd_mt5.csv
```
Confirm the exact gold symbol in Market Watch; some brokers use a suffix or `GOLD`. This exports closed candles only and does not submit orders.

## Market-data guardrails
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

## Dashboard: select and run built-in history

On the GitHub Pages dashboard, open **Backtest data**, choose **Last 1 year**, **Last 2 years**, or **Last 5 years**, then tap **Load built-in history** and **Run historical backtest**. The dashboard requests real daily XAU/USD candles from Yahoo Finance in the browser; internet access and the provider allowing browser requests are required. If the provider blocks the request, use the Python command below on Windows to download the data, or upload a broker-exported CSV. The separate **Load synthetic test fixture** option is only for checking that the UI/backtest runs and is not real market history.

Daily Yahoo candles are not appropriate for evaluating a scalping strategy. Use MT5-exported M1/M5 demo-account candles with realistic spread, slippage and commission assumptions for that purpose. No orders are sent.

## One-command built-in historical candle backtest (new)

Run the full pipeline without manually creating a CSV (requires internet for Yahoo Finance):

```powershell
$env:PYTHONPATH = "src"
python -m aurum_bot.run_backtest --source yahoo --period 5y --output reports/backtest.json
```

The command downloads daily XAU/USD candles, validates OHLC data, runs the chronological holdout backtest, and writes a JSON report with trade count, win rate (when trades exist), net P/L, return, maximum drawdown, assumptions, date range, and data-source warnings. It defaults to **real Yahoo daily history** and fails rather than silently substituting synthetic candles if that download fails.

For broker-specific intraday candles (recommended for scalping), export closed M1 or M5 candles from the MT5 demo terminal, then run:

```powershell
python -m aurum_bot.run_backtest --source csv --input data/xauusd_mt5.csv --output reports/mt5_m5_backtest.json --spread 0.30 --slippage 0.05 --commission-per-lot 0
```

For software tests only, synthetic fixture mode is explicit:

```powershell
python -m aurum_bot.run_backtest --source sample --rows 1200 --output reports/synthetic_test.json
```

**Never interpret synthetic-fixture results as trading performance.** Yahoo daily candles are not appropriate to validate scalping. Check broker-specific symbol, timeframe, spread, slippage, commission units, contract size, tick value, and account currency before interpreting any report. No orders are sent.

## Run holdout research
```powershell
$env:PYTHONPATH = "src"
python -m aurum_bot.research --input data/demo_xauusd.csv --output reports/backtest.json --test-fraction 0.25 --spread 0.30 --slippage 0.05 --commission-per-lot 0 --starting-balance 1000
```
The last chronological fraction is held out for evaluation; parameters are not tuned by the script. This is an approximate bar-based model, not a forecast. Its sizing is illustrative and **not broker-lot sizing**. Before interpreting results, validate contract size, tick size/value, lot minimum/step, margin, account currency and actual commission units. If stop and target are both inside a candle, the model assumes the stop was hit first.

## Hosting
`site/index.html` is a responsive static dashboard. In repository Settings → Pages, choose GitHub Actions as the deployment source. GitHub Actions is not a persistent low-latency trading server. A future MT5 demo feed needs an always-on Windows host and an authenticated backend. Never put broker credentials in browser code, Pages or the repository.

## Safety
No order adapter is present. Keep development demo-first. Synthetic fixtures are for software tests only. Before interpreting results, use real broker-exported candles and realistic spread, slippage, commission, and untouched out-of-sample periods. Live trading must remain disabled by default.


## NanaForex Gold Tester (public historical strategy lab)

The GitHub Pages front end is now branded **NanaForex Gold Tester**. It is designed for public use without sign-in and provides historical XAUUSD candles, candlestick/line charts, EMA 9/21, SMA 50, Bollinger Bands, RSI, configurable EMA-crossover/RSI strategy tests, ATR-based stop/target simulation, chronological out-of-sample results, trade markers/log, equity curve, and CSV export. It does not connect to a broker or place orders.

**Primary free history source:** [misix-git/xaus-api](https://github.com/misix-git/xaus-api), using `https://xaus.com/api/v1/chart?symbol=xau&range=1y&interval=1d`. It is keyless and documents open CORS, OHLCV candles and freshness metadata. The website now requests this source directly from the browser, so the Render API is no longer required for the primary historical-data path. If XAUS is unavailable and a Render API URL is configured, the app falls back to the NanaForex API. Provider coverage and upstream availability can change; the app validates candle values and reports failures instead of inventing data. XAUS asks for attribution, which is displayed in the chart source label.

### Deploy the historical-price API

**Important current setup state:** the frontend API URL is intentionally blank until the Render backend has actually been created. Without this one-time deployment and URL configuration, GitHub Pages cannot fetch market candles; it is a static host and cannot run Python itself.

[Deploy the API Blueprint on Render](https://render.com/deploy?repo=https://github.com/NovaOS-original/aurum-gold-bot)

GitHub Pages serves static files and cannot run the Python API itself. The repository includes a FastAPI read-only market-history service and a Render Blueprint:

1. In Render, create a new Blueprint from this repository and approve the `render.yaml` service named `nanaforex-gold-tester-api`.
2. Wait for deployment. Verify the service URL plus `/health` returns JSON with `"ok": true`.
3. Open `site/config.js` in GitHub and replace the empty value with the Render HTTPS URL, for example:
   ```js
   window.NANA_API_BASE = "https://YOUR-SERVICE.onrender.com";
   ```
4. Commit the change. The existing GitHub Pages workflow deploys the updated `site/` directory automatically.

The API fetches public historical candles for Yahoo Finance's `XAUUSD=X` symbol, normalizes OHLCV values, returns UTC timestamps, validates candle consistency, and caches successful responses briefly. No API key, account, sign-in, or broker credentials are required. The provider may impose availability, delay, retention, and rate limits; the API fails visibly rather than fabricating market candles. Render free services may sleep when idle, so the first request after inactivity can take longer.

### Timeframe and data limitations

Yahoo Finance commonly limits intraday history more tightly than daily/weekly history. The API rejects unsupported long intraday ranges rather than pretending the requested history was returned. Broker-exported candles are still preferred for realistic XAUUSD scalping research. Confirm symbol suffix, spread, slippage, commission, contract size and tick value for the broker you use.

### Public API endpoints

- `GET /health` — service health.
- `GET /api/candles?symbol=XAUUSD&interval=5m&range=1mo` — normalized historical OHLCV candles.
- Supported intervals: `1m`, `5m`, `15m`, `30m`, `1h`, `1d`, `1wk`; range constraints are enforced by the API.

This is a historical research and education tool. Results are approximate bar simulations, not forecasts or guaranteed performance. No live trading is enabled.

### Chart library attribution

The chart currently uses TradingView Lightweight Charts. Its required attribution must remain visible while this library is used. To have a chart with no TradingView branding, the chart engine must be replaced with a different library or an original canvas renderer; simply hiding the attribution would violate the library's attribution terms.
