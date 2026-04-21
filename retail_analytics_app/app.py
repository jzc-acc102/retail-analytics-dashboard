import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Retail Analytics Dashboard", layout="wide")
st.title("📊 Retail Industry Financial Analysis (2020-2025)")
st.markdown("Compare Walmart (WMT), Target (TGT), Costco (COST), Kroger (KR), Dollar Tree (DLTR)")

@st.cache_data
def load_data():
    df = pd.read_csv("data/five_retailers_ratios.csv")
    return df

df = load_data()

st.sidebar.header("🔍 Filter Companies")
companies = st.sidebar.multiselect(
    "Select companies to compare",
    options=df['tic'].unique(),
    default=df['tic'].unique()
)
filtered_df = df[df['tic'].isin(companies)]

# 📈 Financial Trends
st.header("📈 Financial Trends")
metric = st.selectbox(
    "📊 Choose a financial metric",
    options=['gross_margin', 'net_margin', 'roa', 'roe', 'inventory_turnover']
)

plot_df = filtered_df[['fyear', 'tic', metric]].copy()
plot_df = plot_df.rename(columns={metric: 'value'})
industry_avg = df.groupby('fyear')[metric].mean().reset_index()
industry_avg['tic'] = 'Industry Average'
industry_avg = industry_avg.rename(columns={metric: 'value'})
plot_df = pd.concat([plot_df, industry_avg])

fig = px.line(plot_df, x='fyear', y='value', color='tic', markers=True,
              title=f'{metric.replace("_", " ").upper()} Trend (2020-2025)',
              labels={'fyear': 'Year', 'value': metric.replace("_", " ").title(), 'tic': 'Company'})
fig.update_layout(hovermode='x unified')
st.plotly_chart(fig, use_container_width=True)

# 📊 Four-Key Metrics
st.header("📊 Four-Key-Metrics Overview (with Industry Average)")
metrics4 = ['gross_margin', 'net_margin', 'roa', 'roe']
titles4 = ['Gross Margin', 'Net Margin', 'ROA', 'ROE']
industry_avg_all = df.groupby('fyear')[metrics4].mean()

for metric, title in zip(metrics4, titles4):
    plot_df = filtered_df[['fyear', 'tic', metric]].copy()
    plot_df = plot_df.rename(columns={metric: 'value'})
    industry_avg_metric = df.groupby('fyear')[metric].mean().reset_index()
    industry_avg_metric['tic'] = 'Industry Average'
    industry_avg_metric = industry_avg_metric.rename(columns={metric: 'value'})
    plot_df = pd.concat([plot_df, industry_avg_metric])
    fig = px.line(plot_df, x='fyear', y='value', color='tic', markers=True,
                  title=title, labels={'fyear': 'Year', 'value': title, 'tic': 'Company'})
    fig.update_layout(hovermode='x unified', height=400)
    st.plotly_chart(fig, use_container_width=True)

# 🏆 ROE vs ROA
st.header("🏆 ROE vs ROA Comparison (Latest Year)")
latest_year = df['fyear'].max()
latest_data = df[df['fyear'] == latest_year].sort_values('roe', ascending=False)
bar_df = latest_data.melt(id_vars=['tic'], value_vars=['roe', 'roa'], var_name='metric', value_name='value')
fig = px.bar(bar_df, x='tic', y='value', color='metric', barmode='group',
             title=f'ROE vs ROA by Company ({latest_year})',
             labels={'tic': 'Company', 'value': 'Value', 'metric': 'Metric'},
             text='value')
fig.update_traces(texttemplate='%{text:.3f}', textposition='outside')
fig.update_layout(height=500)
st.plotly_chart(fig, use_container_width=True)

# ⚠️ Risk Analysis
st.header("⚠️ Risk Analysis (ROE Volatility)")
volatility = df.groupby('tic')['roe'].std().sort_values()
fig, ax = plt.subplots(figsize=(10, 6))
volatility.plot(kind='bar', ax=ax, color='coral', edgecolor='black')
ax.set_title('ROE Volatility (Lower = More Stable)')
ax.set_xlabel('Company')
ax.set_ylabel('Standard Deviation of ROE')
ax.set_xticklabels(volatility.index, rotation=0)
ax.grid(True, alpha=0.3, axis='y')
st.pyplot(fig)

# 🎯 Radar Chart
st.header("🎯 Company Capability Radar Chart")
radar_data = df[df['fyear'] == latest_year].copy()
metrics_radar = ['gross_margin', 'net_margin', 'roa', 'roe', 'inventory_turnover']
for m in metrics_radar:
    min_val = radar_data[m].min()
    max_val = radar_data[m].max()
    if max_val != min_val:
        radar_data[m + '_norm'] = (radar_data[m] - min_val) / (max_val - min_val)
    else:
        radar_data[m + '_norm'] = 0.5
fig_radar = go.Figure()
for _, row in radar_data.iterrows():
    values = [row[m + '_norm'] for m in metrics_radar]
    fig_radar.add_trace(go.Scatterpolar(r=values, theta=[m.replace('_', ' ').title() for m in metrics_radar],
                                        fill='toself', name=row['tic']))
fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
                        showlegend=True, title=f"Company Capability Radar Chart ({latest_year})")
st.plotly_chart(fig_radar, use_container_width=True)

# 📈 Stock Performance
st.header("📈 Stock Performance (Cumulative Returns)")
try:
    stock_raw = pd.read_csv("data/five_retailers_stock_clean.csv")
    stock_raw['date'] = pd.to_datetime(stock_raw['date'])
    stock_raw = stock_raw.sort_values(['ticker', 'date'])
    stock_raw['cumulative_return'] = stock_raw.groupby('ticker')['ret'].transform(lambda x: (1 + x).cumprod() - 1)
    stock_raw['cumulative_return_pct'] = stock_raw['cumulative_return'] * 100
    fig = px.line(stock_raw, x='date', y='cumulative_return_pct', color='ticker',
                  title='Cumulative Stock Returns: 5 Retailers (2020-2025)',
                  labels={'date': 'Date', 'cumulative_return_pct': 'Cumulative Return (%)', 'ticker': 'Company'})
    fig.update_layout(hovermode='x unified', height=500)
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
    st.plotly_chart(fig, use_container_width=True)
except Exception as e:
    st.info(f"ℹ️ Stock data not available: {e}")

# 🔗 Correlation Analysis
st.header("🔗 Correlation: Profitability vs Stock Returns")
try:
    stock_raw = pd.read_csv("data/five_retailers_stock_clean.csv")
    stock_raw['date'] = pd.to_datetime(stock_raw['date'])
    stock_raw['year'] = stock_raw['date'].dt.year
    annual_return = stock_raw.groupby(['ticker', 'year'])['ret'].apply(lambda x: (1 + x).prod() - 1).reset_index()
    annual_return.columns = ['tic', 'fyear', 'annual_return']
    df_corr = df.merge(annual_return, on=['tic', 'fyear'], how='inner')
    corr_roa = df_corr['roa'].corr(df_corr['annual_return'])
    corr_roe = df_corr['roe'].corr(df_corr['annual_return'])
    corr_netmargin = df_corr['net_margin'].corr(df_corr['annual_return'])
    col1, col2, col3 = st.columns(3)
    col1.metric("ROA vs Stock Return", f"{corr_roa:.3f}")
    col2.metric("ROE vs Stock Return", f"{corr_roe:.3f}")
    col3.metric("Net Margin vs Stock Return", f"{corr_netmargin:.3f}")
    if corr_roa > 0.3:
        st.info("✅ Moderate positive correlation: Higher profitability tends to lead to higher stock returns.")
    else:
        st.info("📉 Weak or no correlation: Profitability alone may not explain stock returns.")
    fig, ax = plt.subplots(figsize=(10, 6))
    for company in df_corr['tic'].unique():
        subset = df_corr[df_corr['tic'] == company]
        ax.scatter(subset['roa'], subset['annual_return'], label=company, s=100, alpha=0.7)
    ax.set_xlabel('ROA')
    ax.set_ylabel('Annual Stock Return')
    ax.set_title('ROA vs Stock Return (2020-2025)')
    ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    ax.axvline(x=0, color='gray', linestyle='--', alpha=0.5)
    ax.legend()
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)
except Exception as e:
    st.info(f"ℹ️ Correlation analysis not available: {e}")

# 🏅 Company Rankings
st.header("🏅 Company Rankings (Latest Year)")
latest = df[df['fyear'] == latest_year].copy()
ranking_data = latest[['tic', 'roe', 'net_margin', 'inventory_turnover']].copy()
for col in ['roe', 'net_margin', 'inventory_turnover']:
    ranking_data[f'{col}_rank'] = ranking_data[col].rank(ascending=False).astype(int)
st.dataframe(ranking_data, use_container_width=True)

# 📅 Year-over-Year Change
st.header("📅 Year-over-Year Change (Latest vs Previous Year)")
prev_year = df[df['fyear'] == latest_year - 1][['tic', 'roe', 'net_margin', 'inventory_turnover']].rename(
    columns={'roe': 'roe_prev', 'net_margin': 'net_margin_prev', 'inventory_turnover': 'turnover_prev'})
current = df[df['fyear'] == latest_year][['tic', 'roe', 'net_margin', 'inventory_turnover']]
yoy_data = current.merge(prev_year, on='tic')
yoy_data['roe_change'] = ((yoy_data['roe'] - yoy_data['roe_prev']) / yoy_data['roe_prev'] * 100).round(1)
yoy_data['net_margin_change'] = ((yoy_data['net_margin'] - yoy_data['net_margin_prev']) / yoy_data['net_margin_prev'] * 100).round(1)
yoy_data['turnover_change'] = ((yoy_data['inventory_turnover'] - yoy_data['turnover_prev']) / yoy_data['turnover_prev'] * 100).round(1)
st.dataframe(yoy_data[['tic', 'roe_change', 'net_margin_change', 'turnover_change']], use_container_width=True)

# 🏢 Company Quick Facts
st.header("🏢 Company Quick Facts")
info_df = pd.DataFrame({
    "Company": ["WMT", "TGT", "COST", "KR", "DLTR"],
    "Description": [
        "World's largest retailer. Known for low prices and supply chain excellence.",
        "Upscale discount retailer. Strong private label brands.",
        "Membership-based warehouse club. High volume, low margin.",
        "Traditional supermarket chain. Largest pure-play grocery retailer.",
        "Deep discount retailer. Fixed price point model."
    ]
})
st.dataframe(info_df, use_container_width=True)

# 💼 Investment Summary
st.header("💼 Investment Summary")
most_stable = volatility.idxmin()
best_roe_company = latest.loc[latest['roe'].idxmax(), 'tic']
st.markdown(f"""
| Investor Type | Recommended | Reason |
|---------------|-------------|--------|
| 🚀 Growth | {best_roe_company} | Highest ROE, strong profitability |
| 🛡️ Stable | {most_stable} | Lowest ROE volatility, most predictable |
| 💰 Value | DLTR | Discount retailer, potential undervalued |
| 🏆 Leader | WMT | Largest scale, operational efficiency |

### ⚠️ Risk Disclaimer
- Past performance does not guarantee future results
- Retail sector is sensitive to inflation and consumer sentiment
""")

# 📥 Download Data
st.header("📥 Download Data")
csv = df.to_csv(index=False).encode('utf-8')
st.download_button("📄 Download Full Data (CSV)", csv, "retail_data.csv", "text/csv")

st.markdown("---")
st.caption("📊 Data source: WRDS Compustat | 👤 Analysis by Jin Zichun | 📚 ACC102 Mini Assignment (Track 4)")