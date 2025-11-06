from backtesting import Strategy
from backtesting.lib import crossover
from finta import TA
import numpy as np
import pandas as pd

def _rsi(arr: np.ndarray, n: int) -> np.ndarray:
    """
    Wrapper for finta RSI to handle data conversion.
    """
    close_series = pd.Series(arr)
    ohlc_data = pd.DataFrame({
        'open': np.zeros_like(close_series),
        'high': np.zeros_like(close_series),
        'low': np.zeros_like(close_series),
        'close': close_series
    })
    rsi_values = TA.RSI(ohlc_data, period=n)
    if rsi_values is None:
        return np.full(arr.shape, np.nan)
    return rsi_values.values

class RsiMomentum(Strategy):
    """
    A momentum strategy that buys on oversold signals from the RSI
    and sells on overbought signals.
    """
    # --- Strategy Parameters ---
    upper_bound = 70
    lower_bound = 30
    rsi_period = 14

    @classmethod
    def get_optimization_ranges(cls):
        return {
            'upper_bound': {'min': 60, 'max': 85, 'step': 5},
            'lower_bound': {'min': 15, 'max': 40, 'step': 5},
            'rsi_period': {'min': 7, 'max': 21, 'step': 7}
        }

    def init(self):
        """
        Initialize the RSI indicator.
        """
        self.rsi = self.I(_rsi, self.data.Close, self.rsi_period)

    def next(self):
        """
        Define the trading logic.
        """
        # If RSI crosses below the lower bound, it's oversold - a buy signal.
        if crossover(self.lower_bound, self.rsi):
            self.buy()
        
        # If RSI crosses above the upper bound, it's overbought - a sell signal.
        elif crossover(self.rsi, self.upper_bound):
            self.position.close()