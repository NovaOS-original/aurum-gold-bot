import unittest
import pandas as pd
from aurum_bot.strategy import add_indicators, latest_signal

class StrategyTests(unittest.TestCase):
    def candles(self,n=80):
        close=[2000+i*0.1 for i in range(n)]
        return pd.DataFrame({"open":close,"high":[x+0.5 for x in close],"low":[x-0.5 for x in close],"close":close})
    def test_indicators_exist(self):
        x=add_indicators(self.candles())
        self.assertIn("ema9",x); self.assertIn("atr14",x)
    def test_short_history_rejected(self):
        with self.assertRaises(ValueError): latest_signal(self.candles(10))
    def test_signal_is_non_executing_label(self):
        result=latest_signal(self.candles())
        self.assertIn(result.side,{"hold","long_candidate","short_candidate"})
if __name__=="__main__": unittest.main()
