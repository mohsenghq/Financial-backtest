import streamlit as st
import os
from google import genai
from google.genai import types
from pathlib import Path
import re
import time

st.set_page_config(
    page_title="Add Strategy with AI",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Add New Strategy with AI")
st.write("Generate a new trading strategy using AI. Describe your strategy, select a model, and save it to the strategies folder.")

# API Key Configuration (Hidden by default)
with st.expander("🔑 API Key Configuration", expanded=False):
    stored_api_key = st.session_state.get('GEMINI_API_KEY', '')
    api_key_input = st.text_input(
        "Google API Key",
        value=stored_api_key,
        type="password",
        help="Enter your Google API key. Leave empty to use system environment variable."
    )
    if api_key_input:
        st.session_state['GEMINI_API_KEY'] = api_key_input

def generate_strategy_code(prompt: str, model: str = "gemini-1.5-flash-latest", temperature: float = 0.7) -> str:
    """
    Generate Python strategy code via the Google Gemini API.

    Args:
        prompt: The user's request for the trading strategy.
        model: The model name to use for generation.
        temperature: The generation temperature (creativity).

    Returns:
        A string containing the generated Python code.

    Raises:
        ValueError: If the Google API key is not found.
        RuntimeError: If the API call fails.
    """

    api_key = st.session_state.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Google API key not found in Streamlit session_state or environment variable.")

    prompt = (
        "Create a trading strategy class for the backtesting.py framework.\n"
        "The strategy must:\n"
        "1. Inherit from backtesting.Strategy.\n"
        "2. Include a clear docstring.\n"
        "3. Have configurable parameters and a classmethod get_optimization_ranges to returen min max and step like 'upper_bound': {'min': 60, 'max': 85, 'step': 5} of each parameter for optimization purpose.\n"
        "4. Implement init() and next() methods.\n"
        "5. Implement all technical indicators using finta if needed.\n"
        "6. from backtesting.lib import crossed_above, crossed_below is not valid. the lib just have crossover (Return `True` if `series1` just crossed over (above) `series2`.) and cross (Return True if series1 and series2 just crossed(above or below) each other.).\n"
        "IMPORTANT: The entire response must be only valid, raw Python code. Do not include markdown formatting or any explanatory text."
        "the strategy:\n"
    ) + prompt

    try:

        client = genai.Client(api_key=api_key)
        max_attempts = 5
        for attempt in range(1, max_attempts + 1):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                )
                return response.text.strip()
            except Exception as e:
                err_str = str(e)
                retryable = any(token in err_str for token in ("503", "UNAVAILABLE", "model is overloaded", "overloaded"))
                if retryable and attempt < max_attempts:
                    time.sleep(5)
                    continue
                raise RuntimeError(f"Strategy generation failed: {e}") from e
    except Exception as e:
        raise RuntimeError(f"Strategy generation failed: {e}") from e


def save_strategy_file(strategy_code, strategy_name):
    clean_name = re.sub(r'[^a-zA-Z0-9_]', '_', strategy_name.lower())
    if not clean_name.endswith('_strategy'):
        clean_name += '_strategy'
    file_path = Path('strategies') / f"{clean_name}.py"
    counter = 1
    while file_path.exists():
        clean_name = f"{clean_name}_{counter}"
        file_path = Path('strategies') / f"{clean_name}.py"
        counter += 1
    with open(file_path, 'w') as f:
        f.write(strategy_code)
    return file_path.name

with st.form("strategy_generation_form"):
    ai_model = st.selectbox(
        "Select AI Model",
        options=["gemini-2.5-pro", "gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-2.0-flash", "gemini-2.0-flash-lite"],
        help="Choose the AI model to generate your strategy"
    )
    strategy_prompt = st.text_area(
        "Strategy Description",
        placeholder="Describe your trading strategy...",
        help="Describe the trading strategy you want to create",
        height=300
    )
    strategy_name = st.text_input(
        "Strategy Name",
        placeholder="MyStrategy",
        help="Enter a name for your strategy"
    )
    generate_button = st.form_submit_button("Generate Strategy")
    if generate_button and strategy_prompt and strategy_name:
        try:
            with st.spinner("Generating strategy..."):
                strategy_code = generate_strategy_code(strategy_prompt, ai_model)
                # Clean up the code block if the model returns it with markdown
                if strategy_code.startswith("```python"):
                    strategy_code = strategy_code[9:]
                if strategy_code.endswith("```"):
                    strategy_code = strategy_code[:-3]
                
                file_name = save_strategy_file(strategy_code, strategy_name)
                st.success(f"Strategy generated and saved as {file_name}!")
                st.info("Refresh the main page to see your new strategy in the selection list.")
        except Exception as e:
            st.error(str(e))
            if "API key not found" in str(e):
                st.warning("Please provide a Google API key in the configuration section.")
