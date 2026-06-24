import os
import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine

# Import configuration and analysis modules
from src import config
from src.analysis import (
    calculate_yearly_returns,
    calculate_volatility,
    calculate_cumulative_returns,
    calculate_sector_performance,
    calculate_correlation_matrix,
    calculate_monthly_gainers_losers
)
from src.macro_data import (
    ANALYSIS_PERIOD,
    get_india_macro_indicators,
    get_us_macro_indicators,
    get_macro_narrative,
)

# Page configuration
st.set_page_config(
    page_title="Nifty 50 Market Intelligence",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom styling using Google Fonts and custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    .main-title {
        font-size: 2.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #FF8C00 0%, #FF2E93 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.1rem;
    }
    
    .subtitle {
        font-size: 1.1rem;
        color: #88888b;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
        transition: transform 0.3s ease, border-color 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        border-color: #FF8C00;
    }
    
    .metric-label {
        font-size: 0.95rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #a0a0a5;
        margin-bottom: 0.5rem;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #ffffff 0%, #a0a0a5 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .metric-value-green {
        font-size: 2.2rem;
        font-weight: 700;
        color: #00FF87;
        text-shadow: 0 0 10px rgba(0, 255, 135, 0.2);
    }
    
    .metric-value-red {
        font-size: 2.2rem;
        font-weight: 700;
        color: #FF3B30;
        text-shadow: 0 0 10px rgba(255, 59, 48, 0.2);
    }

    .macro-card {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.75rem;
        transition: border-color 0.2s ease;
    }

    .macro-card:hover {
        border-color: rgba(255, 140, 0, 0.4);
    }

    .macro-indicator {
        font-size: 0.85rem;
        font-weight: 600;
        color: #FF8C00;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .macro-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #ECECF1;
        margin: 0.25rem 0;
    }

    .macro-meta {
        font-size: 0.8rem;
        color: #88888b;
    }

    .macro-impact {
        font-size: 0.82rem;
        color: #a0a0a5;
        margin-top: 0.4rem;
        line-height: 1.4;
    }

    .macro-region-title {
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid rgba(255, 140, 0, 0.3);
    }

    div[data-testid="stSidebar"] button {
        cursor: pointer;
    }
</style>
""", unsafe_allow_html=True)

# -------------------- DATABASE / DATA LOADING --------------------

@st.cache_data
def get_stock_data():
    """
    Loads core stock data from the SQL Database (SQLite) with CSV fallback.
    """
    engine = create_engine(config.DB_URI)
    try:
        df = pd.read_sql_query("SELECT * FROM stock_data", engine)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values(by=['Ticker', 'date']).reset_index(drop=True)
        return df, "SQL Database"
    except Exception:
        if os.path.exists(config.ALL_STOCK_DATA_CSV):
            df = pd.read_csv(config.ALL_STOCK_DATA_CSV)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values(by=['Ticker', 'date']).reset_index(drop=True)
            return df, "CSV Fallback"
        else:
            return pd.DataFrame(), "None"

# Load shared dataset
df, source_loaded = get_stock_data()

# Calculate tables dynamically to ensure consistency
if not df.empty:
    yearly = calculate_yearly_returns(df)
    volatility = calculate_volatility(df)
else:
    yearly = pd.DataFrame()
    volatility = pd.DataFrame()

# -------------------- NAVIGATION SESSION STATE --------------------

# Initialize current page index and API Key in session state
if 'current_page' not in st.session_state:
    st.session_state.current_page = 0
if 'gemini_api_key' not in st.session_state:
    st.session_state.gemini_api_key = ""

# Page order list
PAGES = [
    "Overview & Market Summary",
    "Volatility Analysis",
    "Cumulative Returns",
    "Sector Performance",
    "Stock Correlation",
    "Monthly Performance Analytics",
    "Gemini AI Market Analyst"
]

# Get active page name
page = PAGES[st.session_state.current_page]

# -------------------- SIDEBAR MAP DIRECTORY --------------------

st.sidebar.markdown(
    '<div style="text-align: center; margin-bottom: 20px;">'
    '<h2 style="background: linear-gradient(135deg, #FF8C00 0%, #FF2E93 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 700;">Nifty 50 Portal</h2>'
    '</div>', 
    unsafe_allow_html=True
)

st.sidebar.subheader("Dashboard Roadmap")
for i, page_name in enumerate(PAGES):
    is_active = i == st.session_state.current_page
    label = f"{'▸ ' if is_active else ''}{i + 1}. {page_name}"
    if st.sidebar.button(
        label,
        key=f"nav_page_{i}",
        use_container_width=True,
        type="primary" if is_active else "secondary",
    ):
        if st.session_state.current_page != i:
            st.session_state.current_page = i
            st.rerun()

st.sidebar.divider()
st.sidebar.subheader("Configuration")
api_key_input = st.sidebar.text_input(
    "Gemini API Key:",
    type="password",
    value=st.session_state.gemini_api_key if st.session_state.gemini_api_key else os.getenv("GEMINI_API_KEY", ""),
    help="Enter your free API key from Google AI Studio to unlock AI features."
)
st.session_state.gemini_api_key = api_key_input

st.sidebar.divider()
st.sidebar.subheader("System Status")
st.sidebar.info(f"Connected to: **{source_loaded}**")

# Get ticker lists
if not df.empty:
    all_tickers = sorted(df['Ticker'].unique().tolist())
else:
    all_tickers = []

# ==================== 1. OVERVIEW & MARKET SUMMARY PAGE ====================
if page == "Overview & Market Summary":
    st.markdown('<div class="main-title">Nifty 50 Market Intelligence</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">HCL GUVI Capstone Project - Overview & Market Summary</div>', unsafe_allow_html=True)
    
    if df.empty:
        st.warning("Please check your database. No stock data is loaded.")
    else:
        # Calculate summary statistics
        green_stocks = len(yearly[yearly['yearly_return_%'] > 0])
        red_stocks = len(yearly) - green_stocks
        avg_yearly_return = yearly['yearly_return_%'].mean()
        avg_price = df['close'].mean()
        avg_volume = df['volume'].mean()
        
        # Display summary cards using custom CSS
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Green Stocks 📈</div>
                <div class="metric-value-green">{green_stocks}</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Red Stocks 📉</div>
                <div class="metric-value-red">{red_stocks}</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Avg Return %</div>
                <div class="metric-value" style="color: {'#00FF87' if avg_yearly_return >= 0 else '#FF3B30'};">{avg_yearly_return:.2f}%</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Avg Price (INR)</div>
                <div class="metric-value" style="color: #64D2FF;">₹{avg_price:,.2f}</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col5:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Avg Daily Vol</div>
                <div class="metric-value" style="color: #BF5AF2;">{avg_volume/1e6:.2f}M</div>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        st.divider()

        # Macro-economic context for institutional analysis
        st.subheader(f"Macro Economic Context ({ANALYSIS_PERIOD})")
        st.caption(
            "Domestic and global fundamentals that banks, FIIs, and asset managers monitor "
            "when positioning in Nifty 50 large-caps."
        )
        st.markdown(get_macro_narrative())

        india_col, us_col = st.columns(2)

        with india_col:
            st.markdown(
                '<div class="macro-region-title">🇮🇳 India — Domestic Fundamentals</div>',
                unsafe_allow_html=True,
            )
            for item in get_india_macro_indicators():
                st.markdown(f"""
                <div class="macro-card">
                    <div class="macro-indicator">{item['indicator']}</div>
                    <div class="macro-value">{item['value']}</div>
                    <div class="macro-meta">{item['as_of']} · {item['trend']}</div>
                    <div class="macro-impact">{item['impact']}</div>
                </div>
                """, unsafe_allow_html=True)

        with us_col:
            st.markdown(
                '<div class="macro-region-title">🇺🇸 United States — Global Drivers</div>',
                unsafe_allow_html=True,
            )
            for item in get_us_macro_indicators():
                st.markdown(f"""
                <div class="macro-card">
                    <div class="macro-indicator">{item['indicator']}</div>
                    <div class="macro-value">{item['value']}</div>
                    <div class="macro-meta">{item['as_of']} · {item['trend']}</div>
                    <div class="macro-impact">{item['impact']}</div>
                </div>
                """, unsafe_allow_html=True)

        with st.expander("How macro factors link to Nifty 50 sectors"):
            st.markdown("""
| Macro Factor | Nifty 50 Sectors Most Affected |
|---|---|
| **RBI Repo Rate / G-Sec yields** | Banks (HDFCBANK, ICICIBANK), NBFCs (BAJFINANCE), Realty |
| **CPI / Inflation** | FMCG (HINDUNILVR, ITC), Auto (MARUTI, M&M), Consumer Durables |
| **INR / USD & FII flows** | IT (TCS, INFY, WIPRO), Pharma exporters, Index heavyweights overall |
| **US Fed Rate / DXY** | FII-sensitive stocks, IT services, Metals (global demand proxy) |
| **Crude Oil prices** | OMCs (BPCL, ONGC), Aviation, Paint (input costs), Logistics |
| **US GDP / IT spending** | IT basket (~15% of Nifty weight), HCLTECH, TECHM |
            """)

        st.divider()

        # Display Top Gainers and Losers Side by Side
        left_col, right_col = st.columns(2)
        
        with left_col:
            st.subheader("Top 10 Performing Stocks (Green Stocks)")
            top10_gainers = yearly.head(10).copy()
            top10_gainers['Rank'] = range(1, 11)
            top10_gainers['yearly_return_%'] = top10_gainers['yearly_return_%'].map('{:.2f}%'.format)
            top10_gainers = top10_gainers.rename(columns={'Ticker': 'Stock Ticker', 'yearly_return_%': 'Yearly Return'})
            st.dataframe(top10_gainers[['Rank', 'Stock Ticker', 'Yearly Return']], hide_index=True, use_container_width=True)
            
        with right_col:
            st.subheader("Top 10 Decliners (Red Stocks)")
            top10_losers = yearly.tail(10).iloc[::-1].copy()
            top10_losers['Rank'] = range(1, 11)
            top10_losers['yearly_return_%'] = top10_losers['yearly_return_%'].map('{:.2f}%'.format)
            top10_losers = top10_losers.rename(columns={'Ticker': 'Stock Ticker', 'yearly_return_%': 'Yearly Return'})
            st.dataframe(top10_losers[['Rank', 'Stock Ticker', 'Yearly Return']], hide_index=True, use_container_width=True)

# ==================== 2. VOLATILITY ANALYSIS PAGE ====================
elif page == "Volatility Analysis":
    st.markdown('<div class="main-title">Market Risk & Volatility</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Analyze daily return fluctuations to assess stock risk profiles</div>', unsafe_allow_html=True)
    
    if df.empty:
        st.warning("No data available.")
    else:
        st.markdown(
            "**Volatility** represents the standard deviation of daily percentage change in close price. "
            "High volatility denotes high risk/high reward stocks, while low volatility points to stability."
        )
        
        top10_vol = volatility.head(10)
        
        # Interactive Plotly Bar Chart
        fig = px.bar(
            top10_vol,
            x='Ticker',
            y='volatility',
            title='Top 10 Most Volatile Nifty 50 Stocks',
            labels={'volatility': 'Volatility (Std Dev of Daily Returns)', 'Ticker': 'Ticker symbol'},
            color='volatility',
            color_continuous_scale=px.colors.sequential.Oranges
        )
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            title_x=0.5,
            height=500,
            xaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.1)')
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Data table details
        st.subheader("Comprehensive Volatility Index")
        vol_df = volatility.copy()
        vol_df['Rank'] = range(1, len(vol_df) + 1)
        vol_df['volatility'] = vol_df['volatility'].map('{:.6f}'.format)
        st.dataframe(vol_df[['Rank', 'Ticker', 'volatility']], use_container_width=True, hide_index=True)

# ==================== 3. CUMULATIVE RETURNS PAGE ====================
elif page == "Cumulative Returns":
    st.markdown('<div class="main-title">Cumulative Performance Trend</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Analyze compound returns of the leading Nifty 50 performers</div>', unsafe_allow_html=True)
    
    if df.empty:
        st.warning("No data available.")
    else:
        st.markdown(
            "This view displays compound returns of the **Top 5 Stocks** based on yearly returns. "
            "Formulated mathematically as: $\\text{Cumulative Return}_t = \\left(\\prod (1 + R_i) - 1\\right) \\times 100$."
        )
        
        # Calculate compound returns
        df_cum = calculate_cumulative_returns(df)
        
        # Get Top 5 Tickers
        top5_tickers = yearly.head(5)['Ticker'].tolist()
        df_top5 = df_cum[df_cum['Ticker'].isin(top5_tickers)]
        
        # Interactive Plotly Line chart
        fig = px.line(
            df_top5,
            x='date',
            y='cumulative_return',
            color='Ticker',
            title='Interactive Cumulative Compound Return of Top 5 Performers',
            labels={'cumulative_return': 'Cumulative Return (%)', 'date': 'Date'},
            hover_data={'date': '|%b %d, %Y', 'cumulative_return': ':.2f%'}
        )
        
        fig.update_layout(
            hovermode='x unified',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            title_x=0.5,
            height=600,
            xaxis=dict(
                gridcolor='rgba(255,255,255,0.05)',
                rangeselector=dict(
                    buttons=list([
                        dict(count=7, label='1w', step='day', stepmode='backward'),
                        dict(count=1, label='1m', step='month', stepmode='backward'),
                        dict(count=6, label='6m', step='month', stepmode='backward'),
                        dict(count=1, label='1y', step='year', stepmode='backward'),
                        dict(step='all')
                    ])
                ),
                rangeslider=dict(visible=True),
                type='date'
            ),
            yaxis=dict(gridcolor='rgba(255,255,255,0.1)')
        )
        
        st.plotly_chart(fig, use_container_width=True)

# ==================== 4. SECTOR PERFORMANCE PAGE ====================
elif page == "Sector Performance":
    st.markdown('<div class="main-title">Sector Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Analyze market trends and average returns grouped by industrial sectors</div>', unsafe_allow_html=True)
    
    if yearly.empty:
        st.warning("No data available.")
    else:
        # Calculate performance
        sector_avg = calculate_sector_performance(yearly)
        
        if sector_avg.empty:
            st.warning("No sector mapped data available. Please verify 'Sector_data - Sheet1.csv' resides in the project root.")
        else:
            st.markdown(
                "Aggregates the performance of individual stock tickers under their respective sectors "
                "to pinpoint industrial strengths and declines."
            )
            
            # Highlight with a gradient bar chart
            fig = px.bar(
                sector_avg,
                x='sector',
                y='yearly_return_%',
                title='Average Yearly Return by Sector',
                labels={'yearly_return_%': 'Average Return (%)', 'sector': 'Sector'},
                color='yearly_return_%',
                color_continuous_scale=px.colors.diverging.RdYlGn,
                hover_name='sector',
                hover_data={'yearly_return_%': ':.2f%'}
            )
            
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                title_x=0.5,
                height=500,
                xaxis_tickangle=-45,
                xaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
                yaxis=dict(gridcolor='rgba(255,255,255,0.1)')
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Displays sector data table
            st.subheader("Sector Index Summary Table")
            sector_table = sector_avg.copy()
            sector_table['yearly_return_%'] = sector_table['yearly_return_%'].map('{:.2f}%'.format)
            st.dataframe(sector_table, use_container_width=True, hide_index=True)

# ==================== 5. STOCK CORRELATION PAGE ====================
elif page == "Stock Correlation":
    st.markdown('<div class="main-title">Stock Price Correlation Heatmap</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Investigate market synergies and movement dependencies among tickers</div>', unsafe_allow_html=True)
    
    if df.empty:
        st.warning("No data available.")
    else:
        st.markdown(
            "Compute Pearson correlation coefficients between stock closing price time-series. "
            "Use the selector below to isolate specific tickers and clear the chart clutter."
        )
        
        # Interactive filters to limit heatmap size for readability
        default_selections = ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK', 'TATASTEEL', 'ADANIENT', 'EICHERMOT']
        selected_tickers = st.multiselect(
            "Select Tickers to correlate:",
            options=all_tickers,
            default=[t for t in default_selections if t in all_tickers]
        )
        
        if len(selected_tickers) < 2:
            st.warning("Please select at least 2 tickers to compute correlation.")
        else:
            # Calculate correlation matrix
            corr_matrix = calculate_correlation_matrix(df, selected_tickers)
            
            # Render using Plotly Heatmap (px.imshow) - FIXED colorscale to a valid Plotly scale 'RdBu'
            fig = px.imshow(
                corr_matrix,
                text_auto='.2f',
                aspect='auto',
                color_continuous_scale='RdBu',
                title=f"Correlation Heatmap ({len(selected_tickers)} Selected Stocks)",
                labels=dict(color="Correlation")
            )
            
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                title_x=0.5,
                height=650
            )
            
            st.plotly_chart(fig, use_container_width=True)

# ==================== 6. MONTHLY PERFORMANCE ANALYTICS PAGE ====================
elif page == "Monthly Performance Analytics":
    st.markdown('<div class="main-title">Monthly Gainers & Losers</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Inspect month-by-month performance anomalies and momentum shifts</div>', unsafe_allow_html=True)
    
    if df.empty:
        st.warning("No data available.")
    else:
        st.markdown(
            "Group stock close prices by month and compute monthly returns. "
            "Select a month below to analyze the Top 5 Gainers and Top 5 Losers."
        )
        
        # Group data and fetch months list
        monthly_df = calculate_monthly_gainers_losers(df)
        months = sorted(monthly_df['month'].unique())
        
        # Filter selectbox
        selected_month = st.selectbox("Select Month for Analysis:", months, index=len(months)-1)
        
        month_data = monthly_df[monthly_df['month'] == selected_month].copy()
        
        # Identify top 5 and bottom 5
        gainers = month_data.sort_values(by='monthly_return_%', ascending=False).head(5).copy()
        losers = month_data.sort_values(by='monthly_return_%', ascending=True).head(5).copy()
        
        # Combine them into a single dataframe for visualization
        gainers['Category'] = 'Gainers (Top 5)'
        losers['Category'] = 'Losers (Bottom 5)'
        combined = pd.concat([gainers, losers]).sort_values(by='monthly_return_%')
        
        # Create a beautiful horizontal bar chart in Plotly
        fig = px.bar(
            combined,
            y='Ticker',
            x='monthly_return_%',
            color='Category',
            orientation='h',
            title=f"Monthly Return Metrics - {selected_month}",
            labels={'monthly_return_%': 'Return (%)', 'Ticker': 'Ticker Symbol'},
            color_discrete_map={
                'Gainers (Top 5)': '#00FF87',
                'Losers (Bottom 5)': '#FF3B30'
            },
            hover_data={'monthly_return_%': ':.2f%'}
        )
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            title_x=0.5,
            height=500,
            xaxis=dict(
                gridcolor='rgba(255,255,255,0.05)',
                title='Return Percentage (%)'
            ),
            yaxis=dict(
                gridcolor='rgba(255,255,255,0.1)',
                categoryorder='total ascending'
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Side-by-side data tables
        col_g, col_l = st.columns(2)
        
        with col_g:
            st.markdown(f"##### Gainers Table - {selected_month}")
            gainers_display = gainers.copy()
            gainers_display['monthly_return_%'] = gainers_display['monthly_return_%'].map('{:.2f}%'.format)
            st.dataframe(gainers_display[['Ticker', 'monthly_return_%']], use_container_width=True, hide_index=True)
            
        with col_l:
            st.markdown(f"##### Losers Table - {selected_month}")
            losers_display = losers.copy()
            losers_display['monthly_return_%'] = losers_display['monthly_return_%'].map('{:.2f}%'.format)
            st.dataframe(losers_display[['Ticker', 'monthly_return_%']], use_container_width=True, hide_index=True)

# ==================== 7. GEMINI AI MARKET ANALYST PAGE ====================
elif page == "Gemini AI Market Analyst":
    st.markdown('<div class="main-title">Gemini AI Market Analyst</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">AI-driven investment recommendations based on real stock metrics</div>', unsafe_allow_html=True)
    
    if df.empty:
        st.warning("No stock data available.")
    else:
        st.markdown(
            f"Leverage Google AI Studio's **{config.GEMINI_MODEL_LABEL}** model to generate professional "
            "financial analyst reports dynamically for any selected Nifty 50 stock."
        )
        
        # Select stock
        selected_ticker = st.selectbox("Select Ticker for AI Analysis:", all_tickers)
        
        # Get metrics for selected stock
        stock_yearly = yearly[yearly['Ticker'] == selected_ticker]
        return_pct = stock_yearly['yearly_return_%'].values[0] if not stock_yearly.empty else 0.0
        
        stock_vol = volatility[volatility['Ticker'] == selected_ticker]
        volatility_val = stock_vol['volatility'].values[0] if not stock_vol.empty else 0.0
        
        # Sector matching
        sector_df = pd.read_csv(config.SECTOR_DATA_CSV)
        sector_df['Ticker'] = sector_df['Symbol'].str.split(': ').str[1].str.strip()
        
        ticker_mapping = {
            'ADANIGREEN': 'ADANIENT',
            'AIRTEL': 'BHARTIARTL',
            'TATACONSUMER': 'TATACONSUM'
        }
        sector_df['Ticker'] = sector_df['Ticker'].replace(ticker_mapping)
        
        # Britannia check
        if selected_ticker == "BRITANNIA":
            sector = "FOOD & TOBACCO"
        else:
            stock_sec = sector_df[sector_df['Ticker'] == selected_ticker]
            sector = stock_sec['sector'].values[0] if not stock_sec.empty else "UNKNOWN"
            
        # Display Stock Metric Brief
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Stock Sector", sector)
        col_m2.metric("Yearly Return %", f"{return_pct:.2f}%")
        col_m3.metric("Daily Volatility (Std Dev)", f"{volatility_val:.5f}")
        
        st.divider()
        
        # API Key check
        api_key = st.session_state.gemini_api_key
        
        if not api_key:
            st.info(
                "💡 **How to unlock AI Analysis:**\n\n"
                "1. Go to **[Google AI Studio](https://aistudio.google.com/)** and click **Get API Key**.\n"
                "2. Generate a free API Key.\n"
                "3. Paste the key into the **Gemini API Key** field in the sidebar navigation menu."
            )
        else:
            if st.button("Generate AI Market Report 🚀", use_container_width=True):
                with st.spinner(f"Querying {config.GEMINI_MODEL_LABEL} for {selected_ticker}..."):
                    from src.analysis import generate_ai_recommendation
                    ai_report = generate_ai_recommendation(
                        ticker=selected_ticker,
                        return_pct=return_pct,
                        volatility_val=volatility_val,
                        sector=sector,
                        api_key=api_key
                    )
                    
                    st.markdown("### 📋 Analyst Investment Report")
                    st.info(ai_report)

# -------------------- PAGINATION BUTTONS AT BOTTOM --------------------

st.markdown("<br><br>", unsafe_allow_html=True)
st.divider()

col_prev, col_middle, col_next = st.columns([1, 2, 1])

with col_prev:
    # Disable or hide button if on the first page
    if st.session_state.current_page > 0:
        if st.button("← Previous Page", use_container_width=True):
            st.session_state.current_page -= 1
            st.rerun()

with col_middle:
    # Progress bar and indicators
    progress_val = st.session_state.current_page / (len(PAGES) - 1)
    st.progress(progress_val)
    st.markdown(f"<p style='text-align: center; color: #a0a0a5; font-size: 0.9rem;'>Page {st.session_state.current_page + 1} of {len(PAGES)}: {page}</p>", unsafe_allow_html=True)

with col_next:
    # Disable or hide button if on the last page
    if st.session_state.current_page < len(PAGES) - 1:
        if st.button("Next Page →", use_container_width=True):
            st.session_state.current_page += 1
            st.rerun()