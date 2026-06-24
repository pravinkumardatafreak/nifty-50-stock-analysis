import os

# Base directory of the project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Database Configuration
# Default to SQLite. To use MySQL or PostgreSQL, change the DB_URI below:
# MySQL: 'mysql+pymysql://username:password@localhost/stock_db'
# PostgreSQL: 'postgresql+psycopg2://username:password@localhost/stock_db'
DB_URI = os.getenv("DATABASE_URL", "sqlite:///" + os.path.join(BASE_DIR, "stock_analysis.db"))

# File Path Configurations
ALL_STOCK_DATA_CSV = os.path.join(BASE_DIR, "all_stock_data.csv")
SECTOR_DATA_CSV = os.path.join(BASE_DIR, "Sector_data - Sheet1.csv")
STOCK_CSVS_DIR = os.path.join(BASE_DIR, "stock_csvs")
VOLATILITY_CSV = os.path.join(BASE_DIR, "volatility.csv")
YEARLY_RETURNS_CSV = os.path.join(BASE_DIR, "yearly_returns.csv")

# Gemini AI Configuration (used by analysis.py and app.py)
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
GEMINI_MODEL_LABEL = "Gemini 2.5 Flash"

__all__ = [
    "BASE_DIR",
    "DB_URI",
    "ALL_STOCK_DATA_CSV",
    "SECTOR_DATA_CSV",
    "STOCK_CSVS_DIR",
    "VOLATILITY_CSV",
    "YEARLY_RETURNS_CSV",
    "GEMINI_MODEL",
    "GEMINI_MODEL_LABEL",
]
