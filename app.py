import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import numpy as np

st.set_page_config(page_title="Nifty 50 Dashboard", layout="wide")
st.title("📈 Nifty 50 Stock Analysis Dashboard")
st.caption("HCL GUVI Capstone Project - By Pravin")

# Load the data
@st.cache_data
def load_data():
    df = pd.read_csv('all_stock_data.csv')
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(['Ticker', 'date'])
    df['daily_return'] = df.groupby('Ticker')['close'].pct_change()
    df['cumulative_return'] = df.groupby('Ticker')['daily_return'].transform(
        lambda x: (1 + x).cumprod()
    ) * 100
    return df

@st.cache_data
def load_yearly():
    df = pd.read_csv('all_stock_data.csv')
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(by=['Ticker', 'date'])
    yearly = df.groupby('Ticker').agg(
        first_close=('close', 'first'),
        last_close=('close', 'last')
    ).reset_index()
    yearly['yearly_return_%'] = ((yearly['last_close'] / yearly['first_close']) - 1) * 100
    yearly = yearly.sort_values(by='yearly_return_%', ascending=False)
    return yearly

@st.cache_data
def load_volatility():
    df = pd.read_csv('all_stock_data.csv')
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(['Ticker', 'date'])
    df['daily_return'] = df.groupby('Ticker')['close'].pct_change()
    volatility = df.groupby('Ticker')['daily_return'].std().reset_index()
    volatility.columns = ['Ticker', 'volatility']
    volatility = volatility.sort_values('volatility', ascending=False)
    return volatility

@st.cache_data
def load_sector():
    sector_df = pd.read_csv('Sector_data - Sheet1.csv')
    sector_df['Ticker'] = sector_df['Symbol'].str.split(': ').str[1].str.strip()
    return sector_df

df = load_data()
yearly = load_yearly()
volatility = load_volatility()
sector_df = load_sector()

# Navigation
page = st.sidebar.selectbox("📊 Navigation", [
    "Overview",
    "Top 10 Most Volatile Stocks",
    "Interactive Cumulative Return",
    "Sector Performance",
    "Correlation Heatmap",
    "Monthly Gainers & Losers"
])

# ==================== OVERVIEW PAGE ====================
if page == "Overview":
    st.header("Market Overview")
    col1, col2, col3 = st.columns(3)
    green = len(yearly[yearly['yearly_return_%'] > 0])
    red = len(yearly) - green
    col1.metric("Green Stocks 📈", green)
    col2.metric("Red Stocks 📉", red)
    col3.metric("Average Return %", f"{yearly['yearly_return_%'].mean():.2f}")
    
    st.divider()
    
    st.subheader("Top 10 Gainers")
    st.dataframe(yearly.nlargest(10, 'yearly_return_%')[['Ticker', 'yearly_return_%']], use_container_width=True)
    
    st.subheader("Top 10 Losers")
    st.dataframe(yearly.nsmallest(10, 'yearly_return_%')[['Ticker', 'yearly_return_%']], use_container_width=True)

# ==================== TOP 10 MOST VOLATILE STOCKS ====================
elif page == "Top 10 Most Volatile Stocks":
    st.header("Top 10 Most Volatile Stocks (Past Year)")
    
    top10 = volatility.head(10)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(top10['Ticker'], top10['volatility'], color='orange')
    ax.set_title('Top 10 Most Volatile Stocks (Past Year)', fontsize=16)
    ax.set_xlabel('Stock Ticker', fontsize=12)
    ax.set_ylabel('Volatility (Standard Deviation)', fontsize=12)
    ax.tick_params(axis='x', rotation=45)
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    st.pyplot(fig)

# ==================== INTERACTIVE CUMULATIVE RETURN ====================
elif page == "Interactive Cumulative Return":
    st.header("Interactive Cumulative Return of Top 5 Performing Stocks (Past Year)")
    
    df_plotly = df.copy()
    top5_tickers = yearly.head(5)['Ticker'].tolist()
    df_top5_plotly = df_plotly[df_plotly['Ticker'].isin(top5_tickers)]
    
    fig = px.line(df_top5_plotly,
                  x='date',
                  y='cumulative_return',
                  color='Ticker',
                  title='Interactive Cumulative Return of Top 5 Performing Stocks (Past Year)',
                  labels={'cumulative_return': 'Cumulative Return (%)', 'date': 'Date'},
                  hover_data={'date': '|%b %d', 'cumulative_return': ':.2f'})
    
    fig.update_layout(
        hovermode='x unified',
        title_x=0.5,
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=7,
                         label='1w',
                         step='day',
                         stepmode='backward'),
                    dict(count=1,
                         label='1m',
                         step='month',
                         stepmode='backward'),
                    dict(count=6,
                         label='6m',
                         step='month',
                         stepmode='backward'),
                    dict(count=1,
                         label='YTD',
                         step='year',
                         stepmode='todate'),
                    dict(count=1,
                         label='1y',
                         step='year',
                         stepmode='backward'),
                    dict(step='all')
                ])
            ),
            rangeslider=dict(
                visible=True
            ),
            type='date'
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)

# ==================== SECTOR PERFORMANCE ====================
elif page == "Sector Performance":
    st.header("Average Yearly Return by Sector")
    
    sector_performance = pd.merge(
        yearly[['Ticker', 'yearly_return_%']],
        sector_df[['Ticker', 'sector']],
        on='Ticker',
        how='left'
    )
    
    sector_avg = sector_performance.groupby('sector')['yearly_return_%'].mean().reset_index()
    sector_avg = sector_avg.sort_values('yearly_return_%', ascending=False)
    
    fig = px.bar(sector_avg,
                 x='sector',
                 y='yearly_return_%',
                 title='Average Yearly Return by Sector',
                 labels={'yearly_return_%': 'Average Yearly Return (%)', 'sector': 'Sector'},
                 hover_name='sector',
                 hover_data={'yearly_return_%': ':.2f%'})
    
    fig.update_layout(
        title_x=0.5,
        xaxis_tickangle=-45
    )
    
    st.plotly_chart(fig, use_container_width=True)

# ==================== CORRELATION HEATMAP ====================
elif page == "Correlation Heatmap":
    st.header("Stock Price Correlation Heatmap (Nifty 50)")
    
    pivot_table = df.pivot_table(index='date', columns='Ticker', values='close')
    corr_matrix = pivot_table.corr()
    
    fig, ax = plt.subplots(figsize=(14, 10))
    sns.heatmap(corr_matrix, cmap='coolwarm', linewidths=0.5, ax=ax)
    plt.title('Stock Price Correlation Heatmap (Nifty 50)', fontsize=16)
    plt.tight_layout()
    st.pyplot(fig)

# ==================== MONTHLY GAINERS & LOSERS ====================
elif page == "Monthly Gainers & Losers":
    st.header("Top 5 Gainers and Losers - Month-wise")
    
    df_monthly = df.copy()
    df_monthly['month'] = df_monthly['date'].dt.to_period('M')
    
    monthly = df_monthly.groupby(['month', 'Ticker']).agg(
        first_close=('close', 'first'),
        last_close=('close', 'last')
    ).reset_index()
    
    monthly['monthly_return_%'] = ((monthly['last_close'] / monthly['first_close']) - 1) * 100
    
    months = sorted(monthly['month'].unique())
    
    # Create subplots (7 rows, 2 columns for 14 months)
    fig, axes = plt.subplots(7, 2, figsize=(16, 24))
    fig.suptitle('Top 5 Gainers and Losers - Month-wise', fontsize=18)
    
    for i, month in enumerate(months):
        month_data = monthly[monthly['month'] == month].copy()
        
        # Gainers
        gainers = month_data.sort_values('monthly_return_%', ascending=False).head(5)
        gainers['rank'] = range(1, len(gainers) + 1)
        
        # Losers
        losers = month_data.sort_values('monthly_return_%', ascending=True).head(5)
        losers['rank'] = range(1, len(losers) + 1)
        
        ax = axes[i//2, i%2]
        
        display_labels = []
        display_returns = []
        bar_colors = []
        text_colors = []
        
        # Add gainers
        for _, row in gainers.iterrows():
            label = f"{row['rank']}. {row['Ticker']}"
            display_labels.append(label)
            display_returns.append(row['monthly_return_%'])
            if row['monthly_return_%'] >= 0:
                bar_colors.append('green')
                text_colors.append('green')
            else:
                bar_colors.append('red')
                text_colors.append('red')
        
        # Add losers
        for _, row in losers.iterrows():
            label = f"{row['rank']}. {row['Ticker']}"
            display_labels.append(label)
            display_returns.append(row['monthly_return_%'])
            bar_colors.append('red')
            text_colors.append('red')
        
        # Reverse for display
        barh_labels = display_labels[::-1]
        barh_returns = display_returns[::-1]
        barh_bar_colors = bar_colors[::-1]
        barh_text_colors = text_colors[::-1]
        
        # Plot
        ax.barh(barh_labels, barh_returns, color=barh_bar_colors)
        
        # Color y-axis labels
        for j, tick_label in enumerate(ax.get_yticklabels()):
            tick_label.set_color(barh_text_colors[j])
        
        ax.set_title(str(month))
        ax.set_xlabel('Monthly Return %')
        
        handles = [plt.Rectangle((0,0),1,1, color='green'), plt.Rectangle((0,0),1,1, color='red')]
        labels = ['Gainers (>=0%)', 'Losers (<0%)']
        ax.legend(handles, labels)
    
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    st.pyplot(fig)

st.sidebar.divider()
st.sidebar.success("✅ Dashboard is running with your real Nifty 50 data!")