import json
import os
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
        return best_params, heatmap

    def get_optimized_params(self, strategy_name, data_name):
        return self.optimized_params.get(strategy_name, {}).get(data_name)

    def set_optimized_params(self, strategy_name, data_name, params):
        if strategy_name not in self.optimized_params:
            self.optimized_params[strategy_name] = {}
        self.optimized_params[strategy_name][data_name] = params
        self._save_optimized_params()
