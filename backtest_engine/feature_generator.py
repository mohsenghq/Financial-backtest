import pandas as pd
import pandas_ta as ta

def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds technical analysis features to the input DataFrame.

    Args:
        df (pd.DataFrame): The OHLCV data.

    Returns:
        pd.DataFrame: The DataFrame with added feature columns.
    """
    print("--- Adding Features ---")
    
    # Use the pandas_ta extension to add indicators
    df.ta.rsi(length=14, append=True)
    df.ta.atr(length=14, append=True)
    
    # The column names will be 'RSI_14' and 'ATRr_14'.
    # You can add as many other indicators as you need here.
    
    # Remove rows with NaN values that were created by the indicators
    df.dropna(inplace=True)
    
    print("Features added: RSI_14, ATRr_14")
    return df