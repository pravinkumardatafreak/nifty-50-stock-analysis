"""
Database Module
This module handles communication with the SQL database (SQLite, MySQL, or PostgreSQL)
using SQLAlchemy. It provides functions to save clean dataframes into tables.
"""

from sqlalchemy import create_engine
import pandas as pd
from src.config import DB_URI

def get_db_engine():
    """
    Initializes and returns a SQLAlchemy engine based on the DB_URI configuration.
    
    Returns:
        sqlalchemy.engine.Engine: Connection engine.
    """
    return create_engine(DB_URI)

def save_dataframe_to_sql(df: pd.DataFrame, table_name: str, if_exists: str = 'replace') -> None:
    """
    Saves a Pandas DataFrame into the specified SQL table using the configuration engine.
    
    Args:
        df (pd.DataFrame): DataFrame to save.
        table_name (str): Name of the target SQL table.
        if_exists (str): Action to take if the table already exists ('fail', 'replace', 'append').
    """
    if df.empty:
        print(f"Skipping database write: DataFrame for table '{table_name}' is empty.")
        return
        
    engine = get_db_engine()
    try:
        print(f"Connecting to database to write table '{table_name}'...")
        df.to_sql(table_name, engine, if_exists=if_exists, index=False)
        print(f"Successfully saved table '{table_name}' (rows: {len(df)}) to the database.")
    except Exception as e:
        print(f"Error saving table '{table_name}' to SQL database: {e}")
        print("Please check your database connection credentials and packages (e.g. pymysql, psycopg2).")
        raise e

def load_stock_data_cached():
    """
    Loads stock data using Streamlit caching. Falls back to CSV.
    This function dynamically imports Streamlit so that the module can still be
    imported in CLI scripts without forcing a Streamlit dependency.
    """
    import streamlit as st
    from src.config import ALL_STOCK_DATA_CSV
    
    @st.cache_data(show_spinner="Loading Nifty 50 database...")
    def _load():
        engine = get_db_engine()
        try:
            df = pd.read_sql_query("SELECT * FROM stock_data", engine)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values(by=['Ticker', 'date']).reset_index(drop=True)
            return df, "SQL Database"
        except Exception:
            import os
            if os.path.exists(ALL_STOCK_DATA_CSV):
                df = pd.read_csv(ALL_STOCK_DATA_CSV)
                df['date'] = pd.to_datetime(df['date'])
                df = df.sort_values(by=['Ticker', 'date']).reset_index(drop=True)
                return df, "CSV Fallback"
            else:
                return pd.DataFrame(), "None"
    return _load()

