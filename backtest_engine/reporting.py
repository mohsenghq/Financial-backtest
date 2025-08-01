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
    Generates and saves a full backtest report. If the strategy is not
    'BuyAndHold', it includes a comparison against a Buy & Hold benchmark.
    """
    print(f"\n--- Generating Full Report for {asset_name} ---")
    
    report_folder = os.path.join(output_dir, strategy_name, asset_name)
    os.makedirs(report_folder, exist_ok=True)
    
    equity_curve = stats['_equity_curve']['Equity']
    report_path = os.path.join(report_folder, "report.html")

    # --- THE FIX: Conditional Benchmark ---
    # Only add the benchmark if the strategy is NOT BuyAndHold
    if strategy_name == 'BuyAndHold':
        qs.reports.html(
            returns=equity_curve,
            output=report_path,
            title=f'{strategy_name} Performance on {asset_name}'
        )
    else:
        # For all other strategies, calculate and add the benchmark
        close_prices = bt._data.Close
        benchmark_returns = close_prices.pct_change().fillna(0)
        benchmark_returns.name = "Buy and Hold"
        
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