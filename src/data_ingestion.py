"""
Data Ingestion Module (ETL Pipeline)
This module handles loading and parsing stock data from raw YAML files,
consolidating them into a single dataset, and splitting them into symbol-wise CSV files.
"""

import os
import yaml
import pandas as pd
from typing import List, Dict, Any
from src.config import ALL_STOCK_DATA_CSV, STOCK_CSVS_DIR

def extract_yaml_data(raw_data_dir: str) -> List[Dict[str, Any]]:
    """
    Traverses the monthly subfolders in raw_data_dir, parses all date-wise
    YAML files, and consolidates the records into a single list.
    
    Args:
        raw_data_dir (str): Path to the folder containing raw monthly subfolders.
        
    Returns:
        List[Dict[str, Any]]: List of dictionary records parsed from YAML.
    """
    consolidated_records = []
    
    if not os.path.exists(raw_data_dir):
        print(f"Warning: Raw data directory '{raw_data_dir}' not found.")
        return []

    print(f"Scanning raw data directory: {raw_data_dir}")
    # Sort folders to ensure chronological sequence during processing
    month_folders = sorted([f for f in os.listdir(raw_data_dir) 
                            if os.path.isdir(os.path.join(raw_data_dir, f))])
    
    for month_folder in month_folders:
        month_path = os.path.join(raw_data_dir, month_folder)
        yaml_files = sorted([f for f in os.listdir(month_path) if f.endswith('.yaml')])
        
        print(f"Processing {month_folder} (found {len(yaml_files)} YAML files)...")
        for yaml_file in yaml_files:
            file_path = os.path.join(month_path, yaml_file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    if isinstance(data, list):
                        consolidated_records.extend(data)
                    elif isinstance(data, dict):
                        consolidated_records.append(data)
            except Exception as e:
                print(f"Error parsing file {file_path}: {e}")
                
    return consolidated_records

def transform_and_save(records: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Transforms the consolidated raw records list into a DataFrame, formats
    data types, and saves the full dataset and symbol-wise subsets to CSV files.
    
    Args:
        records (List[Dict[str, Any]]): Raw list of dictionaries.
        
    Returns:
        pd.DataFrame: Cleaned Pandas DataFrame.
    """
    if not records:
        print("No records to transform.")
        return pd.DataFrame()
        
    df = pd.DataFrame(records)
    
    # Ensure correct data types
    df['date'] = pd.to_datetime(df['date'])
    df['close'] = pd.to_numeric(df['close'], errors='coerce')
    df['open'] = pd.to_numeric(df['open'], errors='coerce')
    df['high'] = pd.to_numeric(df['high'], errors='coerce')
    df['low'] = pd.to_numeric(df['low'], errors='coerce')
    df['volume'] = pd.to_numeric(df['volume'], errors='coerce')
    
    # Add month column for month-wise calculations (Format: YYYY-MM)
    df['month'] = df['date'].dt.to_period('M').astype(str)
    
    # Sort chronologically by stock and date
    df = df.sort_values(by=['Ticker', 'date']).reset_index(drop=True)
    
    # Save the consolidated dataset
    df.to_csv(ALL_STOCK_DATA_CSV, index=False)
    print(f"Consolidated data successfully saved to: {ALL_STOCK_DATA_CSV}")
    
    # Create symbol-wise split CSV files
    os.makedirs(STOCK_CSVS_DIR, exist_ok=True)
    tickers = df['Ticker'].unique()
    for ticker in tickers:
        stock_df = df[df['Ticker'] == ticker].copy()
        ticker_csv = os.path.join(STOCK_CSVS_DIR, f"{ticker}.csv")
        stock_df.to_csv(ticker_csv, index=False)
        
    print(f"Successfully generated {len(tickers)} individual stock CSV files in: {STOCK_CSVS_DIR}")
    return df

def run_etl_pipeline(raw_data_dir: str = 'stock_data') -> None:
    """
    Executes the complete ETL Pipeline process.
    """
    records = extract_yaml_data(raw_data_dir)
    if records:
        transform_and_save(records)
    else:
        print("ETL skipped. Raw data not found, utilizing existing CSV files.")
