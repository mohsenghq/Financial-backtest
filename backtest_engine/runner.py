import pandas as pd
from backtesting import Backtest, Strategy
from .reporting import generate_report

def run_backtest(
    strategy: Strategy,
    data: pd.DataFrame,
    cash: int,
    commission: float,
    params: dict,
    asset_name: str
) -> pd.Series: # It already returns the stats, which is perfect
    """
    Initializes and runs a backtest, generates a report, and returns the stats.
    """
    print(f"\n--- Running Backtest for {strategy.__name__} on {asset_name} ---")

    # Create a wrapper class to close positions on the last bar
    class StrategyWrapper(strategy):
        def next(self):
            # First, execute the original strategy's logic
            super().next()

            # If it's the last bar, close any open position
            if len(self.data) == len(self.data.df) and strategy.__name__ != 'BuyAndHold':
                self.position.close()

    # Preserve the original strategy name for reporting
    StrategyWrapper.__name__ = strategy.__name__
    
    bt = Backtest(data, StrategyWrapper, cash=cash, commission=commission)
    
    try:
        stats = bt.run(**params)
    except ValueError as e:
        if "Cannot calculate a linear regression" in str(e):
            print(f"Warning: Could not compute stats for {asset_name} with {strategy.__name__}. "
                  f"This is likely due to no trades being executed. Error: {e}")
            
            # Create a default stats series that matches the structure of the backtesting library's output
            stats_data = {
                'Start': data.index[0],
                'End': data.index[-1],
                'Duration': data.index[-1] - data.index[0],
                'Exposure Time [%]': 0,
                'Equity Final [$]': cash,
                'Equity Peak [$]': cash,
                'Return [%]': 0,
                # 'Buy & Hold Return [%]': (data['Close'].iloc[-1] - data['Close'].iloc[0]) / data['Close'].iloc[0] * 100,
                'Return (Ann.) [%]': 0,
                'Volatility (Ann.) [%]': 0,
                'Sharpe Ratio': 0,
                'Sortino Ratio': 0,
                'Calmar Ratio': 0,
                'Max. Drawdown [%]': 0,
                'Avg. Drawdown [%]': 0,
                'Max. Drawdown Duration': pd.Timedelta(0),
                'Avg. Drawdown Duration': pd.Timedelta(0),
                '# Trades': 0,
                'Win Rate [%]': 0,
                'Best Trade [%]': 0,
                'Worst Trade [%]': 0,
                'Avg. Trade [%]': 0,
                'Max. Trade Duration': pd.Timedelta(0),
                'Avg. Trade Duration': pd.Timedelta(0),
                'Profit Factor': 0,
                'Expectancy [%]': 0,
                'SQN': 0,
                '_strategy': strategy(**params),
                '_equity_curve': pd.DataFrame({'Equity': [cash] * len(data.index)}, index=data.index),
                '_trades': pd.DataFrame()
            }
            stats = pd.Series(stats_data)
        else:
            raise e  # Re-raise other ValueErrors
    
    print("\n--- Backtest Results ---")
    print(stats)
    
    # This part remains, generating the individual HTML reports
    generate_report(bt, stats, strategy_name=strategy.__name__, asset_name=asset_name)
    
    return stats # We will use these returned stats