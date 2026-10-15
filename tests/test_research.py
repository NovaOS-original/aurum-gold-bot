import unittest
import pandas as pd
from aurum_bot.research import backtest

class ResearchTests(unittest.TestCase):
    def candles(self,n=300):
        # Deterministic software fixture only; not real market data.
        c=[2000 + i*.03 + ((i%18)-9)*.12 for i in range(n)]
        return pd.DataFrame({"open":c,"high":[v+.8 for v in c],"low":[v-.8 for v in c],"close":c})
    def test_chronological_holdout_and_metrics(self):
        r=backtest(self.candles(),test_fraction=.25,spread=.3,slippage=.05)
        self.assertEqual(r["training_rows"],225)
        self.assertEqual(r["holdout_rows"],75)
        self.assertIn("net_profit",r); self.assertIn("max_drawdown_pct",r)
        self.assertEqual(r["mode"],"historical_research_only")
    def test_invalid_cost_rejected(self):
        with self.assertRaises(ValueError): backtest(self.candles(),spread=-1)
    def test_too_short_rejected(self):
        with self.assertRaises(ValueError): backtest(self.candles(50))
if __name__=="__main__": unittest.main()
