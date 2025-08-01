import pandas as pd
from backtesting import Backtest, Strategy
from .reporting import generate_report

def run_backtest(
    strategy: Strategy,
    data: pd.DataFrame,
    cash: int,
    commission: float,
    params: dict,
    asset_name: str # NEW: To pass to the reporter
) -> pd.Series:
    print(f"\n--- Running Backtest for {strategy.__name__} on {asset_name} ---")
    
    bt = Backtest(data, strategy, cash=cash, commission=commission)
    stats = bt.run(**params)
    
    print("\n--- Backtest Results ---")
    print(stats)
    
    generate_report(bt, stats, strategy_name=strategy.__name__, asset_name=asset_name)
    
    return stats