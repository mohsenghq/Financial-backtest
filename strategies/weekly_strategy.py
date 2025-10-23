from backtesting import Strategy
from backtesting.lib import crossover
import pandas as pd
import numpy as np

def rolling_min(arr: np.ndarray, n: int) -> np.ndarray:
    """
    Helper function to calculate the rolling minimum of a data series.
    """
    series = pd.Series(arr)
    # Use min_periods=1 to get an output even if the window is not full at the start
    return series.rolling(n, min_periods=1).min().values

def rolling_max(arr: np.ndarray, n: int) -> np.ndarray:
    """
    Helper function to calculate the rolling maximum of a data series.
    """
    series = pd.Series(arr)
    # Use min_periods=1 to get an output even if the window is not full at the start
    return series.rolling(n, min_periods=1).max().values

class PriceLevelStrategy(Strategy):
    """
    A mean-reversion strategy that trades based on key price levels derived
    from the min/max of a recent lookback period. It buys on dips and
    sells on rallies within the calculated range.
    """
    # --- Strategy Parameters ---
    lookback_period = 7  # Lookback period in bars (e.g., days)

    def init(self):
        """
        Initialize the indicators for the dynamic price levels.
        """
        if self.lookback_period <= 0:
            raise ValueError("Lookback period must be greater than 0.")
        
        # Calculate the rolling min and max over the lookback period
        self.min_price = self.I(rolling_min, self.data.Close, self.lookback_period)
        self.max_price = self.I(rolling_max, self.data.Close, self.lookback_period)

        # Calculate the total price range
        price_range = self.max_price - self.min_price

        # Define the five important price levels based on the range
        self.level_0   = self.min_price                  # The minimum price
        self.level_25  = self.min_price + price_range * 0.25  # 25% level
        self.level_50  = self.min_price + price_range * 0.50  # 50% level (midpoint)
        self.level_75  = self.min_price + price_range * 0.75  # 75% level
        self.level_100 = self.max_price                 # The maximum price

    def next(self):
        """
        Define the trading logic based on the price crossing key levels.
        """
        # If the price range over the lookback period is zero, do nothing.
        if self.max_price[-1] - self.min_price[-1] == 0:
            return

        # Entry condition: If there's no open position, check for a buy signal.
        # A buy signal occurs if the price crosses BELOW the 25% level,
        # suggesting the asset is oversold relative to its recent range.
        if not self.position:
            if crossover(self.level_25, self.data.Close) or crossover(self.level_0, self.data.Close):
                self.buy()
                self.buyed = True
                self.selled = False
            elif crossover(self.level_75, self.data.Close) or crossover(self.level_100, self.data.Close):
                self.sell()
                self.buyed = False
                self.selled = True

        # Exit condition: If there is an open position, check for a sell signal.
        # A sell signal occurs if the price crosses ABOVE the 75% level,
        # suggesting the asset is overbought and it's a good time to take profit.
        else:
            if (crossover(self.data.Close, self.level_75) or crossover(self.level_100, self.data.Close)) and self.buyed:
                self.position.close()
            elif (crossover(self.data.Close, self.level_25) or crossover(self.level_0, self.data.Close)) and self.selled:
                self.position.close()