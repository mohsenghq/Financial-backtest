import pandas as pd
from backtesting import Backtest, Strategy
from .reporting import generate_report

def run_backtest(
    strategy: Strategy,
    data: pd.DataFrame,
    cash: int = 10000,
    commission: float = 0.002
) -> pd.Series:
    """
    Initializes and runs a backtest, then generates a report.
    """
    print(f"--- Running Backtest for {strategy.__name__} ---")
    
    bt = Backtest(data, strategy, cash=cash, commission=commission)
    
    stats = bt.run()
    
    print("\n--- Backtest Results ---")
    print(stats)
    
    # THE FIX: Pass the entire 'bt' object to the report generator
    generate_report(bt, stats, strategy_name=strategy.__name__)
    
    return stats