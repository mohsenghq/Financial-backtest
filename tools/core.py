import yaml
import importlib
import pandas as pd
import os
from backtest_engine.data_loader import load_data
from backtest_engine.feature_generator import add_features
from backtest_engine.runner import run_backtest
from tools.optimizer import StrategyOptimizer

def save_results_for_dashboard(stats: pd.Series, strategy_name: str, asset_name: str, log_callback=print):
    """Saves the necessary backtest output for the dashboard."""
    results_dir = os.path.join("results", strategy_name, asset_name)
    os.makedirs(results_dir, exist_ok=True)

    equity_curve = stats['_equity_curve']
    equity_curve.to_json(os.path.join(results_dir, "equity_curve.json"))

    summary_stats = stats.drop(['_equity_curve', '_trades', '_strategy'])
    summary_stats.to_json(os.path.join(results_dir, "summary_stats.json"))
    log_callback(f"Dashboard data saved for {strategy_name} on {asset_name}")


def run_backtests_from_config(config: dict, log_callback=print):
    """
    Runs the backtesting process based on a given configuration dictionary.
    This function is designed to be called from different interfaces (CLI, UI).
    """
    settings = config['backtest_settings']
    strategies_to_run = config['strategies']
    assets_to_run = config.get('assets_to_run', []) # Get specific assets or all
    errors = []

    all_market_data = load_data(settings['data_source'])
    if not all_market_data:
        log_callback("No data loaded. Exiting.")
        return ["No data loaded."]

    # If no specific assets are requested, run on all available data
    if not assets_to_run:
        assets_to_run = list(all_market_data.keys())

    # --- Loop through all selected assets ---
    for asset_name in assets_to_run:
        if asset_name not in all_market_data:
            log_callback(f"Warning: Data for asset '{asset_name}' not found. Skipping.")
            continue

        market_data = all_market_data[asset_name]
        log_callback(f"\n{'='*20} Processing Asset: {asset_name} {'='*20}")

        # --- Loop through all strategies for the current asset ---
        for strategy_config in strategies_to_run:
            strategy_name = strategy_config['name']
            try:
                strategy_file = strategy_config['file']
                params = strategy_config.get('params', {})
                optimize = strategy_config.get('optimize', False)
                param_ranges = strategy_config.get('param_ranges', {})

                module = importlib.import_module(f"strategies.{strategy_file}")
                StrategyClass = getattr(module, strategy_name)

                features_df = add_features(market_data.copy())
                optimizer = StrategyOptimizer(StrategyClass, features_df[:len(features_df)// 2])

                if optimize:
                    log_callback(f"Optimizing {strategy_name} on {asset_name}...")
                    best_params, heatmap_df = optimizer.optimize(param_ranges)
                    heatmap_path = os.path.join(f"results/{strategy_name}/{asset_name}", "heatmap.html")
                    optimizer.save_heatmap_html(heatmap_df, heatmap_path)
                    optimizer.set_optimized_params(strategy_name, asset_name, best_params)
                    params = best_params
                else:
                    optimized_params = optimizer.get_optimized_params(strategy_name, asset_name)
                    if optimized_params:
                        log_callback(f"Using optimized parameters for {strategy_name} on {asset_name}: {optimized_params}")
                        params = optimized_params

                stats = run_backtest(
                    strategy=StrategyClass, data=features_df, cash=settings['initial_cash'],
                    commission=settings['commission_pct'], params=params, asset_name=asset_name
                )

                save_results_for_dashboard(stats, strategy_name, asset_name, log_callback=log_callback)

            except Exception as e:
                error_msg = f"!!! ERROR processing {strategy_name} on {asset_name}: {e} !!!"
                log_callback(error_msg)
                errors.append(error_msg)
                continue
    return errors

def main(config_path: str):
    """Main function to run multiple backtests based on a config file."""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: Configuration file not found at {config_path}")
        return

    # The core logic is now in a separate, callable function
    errors = run_backtests_from_config(config)
    if errors:
        print("\n--- ERRORS OCCURRED ---")
        for error in errors:
            print(error)

if __name__ == "__main__":
    main('config.yaml')