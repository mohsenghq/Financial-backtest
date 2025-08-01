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
    
    bt = Backtest(data, strategy, cash=cash, commission=commission)
    stats = bt.run(**params)
    
    print("\n--- Backtest Results ---")
    print(stats)
    
    # This part remains, generating the individual HTML reports
    generate_report(bt, stats, strategy_name=strategy.__name__, asset_name=asset_name)
    
    return stats # We will use these returned stats