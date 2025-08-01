from backtest_engine.data_loader import load_data
from backtest_engine.feature_generator import add_features # Import feature function
from backtest_engine.runner import run_backtest
from strategies.sma_cross_strategy import SmaCross

if __name__ == "__main__":
    # --- Configuration ---
    data_file = 'data/AAPL_1D_2021-08-01-2025-04-03.csv'
    strategy_to_run = SmaCross
    initial_cash = 100_000
    commission_pct = 0.002

    # --- Execution ---
    try:
        # 1. Load Data
        market_data = load_data(data_file)
        
        # 2. Add Features
        market_data_with_features = add_features(market_data)
        
        # 3. Run Backtest on data with features
        run_backtest(
            strategy=strategy_to_run,
            data=market_data_with_features,
            cash=initial_cash,
            commission=commission_pct
        )

    except (FileNotFoundError, ValueError) as e:
        print(f"An error occurred: {e}")


