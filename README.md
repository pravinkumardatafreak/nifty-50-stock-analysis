# Nifty 50 Stock Analysis: Organizing, Cleaning, and Visualizing Market Trends

**HCL CoE Capstone Project**  
**Author:** Pravin  
**Academic Program:** GUVI Capstone Project (Finance / Data Analytics Domain)

---

## 🛠️ Project Architecture (PEP-8 Modular Design)

The codebase has been refactored from a flat Jupyter notebook into a clean, production-ready modular structure:

```text
nifty-50-stock-analysis/
├── src/
│   ├── __init__.py           # Declares 'src' as a Python package
│   ├── config.py             # Centralizes all paths and database URIs
│   ├── data_ingestion.py     # Local ETL Pipeline (YAML parsing to CSVs)
│   ├── analysis.py           # Core analytics (returns, volatility, compounding, correlation)
│   └── database.py           # Database operations handler (SQLAlchemy engine & insertions)
├── app.py                    # Interactive Streamlit dashboard UI (Plotly-driven)
├── create_db.py              # Database CLI setup utility
├── requirements.txt          # Python dependencies list
└── README.md                 # Project and Viva Study Guide (This document)
```

---

## 🧪 Data Science Theory & Viva-Style Study Guide

This section is prepared to help you answer questions during your **Live Evaluation**.

### 1. Daily Returns Calculation
* **Formula:** 
  $$\text{Daily Return}_t = \frac{\text{Close}_t - \text{Close}_{t-1}}{\text{Close}_{t-1}}$$
* **Why use percentage change instead of absolute differences?**  
  Absolute price changes are not comparable across stocks. For example, a ₹10 increase on a ₹100 stock (10% return) is much more significant than a ₹10 increase on a ₹10,000 stock (0.1% return). Using percentage change normalizes the scale, enabling direct comparisons between different tickers.

### 2. Volatility (Risk Assessment)
* **Formula:** 
  $$\text{Volatility} = \sigma = \sqrt{\frac{1}{N-1} \sum_{t=1}^N (R_t - \bar{R})^2}$$
  *(where $R_t$ is the daily return, and $\bar{R}$ is the average return over the period).*
* **Interpretation:**  
  Volatility measures the dispersion of daily returns from their historical mean. 
  - **High Volatility (e.g., ADANIENT):** Indicates high price fluctuations, representing a high-risk, high-reward profile.
  - **Low Volatility:** Points to price stability, suitable for risk-averse investors.

### 3. Cumulative Compound Returns
* **Formula:** 
  $$\text{Cumulative Return}_T = \left[ \prod_{t=1}^T (1 + \text{Daily Return}_t) - 1 \right] \times 100$$
* **Why compound instead of summing returns?**  
  Summing daily returns (arithmetic return sum) ignores the compounding effect (gains reinvested over time). Compound returns (geometric return) reflect the actual growth of a ₹100 investment made at the beginning of the year.

### 4. Stock Price Correlation
* **Formula:** Pearson Correlation Coefficient ($r$)
  $$r = \frac{\sum (X_i - \bar{X})(Y_i - \bar{Y})}{\sqrt{\sum (X_i - \bar{X})^2 \sum (Y_i - \bar{Y})^2}}$$
* **Value Range:** $-1$ (perfect negative correlation) to $+1$ (perfect positive correlation).
* **Viva Explanation:**  
  Helps portfolio managers with **diversification**. If two stocks are highly correlated ($r > 0.8$), holding both does not reduce risk. Diversifying requires holding stocks with low or negative correlation.

---

## 💾 Database Integration & Transition

The project utilizes **SQLAlchemy**, making database interactions independent of the underlying database engine. 
- **Default Database:** SQLite (`stock_analysis.db`). It runs locally out-of-the-box without requiring installation, ensuring **high portability**.
- **Switching to MySQL or PostgreSQL:**  
  You can migrate the database simply by updating the `DB_URI` in [config.py](file:///c:/Users/pravi/Desktop/nifty-50-stock-analysis/src/config.py):
  * **MySQL:** `mysql+pymysql://user:password@host:port/dbname`
  * **PostgreSQL:** `postgresql+psycopg2://user:password@host:port/dbname`

---

## 🤖 Google AI Studio & Gemini Integration

The dashboard features a **Gemini AI Market Analyst** page. This tool calls Google AI Studio's `gemini-1.5-flash` model to analyze your database metrics and generate custom, professional investment recommendations.

### How to Get Your Free API Key:
1. Navigate to **[Google AI Studio](https://aistudio.google.com/)**.
2. Sign in with your Google account and click **Get API Key**.
3. Create a free API key in a new or existing project.
4. Launch the dashboard, and paste your API key into the secure **Gemini API Key** password box in the sidebar config panel.

---

## 🚀 How to Run the Project

### 1. Install Dependencies
Ensure you have the required packages installed:
```bash
pip install -r requirements.txt
```

### 2. Initialize Database and Calculate CSVs
Run the setup script to calculate volatility, yearly returns, and load them into the SQL Database:
```bash
python create_db.py
```

### 3. Launch the Streamlit Dashboard
Run the following command to start the interactive web application:
```bash
streamlit run app.py
```
This will automatically launch the dashboard in your default browser at `http://localhost:8501`.
