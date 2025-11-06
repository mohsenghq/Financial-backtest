from backtesting import Strategy
from backtesting.lib import crossover
from finta import TA
import pandas as pd
import numpy as np

class SmaCross(Strategy):
    """
    A simple strategy that buys when a short-term SMA crosses
    above a long-term SMA and sells when the opposite occurs.
    """
    n1 = 10  # Short-term moving average period
    n2 = 20  # Long-term moving average period

    @classmethod
    def get_optimization_ranges(cls):
        return {
            'n1': {'min': 5, 'max': 15, 'step': 5},
            'n2': {'min': 15, 'max': 30, 'step': 5}
        }

    def init(self):
        """
        Called once for the backtest to initialize indicators.
        """
        # Convert Close to pandas Series for finta compatibility
        close = pd.Series(self.data.Close, index=self.data.index)
        ohlc_data = pd.DataFrame({
            'open': np.zeros_like(close),
            'high': np.zeros_like(close),
            'low': np.zeros_like(close),
            'close': close
        })
        self.sma1 = self.I(TA.SMA, ohlc_data, self.n1)
        self.sma2 = self.I(TA.SMA, ohlc_data, self.n2)

    def next(self):
        """
        Called on each candlestick of the data.
        This is where the trading logic resides.
        """
        if crossover(self.sma1, self.sma2):
            self.buy()
        elif crossover(self.sma2, self.sma1):
            self.position.close()