# Nifty 50 Stock Analysis Dashboard

**HCL CoE Capstone Project**  
**Author:** Pravin  
**Date:** April 2026  

## Project Summary
- Extracted Nifty 50 stock data from YAML files (14 months)
- Created 50 individual CSV files (one per stock)
- Calculated Yearly Return, Volatility, Cumulative Return, Sector Performance, Correlation and Monthly Gainers/Losers
- Built interactive Streamlit dashboard
- Stored clean data in SQLite database

## Key Results (Oct 2023 - Nov 2024)
- Top Gainer: EICHERMOT (+25.32%)
- Top Loser: HCLTECH (-17.69%)
- Most Volatile Stock: ADANIENT
- Best Sector: IT / Auto (from sector analysis)

## Files Included
- `main.py` → Full pipeline
- `app.py` → Streamlit dashboard
- `stock_analysis_original.py` → My original Colab work
- `stock_analysis.db` → SQL database
- All CSV files and charts

## How to Run
1. Install requirements: `pip install -r requirements.txt`
2. Create database: `python create_db.py`
3. Run dashboard: `streamlit run app.py`

GitHub ready. Modular code. All project requirements completed.