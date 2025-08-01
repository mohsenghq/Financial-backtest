import yaml
import importlib
import pandas as pd
import os
from backtest_engine.data_loader import load_data
from backtest_engine.feature_generator import add_features
from backtest_engine.runner import run_backtest

def save_results_for_dashboard(stats: pd.Series, strategy_name: str, asset_name: str):
    """Saves the necessary backtest output for the dashboard."""
    results_dir = os.path.join("results", strategy_name, asset_name)
    os.makedirs(results_dir, exist_ok=True)

    equity_curve = stats['_equity_curve']
    equity_curve.to_json(os.path.join(results_dir, "equity_curve.json"))

    summary_stats = stats.drop(['_equity_curve', '_trades', '_strategy'])
    summary_stats.to_json(os.path.join(results_dir, "summary_stats.json"))
    print(f"Dashboard data saved for {strategy_name} on {asset_name}")


def main(config_path: str):
    """Main function to run multiple backtests based on a config file."""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: Configuration file not found at {config_path}")
        return

    settings = config['backtest_settings']
    strategies_to_run = config['strategies']

    all_market_data = load_data(settings['data_source'])
    if not all_market_data:
        print("No data loaded. Exiting.")
        return

    mode = settings.get('backtest_mode', 'single')

    # This outer loop handles portfolio mode if you ever use it
    if mode == 'portfolio':
         # This logic can be expanded later if needed
        print("Portfolio mode processing can be implemented here.")
        pass
    else: # Default to 'single' mode
        # --- Loop through all assets ---
        for asset_name, market_data in all_market_data.items():
            print(f"\n{'='*20} Processing Asset: {asset_name} {'='*20}")

            # --- Loop through all strategies for the current asset ---
            for strategy_config in strategies_to_run:
                strategy_name = strategy_config['name']
                try:
                    strategy_file = strategy_config['file']
                    params = strategy_config.get('params', {}) # Use .get for safety

                    # Import the strategy class
                    module = importlib.import_module(f"strategies.{strategy_file}")
                    StrategyClass = getattr(module, strategy_name)

                    # Prepare data and run backtest
                    features_df = add_features(market_data.copy())
                    stats = run_backtest(
                        strategy=StrategyClass, data=features_df, cash=settings['initial_cash'],
                        commission=settings['commission_pct'], params=params, asset_name=asset_name
                    )

                    save_results_for_dashboard(stats, strategy_name, asset_name)

                except Exception as e:
                    print(f"!!! ERROR processing {strategy_name} on {asset_name}: {e} !!!")
                    continue

if __name__ == "__main__":
    main('config.yaml')