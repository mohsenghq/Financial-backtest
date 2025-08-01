from backtesting import Strategy
from backtesting.lib import crossover
import pandas_ta as ta
import numpy as np
import pandas as pd

def _rsi(arr: np.ndarray, n: int) -> np.ndarray:
    """
    Wrapper for pandas-ta RSI to handle data conversion.
    """
    close_series = pd.Series(arr)
    rsi_values = ta.rsi(close=close_series, length=n)
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