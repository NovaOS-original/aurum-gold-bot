# Browser backtest regression checklist

- [ ] Open the public tester and confirm the original NanaForex canvas chart renders without a TradingView script, logo or attribution.
- [ ] Load real XAUS XAUUSD history for 1d/1mo and confirm the source, candle count and UTC date range are shown.
- [ ] Change history range and timeframe; confirm the displayed candles and dataset label update.
- [ ] If XAUS fails, confirm the optional configured API fallback is used; if neither provider works, confirm the error is visible and no synthetic data is silently substituted.
- [ ] Switch between Candles and Line; verify both views use the same loaded history.
- [ ] Toggle EMA 9, EMA 21, SMA 50, Bollinger Bands and RSI; verify overlays appear/disappear without clearing candles.
- [ ] Zoom with the mouse wheel and pan by dragging; use Fit chart / Reset zoom to restore the view.
- [ ] Run a valid strategy test and confirm the holdout is chronological and earlier candles are only used for indicator warm-up.
- [ ] Verify Net P/L, win rate, closed trades, profit factor, max drawdown, ending balance, average trade and test-candle count update.
- [ ] Verify the trade log, indicator values and equity curve populate and trade markers align with entry candles.
- [ ] Increase spread, slippage or commission; net P/L must not improve solely because costs increased.
- [ ] Verify stop is assumed first when stop and target are both touched in one candle.
- [ ] Export candles as CSV and confirm the file contains time, OHLC and volume columns.
- [ ] Confirm live/demo order placement remains unavailable.

These checks require a real browser and a successful public-provider response; CI also performs source-contract and JavaScript syntax checks.
