"""
Data Analysis Module
This module implements the mathematical and statistical calculations required for 
stock performance evaluation, such as yearly returns, volatility, cumulative returns,
sector performance, correlation matrices, and monthly gainers/losers.
"""

import os
import pandas as pd
import numpy as np
from typing import Tuple, List
from src.config import SECTOR_DATA_CSV, GEMINI_MODEL

def calculate_yearly_returns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates the yearly return for each stock based on the first and last close prices.
    Formula: ((last_close / first_close) - 1) * 100
    
    Args:
        df (pd.DataFrame): Stock data DataFrame containing Ticker, date, and close columns.
        
    Returns:
        pd.DataFrame: DataFrame containing Ticker, first_close, last_close, and yearly_return_%.
    """
    # Ensure sorted order chronologically
    df_sorted = df.sort_values(by=['Ticker', 'date'])
    
    yearly = df_sorted.groupby('Ticker').agg(
        first_close=('close', 'first'),
        last_close=('close', 'last')
    ).reset_index()
    
    # Calculate return percentage
    yearly['yearly_return_%'] = ((yearly['last_close'] / yearly['first_close']) - 1) * 100
    yearly = yearly.sort_values(by='yearly_return_%', ascending=False).reset_index(drop=True)
    return yearly

def calculate_volatility(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates the volatility of each stock, defined as the standard deviation of daily returns.
    Formula:
      daily_return_t = (close_t - close_{t-1}) / close_{t-1}
      volatility = std(daily_return)
      
    Args:
        df (pd.DataFrame): Stock data DataFrame.
        
    Returns:
        pd.DataFrame: DataFrame containing Ticker and volatility, sorted descending.
    """
    df_sorted = df.sort_values(by=['Ticker', 'date']).copy()
    
    # Calculate daily return using percentage change
    df_sorted['daily_return'] = df_sorted.groupby('Ticker')['close'].pct_change()
    
    # Calculate standard deviation of daily returns
    volatility = df_sorted.groupby('Ticker')['daily_return'].std().reset_index()
    volatility.columns = ['Ticker', 'volatility']
    
    volatility = volatility.sort_values(by='volatility', ascending=False).reset_index(drop=True)
    return volatility

def calculate_cumulative_returns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates the cumulative return over time for each stock.
    Formula (Compounding):
      cumulative_return_t = (cumprod(1 + daily_return) - 1) * 100
      
    Args:
        df (pd.DataFrame): Stock data DataFrame.
        
    Returns:
        pd.DataFrame: DataFrame with an added 'cumulative_return' column.
    """
    df_sorted = df.sort_values(by=['Ticker', 'date']).copy()
    
    # Group by Ticker and calculate percentage change
    df_sorted['daily_return'] = df_sorted.groupby('Ticker')['close'].pct_change().fillna(0)
    
    # Calculate compounded cumulative returns in percent: (cumprod(1 + r) - 1) * 100
    df_sorted['cumulative_return'] = df_sorted.groupby('Ticker')['daily_return'].transform(
        lambda x: (1 + x).cumprod() - 1
    ) * 100
    
    return df_sorted

def calculate_sector_performance(yearly_df: pd.DataFrame) -> pd.DataFrame:
    """
    Maps stocks to their respective sectors and calculates average yearly returns.
    
    Args:
        yearly_df (pd.DataFrame): Pre-calculated yearly returns DataFrame.
        
    Returns:
        pd.DataFrame: Average yearly return grouped by sector, sorted descending.
    """
    if not os.path.exists(SECTOR_DATA_CSV):
        print(f"Warning: Sector data file '{SECTOR_DATA_CSV}' not found.")
        return pd.DataFrame(columns=['sector', 'yearly_return_%'])
        
    sector_df = pd.read_csv(SECTOR_DATA_CSV)
    
    # Extract ticker from symbol: "COMPANY NAME: TICKER" -> "TICKER"
    # Example: "ASIAN PAINTS: ASIANPAINT" -> "ASIANPAINT"
    sector_df['Ticker'] = sector_df['Symbol'].str.split(': ').str[1].str.strip()
    
    # Map mismatched tickers between the dataset and the sector sheet
    ticker_mapping = {
        'ADANIGREEN': 'ADANIENT',
        'AIRTEL': 'BHARTIARTL',
        'TATACONSUMER': 'TATACONSUM'
    }
    sector_df['Ticker'] = sector_df['Ticker'].replace(ticker_mapping)
    
    # Manually append BRITANNIA as it is completely missing from the sheet
    if 'BRITANNIA' not in sector_df['Ticker'].values:
        britannia_row = pd.DataFrame([{
            'COMPANY': 'BRITANNIA INDUSTRIES',
            'sector': 'FOOD & TOBACCO',
            'Symbol': 'BRITANNIA: BRITANNIA',
            'Ticker': 'BRITANNIA'
        }])
        sector_df = pd.concat([sector_df, britannia_row], ignore_index=True)
        
    # Merge with yearly returns
    merged = pd.merge(
        yearly_df[['Ticker', 'yearly_return_%']],
        sector_df[['Ticker', 'sector']],
        on='Ticker',
        how='inner'
    )
    
    sector_avg = merged.groupby('sector')['yearly_return_%'].mean().reset_index()
    sector_avg = sector_avg.sort_values(by='yearly_return_%', ascending=False).reset_index(drop=True)
    return sector_avg


def calculate_correlation_matrix(df: pd.DataFrame, tickers: List[str] = None) -> pd.DataFrame:
    """
    Calculates the stock price correlation matrix based on closing prices.
    
    Args:
        df (pd.DataFrame): Stock data DataFrame.
        tickers (List[str], optional): List of tickers to filter. If None, correlates all.
        
    Returns:
        pd.DataFrame: Correlation matrix DataFrame.
    """
    # Pivot to create date index, ticker columns, and closing prices as values
    pivot_table = df.pivot_table(index='date', columns='Ticker', values='close')
    
    if tickers:
        # Filter for selected tickers if provided and present
        valid_tickers = [t for t in tickers if t in pivot_table.columns]
        if valid_tickers:
            pivot_table = pivot_table[valid_tickers]
            
    return pivot_table.corr()

def calculate_monthly_gainers_losers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Groups stock data by calendar month and calculates the return for each stock.
    Formula: ((last_close / first_close) - 1) * 100
    
    Args:
        df (pd.DataFrame): Stock data DataFrame.
        
    Returns:
        pd.DataFrame: DataFrame containing month, Ticker, first_close, last_close, and monthly_return_%.
    """
    df_sorted = df.sort_values(by=['Ticker', 'date']).copy()
    
    # Create month column if it doesn't exist
    if 'month' not in df_sorted.columns:
        df_sorted['month'] = df_sorted['date'].dt.to_period('M').astype(str)
        
    # Group by month and ticker, aggregating first and last close price
    monthly = df_sorted.groupby(['month', 'Ticker']).agg(
        first_close=('close', 'first'),
        last_close=('close', 'last')
    ).reset_index()
    
    monthly['monthly_return_%'] = ((monthly['last_close'] / monthly['first_close']) - 1) * 100
    return monthly

def generate_ai_recommendation(ticker: str, return_pct: float, volatility_val: float, sector: str, api_key: str) -> str:
    """
    Calls the Google Gemini API to generate a professional investment recommendation
    for a selected stock based on its performance metrics.
    
    Args:
        ticker (str): Stock ticker symbol.
        return_pct (float): Stock's yearly return percentage.
        volatility_val (float): Stock's volatility (std dev of daily returns).
        sector (str): Stock's industry sector.
        api_key (str): Google AI Studio Gemini API key.
        
    Returns:
        str: Markdown formatted recommendation text from Gemini.
    """
    if not api_key or api_key.strip() == "":
        return "Error: Gemini API Key is missing. Please enter your API key in the sidebar."
        
    import google.generativeai as genai
    
    try:
        # Configure client
        genai.configure(api_key=api_key)
        
        # Select model (configured in src/config.py)
        model = genai.GenerativeModel(GEMINI_MODEL)
        
        # Construct prompt
        prompt = f"""
        You are an expert financial advisor and stock market analyst. 
        Analyze the following Nifty 50 stock data and provide a concise, professional investment recommendation.
        
        Stock Ticker: {ticker}
        Industry Sector: {sector}
        Yearly Return (Oct 2023 - Nov 2024): {return_pct:.2f}%
        Volatility (Standard Deviation of Daily Returns): {volatility_val:.6f}
        
        Structure your analysis in exactly 3 sections:
        1. **Market Performance & Risk Assessment**: Analyze what the yearly return and volatility mean for this stock's risk profile.
        2. **Sector Context**: Relate the performance to the industry sector context.
        3. **Investment Recommendation**: State a clear Buy, Hold, or Sell recommendation with brief justification for retail investors.
        
        Keep the response professional, actionable, and formatted in clean markdown. 
        Limit your total response to 200-250 words.
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error communicating with Gemini API: {str(e)}\n\nPlease check your API key validity and internet connection."

