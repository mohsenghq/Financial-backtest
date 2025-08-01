import yaml
import importlib
from backtest_engine.data_loader import load_data
from backtest_engine.feature_generator import add_features
from backtest_engine.runner import run_backtest

def main(config_path: str):
    """
    Main function to run the backtesting process based on a config file.
    """
    # --- Load Configuration ---
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: Configuration file not found at {config_path}")
        return
        
    settings = config['backtest_settings']
    params = config['strategy_params']
    
    # --- Dynamically Import Strategy ---
    try:
        strategy_module = importlib.import_module(f"strategies.{settings['strategy_file']}")
        StrategyClass = getattr(strategy_module, settings['strategy_name'])
    except (ImportError, AttributeError) as e:
        print(f"Error: Could not import strategy '{settings['strategy_name']}' from '{settings['strategy_file']}'. {e}")
        return

    # --- Execution ---
    try:
        # 1. Load Data
        market_data = load_data(settings['data_source'])
        
        # 2. Add Features
        market_data_with_features = add_features(market_data)
        
        # 3. Run Backtest
        run_backtest(
            strategy=StrategyClass,
            data=market_data_with_features,
            cash=settings['initial_cash'],
            commission=settings['commission_pct'],
            params=params
        )

    except (FileNotFoundError, ValueError) as e:
        print(f"An error occurred during execution: {e}")

if __name__ == "__main__":
    config_file = 'config.yaml'
    main(config_file)