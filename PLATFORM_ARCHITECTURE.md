# Cross-platform and GitHub-hosted architecture

## Cross-device access
The `site/index.html` dashboard is a responsive static web app for modern mobile and desktop browsers. GitHub Pages can host it without installing Python or MT5 on the device.

## GitHub responsibilities
GitHub stores source and tests; Actions runs CI and periodic non-critical research; Pages serves the static dashboard. The dashboard may display `site/report.json` when a validated report is supplied. Do not invent market performance or publish private account data.

## MT5 limitation
GitHub Actions jobs are ephemeral and scheduled timing is not guaranteed. They are not a persistent API server or low-latency execution host. The Python MetaTrader5 integration normally talks to a running desktop terminal, typically on Windows.

Recommended future architecture: private repository for source/tests; GitHub Pages for public-safe dashboard; always-on Windows VPS with MT5 demo terminal for broker connectivity and execution; authenticated HTTPS API/private relay for status. Keep broker credentials on the execution host, never in browser code or Pages.

## Safety requirements
- Demo-first; live trading disabled by default.
- Never commit passwords, tokens, account IDs or private data.
- Add idempotency, stale-data rejection, spread caps, daily loss and position caps, server-side SL/TP verification, reconnect logic and kill switch before any execution.
- Verify broker symbol, contract size, tick value, lot minimum/step, margin and account currency.

## Pages
In repository Settings → Pages, select GitHub Actions as the deployment source. The workflow deploys `site/`. Do not publish private reports.