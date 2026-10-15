"""Read-only local MetaTrader 5 market-data bridge for Aurum Gold Bot.

This service never sends orders. It binds to loopback only and requires a bearer token.
"""
from __future__ import annotations

import os
import secrets
from datetime import datetime, timezone
from typing import Any

import MetaTrader5 as mt5
from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

API_TOKEN = os.environ.get("AURUM_API_TOKEN", "")
SYMBOL = os.environ.get("AURUM_SYMBOL", "XAUUSD")
ALLOWED_ORIGINS = [
    item.strip()
    for item in os.environ.get(
        "AURUM_ALLOWED_ORIGINS",
        "https://novaos-original.github.io",
    ).split(",")
    if item.strip()
]
TIMEFRAME_NAMES = {
    "M1": mt5.TIMEFRAME_M1,
    "M5": mt5.TIMEFRAME_M5,
    "M15": mt5.TIMEFRAME_M15,
    "M30": mt5.TIMEFRAME_M30,
    "H1": mt5.TIMEFRAME_H1,
    "H4": mt5.TIMEFRAME_H4,
    "D1": mt5.TIMEFRAME_D1,
}

app = FastAPI(title="Aurum Gold Bot local MT5 bridge", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["Authorization"],
)


def require_token(authorization: str | None = Header(default=None)) -> None:
    if not API_TOKEN or len(API_TOKEN) < 32:
        raise HTTPException(
            status_code=503,
            detail="Bridge token is not configured. Set AURUM_API_TOKEN to a random secret of at least 32 characters.",
        )
    expected = f"Bearer {API_TOKEN}"
    if authorization is None or not secrets.compare_digest(authorization, expected):
        raise HTTPException(status_code=401, detail="Missing or invalid bearer token.")


def connect_mt5() -> None:
    if not mt5.initialize():
        raise HTTPException(
            status_code=503,
            detail=f"Could not initialize MT5 terminal: {mt5.last_error()}",
        )


def ensure_symbol(symbol: str) -> None:
    info = mt5.symbol_info(symbol)
    if info is None:
        raise HTTPException(
            status_code=404,
            detail=f"Symbol {symbol!r} not found. Check your broker's gold symbol (for example XAUUSD, GOLD, or XAUUSD.a).",
        )
    if not info.visible and not mt5.symbol_select(symbol, True):
        raise HTTPException(status_code=503, detail=f"Could not select symbol {symbol!r}.")


@app.get("/health")
def health() -> dict[str, Any]:
    """Non-sensitive process health only; does not reveal account information."""
    return {
        "service": "aurum-mt5-bridge",
        "status": "running",
        "utc": datetime.now(timezone.utc).isoformat(),
        "read_only": True,
    }


@app.get("/api/status", dependencies=[Depends(require_token)])
def status(symbol: str = Query(default=SYMBOL, min_length=1, max_length=32)) -> dict[str, Any]:
    connect_mt5()
    try:
        ensure_symbol(symbol)
        terminal = mt5.terminal_info()
        account = mt5.account_info()
        tick = mt5.symbol_info_tick(symbol)
        if terminal is None or tick is None:
            raise HTTPException(status_code=503, detail=f"MT5 status/tick unavailable: {mt5.last_error()}")
        # Account number, name, server and balance are intentionally not returned.
        return {
            "connected": True,
            "terminal_connected": bool(terminal.connected),
            "symbol": symbol,
            "bid": float(tick.bid),
            "ask": float(tick.ask),
            "last": float(tick.last),
            "spread": float(tick.ask - tick.bid),
            "tick_time_utc": datetime.fromtimestamp(tick.time, timezone.utc).isoformat(),
            "account_demo": bool(account.trade_mode == mt5.ACCOUNT_TRADE_MODE_DEMO) if account else None,
            "read_only": True,
        }
    finally:
        mt5.shutdown()


@app.get("/api/candles", dependencies=[Depends(require_token)])
def candles(
    symbol: str = Query(default=SYMBOL, min_length=1, max_length=32),
    timeframe: str = Query(default="M5"),
    count: int = Query(default=500, ge=40, le=5000),
) -> dict[str, Any]:
    timeframe_key = timeframe.upper()
    if timeframe_key not in TIMEFRAME_NAMES:
        raise HTTPException(status_code=400, detail=f"Unsupported timeframe. Choose one of {', '.join(TIMEFRAME_NAMES)}.")
    connect_mt5()
    try:
        ensure_symbol(symbol)
        rates = mt5.copy_rates_from_pos(symbol, TIMEFRAME_NAMES[timeframe_key], 0, count)
        if rates is None or len(rates) < 1:
            raise HTTPException(status_code=503, detail=f"No candle data returned: {mt5.last_error()}")
        data = []
        for rate in rates:
            data.append({
                "time": datetime.fromtimestamp(int(rate["time"]), timezone.utc).isoformat(),
                "open": float(rate["open"]),
                "high": float(rate["high"]),
                "low": float(rate["low"]),
                "close": float(rate["close"]),
                "tick_volume": int(rate["tick_volume"]),
                "spread_points": int(rate["spread"]),
            })
        return {
            "symbol": symbol,
            "timeframe": timeframe_key,
            "count": len(data),
            "candles": data,
            "read_only": True,
        }
    finally:
        mt5.shutdown()
