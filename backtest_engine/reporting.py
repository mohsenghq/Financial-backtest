import pandas as pd
import quantstats as qs
import os
from backtesting import Backtest # Import Backtest for type hinting

def generate_report(
    bt: Backtest, # Add the Backtest object as an argument
    stats: pd.Series,
    strategy_name: str,
    output_dir: str = "results"
):
    """
    Generates and saves a full backtest report.

    Args:
        bt (Backtest): The Backtest object after running.
        stats (pd.Series): The statistics Series from the run.
        strategy_name (str): The name of the strategy tested.
        output_dir (str): The directory to save the reports in.
    """
    print("\n--- Generating Full Report ---")
    
    trades = stats['_trades']
    
    report_folder = os.path.join(output_dir, strategy_name)
    os.makedirs(report_folder, exist_ok=True)
    
    # --- Generate QuantStats HTML Report ---
    equity_curve = stats['_equity_curve']['Equity']
    report_path = os.path.join(report_folder, "report.html")
    
    qs.reports.html(
        returns=equity_curve,
        output=report_path,
        title=f'{strategy_name} Performance'
    )
    
    print(f"QuantStats report saved to: {report_path}")
    
    # --- Save the backtesting.py plot ---
    # THE FIX: Call plot() directly on the Backtest object
    plot_path = os.path.join(report_folder, "plot.html")
    bt.plot(filename=plot_path, open_browser=False)
    print(f"Interactive plot saved to: {plot_path}")