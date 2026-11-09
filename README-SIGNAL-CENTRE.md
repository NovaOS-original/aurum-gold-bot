# Aurum Gold Signal Centre

A responsive, static XAUUSD signal dashboard for research and demo use.

## Current status
- Dashboard and risk calculator are published from GitHub Pages.
- The signal feed is intentionally empty until a trusted live market-data source and validated signal-generation service are configured.
- No sample or fabricated trade is presented as live.
- No broker execution or live trading is enabled.

## Risk policy
- Maximum three new trades per UTC day; fewer or zero is valid.
- Planned reward:risk must be at least 1:3 after a realistic costs allowance.
- Suggested risk is 0.5% per trade, hard cap 1%.
- Daily stop is 2%; halt new signals after reaching it.
- Every signal needs entry, invalidation/stop, target, timestamp, timeframe, rationale, source and expiry.
- Signals must be cancelled/marked stale if the feed is delayed or market conditions invalidate the setup.

## Feed contract
Update `signals.json` with:
```json
{
  "updated_at": "ISO-8601 UTC timestamp",
  "source": "market-data provider and instrument",
  "signals": [
    {
      "id": "unique-id",
      "symbol": "XAUUSD",
      "side": "BUY",
      "status": "ACTIVE",
      "timeframe": "M15",
      "entry": 0,
      "stop_loss": 0,
      "take_profit": 0,
      "rr": 3,
      "risk_percent": 0.5,
      "published_at": "ISO-8601 UTC timestamp",
      "reason": "Concise setup rationale"
    }
  ]
}
```

## Deployment
Enable GitHub Pages for this repository with **GitHub Actions** as the source. The included workflow deploys the repository root on pushes to `main`.

## Important architecture limitation
GitHub Pages serves the site but is not a continuously running low-latency trading server. GitHub Actions schedules can be delayed and are not suitable for guaranteed 24/7 signal generation. A production signal service needs a reliable always-on backend, authenticated market-data feed, secret-managed credentials, health monitoring, stale-data protection and audit logs. Keep broker execution disabled; this project does not place orders.

This is research/educational software, not financial advice. A 1:3 target is not a guaranteed realised return.
