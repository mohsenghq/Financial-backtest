
import numpy as np
from backtesting import Strategy
from backtesting.lib import crossover

def atr_func(high: np.ndarray, low: np.ndarray, close: np.ndarray, n: int) -> np.ndarray:
    """
    Calculates the Average True Range (ATR) indicator.
    This is a custom implementation as required.
    """
    if not isinstance(high, np.ndarray):
        high = np.array(high)
    if not isinstance(low, np.ndarray):
        low = np.array(low)
    if not isinstance(close, np.ndarray):
        close = np.array(close)

    tr = np.full_like(close, np.nan)
    atr = np.full_like(close, np.nan)

    # Calculate True Range (TR)
    # TR is the greatest of:
    # 1. Current High - Current Low
    # 2. abs(Current High - Previous Close)
    # 3. abs(Current Low - Previous Close)
    tr[1:] = np.maximum(high[1:] - low[1:],
                      np.maximum(np.abs(high[1:] - close[:-1]),
                                 np.abs(low[1:] - close[:-1])))

    # Calculate initial ATR as a simple moving average of the first n TR values
    if len(tr) >= n:
        atr[n - 1] = np.nanmean(tr[1:n])

        # Subsequent ATR values use Wilder's smoothing method (similar to EMA)
        for i in range(n, len(tr)):
            if not np.isnan(tr[i]):
                atr[i] = (atr[i - 1] * (n - 1) + tr[i]) / n

    return atr


class FVGStrategy(Strategy):
    """
    Implements a trading strategy based on Fair Value Gaps (FVG).

    A Fair Value Gap is a three-candle pricing pattern that indicates a market
    inefficiency or imbalance.

    - A Bullish FVG forms when the high of the first candle is lower than the
      low of the third candle, created by a strong upward move in the second candle.
      This gap represents a zone of potential support.

    - A Bearish FVG forms when the low of the first candle is higher than the
      high of the third candle, created by a strong downward move in the second candle.
      This gap represents a zone of potential resistance.

    Strategy Logic:
    1.  Detects new FVGs as they form.
    2.  Monitors active FVGs, which remain valid for a configurable number of bars.
    3.  Waits for the price to "pull back" into a valid FVG zone.
    4.  If price enters a Bullish FVG from above, a long position is opened.
    5.  If price enters a Bearish FVG from below, a short position is opened.
    6.  Positions are managed with a Stop Loss and Take Profit based on a
        multiple of the Average True Range (ATR).
    7.  An FVG is considered "used" after one trade is initiated from it and will
        not be traded again. It is invalidated if price trades completely through it.
    """
    # --- Strategy Parameters ---
    atr_period = 14
    sl_atr_multiplier = 2.0
    tp_atr_multiplier = 4.0
    fvg_expiry = 15  # FVG is considered valid for this many bars after creation

    def init(self):
        """
        Initialize the strategy, indicators, and state variables.
        """
        # Calculate ATR using the custom implementation
        self.atr = self.I(atr_func, self.data.High, self.data.Low, self.data.Close, self.atr_period)

        # List to store active FVG dictionaries
        self.active_fvgs = []

    def next(self):
        """
        The main strategy logic, executed on each bar of data.
        """
        # Ensure we have enough data and a valid ATR value to proceed
        if len(self.data.Close) < self.atr_period or np.isnan(self.atr[-1]):
            return

        current_index = len(self.data.Close) - 1
        
        # --- 1. FVG Management: Clean up old/invalidated FVGs ---
        fvgs_to_keep = []
        for fvg in self.active_fvgs:
            is_expired = current_index > fvg['created_at'] + self.fvg_expiry
            is_invalidated = False

            if fvg['type'] == 'bullish':
                # Invalidated if a candle's low trades completely below the gap
                if self.data.Low[-1] < fvg['bottom']:
                    is_invalidated = True
            elif fvg['type'] == 'bearish':
                # Invalidated if a candle's high trades completely above the gap
                if self.data.High[-1] > fvg['top']:
                    is_invalidated = True

            if not fvg['used'] and not is_expired and not is_invalidated:
                fvgs_to_keep.append(fvg)
        self.active_fvgs = fvgs_to_keep


        # --- 2. FVG Detection: Look for new FVGs ---
        # We need at least 3 bars to form a pattern
        if len(self.data.Close) < 3:
            return

        # Check for Bullish FVG
        # High of candle[-3] is lower than the Low of candle[-1]
        if self.data.High[-3] < self.data.Low[-1]:
            # Check if this FVG is substantially different from the last one
            is_new = True
            if self.active_fvgs and self.active_fvgs[-1]['type'] == 'bullish':
                if abs(self.active_fvgs[-1]['bottom'] - self.data.High[-3]) < 1e-9:
                    is_new = False # Avoid adding overlapping FVGs
            if is_new:
                fvg = {
                    'type': 'bullish',
                    'top': self.data.Low[-1],
                    'bottom': self.data.High[-3],
                    'created_at': current_index,
                    'used': False
                }
                self.active_fvgs.append(fvg)

        # Check for Bearish FVG
        # Low of candle[-3] is higher than the High of candle[-1]
        if self.data.Low[-3] > self.data.High[-1]:
            is_new = True
            if self.active_fvgs and self.active_fvgs[-1]['type'] == 'bearish':
                 if abs(self.active_fvgs[-1]['top'] - self.data.Low[-3]) < 1e-9:
                    is_new = False
            if is_new:
                fvg = {
                    'type': 'bearish',
                    'top': self.data.Low[-3],
                    'bottom': self.data.High[-1],
                    'created_at': current_index,
                    'used': False
                }
                self.active_fvgs.append(fvg)

        # --- 3. Trade Execution ---
        # Do not open a new trade if a position is already open
        if self.position:
            return

        for fvg in self.active_fvgs:
            if fvg['used']:
                continue

            # Bullish Entry Condition:
            # Price was previously above the FVG and the current candle's low has entered it.
            if fvg['type'] == 'bullish':
                # Check for pullback into the FVG zone
                if len(self.data.Close) > 3 and self.data.Low[-2] > fvg['top'] and self.data.Low[-1] <= fvg['top']:
                    sl = self.data.Close[-1] - self.atr[-1] * self.sl_atr_multiplier
                    tp = self.data.Close[-1] + self.atr[-1] * self.tp_atr_multiplier
                    self.buy(sl=sl, tp=tp)
                    fvg['used'] = True  # Mark FVG as used
                    break  # Exit loop after placing a trade

            # Bearish Entry Condition:
            # Price was previously below the FVG and the current candle's high has entered it.
            elif fvg['type'] == 'bearish':
                # Check for pullback into the FVG zone
                if len(self.data.Close) > 3 and self.data.High[-2] < fvg['bottom'] and self.data.High[-1] >= fvg['bottom']:
                    sl = self.data.Close[-1] + self.atr[-1] * self.sl_atr_multiplier
                    tp = self.data.Close[-1] - self.atr[-1] * self.tp_atr_multiplier
                    self.sell(sl=sl, tp=tp)
                    fvg['used'] = True  # Mark FVG as used
                    break  # Exit loop after placing a trade
