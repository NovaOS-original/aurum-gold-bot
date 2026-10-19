"""Fail-closed validation for market data before it reaches research or demo UI."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Mapping, Any


@dataclass(frozen=True)
class FeedCheck:
    ok: bool
    reasons: tuple[str, ...]
    age_seconds: float | None


def validate_candle(
    candle: Mapping[str, Any],
    *,
    now: datetime | None = None,
    max_age_seconds: float = 180.0,
) -> FeedCheck:
    """Validate one UTC-timestamped OHLC candle; never places or enables orders.

    Required keys: time, open, high, low, close. Timestamp must be ISO-8601.
    Naive timestamps are rejected to avoid ambiguous timezone interpretation.
    """
    reasons: list[str] = []
    if max_age_seconds <= 0:
        raise ValueError("max_age_seconds must be positive")
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ValueError("now must be timezone-aware")

    age: float | None = None
    raw_time = candle.get("time")
    try:
        if not isinstance(raw_time, str):
            raise ValueError("time must be an ISO-8601 string")
        parsed = datetime.fromisoformat(raw_time.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            raise ValueError("timestamp must include timezone")
        age = (now.astimezone(timezone.utc) - parsed.astimezone(timezone.utc)).total_seconds()
        if age < -5:
            reasons.append("candle_timestamp_in_future")
        elif age > max_age_seconds:
            reasons.append("stale_candle")
    except (TypeError, ValueError) as exc:
        reasons.append(f"invalid_timestamp:{exc}")

    prices: dict[str, float] = {}
    for key in ("open", "high", "low", "close"):
        try:
            value = float(candle[key])
            if not (value > 0 and value < float("inf")):
                raise ValueError
            prices[key] = value
        except (KeyError, TypeError, ValueError, OverflowError):
            reasons.append(f"invalid_{key}")

    if len(prices) == 4:
        o, h, l, c = (prices[k] for k in ("open", "high", "low", "close"))
        if h < max(o, c, l):
            reasons.append("inconsistent_high")
        if l > min(o, c, h):
            reasons.append("inconsistent_low")

    return FeedCheck(ok=not reasons, reasons=tuple(reasons), age_seconds=age)


def validate_spread(*, bid: float, ask: float, max_spread: float) -> FeedCheck:
    """Reject crossed/invalid quotes and spreads above a configured price-unit cap."""
    if max_spread <= 0:
        raise ValueError("max_spread must be positive")
    reasons: list[str] = []
    try:
        bid, ask = float(bid), float(ask)
        if not (bid > 0 and ask > 0 and bid < float("inf") and ask < float("inf")):
            reasons.append("invalid_quote")
        elif ask < bid:
            reasons.append("crossed_quote")
        elif ask - bid > max_spread:
            reasons.append("spread_too_wide")
    except (TypeError, ValueError, OverflowError):
        reasons.append("invalid_quote")
    return FeedCheck(ok=not reasons, reasons=tuple(reasons), age_seconds=None)
