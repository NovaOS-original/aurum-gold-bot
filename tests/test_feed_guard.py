import unittest
from datetime import datetime, timezone, timedelta
from aurum_bot.feed_guard import validate_candle, validate_spread


class FeedGuardTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 10, 19, 12, 0, tzinfo=timezone.utc)
        self.candle = {
            "time": (self.now - timedelta(seconds=30)).isoformat(),
            "open": 2700, "high": 2710, "low": 2690, "close": 2705,
        }

    def test_fresh_valid_candle_passes(self):
        result = validate_candle(self.candle, now=self.now)
        self.assertTrue(result.ok)
        self.assertEqual(result.reasons, ())

    def test_stale_candle_fails_closed(self):
        old = dict(self.candle, time=(self.now - timedelta(minutes=10)).isoformat())
        result = validate_candle(old, now=self.now)
        self.assertFalse(result.ok)
        self.assertIn("stale_candle", result.reasons)

    def test_timezone_naive_timestamp_rejected(self):
        naive = dict(self.candle, time="2026-10-19T11:59:00")
        self.assertFalse(validate_candle(naive, now=self.now).ok)

    def test_inconsistent_ohlc_rejected(self):
        bad = dict(self.candle, high=2700)
        self.assertIn("inconsistent_high", validate_candle(bad, now=self.now).reasons)

    def test_wide_spread_rejected(self):
        result = validate_spread(bid=2700, ask=2701, max_spread=0.5)
        self.assertFalse(result.ok)
        self.assertIn("spread_too_wide", result.reasons)

    def test_crossed_quote_rejected(self):
        self.assertIn("crossed_quote", validate_spread(
            bid=2701, ask=2700, max_spread=2).reasons)


if __name__ == "__main__":
    unittest.main()
