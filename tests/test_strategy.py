import pytest
import pandas as pd
from backtesting import Backtest
from strategies.sma_cross_strategy import SmaCross

# Create synthetic price data for testing
def create_test_data(n=100):
    data = pd.DataFrame({
        'Open': [100 + i * 0.1 for i in range(n)],
        'High': [100.5 + i * 0.1 for i in range(n)],
        'Low': [99.5 + i * 0.1 for i in range(n)],
        'Close': [100 + i * 0.1 for i in range(n)],
        'Volume': [1000] * n
    }, index=pd.date_range('2025-01-01', periods=n, freq='D'))
    return data

@pytest.fixture
def backtest():
    data = create_test_data()
    bt = Backtest(data, SmaCross, cash=10000, commission=.002)
    return bt

def test_sma_cross_strategy_initialization(backtest):
    stats = backtest.run()
    assert stats['# Trades'] >= 0, "Strategy should initialize and run without errors"
