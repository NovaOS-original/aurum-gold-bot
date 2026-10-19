"""Prepare built-in XAU/USD demo candles, preferring real Yahoo Finance history.

No trading or broker connection is performed. If network data is unavailable in auto
mode, a deterministic synthetic fixture is generated and clearly labelled in metadata.
"""
import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


def synthetic_history(rows: int = 1200) -> pd.DataFrame:
    """Deterministic test fixture, NOT real market data."""
    if rows < 100:
        raise ValueError("rows must be at least 100")
    import random
    rng = random.Random(20261019)
    price = 2200.0
    values = []
    start = pd.Timestamp("2021-01-04", tz="UTC")
    date = start
    for i in range(rows):
        while date.weekday() >= 5:
            date += pd.Timedelta(days=1)
        phase = math.sin(i / 43.0) * 0.65 + math.sin(i / 137.0) * 0.35
        shock = rng.gauss(0, 11.0 if (i // 37) % 3 == 0 else 5.0)
        change = 0.35 + phase * 1.8 + shock
        open_price = price
        close = max(100.0, open_price + change)
        wick = abs(rng.gauss(5.0, 3.0))
        high = max(open_price, close) + wick
        low = min(open_price, close) - abs(rng.gauss(5.0, 3.0))
        values.append({
            "time": date.strftime("%Y-%m-%dT00:00:00Z"),
            "open": round(open_price, 2), "high": round(high, 2),
            "low": round(max(1.0, low), 2), "close": round(close, 2),
            "volume": rng.randint(500, 9000),
        })
        price = close
        date += pd.Timedelta(days=1)
    return pd.DataFrame(values)


def yahoo_history(period: str = "5y") -> pd.DataFrame:
    """Fetch daily XAU/USD history; requires internet and yfinance."""
    try:
        import yfinance as yf
    except ImportError as exc:
        raise RuntimeError("yfinance is not installed") from exc
    frame = yf.download("XAUUSD=X", period=period, interval="1d",
                        auto_adjust=False, progress=False, threads=False)
    if frame is None or frame.empty:
        raise RuntimeError("Yahoo Finance returned no XAU/USD history")
    if isinstance(frame.columns, pd.MultiIndex):
        frame.columns = frame.columns.get_level_values(0)
    frame.columns = [str(c).lower() for c in frame.columns]
    frame = frame.reset_index()
    frame.columns = [str(c).lower() for c in frame.columns]
    time_col = "date" if "date" in frame.columns else "datetime"
    required = {"open", "high", "low", "close", time_col}
    if not required.issubset(frame.columns):
        raise RuntimeError(f"Unexpected Yahoo Finance columns: {list(frame.columns)}")
    frame["time"] = pd.to_datetime(frame[time_col], utc=True).dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    if "volume" not in frame.columns:
        frame["volume"] = 0
    out = frame[["time", "open", "high", "low", "close", "volume"]].copy()
    out = out.dropna(subset=["open", "high", "low", "close"])
    if len(out) < 100:
        raise RuntimeError(f"Only {len(out)} valid historical rows returned")
    return out


def main():
    parser = argparse.ArgumentParser(description="Prepare built-in XAU/USD history for demo/testing; never places orders")
    parser.add_argument("--source", choices=["auto", "yahoo", "sample"], default="auto")
    parser.add_argument("--period", choices=["1y", "2y", "5y", "10y"], default="5y")
    parser.add_argument("--rows", type=int, default=1200, help="synthetic rows if sample fallback is used")
    parser.add_argument("--output", default="data/demo_xauusd.csv")
    args = parser.parse_args()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    source = args.source
    error = None
    frame = None
    if source in ("auto", "yahoo"):
        try:
            frame = yahoo_history(args.period)
            source = "yahoo_finance_XAUUSD_equals"
        except Exception as exc:
            error = str(exc)
            if args.source == "yahoo":
                raise SystemExit(f"Could not fetch real history: {error}") from exc
    if frame is None:
        frame = synthetic_history(args.rows)
        source = "synthetic_fixture_NOT_real_market_data"
    frame.to_csv(output, index=False)
    metadata = {
        "symbol": "XAU/USD",
        "timeframe": "1d",
        "source": source,
        "rows": int(len(frame)),
        "first_timestamp": str(frame.iloc[0]["time"]),
        "last_timestamp": str(frame.iloc[-1]["time"]),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "network_fetch_error": error,
        "warning": "Yahoo historical prices may differ from the user's MT5 broker feed. Synthetic fallback is for software tests only and must never be used to claim trading performance.",
        "order_placement": "not implemented",
    }
    metadata_path = output.with_suffix(".meta.json")
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(json.dumps({"csv": str(output), "metadata": str(metadata_path), **metadata}, indent=2))


if __name__ == "__main__":
    main()
