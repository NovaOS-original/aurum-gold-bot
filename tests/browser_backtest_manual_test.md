# Browser regression checklist: history, backtest and market replay

- [ ] Open the public tester and confirm the original NanaForex canvas chart renders without a TradingView script, logo or attribution.
- [ ] Load real XAUS XAUUSD history for 1d/1mo and confirm the source, candle count and UTC date range are shown.
- [ ] Change history range and timeframe; confirm the displayed candles and dataset label update.
- [ ] If XAUS fails, confirm the optional configured API fallback is used; if neither provider works, confirm the error is visible and no synthetic data is silently substituted.
- [ ] Switch between Candles and Line; verify both views use the same loaded history.
- [ ] Toggle EMA 9, EMA 21, SMA 50, Bollinger Bands and RSI; verify overlays appear/disappear without clearing candles.
- [ ] Zoom with the mouse wheel and pan by dragging; use Fit chart / Reset zoom to restore the view.
- [ ] Start market replay; confirm the chart initially shows only candles up to the replay cursor, not future candles.
- [ ] Pause, step one candle, restart, change speed and scrub forward; confirm date, price and candle count update.
- [ ] Place a BUY setup with SL below entry and TP above entry; verify invalid level ordering is rejected.
- [ ] Place a SELL setup with TP below entry and SL above entry; verify invalid level ordering is rejected.
- [ ] Confirm a setup is pending until a later candle reaches entry; the candle present when the setup is placed must not fill it.
- [ ] Confirm an open BUY closes on SL when low reaches SL or TP when high reaches TP; reverse conditions for SELL.
- [ ] If TP and SL are both touched in the same candle, confirm the conservative stop-first rule.
- [ ] Confirm entry, stop and target price levels and setup/fill/exit markers are visible on the chart.
- [ ] Confirm pause/resume and playback speed do not skip candles; replay end stops playback without fabricating a trade result.
- [ ] Run a strategy backtest after replay; confirm it restores the complete history and scores the chronological holdout.
- [ ] Verify backtest metrics, trade log, indicator values and equity curve populate.
- [ ] Export candles during replay and confirm CSV contains the complete loaded dataset, not only candles revealed so far.
- [ ] Confirm all replay setups are simulated only; no broker connection, order routing or live trading is available.

These checks require a real browser and a successful public-provider response. CI also performs source-contract and JavaScript syntax checks.
