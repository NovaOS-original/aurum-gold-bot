import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "site" / "index.html"


class FrontendContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = HTML.read_text(encoding="utf-8")
        scripts = re.findall(r"<script(?:\s[^>]*)?>(.*?)</script>", cls.html, re.S | re.I)
        cls.script = "\n".join(scripts)

    def test_original_chart_and_required_controls_are_present(self):
        lowered = self.html.lower()
        self.assertNotIn("lightweight-charts", lowered)
        self.assertNotIn("tradingview", lowered)
        for token in ("class NanaChart", "function loadHistory", "function refreshOverlays",
                      "function runBacktest", "function exportCSV", "function replayAdvanceTo", "function replayCheckCandle", "function placeReplaySetup", "function prepareReplay"):
            self.assertIn(token, self.script)
        for element_id in ("mainChart", "rsiChart", "equityChart", "load", "run",
                           "tradeRows", "indicatorRows", "sourceLabel", "export", "replayProgress", "replayPlay", "replayStep", "replayReset", "setupSide", "setupEntry", "setupSL", "setupTP", "placeSetup", "cancelSetup", "ema9", "ema21", "bb", "rsiToggle"):
            self.assertIn(f'id="{element_id}"', self.html)

    def test_real_market_provider_is_explicit_and_no_fake_fallback(self):
        self.assertIn("https://xaus.com/api/v1/chart", self.script)
        self.assertIn("Free XAUS history service could not return enough real candles", self.script)
        self.assertIn("XAUS Gold Data API", self.script)

    @unittest.skipUnless(shutil.which("node"), "Node.js is not installed")
    def test_inline_javascript_syntax(self):
        with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8") as tmp:
            tmp.write(self.script)
            tmp.flush()
            result = subprocess.run(["node", "--check", tmp.name], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
