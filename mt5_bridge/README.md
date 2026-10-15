# Aurum Gold Bot — local MT5 bridge (read-only)

This small Windows service exposes **market quotes and historical candles only** from a locally running MetaTrader 5 terminal. It does not contain order-placement routes and never submits trades.

## Requirements

- Windows 10/11, 64-bit Python, and the desktop MetaTrader 5 terminal installed.
- MT5 open and signed in to a broker **demo** account.
- Internet access to install Python packages.

## Start it

Open PowerShell in this folder (or run `run_bridge.ps1` from an appropriately configured PowerShell session). Set a private bearer token first:

```powershell
$env:AURUM_API_TOKEN = [guid]::NewGuid().ToString() + [guid]::NewGuid().ToString()
$env:AURUM_SYMBOL = "XAUUSD"
.un_bridge.ps1
```

If your broker uses a different symbol (for example `GOLD` or `XAUUSD.a`), change `AURUM_SYMBOL` to the exact name shown in MT5 Market Watch.

The service binds to `127.0.0.1` only, not your LAN or the public internet. Keep the token private; anyone who obtains it can read the local endpoints. Do not put it in GitHub, HTML, screenshots, or a public issue. Use a fresh token whenever you restart your PowerShell session.

## Endpoints

- `GET http://127.0.0.1:8765/health` — process health, no account details.
- `GET /api/status?symbol=XAUUSD` — current bid/ask, spread and whether MT5 reports a demo account.
- `GET /api/candles?symbol=XAUUSD&timeframe=M5&count=500` — OHLC candle history (M1, M5, M15, M30, H1, H4, D1).

Protected endpoints require `Authorization: Bearer YOUR_TOKEN`. The bridge deliberately omits account number, server, balance, and personal account details.

## Test from PowerShell

In the same PowerShell session where `AURUM_API_TOKEN` is set:

```powershell
Invoke-RestMethod http://127.0.0.1:8765/health
$headers = @{ Authorization = "Bearer $env:AURUM_API_TOKEN" }
Invoke-RestMethod "http://127.0.0.1:8765/api/status?symbol=$env:AURUM_SYMBOL" -Headers $headers
Invoke-RestMethod "http://127.0.0.1:8765/api/candles?symbol=$env:AURUM_SYMBOL&timeframe=M5&count=100" -Headers $headers
```

## Browser/dashboard integration status

The GitHub Pages site is HTTPS while this service is local HTTP. Browser mixed-content and local-network access restrictions vary, and a public page cannot safely embed a secret token in JavaScript. **Do not paste the bearer token into the public dashboard.** This bridge is a first, local connectivity milestone; a secure dashboard pairing flow or a locally served UI is needed before a remote phone/tablet can access it safely. A loopback service is accessible only from the same PC, not directly from a phone on another device.

## Safety limitations

- Read-only endpoints only; no order placement or trade modification routes exist.
- Start with a demo account and verify `account_demo` is `true`.
- Do not expose port 8765 publicly or configure router port forwarding.
- The bridge requires the MT5 desktop terminal and Python MetaTrader5 package on Windows.
