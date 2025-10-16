from backtesting import Strategy
from backtesting.lib import crossover
import pandas as pd
import numpy as np


class IchimokuStrategy(Strategy):
    """
    Ichimoku Cloud trading strategy (no pandas_ta).
    - Buy: Price above cloud, Tenkan crosses above Kijun, Chikou > price[-26].
    - Sell: Price below cloud, Tenkan crosses below Kijun, Chikou < price[-26].
    - Stop-loss = Kumo edge, Take-profit = 1.5× risk.
    - ATR filter prevents trading in low-volatility conditions.
    """

    tenkan_period = 9
    kijun_period = 26
    senkou_b_period = 52
    atr_period = 14
    atr_threshold = 0.005  # 0.5%

    def init(self):
        high, low, close = self.data.High, self.data.Low, self.data.Close

        # Tenkan-sen
        self.tenkan = self.I(self._midpoint, high, low, self.tenkan_period)
        # Kijun-sen
        self.kijun = self.I(self._midpoint, high, low, self.kijun_period)
        # Senkou spans (shifted cloud components)
        self.senkou_a = self.I(lambda t, k: (t + k) / 2, self.tenkan, self.kijun)
        self.senkou_b = self.I(self._midpoint, high, low, self.senkou_b_period)
        # Chikou span (lagging)
        self.chikou = self.I(lambda c: np.concatenate([c[self.kijun_period:], np.repeat(np.nan, self.kijun_period)]), close)
        # ATR for volatility filter
        self.atr = self.I(self._atr, high, low, close)

    def _midpoint(self, high, low, period):
        highs = pd.Series(high)
        lows = pd.Series(low)
        out = (highs.rolling(period).max() + lows.rolling(period).min()) / 2
        return out.to_numpy()

    def _atr(self, high, low, close):
        high, low, close = map(pd.Series, (high, low, close))
        prev_close = close.shift(1)
        tr = pd.concat([
            high - low,
            (high - prev_close).abs(),
            (low - prev_close).abs()
        ], axis=1).max(axis=1)
        atr = tr.rolling(self.atr_period).mean()
        return atr.to_numpy()

    def next(self):
        i = -1
        price = self.data.Close[i]
        tenkan = self.tenkan[i]
        kijun = self.kijun[i]
        chikou = self.chikou[i]
        atr = self.atr[i]

        # forward-shifted spans (simulate 26-period projection)
        shift = self.kijun_period
        if len(self.senkou_a) <= shift or len(self.senkou_b) <= shift:
            return
        senkou_a = self.senkou_a[i - shift]
        senkou_b = self.senkou_b[i - shift]

        cloud_top = max(senkou_a, senkou_b)
        cloud_bottom = min(senkou_a, senkou_b)
        in_cloud = cloud_bottom <= price <= cloud_top

        # ATR-based volatility filter
        if atr / price < self.atr_threshold:
            return

        # --- Buy ---
        if not self.position and price > cloud_top and crossover(self.tenkan, self.kijun) and chikou > price:
            stop_loss = cloud_bottom
            risk = price - stop_loss
            take_profit = price + 1.5 * risk
            self.buy(sl=stop_loss, tp=take_profit)

        # --- Sell ---
        elif not self.position and price < cloud_bottom and crossover(self.kijun, self.tenkan) and chikou < price:
            stop_loss = cloud_top
            risk = stop_loss - price
            take_profit = price - 1.5 * risk
            self.sell(sl=stop_loss, tp=take_profit)

        # --- Exit conditions ---
        elif self.position.is_long and (in_cloud or crossover(self.kijun, self.tenkan)):
            self.position.close()
        elif self.position.is_short and (in_cloud or crossover(self.tenkan, self.kijun)):
            self.position.close()
