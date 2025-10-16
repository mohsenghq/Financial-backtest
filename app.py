import streamlit as st
import os
import importlib
import inspect
from main import run_backtests_from_config
import yaml

# --- App Configuration ---
st.set_page_config(
    page_title="Backtest Configuration",
    page_icon="⚙️",
    layout="wide"
)

# --- Helper Functions ---

def get_available_strategies():
    """
    Scans the 'strategies' directory to find available strategy files and classes.
    Returns a dictionary mapping strategy class names to their file and class objects.
    """
    strategies = {}
    strategy_dir = "strategies"
    for filename in os.listdir(strategy_dir):
        if filename.endswith(".py") and not filename.startswith("__"):
            file_name_without_ext = filename[:-3]
            module = importlib.import_module(f"{strategy_dir}.{file_name_without_ext}")
            for name, obj in inspect.getmembers(module):
                # Heuristic: Find a class that is not the base 'Strategy' class
                if inspect.isclass(obj) and 'Strategy' in str(obj.__base__):
                    strategies[name] = {
                        "file": file_name_without_ext,
                        "class": obj,
                        "params": get_strategy_params(obj)
                    }
    return strategies

def get_strategy_params(strategy_class):
    """
    Inspects a strategy class to find its parameters, excluding special methods.
    It looks for class attributes that are integers or floats.
    """
    params = {}
    # Get all members of the class
    for name, value in inspect.getmembers(strategy_class):
        # Filter for attributes that are parameters (heuristic: int or float, not private)
        if not name.startswith('_') and not callable(value) and isinstance(value, (int, float)):
            params[name] = value
    return params

def get_available_assets(data_path):
    """Scans the data directory for available asset data files."""
    assets = []
    if os.path.exists(data_path) and os.path.isdir(data_path):
        for filename in os.listdir(data_path):
            # Assuming CSV files, but could be adapted
            if filename.endswith(".csv"):
                assets.append(filename.replace('.csv', ''))
    return sorted(assets)

# --- Main UI ---
st.title("⚙️ Backtest Configuration")
st.write("Select a strategy, adjust its parameters, choose assets, and run a new backtest.")

# Load base config to get data path
try:
    with open('config.yaml', 'r') as f:
        base_config = yaml.safe_load(f)
    data_source_path = base_config['backtest_settings']['data_source']
except FileNotFoundError:
    st.error("`config.yaml` not found. Please ensure it exists in the root directory.")
    st.stop()

# --- UI Components ---
available_strategies = get_available_strategies()
available_assets = get_available_assets(data_source_path)

if not available_strategies:
    st.error("No strategies found in the `strategies/` directory.")
    st.stop()

if not available_assets:
    st.error(f"No asset data found in the `{data_source_path}` directory.")
    st.stop()

st.sidebar.header("Run New Backtest")
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("1. Select Strategy")
    selected_strategy_name = st.selectbox(
        "Choose a strategy",
        options=list(available_strategies.keys())
    )
    strategy_info = available_strategies[selected_strategy_name]

    st.subheader("2. Configure Parameters")
    params = {}
    if strategy_info['params']:
        for param, default_value in strategy_info['params'].items():
            if isinstance(default_value, int):
                params[param] = st.number_input(
                    f"Parameter: {param}",
                    value=default_value,
                    step=1
                )
            elif isinstance(default_value, float):
                params[param] = st.number_input(
                    f"Parameter: {param}",
                    value=default_value,
                    format="%.2f"
                )
    else:
        st.info("This strategy has no configurable parameters.")

with col2:
    st.subheader("3. Select Assets")
    selected_assets = st.multiselect(
        "Choose one or more assets to run the backtest on",
        options=available_assets,
        default=available_assets[0] if available_assets else []
    )

    st.subheader("4. Execute Backtest")
    run_button = st.button("🚀 Run Backtest", type="primary", use_container_width=True)

# --- Execution Logic ---
if run_button:
    if not selected_strategy_name or not selected_assets:
        st.warning("Please select a strategy and at least one asset.")
    else:
        # 1. Construct the configuration for the backtest run
        run_config = {
            'backtest_settings': base_config['backtest_settings'],
            'assets_to_run': selected_assets,
            'strategies': [{
                'name': selected_strategy_name,
                'file': strategy_info['file'],
                'params': params
            }]
        }

        # 2. Execute the backtest
        st.write("---")
        st.info(f"Running **{selected_strategy_name}** on **{', '.join(selected_assets)}**...")

        progress_bar = st.progress(0, text="Backtest in progress...")

        try:
            # This is where the main logic is called
            run_backtests_from_config(run_config)

            progress_bar.progress(100, text="Backtest complete!")
            st.success("✅ Backtest finished successfully!")
            st.info("Navigate to the 'Results Dashboard' page to view the output.")

            # Use st.cache_data.clear() to force the results page to reload its data
            st.cache_data.clear()

        except Exception as e:
            st.error(f"An error occurred during the backtest: {e}")
            progress_bar.progress(100, text="Backtest failed.")