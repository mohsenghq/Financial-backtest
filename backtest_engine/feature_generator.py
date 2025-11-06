import pandas as pd
import numpy as np
from finta import TA

def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds technical analysis features to the input DataFrame using finta library.

    Args:
        df (pd.DataFrame): The OHLCV data with columns: 'Open', 'High', 'Low', 'Close', 'Volume'

    Returns:
        pd.DataFrame: The DataFrame with added feature columns.
    """
    print("--- Adding Features ---")
    
    # Ensure the DataFrame has the required OHLCV columns
    required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    if not all(col in df.columns for col in required_columns):
        raise ValueError(f"DataFrame must contain columns: {required_columns}")
    
    # Make a copy to avoid modifying the original DataFrame
    df = df.copy()
    
    # Prepare data for finta (ensure correct column names)
    ohlc_data = df[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
    
    # Add RSI using finta
    rsi_values = TA.RSI(ohlc_data, period=14)
    df['RSI_14'] = rsi_values
    
    # Add ATR using finta
    atr_values = TA.ATR(ohlc_data, period=14)
    df['ATR_14'] = atr_values
    
    # You can add more indicators as needed:
    
    # Moving averages
    df['SMA_20'] = TA.SMA(ohlc_data, period=20)
    df['EMA_12'] = TA.EMA(ohlc_data, period=12)
    
    # MACD
    macd = TA.MACD(ohlc_data)
    if isinstance(macd, pd.DataFrame):
        df['MACD'] = macd['MACD']
        df['MACD_SIGNAL'] = macd['SIGNAL']
        df['MACD_HISTOGRAM'] = macd['MACD'] - macd['SIGNAL']
    
    # Bollinger Bands
    bb = TA.BBANDS(ohlc_data, period=20)
    if isinstance(bb, pd.DataFrame):
        df['BB_UPPER'] = bb['BB_UPPER']
        df['BB_MIDDLE'] = bb['BB_MIDDLE'] 
        df['BB_LOWER'] = bb['BB_LOWER']
        df['BB_WIDTH'] = (bb['BB_UPPER'] - bb['BB_LOWER']) / bb['BB_MIDDLE']
    
    # Stochastic
    stoch = TA.STOCH(ohlc_data, period=14)
    if isinstance(stoch, pd.DataFrame):
        df['STOCH_K'] = stoch['STOCH_K']
        df['STOCH_D'] = stoch['STOCH_D']
    
    # Volume indicators
    df['OBV'] = TA.OBV(ohlc_data)
    
    # Remove rows with NaN values that were created by the indicators
    initial_rows = len(df)
    df.dropna(inplace=True)
    final_rows = len(df)
    
    print(f"Features added: RSI_14, ATR_14, SMA_20, EMA_12, MACD, Bollinger Bands, Stochastic, OBV")
    print(f"Removed {initial_rows - final_rows} rows with NaN values")
    print(f"Final dataset shape: {df.shape}")
    
    return df

# Alternative minimal version if you only need basic indicators:
def add_features_minimal(df: pd.DataFrame) -> pd.DataFrame:
    """
    Minimal version adding only RSI and ATR.
    """
    print("--- Adding Features (Minimal) ---")
    
    df = df.copy()
    ohlc_data = df[['Open', 'High', 'Low', 'Close', 'Volume']]
    
    # Add RSI
    df['RSI_14'] = TA.RSI(ohlc_data, period=14)
    
    # Add ATR
    df['ATR_14'] = TA.ATR(ohlc_data, period=14)
    
    # Remove NaN values
    initial_rows = len(df)
    df.dropna(inplace=True)
    
    print(f"Features added: RSI_14, ATR_14")
    print(f"Removed {initial_rows - len(df)} rows with NaN values")
    
    return df

# Example usage:
if __name__ == "__main__":
    # Sample data creation for testing
    sample_data = {
        'Open': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109],
        'High': [102, 103, 104, 105, 106, 107, 108, 109, 110, 111],
        'Low': [98, 99, 100, 101, 102, 103, 104, 105, 106, 107],
        'Close': [101, 102, 103, 104, 105, 106, 107, 108, 109, 110],
        'Volume': [1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900]
    }
    
    df = pd.DataFrame(sample_data)
    df_with_features = add_features(df)
    print(df_with_features.head())