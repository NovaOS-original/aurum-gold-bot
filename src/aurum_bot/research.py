"""Chronological XAU/USD candle backtest; research only, never sends orders."""
import argparse, json
from pathlib import Path
import pandas as pd
from .strategy import add_indicators

def backtest(candles: pd.DataFrame, test_fraction=0.25, spread=0.30, slippage=0.05,
             commission_per_lot=0.0, starting_balance=1000.0, risk_fraction=0.005):
    required={"open","high","low","close"}
    if not required.issubset(candles.columns): raise ValueError(f"input must include {sorted(required)}")
    if not 0.1 <= test_fraction <= 0.5: raise ValueError("test_fraction must be between 0.1 and 0.5")
    if min(spread,slippage,commission_per_lot)<0 or starting_balance<=0 or not 0<risk_fraction<=0.02:
        raise ValueError("costs must be nonnegative, balance positive, risk_fraction in (0, 0.02]")
    x=add_indicators(candles.reset_index(drop=True))
    split=int(len(x)*(1-test_fraction))
    if split<40 or len(x)-split<20: raise ValueError("need at least 40 training and 20 holdout candles")
    # Strategy is evaluated only on the holdout segment; it is not optimized on the training segment.
    balance=float(starting_balance); equity=balance; peak=balance; max_dd=0.0; trades=[]
    i=max(split,30)
    while i < len(x)-1:
        prev,cur=x.iloc[i-1],x.iloc[i]
        side=None
        if prev.ema9<=prev.ema21 and cur.ema9>cur.ema21 and cur.rsi14>=52: side=1
        elif prev.ema9>=prev.ema21 and cur.ema9<cur.ema21 and cur.rsi14<=48: side=-1
        if side is None or pd.isna(cur.atr14) or cur.atr14<=0:
            i+=1; continue
        entry_i=i+1; entry=float(x.iloc[entry_i].open) + side*(spread/2+slippage)
        atr=float(cur.atr14); stop_dist=1.2*atr; target_dist=1.5*atr
        stop=entry-side*stop_dist; target=entry+side*target_dist
        exit_price=None; reason="timeout"; exit_i=min(entry_i+12,len(x)-1)
        for j in range(entry_i, min(entry_i+13,len(x))):
            bar=x.iloc[j]
            # Conservative same-candle ambiguity: stop is assumed hit before target.
            if (side==1 and bar.low<=stop) or (side==-1 and bar.high>=stop):
                exit_price=stop; reason="stop"; exit_i=j; break
            if (side==1 and bar.high>=target) or (side==-1 and bar.low<=target):
                exit_price=target; reason="target"; exit_i=j; break
        if exit_price is None: exit_price=float(x.iloc[exit_i].close)-side*(spread/2+slippage)
        risk_cash=balance*risk_fraction
        units=risk_cash/stop_dist
        gross=(exit_price-entry)*side*units
        costs=commission_per_lot*units
        pnl=gross-costs; balance+=pnl; peak=max(peak,balance); max_dd=max(max_dd,(peak-balance)/peak if peak else 0)
        trades.append({"entry_index":entry_i,"exit_index":exit_i,"side":"long" if side==1 else "short","entry":entry,"exit":exit_price,"reason":reason,"pnl":pnl,"costs":costs})
        i=exit_i+1
    wins=sum(t["pnl"]>0 for t in trades); net=sum(t["pnl"] for t in trades)
    return {"mode":"historical_research_only","training_rows":split,"holdout_rows":len(x)-split,"trades":len(trades),
            "wins":wins,"win_rate":wins/len(trades) if trades else None,"starting_balance":starting_balance,
            "ending_balance":balance,"net_profit":net,"return_pct":100*net/starting_balance,
            "max_drawdown_pct":100*max_dd,"spread_assumption":spread,"slippage_assumption":slippage,
            "commission_per_unit_assumption":commission_per_lot,
            "warning":"Approximate bar-based model, not a forecast. Confirm units, contract size, tick value, spread and commissions for your broker. No execution."}

def main():
    p=argparse.ArgumentParser(description="Historical holdout backtest; no broker orders")
    p.add_argument("--input",required=True); p.add_argument("--output",default="reports/backtest.json")
    p.add_argument("--test-fraction",type=float,default=.25); p.add_argument("--spread",type=float,default=.30)
    p.add_argument("--slippage",type=float,default=.05); p.add_argument("--commission-per-lot",type=float,default=0)
    p.add_argument("--starting-balance",type=float,default=1000); p.add_argument("--risk-fraction",type=float,default=.005)
    a=p.parse_args(); result=backtest(pd.read_csv(a.input),a.test_fraction,a.spread,a.slippage,a.commission_per_lot,a.starting_balance,a.risk_fraction)
    Path(a.output).parent.mkdir(parents=True,exist_ok=True); Path(a.output).write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(json.dumps(result,indent=2))
if __name__=="__main__": main()
