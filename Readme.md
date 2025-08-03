# Financial Backtesting Engine & Dashboard

A flexible, end-to-end Python framework for backtesting trading strategies on historical financial data. This engine allows you to run multiple strategies across multiple assets, generate detailed performance reports, and visualize results in an interactive dashboard.

![Python Version](https://img.shields.io/badge/python-3.9+-blue)

## Overview

This project provides a structured environment to:
1.  **Load** historical OHLCV data from CSV files.
2.  **Add** technical analysis features using `pandas-ta`.
3.  **Backtest** custom trading strategies using the powerful `backtesting.py` library.
4.  **Analyze** performance with detailed static reports from `quantstats`.
5.  **Compare** multiple strategies dynamically using an interactive Streamlit dashboard.

The core philosophy is to separate calculation from visualization, allowing you to run complex backtests once and explore the results many times.

---

## Features

- **Multi-Asset & Multi-Strategy**: Test a list of strategies on a single asset or a whole folder of assets.
- **Configuration Driven**: Easily change assets, strategies, and parameters via a central `config.yaml` file without touching the code.
- **Detailed Static Reports**: Automatically generates a `quantstats` HTML report for each backtest, comparing performance against a "Buy and Hold" benchmark.
- **Interactive Dashboard**: A Streamlit application to visually compare the equity curves and performance metrics of different strategies side-by-side.
- **Modular Structure**: Cleanly organized code (data loading, feature generation, strategies, reporting) makes it easy to maintain and extend.
- **Extensible**: Simple to add your own custom strategies.

---

## Project Structure

```plaintext
financial_backtester/
├── data/
│   ├── AAPL.csv
│   └── GOOGL.csv
├── results/
│   ├── SmaCross/
│   │   └── AAPL/
│   │       ├── report.html         (Static Report)
│   │       ├── equity_curve.json   (Data for Dashboard)
│   │       └── ...
│   └── ...
├── backtest_engine/
│   ├── data_loader.py
│   ├── feature_generator.py
│   ├── reporting.py
│   └── runner.py
├── strategies/
│   ├── sma_cross_strategy.py
│   ├── rsi_momentum_strategy.py
│   └── buy_and_hold_strategy.py
│
├── config.yaml             # Main configuration file
├── main.py                 # Script to run the backtests
├── dashboard.py            # Script to launch the interactive dashboard
└── requirements.txt