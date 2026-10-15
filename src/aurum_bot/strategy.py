"""Closed-candle EMA/RSI signal helpers; no order placement."""
from dataclasses import dataclass
import pandas as pd

@dataclass(frozen=True)
class Signal:
    side: str
    reason: str

def add_indicators(candles: pd.DataFrame) -> pd.DataFrame:
    required = {"open", "high", "low", "close"}
    if not required.issubset(candles.columns):
        raise ValueError(f"candles must include {sorted(required)}")
    out = candles.copy()
    close = out["close"].astype(float)
    out["ema9"] = close.ewm(span=9, adjust=False).mean()
    out["ema21"] = close.ewm(span=21, adjust=False).mean()
    delta = close.diff()
    gain = delta.clip(lower=0).ewm(alpha=1/14, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1/14, adjust=False).mean()
    rs = gain / loss.replace(0, float("nan"))
    out["rsi14"] = 100 - (100 / (1 + rs))
    tr = pd.concat([out["high"]-out["low"], (out["high"]-close.shift()).abs(), (out["low"]-close.shift()).abs()], axis=1).max(axis=1)
    out["atr14"] = tr.rolling(14).mean()
    return out

def latest_signal(candles: pd.DataFrame) -> Signal:
    """Return a candidate from the latest closed candle; informational only."""
    if len(candles) < 30:
        raise ValueError("at least 30 candles are required")
    x = add_indicators(candles).dropna(subset=["ema9", "ema21", "rsi14"])
    if len(x) < 2:
        return Signal("hold", "Indicators are not ready")
    prev, cur = x.iloc[-2], x.iloc[-1]
    if prev.ema9 <= prev.ema21 and cur.ema9 > cur.ema21 and cur.rsi14 >= 52:
        return Signal("long_candidate", "EMA9 crossed above EMA21 with RSI confirmation")
    if prev.ema9 >= prev.ema21 and cur.ema9 < cur.ema21 and cur.rsi14 <= 48:
        return Signal("short_candidate", "EMA9 crossed below EMA21 with RSI confirmation")
    return Signal("hold", "No confirmed crossover")
