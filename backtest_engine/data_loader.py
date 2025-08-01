import pandas as pd
import os
import glob

def _load_and_prepare_csv(file_path: str) -> pd.DataFrame | None:
    """Helper function to load and prepare a single CSV file."""
    try:
        df = pd.read_csv(file_path, index_col='Date', parse_dates=True)
        column_map = {'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'}
        df.rename(columns={col: column_map.get(col.lower(), col) for col in df.columns}, inplace=True)
        
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"Missing required columns in {file_path}")
            
        df.sort_index(inplace=True)
        df.dropna(inplace=True)
        print(f"Loaded {len(df)} data points from {os.path.basename(file_path)}")
        return df[required_columns]
    except Exception as e:
        print(f"Warning: Could not process {file_path}. Reason: {e}")
        return None

def load_data(source_path: str) -> dict[str, pd.DataFrame]:
    """
    Loads financial data from a single CSV file or a directory of CSV files.

    Args:
        source_path (str): The path to the CSV file or directory.

    Returns:
        dict[str, pd.DataFrame]: A dictionary where keys are asset names
                                 (from filenames) and values are the DataFrames.
    """
    data_frames = {}
    if os.path.isfile(source_path):
        asset_name = os.path.splitext(os.path.basename(source_path))[0]
        print(f"--- Loading Single File: {asset_name} ---")
        df = _load_and_prepare_csv(source_path)
        if df is not None:
            data_frames[asset_name] = df
    elif os.path.isdir(source_path):
        print(f"--- Loading All Files from Directory: {source_path} ---")
        csv_files = glob.glob(os.path.join(source_path, '*.csv'))
        if not csv_files:
            raise FileNotFoundError(f"No CSV files found in directory: {source_path}")
        for file_path in csv_files:
            asset_name = os.path.splitext(os.path.basename(file_path))[0]
            df = _load_and_prepare_csv(file_path)
            if df is not None:
                data_frames[asset_name] = df
    else:
        raise FileNotFoundError(f"Path is not a valid file or directory: {source_path}")

    return data_frames