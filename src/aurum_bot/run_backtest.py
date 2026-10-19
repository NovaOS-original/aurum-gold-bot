"""One-command historical candle backtest; research only, never sends orders."""
import argparse
import json
from pathlib import Path

import pandas as pd

from .demo_history import synthetic_history, yahoo_history
from .research import backtest


def load_candles(source: str, input_path: str | None, period: str, rows: int):
    if source == "csv":
        if not input_path:
            raise ValueError("--input is required with --source csv")
        path = Path(input_path)
        frame = pd.read_csv(path)
        actual_source = f"csv:{path}"
    elif source == "yahoo":
        frame = yahoo_history(period)
        actual_source = f"yahoo_finance_XAUUSD_equals:{period}:daily"
    elif source == "sample":
        frame = synthetic_history(rows)
        actual_source = "synthetic_fixture_NOT_real_market_data"
    else:
        raise ValueError(f"unsupported source: {source}")

    frame.columns = [str(c).strip().lower() for c in frame.columns]
    required = {"open", "high", "low", "close"}
    if not required.issubset(frame.columns):
        raise ValueError(f"candle input must include {sorted(required)}")
    for col in required:
        frame[col] = pd.to_numeric(frame[col], errors="coerce")
    if frame[list(required)].isna().any().any():
        raise ValueError("OHLC columns contain missing or non-numeric values")
    if (frame["low"] <= 0).any():
        raise ValueError("candle prices must be positive")
    if (frame["high"] < frame[["open", "close", "low"]].max(axis=1)).any():
        raise ValueError("invalid candle: high is below open, close, or low")
    if (frame["low"] > frame[["open", "close", "high"]].min(axis=1)).any():
        raise ValueError("invalid candle: low is above open, close, or high")
    if "time" in frame.columns:
        frame["time"] = pd.to_datetime(frame["time"], errors="coerce", utc=True)
        if frame["time"].isna().any():
            raise ValueError("time column contains invalid timestamps")
        frame = frame.sort_values("time").drop_duplicates("time").reset_index(drop=True)
    return frame, actual_source


def run(source="yahoo", input_path=None, period="5y", rows=1200,
        test_fraction=0.25, spread=0.30, slippage=0.05,
        commission_per_lot=0.0, starting_balance=1000.0, risk_fraction=0.005):
    candles, source_label = load_candles(source, input_path, period, rows)
    metrics = backtest(
        candles, test_fraction=test_fraction, spread=spread, slippage=slippage,
        commission_per_lot=commission_per_lot, starting_balance=starting_balance,
        risk_fraction=risk_fraction,
    )
    metrics["symbol"] = "XAU/USD"
    metrics["data_source"] = source_label
    metrics["candle_rows"] = len(candles)
    metrics["first_timestamp"] = str(candles.iloc[0]["time"]) if "time" in candles.columns else None
    metrics["last_timestamp"] = str(candles.iloc[-1]["time"]) if "time" in candles.columns else None
    metrics["data_warning"] = (
        "Synthetic fixture only: these results are not evidence of market performance."
        if source == "sample" else
        "Daily Yahoo candles are not suitable to validate a scalping strategy; use broker-exported M1/M5 candles and realistic costs."
        if source == "yahoo" else
        "CSV results depend on the source and quality of the supplied candles; verify timeframe and broker costs."
    )
    return metrics


def main():
    parser = argparse.ArgumentParser(description="Run an XAU/USD historical candle holdout backtest; no orders are sent")
    parser.add_argument("--source", choices=["yahoo", "csv", "sample"], default="yahoo",
                        help="Yahoo daily history by default; use csv for broker-exported candles")
    parser.add_argument("--input", help="CSV file containing time, open, high, low, close")
    parser.add_argument("--period", choices=["1y", "2y", "5y", "10y"], default="5y")
    parser.add_argument("--rows", type=int, default=1200, help="number of synthetic rows when --source sample")
    parser.add_argument("--output", default="reports/backtest.json")
    parser.add_argument("--test-fraction", type=float, default=0.25)
    parser.add_argument("--spread", type=float, default=0.30)
    parser.add_argument("--slippage", type=float, default=0.05)
    parser.add_argument("--commission-per-lot", type=float, default=0.0)
    parser.add_argument("--starting-balance", type=float, default=1000.0)
    parser.add_argument("--risk-fraction", type=float, default=0.005)
    args = parser.parse_args()
    try:
        result = run(args.source, args.input, args.period, args.rows, args.test_fraction,
                     args.spread, args.slippage, args.commission_per_lot,
                     args.starting_balance, args.risk_fraction)
    except Exception as exc:
        raise SystemExit(f"Backtest could not run: {exc}") from exc
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({"report": str(output), **result}, indent=2))


if __name__ == "__main__":
    main()
