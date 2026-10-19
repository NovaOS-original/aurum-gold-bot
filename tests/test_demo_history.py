import unittest
from aurum_bot.demo_history import synthetic_history


class DemoHistoryTests(unittest.TestCase):
    def test_builtin_history_has_valid_ohlc_and_metadata_columns(self):
        frame = synthetic_history(250)
        self.assertEqual(len(frame), 250)
        self.assertTrue({"time", "open", "high", "low", "close", "volume"}.issubset(frame.columns))
        self.assertTrue((frame["high"] >= frame[["open", "close", "low"]].max(axis=1)).all())
        self.assertTrue((frame["low"] <= frame[["open", "close", "high"]].min(axis=1)).all())

    def test_small_history_rejected(self):
        with self.assertRaises(ValueError):
            synthetic_history(50)


if __name__ == "__main__":
    unittest.main()
