# btc-race-24h-20261115-0828

[![make.fun · btc-race-24h-20261115-0828](https://make.fun/badge/btc-race-24h-20261115-0828.svg)](https://make.fun/bounty/btc-race-24h-20261115-0828?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261115-0828)
[![rank](https://make.fun/badge/btc-race-24h-20261115-0828/Endijuan33/btc-race-24h-20261115-0828/rank.svg)](https://make.fun/bounty/btc-race-24h-20261115-0828/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261115-0828)
[![reward](https://make.fun/badge/btc-race-24h-20261115-0828/Endijuan33/btc-race-24h-20261115-0828/reward.svg)](https://make.fun/bounty/btc-race-24h-20261115-0828?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261115-0828)

A bot that trades Coinbase Wrapped BTC (cbBTC) on 1-minute on-chain prices with $1,000 of paper money, for the [make.fun bounty](https://make.fun/bounty/btc-race-24h-20261115-0828): **Race a BTC trading bot live for 24 hours** ($250).

## Strategy: deep-drop reversal rider

The dev day falls 3.9% with one violent V-bounce (+4.4% off the low in under an hour). Every trend, breakout and frequent dip-buy variant loses money on it; the only edge is to wait for a genuinely deep washout and ride the turn:

- **Entry:** close is ≥150 bps below EMA(120) **and** closes back above EMA(5) — the turn, not the fall. Fires 1–2 times a day.
- **Exit:** trailing stop 60 bps from the peak close, hard stop 80 bps below the fill price. No take-profit — the bounce is allowed to run.
- Long only, one position, full size, max slippage 500 bps. Pure Python stdlib; the kit's `makefun_bars` SDK shim is vendored under `vendor/`.

## Local grade (published dev window, real bot through the SDK wire protocol)

- **Net PnL +$39.57** on $1,000 (passes the >$0 dev gate), 1 round trip (buy $62,406.27 → sell $64,927.49), max drawdown 0.88%.
- Deterministic: two identical replays, byte-identical fills.
- Same logic on the previous race's dev window: −$5.31, 1 round trip — the edge is the V-bounce and the race day is unseen; the stop keeps the loss small when the turn fails.
