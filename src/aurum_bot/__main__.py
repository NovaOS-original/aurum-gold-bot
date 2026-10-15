"""CLI for a research-only signal scan."""
import argparse, json
from pathlib import Path
import pandas as pd
from .strategy import latest_signal

def main():
    p=argparse.ArgumentParser(description="Aurum Gold Bot paper signal scan (no orders)")
    p.add_argument("--input",required=True); p.add_argument("--output",required=True)
    a=p.parse_args(); candles=pd.read_csv(a.input)
    result=latest_signal(candles)
    payload={"mode":"paper_only","signal":result.side,"reason":result.reason,"rows":len(candles)}
    Path(a.output).parent.mkdir(parents=True,exist_ok=True)
    Path(a.output).write_text(json.dumps(payload,indent=2),encoding="utf-8")
    print(json.dumps(payload,indent=2))
if __name__=="__main__": main()
