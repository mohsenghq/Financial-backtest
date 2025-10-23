from backtesting import Strategy

class BuyAndHold(Strategy):
    """
    A simple strategy that buys on the first data point it receives
    and holds until the end. This serves as a benchmark.
    """
    def init(self):
        """
        Initialize a flag to track if we have already bought.
        """
        self.bought = False

    def next(self):
        """
        On the first bar we process, buy and set the flag.
        """
        # If we haven't bought yet, buy on the current bar.
        if not self.bought:
            self.buy(size=0.9999999)
            # Set the flag to True to prevent further buying.
            self.bought = True