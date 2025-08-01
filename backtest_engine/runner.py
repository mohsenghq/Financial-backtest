import pandas as pd
from backtesting import Backtest, Strategy
from .reporting import generate_report

def run_backtest(
    strategy: Strategy,
    data: pd.DataFrame,
    cash: int,
    commission: float,
    params: dict
) -> pd.Series:
    """
    Initializes and runs a backtest with strategy-specific parameters.

    Args:
        strategy (Strategy): The strategy class to be tested.
        data (pd.DataFrame): The OHLCV data for the backtest.
        cash (int): The initial cash amount.
        commission (float): The commission rate for trades.
        params (dict): A dictionary of parameters to pass to the strategy.

    Returns:
        pd.Series: A pandas Series containing the backtest statistics.
    """
    print(f"--- Running Backtest for {strategy.__name__} with params: {params} ---")
    
    bt = Backtest(data, strategy, cash=cash, commission=commission)
    
    # The backtesting library automatically uses the keys from 'params'
    # to set the strategy's attributes (e.g., n1, n2).
    stats = bt.run(**params)
    
    print("\n--- Backtest Results ---")
    print(stats)
    
    generate_report(bt, stats, strategy_name=strategy.__name__)
    
    return stats