# Browser backtest manual regression checklist

- [ ] Load built-in Yahoo history; verify source label identifies real provider data.
- [ ] If provider request fails, verify no synthetic fallback is silently substituted.
- [ ] Load synthetic fixture; verify it is explicitly labelled synthetic in the result.
- [ ] Run backtest with valid parameters and verify only the final selected chronological holdout is scored.
- [ ] Change spread, slippage, or commission upward; net P/L should not improve solely because costs increased.
- [ ] Verify stop is assumed first if both stop and target are touched in one candle.
- [ ] Confirm live/demo order placement remains unavailable.

These checks are manual; automated browser testing is not configured in this repository yet.
