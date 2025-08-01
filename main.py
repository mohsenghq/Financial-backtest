import yaml
import importlib
import pandas as pd
from backtest_engine.data_loader import load_data
from backtest_engine.feature_generator import add_features
from backtest_engine.runner import run_backtest

def main(config_path: str):
    """Main function to run the backtesting process based on a config file."""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: Configuration file not found at {config_path}")
        return
        
    settings = config['backtest_settings']
    params = config['strategy_params']
    
    try:
        strategy_module = importlib.import_module(f"strategies.{settings['strategy_file']}")
        StrategyClass = getattr(strategy_module, settings['strategy_name'])
    except (ImportError, AttributeError) as e:
        print(f"Error: Could not import strategy. {e}")
        return

    all_market_data = load_data(settings['data_source'])
    if not all_market_data:
        print("No data loaded. Exiting.")
        return

    mode = settings.get('backtest_mode', 'single')

    if mode == 'portfolio':
        print("\n--- Running in Portfolio Mode ---")
        # Combine all dataframes into one, sorting by date
        portfolio_df = pd.concat(all_market_data.values()).sort_index()
        print(f"Combined {len(all_market_data)} assets into a single timeline.")
        
        features_df = add_features(portfolio_df)
        run_backtest(
            strategy=StrategyClass, data=features_df, cash=settings['initial_cash'],
            commission=settings['commission_pct'], params=params, asset_name='Portfolio'
        )
    else: # Default to 'single' mode
        print("\n--- Running in Single Asset Mode ---")
        for asset_name, market_data in all_market_data.items():
            print(f"\n{'='*20} Processing Asset: {asset_name} {'='*20}")
            try:
                features_df = add_features(market_data.copy())
                run_backtest(
                    strategy=StrategyClass, data=features_df, cash=settings['initial_cash'],
                    commission=settings['commission_pct'], params=params, asset_name=asset_name
                )
            except Exception as e:
                print(f"!!! ERROR processing {asset_name}: {e} !!!")
                continue

if __name__ == "__main__":
    main('config.yaml')