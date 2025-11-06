# run with:
# python -m streamlit run app.py

import streamlit as st
import os
import importlib
import inspect
from tools.core import run_backtests_from_config
import yaml
import json
import warnings
warnings.filterwarnings("ignore")
from dotenv import load_dotenv
load_dotenv()

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

def get_optimized_params(strategy_name, asset_name):
    """Loads optimized parameters for a given strategy and asset."""
    opt_params_path = 'results/optimized_params.json'
    if os.path.exists(opt_params_path):
        with open(opt_params_path, 'r') as f:
            all_opt_params = json.load(f)
            return all_opt_params.get(strategy_name, {}).get(asset_name)
    return None

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

# # Sidebar Sections
# st.sidebar.header("Run New Backtest")
# st.sidebar.markdown("---")
# st.sidebar.page_link("pages/2_Add_Strategy_AI.py", label="Add new strategy with AI 🤖")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("1. Select Strategy")
    
    strategy_options = ["All"] + list(available_strategies.keys())
    selected_strategy_names = st.multiselect(
        "Choose one or more strategies",
        options=strategy_options,
        default="All"
    )

    if "All" in selected_strategy_names:
        selected_strategy_names = list(available_strategies.keys())

    st.subheader("2. Select Assets")
    asset_options = ["All"] + available_assets
    selected_assets = st.multiselect(
        "Choose one or more assets to run the backtest on",
        options=asset_options,
        default="All"
    )

    if "All" in selected_assets:
        selected_assets = available_assets

    # For the parameter configuration, we'll just show the first selected strategy's params
    # This is a simplification for the UI. The backtest will use default params for others.
    if selected_strategy_names:
        first_strategy_name = selected_strategy_names[0]
        strategy_info = available_strategies[first_strategy_name]
        if len(selected_strategy_names) > 1:
            st.info(f"Parameter configuration is shown for '{first_strategy_name}'.\n\nOther selected strategies will use their default parameters.")
    else:
        strategy_info = {"params": {}} # Empty dict to prevent errors

    st.subheader("3. Configure Parameters")

    # --- Optimization Checkbox ---
    # It's always available, but its behavior changes based on selection.
    optimize = st.checkbox("Optimize", value=True, disabled=not any(s['params'] for s in available_strategies.values()))

    # --- Parameter Configuration UI ---
    # This section is now more dynamic based on the selections and optimize flag.
    params = {}
    param_ranges = {}

    # Case 1: Single strategy selected -> Full interactive UI
    if len(selected_strategy_names) == 1:
        selected_asset = selected_assets[0] if len(selected_assets) == 1 else None
        
        # Load optimized params if not optimizing and a single asset is selected
        loaded_opt_params = {}
        if not optimize and selected_asset:
            loaded_opt_params = get_optimized_params(first_strategy_name, selected_asset) or {}
            if loaded_opt_params:
                st.info(f"Loaded optimized parameters for {selected_asset}.")

        strategy_class = strategy_info.get('class')
        opt_ranges = {}
        if strategy_class and hasattr(strategy_class, 'get_optimization_ranges'):
            opt_ranges = strategy_class.get_optimization_ranges()

        if strategy_info['params']:
            if optimize:
                st.markdown("Define optimization ranges:")
                for param, default_value in strategy_info['params'].items():
                    param_range = opt_ranges.get(param, {})
                    col_start, col_end, col_step = st.columns(3)

                    if isinstance(default_value, int):
                        min_val = param_range.get('min', 1)
                        max_val = param_range.get('max', default_value * 10)
                        step = param_range.get('step', 1)

                        with col_start:
                            start_val = st.number_input(f"{param} start", value=min_val, min_value=min_val, step=step, key=f"{param}_start")
                        with col_end:
                            end_val = st.number_input(f"{param} end", value=max_val, min_value=min_val, step=step, key=f"{param}_end")
                        with col_step:
                            step_val = st.number_input(f"{param} step", value=step, min_value=step, step=step, key=f"{param}_step")

                        import numpy as np
                        param_ranges[param] = list(np.arange(start_val, end_val + step_val, step_val).astype(int))

                    else:  # float
                        min_val = param_range.get('min', 0.001)
                        max_val = param_range.get('max', float(default_value * 10))
                        step = param_range.get('step', 0.001)

                        with col_start:
                            start_val = st.number_input(f"{param} start", value=min_val, min_value=min_val, step=step, key=f"{param}_start", format="%.4f")
                        with col_end:
                            end_val = st.number_input(f"{param} end", value=max_val, min_value=min_val, step=step, key=f"{param}_end", format="%.4f")
                        with col_step:
                            step_val = st.number_input(f"{param} step", value=step, min_value=step, step=step, key=f"{param}_step", format="%.4f")

                        import numpy as np
                        # Use linspace for float ranges to avoid precision issues
                        param_ranges[param] = list(np.round(np.arange(start_val, end_val + step_val, step_val), 4))

            else:  # Not optimizing
                for param, default_value in strategy_info['params'].items():
                    param_range = opt_ranges.get(param, {})
                    value = loaded_opt_params.get(param, default_value)

                    if isinstance(default_value, int):
                        min_val = param_range.get('min', 1)
                        params[param] = st.number_input(f"Parameter: {param}", value=value, min_value=min_val, step=1)
                    else:  # float
                        min_val = param_range.get('min', 0.001)
                        # Ensure value is not less than min_val
                        display_value = max(float(value), min_val)
                        params[param] = st.number_input(f"Parameter: {param}", value=display_value, min_value=min_val, step=0.001, format="%.4f")
        else:
            st.info("This strategy has no configurable parameters.")

    # Case 2: Multiple strategies selected
    else:
        if optimize:
            st.info("Default optimization ranges (1x to 10x the default parameter value) will be used for all selected strategies.")
            # The logic to create these ranges will be handled during config construction.
        else:
            st.info("Strategies will run with their default parameters.")


with col2:
    st.subheader("4. Execute Backtest")
    run_button = st.button("🚀 Run Backtest", type="primary", use_container_width=True)

# --- Execution Logic ---
if run_button:
    if not selected_strategy_names or not selected_assets:
        st.warning("Please select at least one strategy and at least one asset.")
    else:
        # 1. Construct the configuration for the backtest run
        strategies_to_run = []
        for strategy_name in selected_strategy_names:
            strategy_info = available_strategies[strategy_name]
            
            current_params = {}
            current_param_ranges = {}
            current_optimize = optimize

            # If multiple strategies are selected, we might use default optimization ranges
            if len(selected_strategy_names) > 1:
                if current_optimize:
                    # Generate default optimization ranges
                    for param, default_value in strategy_info['params'].items():
                        if isinstance(default_value, int):
                            start_val = 1
                            end_val = default_value * 10
                            step_val = 1
                            import numpy as np
                            current_param_ranges[param] = list(np.arange(start_val, end_val + step_val, step_val).astype(int))
                        elif isinstance(default_value, float):
                            start_val = 0.1
                            end_val = default_value * 10
                            step_val = 0.1
                            import numpy as np
                            current_param_ranges[param] = list(np.arange(start_val, end_val + step_val, step_val))
                else:
                    # Use default params (which is an empty dict, so the strategy uses its class defaults)
                    pass
            
            # If only one strategy is selected, use the values from the UI
            else:
                current_params = params
                current_param_ranges = param_ranges

            strategies_to_run.append({
                'name': strategy_name,
                'file': strategy_info['file'],
                'params': current_params,
                'optimize': current_optimize if strategy_info['params'] else False,
                'param_ranges': current_param_ranges
            })

        run_config = {
            'backtest_settings': base_config['backtest_settings'],
            'assets_to_run': selected_assets,
            'strategies': strategies_to_run
        }

        # 2. Execute the backtest
        st.write("---")
        st.info(f"Running **{', '.join(selected_strategy_names)}** on **{', '.join(selected_assets)}**...")

        log_placeholder = st.empty()
        log_messages = []
        def streamlit_log(message):
            log_messages.append(message)
            log_placeholder.code("\n".join(log_messages))

        try:
            # This is where the main logic is called
            errors = run_backtests_from_config(run_config, log_callback=streamlit_log)

            if errors:
                st.error("Backtest completed with errors.")
            else:
                st.success("✅ Backtest finished successfully!")
                st.info("Navigate to the 'Results Dashboard' page to view the output.")
                st.cache_data.clear()

        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")