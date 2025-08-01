from backtesting import Strategy
from backtesting.lib import crossover
import pandas_ta as ta
import pandas as pd

class SmaCross(Strategy):
    """
    A simple strategy that buys when a short-term SMA crosses
    above a long-term SMA and sells when the opposite occurs.
    """
    n1 = 10  # Short-term moving average period
    n2 = 20  # Long-term moving average period

    def init(self):
        """
        Called once for the backtest to initialize indicators.
        """
        # Convert Close to pandas Series for pandas_ta compatibility
        close = pd.Series(self.data.Close, index=self.data.index)
        self.sma1 = self.I(ta.sma, close, length=self.n1)
        self.sma2 = self.I(ta.sma, close, length=self.n2)

    def next(self):
        """
        Called on each candlestick of the data.
        This is where the trading logic resides.
        """
        if crossover(self.sma1, self.sma2):
            self.buy()
        elif crossover(self.sma2, self.sma1):
            self.position.close()