import json
import os
import pandas as pd
from backtesting import Backtest

class StrategyOptimizer:
    def __init__(self, strategy, data):
        self.strategy = strategy
        self.data = data
        self.optimized_params_path = 'results/optimized_params.json'
        self.optimized_params = self._load_optimized_params()

    def _load_optimized_params(self):
        if os.path.exists(self.optimized_params_path):
            with open(self.optimized_params_path, 'r') as f:
                return json.load(f)
        return {}

    def _save_optimized_params(self):
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.optimized_params_path), exist_ok=True)
        with open(self.optimized_params_path, 'w') as f:
            json.dump(self.optimized_params, f, indent=4)

    def optimize(self, param_grid):
        """
        Run the optimization for the strategy.
        `param_grid` should be a dictionary of parameters to optimize,
        e.g., {'n1': range(10, 31, 5), 'n2': range(20, 61, 10)}
        """
        bt = Backtest(self.data, self.strategy, cash=1000000, commission=.002)
        stats, heatmap = bt.optimize(
            maximize='Sharpe Ratio',
            **param_grid,
            method='sambo',
            max_tries=1000,
            return_heatmap=True
        )
        best_params = stats._strategy._params
        
        # Convert heatmap Series to DataFrame for easier handling
        heatmap_df = self._process_heatmap(heatmap, param_grid)
        
        return best_params, heatmap_df

    def _process_heatmap(self, heatmap_series, param_grid):
        """
        Convert the heatmap Series to a proper DataFrame for HTML export.
        """
        if heatmap_series.empty:
            return pd.DataFrame()
            
        # Convert Series to DataFrame
        heatmap_df = heatmap_series.reset_index()
        
        # The Series has a MultiIndex for parameters and the performance metric as values
        # Rename columns appropriately
        if len(heatmap_df.columns) == len(param_grid) + 1:
            # Name the performance column
            performance_col = heatmap_df.columns[-1]
            heatmap_df = heatmap_df.rename(columns={performance_col: 'Performance'})
        
        return heatmap_df

    def get_optimized_params(self, strategy_name, data_name):
        return self.optimized_params.get(strategy_name, {}).get(data_name)

    def set_optimized_params(self, strategy_name, data_name, params):
        if strategy_name not in self.optimized_params:
            self.optimized_params[strategy_name] = {}
        self.optimized_params[strategy_name][data_name] = params
        self._save_optimized_params()

    def save_heatmap_html(self, heatmap_df, filepath):
        """
        Save heatmap DataFrame as HTML file.
        """
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        if heatmap_df.empty:
            print(f"Warning: Heatmap is empty, cannot save to {filepath}")
            return
            
        # Create a styled HTML table
        styled_df = heatmap_df.style.background_gradient(cmap='RdYlGn', axis=0)
        
        # Save as HTML
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(styled_df.to_html())
        
        print(f"Heatmap saved to: {filepath}")