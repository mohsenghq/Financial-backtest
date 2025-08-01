import pandas as pd
import quantstats as qs
import os
from backtesting import Backtest

def generate_report(
    bt: Backtest,
    stats: pd.Series,
    strategy_name: str,
    asset_name: str, # NEW: To create separate report folders
    output_dir: str = "results"
):
    print(f"\n--- Generating Full Report for {asset_name} ---")
    
    # Create a unique results folder for the strategy and asset
    report_folder = os.path.join(output_dir, strategy_name, asset_name)
    os.makedirs(report_folder, exist_ok=True)
    
    equity_curve = stats['_equity_curve']['Equity']
    
    # QuantStats HTML Report
    report_path = os.path.join(report_folder, "report.html")
    qs.reports.html(
        returns=equity_curve,
        output=report_path,
        title=f'{strategy_name} on {asset_name}'
    )
    print(f"QuantStats report saved to: {report_path}")
    
    # Backtesting.py Interactive Plot
    plot_path = os.path.join(report_folder, "plot.html")
    bt.plot(filename=plot_path, open_browser=False)
    print(f"Interactive plot saved to: {plot_path}")