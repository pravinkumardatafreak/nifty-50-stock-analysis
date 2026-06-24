import sys
import pandas as pd
from src.config import ALL_STOCK_DATA_CSV, VOLATILITY_CSV, YEARLY_RETURNS_CSV
from src.analysis import calculate_yearly_returns, calculate_volatility
from src.database import save_dataframe_to_sql

def main():
    """
    Database creation CLI script.
    Loads the processed stock data, calculates yearly returns and volatility tables,
    and updates the database tables.
    """
    print("[Database Setup] Initializing stock analysis database...")
    
    try:
        # Load main dataset
        print(f"Loading stock data from: {ALL_STOCK_DATA_CSV}")
        df = pd.read_csv(ALL_STOCK_DATA_CSV)
        df['date'] = pd.to_datetime(df['date'])
        
        # Calculate tables dynamically
        print("Calculating yearly returns...")
        yearly = calculate_yearly_returns(df)
        yearly.to_csv(YEARLY_RETURNS_CSV, index=False)
        print(f"Saved yearly returns CSV to: {YEARLY_RETURNS_CSV}")
        
        print("Calculating volatility metrics...")
        volatility = calculate_volatility(df)
        volatility.to_csv(VOLATILITY_CSV, index=False)
        print(f"Saved volatility CSV to: {VOLATILITY_CSV}")
        
        # Write tables to SQL Database
        print("Writing tables to SQL database...")
        save_dataframe_to_sql(df, 'stock_data')
        save_dataframe_to_sql(yearly, 'yearly_returns')
        save_dataframe_to_sql(volatility, 'volatility')
        
        print("Success: Database created successfully! (Tables: stock_data, yearly_returns, volatility)")
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please ensure 'all_stock_data.csv' is generated and available in the workspace.")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()