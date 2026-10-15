"""Read-only OHLCV export from a running local MetaTrader 5 terminal."""
import argparse
from pathlib import Path
import pandas as pd

def main():
    p=argparse.ArgumentParser(description="Export MT5 candles only; this script cannot place orders")
    p.add_argument("--symbol",default="XAUUSD"); p.add_argument("--timeframe",choices=["M1","M5","M15","M30","H1","H4","D1"],default="M5")
    p.add_argument("--bars",type=int,default=20000); p.add_argument("--output",default="data/xauusd_mt5.csv")
    a=p.parse_args()
    if a.bars<100: p.error("--bars must be at least 100")
    try: import MetaTrader5 as mt5
    except ImportError as e: raise SystemExit("Install MetaTrader5 in Windows Python with a running MT5 terminal.") from e
    if not mt5.initialize(): raise SystemExit(f"MT5 initialize failed: {mt5.last_error()}")
    try:
        tf={"M1":mt5.TIMEFRAME_M1,"M5":mt5.TIMEFRAME_M5,"M15":mt5.TIMEFRAME_M15,"M30":mt5.TIMEFRAME_M30,"H1":mt5.TIMEFRAME_H1,"H4":mt5.TIMEFRAME_H4,"D1":mt5.TIMEFRAME_D1}[a.timeframe]
        if not mt5.symbol_select(a.symbol,True): raise SystemExit(f"Cannot select {a.symbol}; check broker's exact Market Watch symbol.")
        rates=mt5.copy_rates_from_pos(a.symbol,tf,1,a.bars) # start at shift 1 to exclude current forming candle
        if rates is None or len(rates)==0: raise SystemExit(f"No rates returned: {mt5.last_error()}")
        df=pd.DataFrame(rates); df["time"]=pd.to_datetime(df["time"],unit="s",utc=True)
        df=df.rename(columns={"tick_volume":"volume"})
        cols=["time","open","high","low","close","volume"]
        Path(a.output).parent.mkdir(parents=True,exist_ok=True); df[cols].to_csv(a.output,index=False)
        print(f"Exported {len(df)} closed candles to {a.output}. Read-only; no orders sent.")
    finally: mt5.shutdown()
if __name__=="__main__": main()
