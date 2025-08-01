from backtesting import Strategy

class BuyAndHold(Strategy):
    """
    A simple strategy that buys on the first data point and holds until the end.
    This serves as a benchmark for other strategies.
    """
    def init(self):
        """
        Called once for the backtest to initialize.
        """
        # Nothing to initialize.
        pass

    def next(self):
        """
        Called on each candlestick of the data.
        """
        # If it's the first bar and we haven't bought yet, buy.
        if len(self.data.Close) == 1:
            self.buy()