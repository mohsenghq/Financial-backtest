import pandas as pd

def load_data(file_path: str) -> pd.DataFrame:
    """
    Loads financial data from a CSV file and prepares it for backtesting.

    Args:
        file_path (str): The path to the CSV file.

    Returns:
        pd.DataFrame: A DataFrame with 'Date' as the index and the required
                      'Open', 'High', 'Low', 'Close', 'Volume' columns.
                      
    Raises:
        FileNotFoundError: If the file path does not exist.
        ValueError: If the CSV does not contain the required date and price columns.
    """
    try:
        # Load the data, parsing 'Date' column as dates and setting it as the index
        df = pd.read_csv(
            file_path,
            index_col='Date',
            parse_dates=True
        )
    except FileNotFoundError:
        print(f"Error: The file at {file_path} was not found.")
        raise

    # --- Column Name Standardization ---
    # backtesting.py expects column names to be capitalized: 'Open', 'High', etc.
    # We create a mapping to handle common variations (e.g., 'open', 'low', 'close_price').
    column_map = {
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'volume': 'Volume'
    }
    
    # Rename columns based on the map, handling case-insensitivity
    df.rename(columns={col: column_map.get(col.lower(), col) for col in df.columns}, inplace=True)

    # --- Data Validation ---
    required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    if not all(col in df.columns for col in required_columns):
        raise ValueError(
            f"CSV file must contain the following columns: {required_columns}"
        )

    # Ensure data is sorted by date
    df.sort_index(inplace=True)
    
    # Remove any rows with missing values that might cause issues
    df.dropna(inplace=True)

    print(f"Successfully loaded {len(df)} data points from {file_path}")
    return df[required_columns] # Return only the required columns in the correct order