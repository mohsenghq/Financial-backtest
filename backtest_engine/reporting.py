import pandas as pd
import quantstats as qs
import os
from backtesting import Backtest

def generate_report(
    bt: Backtest,
    stats: pd.Series,
    strategy_name: str,
    asset_name: str,
    output_dir: str = "results"
):
    """
    Generates and saves a full backtest report, including a
    comparison against a Buy & Hold benchmark.
    """
    print(f"\n--- Generating Full Report for {asset_name} ---")
    
    report_folder = os.path.join(output_dir, strategy_name, asset_name)
    os.makedirs(report_folder, exist_ok=True)
    
    equity_curve = stats['_equity_curve']['Equity']
    
    # --- Calculate Benchmark Returns (Buy & Hold) ---
    close_prices = bt._data.Close
    benchmark_returns = close_prices.pct_change().fillna(0)
    
    # --- THE FIX: Rename the benchmark Series for the plot legend ---
    benchmark_returns.name = "Buy and Hold"
    
    # --- Generate QuantStats HTML Report with Benchmark ---
    report_path = os.path.join(report_folder, "report.html")
    
    qs.reports.html(
        returns=equity_curve,
        benchmark=benchmark_returns,
        output=report_path,
        title=f'{strategy_name} vs. Buy & Hold on {asset_name}'
    )
    print(f"QuantStats report saved to: {report_path}")
    
    # --- Save the backtesting.py plot ---
    plot_path = os.path.join(report_folder, "plot.html")
    bt.plot(filename=plot_path, open_browser=False)
    print(f"Interactive plot saved to: {plot_path}")