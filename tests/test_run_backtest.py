import unittest
import pandas as pd

from aurum_bot.run_backtest import load_candles, run


class BuiltInBacktestTests(unittest.TestCase):
    def test_sample_backtest_is_explicitly_labelled_synthetic(self):
        result = run(source="sample", rows=300)
        self.assertEqual(result["mode"], "historical_research_only")
        self.assertEqual(result["data_source"], "synthetic_fixture_NOT_real_market_data")
        self.assertIn("not evidence", result["data_warning"])
        self.assertIn("max_drawdown_pct", result)

    def test_invalid_ohlc_rejected(self):
        frame = pd.DataFrame({
            "time": ["2025-01-01", "2025-01-02"],
            "open": [100, 100], "high": [99, 102],
            "low": [98, 99], "close": [99, 101],
        })
        # Exercise the same validation logic through a temporary CSV without external data.
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.csv"
            frame.to_csv(path, index=False)
            with self.assertRaises(ValueError):
                load_candles("csv", str(path), "5y", 1200)

    def test_csv_requires_input(self):
        with self.assertRaises(ValueError):
            load_candles("csv", None, "5y", 1200)


if __name__ == "__main__":
    unittest.main()
