import os, time
from functools import lru_cache
from typing import Literal
import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="NanaForex Gold Tester API", version="1.0.0",
              description="Public, read-only historical XAUUSD candle service.")
origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(CORSMiddleware, allow_origins=origins,
                   allow_credentials=False, allow_methods=["GET"],
                   allow_headers=["Accept", "Content-Type"])

RANGES = {"1mo", "3mo", "6mo", "1y", "2y", "5y"}
INTERVALS = {"1m", "5m", "15m", "30m", "1h", "1d", "1wk"}
CACHE = {}
CACHE_TTL = 180

@app.get("/health")
async def health():
    return {"ok": True, "service": "NanaForex Gold Tester API", "provider": "Yahoo Finance"}

@app.get("/api/candles")
async def candles(symbol: Literal["XAUUSD"] = "XAUUSD",
                  interval: str = Query("1d"),
                  range: str = Query("1y")):
    if interval not in INTERVALS or range not in RANGES:
        raise HTTPException(400, "Unsupported interval or history range.")
    # Yahoo's public chart endpoint limits the depth of intraday data.
    if interval == "1m" and range not in {"1mo"}:
        raise HTTPException(400, "Yahoo Finance 1-minute history is limited; choose 1 month or less.")
    if interval in {"5m", "15m", "30m", "1h"} and range in {"2y", "5y"}:
        raise HTTPException(400, "Yahoo Finance intraday history is limited; choose 1 year or less.")
    key = (interval, range)
    now = time.time()
    cached = CACHE.get(key)
    if cached and now - cached["at"] < CACHE_TTL:
        return {**cached["data"], "cached": True}
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/XAUUSD%3DX?range={range}&interval={interval}&events=history"
    try:
        async with httpx.AsyncClient(timeout=20, headers={"User-Agent": "Mozilla/5.0 NanaForexGoldTester/1.0"}) as client:
            response = await client.get(url)
            response.raise_for_status()
            payload = response.json()
        result = payload.get("chart", {}).get("result") or []
        if not result:
            err = payload.get("chart", {}).get("error") or {}
            raise ValueError(err.get("description") or "No historical data returned by provider.")
        item = result[0]
        quote = item.get("indicators", {}).get("quote", [{}])[0]
        timestamps = item.get("timestamp") or []
        candles = []
        for i, stamp in enumerate(timestamps):
            try:
                o, h, l, c = (quote.get(k, [])[i] for k in ("open", "high", "low", "close"))
                if any(v is None for v in (o, h, l, c)):
                    continue
                o, h, l, c = map(float, (o, h, l, c))
                if min(o, h, l, c) <= 0 or h < max(o, c, l) or l > min(o, c, h):
                    continue
                vol = (quote.get("volume") or [None] * len(timestamps))[i]
                candles.append({"time": int(stamp), "open": o, "high": h, "low": l,
                                "close": c, "volume": int(vol) if vol is not None else 0})
            except (IndexError, TypeError, ValueError):
                continue
        if len(candles) < 2:
            raise ValueError("Provider returned too few valid OHLC candles.")
        data = {"symbol": "XAUUSD", "provider_symbol": "XAUUSD=X",
                "interval": interval, "range": range, "source": "Yahoo Finance",
                "timezone": "UTC", "count": len(candles), "candles": candles,
                "fetched_at": int(now)}
        CACHE[key] = {"at": now, "data": data}
        return data
    except (httpx.HTTPError, ValueError, KeyError, TypeError) as exc:
        raise HTTPException(502, f"Historical price provider unavailable: {str(exc)[:240]}")
