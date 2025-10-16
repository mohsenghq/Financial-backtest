# run with:
# python -m streamlit run dashboard.py
import streamlit as st
import pandas as pd
import os
import plotly.graph_objects as go

# --- Page Configuration ---
st.set_page_config(
    page_title="Backtest Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Interactive Backtest Dashboard")
st.write("Compare the performance of different trading strategies across various assets.")

# --- Data Loading ---
@st.cache_data
def load_results_data():
    """
    Scans the results directory and loads all summary stats and equity curves.
    Uses Streamlit's cache to avoid reloading data on every interaction.
    """
    base_dir = "results"
    all_stats = []
    all_equities = {}

    if not os.path.exists(base_dir):
        return pd.DataFrame(), {}

    for strategy_name in os.listdir(base_dir):
        strategy_path = os.path.join(base_dir, strategy_name)
        if os.path.isdir(strategy_path):
            for asset_name in os.listdir(strategy_path):
                asset_path = os.path.join(strategy_path, asset_name)
                stats_file = os.path.join(asset_path, "summary_stats.json")
                equity_file = os.path.join(asset_path, "equity_curve.json")

                if os.path.exists(stats_file) and os.path.exists(equity_file):
                    # Load summary stats
                    stats = pd.read_json(stats_file, typ='series')
                    stats['Strategy'] = strategy_name
                    stats['Asset'] = asset_name
                    all_stats.append(stats)

                    # Load equity curve
                    equity = pd.read_json(equity_file)
                    if asset_name not in all_equities:
                        all_equities[asset_name] = {}
                    all_equities[asset_name][strategy_name] = equity['Equity']

    if not all_stats:
        return pd.DataFrame(), {}

    return pd.DataFrame(all_stats), all_equities

# Load the data once
stats_df, equities_data = load_results_data()

# --- Sidebar Controls ---
st.sidebar.header("Dashboard Controls")

if stats_df.empty:
    st.sidebar.warning("No backtest results found. Please run `main.py` first.")
else:
    # Asset Selector
    available_assets = sorted(stats_df['Asset'].unique())
    selected_asset = st.sidebar.selectbox(
        "Select an Asset to Analyze",
        options=available_assets
    )

    # Strategy Selector
    available_strategies = sorted(
        stats_df[stats_df['Asset'] == selected_asset]['Strategy'].unique()
    )
    selected_strategies = st.sidebar.multiselect(
        "Select Strategies to Compare",
        options=available_strategies,
        default=available_strategies
    )

    # --- Main Panel Display ---
    if not selected_strategies:
        st.warning("Please select at least one strategy from the sidebar.")
    else:
        # Filter data based on selections
        filtered_stats = stats_df[
            (stats_df['Asset'] == selected_asset) &
            (stats_df['Strategy'].isin(selected_strategies))
        ].set_index('Strategy')

        filtered_equities = equities_data.get(selected_asset, {})

        # 1. Equity Curve Chart
        st.subheader(f"Equity Curve Comparison for {selected_asset}")
        fig = go.Figure()

        for strategy in selected_strategies:
            if strategy in filtered_equities:
                equity_series = filtered_equities[strategy]
                fig.add_trace(go.Scatter(
                    x=equity_series.index,
                    y=equity_series.values,
                    mode='lines',
                    name=strategy
                ))

        fig.update_layout(
            title=f'Strategy Performance on {selected_asset}',
            xaxis_title='Date',
            yaxis_title='Equity [$]',
            legend_title='Strategy',
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)

        # 2. Performance Statistics Table
        st.subheader("Performance Statistics")
        st.write("Key metrics for the selected strategies.")
        
        # Define columns to display for clarity
        display_columns = [
            'Return [%]', 'Buy & Hold Return [%]', 'Max. Drawdown [%]',
            'Sharpe Ratio', 'Calmar Ratio', '# Trades', 'Win Rate [%]'
        ]
        
        # Ensure columns exist before trying to display them
        stats_to_display = filtered_stats[[col for col in display_columns if col in filtered_stats.columns]]
        
        st.dataframe(stats_to_display.style.format("{:.2f}"))

