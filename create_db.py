from sqlalchemy import create_engine
import pandas as pd

engine = create_engine('sqlite:///stock_analysis.db')

df = pd.read_csv('all_stock_data.csv')
yearly = pd.read_csv('yearly_returns.csv')
volatility = pd.read_csv('volatility.csv')

df.to_sql('stock_data', engine, if_exists='replace', index=False)
yearly.to_sql('yearly_returns', engine, if_exists='replace', index=False)
volatility.to_sql('volatility', engine, if_exists='replace', index=False)

print("✅ Database created successfully!")