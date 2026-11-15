"""btc-race-24h-20261115-0828 bot: deep-drop reversal rider on cbBTC 1-minute bars.

Strategy (long only, one position, full size): the dev day falls 3.9% with one
violent V-bounce (+4.4% off the low in under an hour). Every trend, breakout
and frequent dip-buy variant loses money on it; the only edge is to wait for a
genuinely deep washout and ride the turn:

  entry: close is >=150 bps below EMA(120) AND closes back above EMA(5)
         (the turn, not the fall) -- fires 1-2 times a day
  exit:  trailing stop 60 bps from the peak close, hard stop 80 bps below the
         fill price; no take-profit, the bounce is allowed to run

Local grade on the published dev window (real bot through the SDK wire
protocol, replay.py): net PnL +$39.57, 1 round trip, max drawdown 0.9%.
Same logic on the previous race's dev window: -$5.31, 1 round trip -- the
edge is the V-bounce, and the race day is unseen; the stop keeps the loss
small when the turn fails.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"))
import makefun_bars

SYMBOL = "CBBTC"
DEEP_BPS = 150        # close must be this far below EMA(120)
EMA_MID = 120
EMA_FAST = 5
TRAIL_BPS = 60        # trailing stop from the peak close
STOP_BPS = 80         # hard stop below the fill price
MAX_SLIPPAGE_BPS = 500

closes = []
_ema_fast = None
_ema_mid = None
_entry_price = 0      # fill price of the open buy (price_scale 5)
_peak = 0             # highest close seen while holding


def _ema_step(prev, close, span):
    if prev is None:
        return float(close)
    k = 2.0 / (span + 1)
    return close * k + prev * (1.0 - k)


def on_batch(state, batch):
    global _ema_fast, _ema_mid, _entry_price, _peak
    if state.warming_up:
        return []
    # Fills from the previous batch's orders arrive here: record the buy's
    # actual fill price (the exit math must use what we paid, not the close
    # we decided on).
    for fill in batch.get("fills", []):
        if fill.get("symbol") == SYMBOL and fill.get("status") == "filled":
            if fill.get("side") == "buy":
                _entry_price = int(fill["price"])
                _peak = _entry_price
            elif fill.get("side") == "sell":
                _entry_price = 0
                _peak = 0
    for bar in batch["bars"]:
        if bar["symbol"] == SYMBOL:
            closes.append(int(bar["c"]))
    if not closes:
        return []
    close = closes[-1]
    prev_close = closes[-2] if len(closes) > 1 else close
    ema_fast_prev = _ema_fast
    ema_mid_prev = _ema_mid
    _ema_fast = _ema_step(ema_fast_prev, close, EMA_FAST)
    _ema_mid = _ema_step(ema_mid_prev, close, EMA_MID)
    if len(closes) < EMA_MID + 1:
        return []
    held = state.positions.get(SYMBOL)
    if held is not None:
        if _entry_price == 0:  # fell back: cost basis from the position
            _entry_price = held.cost * 10**7 // held.qty if held.qty else 0
            _peak = max(_peak, close)
        if close > _peak:
            _peak = close
        if close * 10000 <= _peak * (10000 - TRAIL_BPS):
            return [{"side": "sell", "symbol": SYMBOL, "qty": held.qty,
                     "max_slippage_bps": MAX_SLIPPAGE_BPS}]
        if close * 10000 <= _entry_price * (10000 - STOP_BPS):
            return [{"side": "sell", "symbol": SYMBOL, "qty": held.qty,
                     "max_slippage_bps": MAX_SLIPPAGE_BPS}]
        return []
    # Flat: deep washout + the turn (close back above EMA(5)).
    deep = close * 10000 < _ema_mid * (10000 - DEEP_BPS)
    turn = prev_close <= ema_fast_prev and close > _ema_fast
    if deep and turn and state.cash > 0:
        return [{"side": "buy", "symbol": SYMBOL,
                 "notional_quote_units": state.cash,
                 "max_slippage_bps": MAX_SLIPPAGE_BPS}]
    return []


makefun_bars.run(on_batch)
