import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go

# 页面设置
st.set_page_config(page_title="Retail Analytics Dashboard", layout="wide")
st.title("📊 Retail Industry Financial Analysis (2020-2025)")
st.markdown("Compare Walmart (WMT), Target (TGT), Costco (COST), Kroger (KR), Dollar Tree (DLTR)")

# 加载数据
@st.cache_data
def load_data():
    df = pd.read_csv("data/five_retailers_ratios.csv")
    return df

df = load_data()

# 侧边栏：公司筛选
companies = st.sidebar.multiselect(
    "Select companies to compare",
    options=df['tic'].unique(),
    default=df['tic'].unique()
)
filtered_df = df[df['tic'].isin(companies)]

# ==================== 图表1：折线图（下拉菜单选择指标） ====================
import plotly.express as px

st.header("Financial Trends")

metric = st.selectbox(
    "Choose a financial metric",
    options=['gross_margin', 'net_margin', 'roa', 'roe', 'inventory_turnover']
)

# 准备数据
plot_df = filtered_df[['fyear', 'tic', metric]].copy()
plot_df = plot_df.rename(columns={metric: 'value'})

# 计算行业平均
industry_avg = df.groupby('fyear')[metric].mean().reset_index()
industry_avg['tic'] = 'Industry Average'
industry_avg = industry_avg.rename(columns={metric: 'value'})

# 合并
plot_df = pd.concat([plot_df, industry_avg])

# 用 Plotly 画图
fig = px.line(
    plot_df, 
    x='fyear', 
    y='value', 
    color='tic',
    markers=True,
    title=f'{metric.replace("_", " ").upper()} Trend (2020-2025)',
    labels={'fyear': 'Year', 'value': metric.replace("_", " ").title(), 'tic': 'Company'}
)
fig.update_layout(hovermode='x unified')
st.plotly_chart(fig, use_container_width=True)

# ==================== 图表2：四合一子图（毛利率、净利率、ROA、ROE） ====================
st.header("Four-Key-Metrics Overview (with Industry Average)")
fig2, axes = plt.subplots(2, 2, figsize=(14, 10))
metrics4 = ['gross_margin', 'net_margin', 'roa', 'roe']
titles4 = ['Gross Margin', 'Net Margin', 'ROA', 'ROE']
industry_avg_all = df.groupby('fyear')[metrics4].mean()

for i, (metric, title) in enumerate(zip(metrics4, titles4)):
    ax = axes[i//2, i%2]
    for company in filtered_df['tic'].unique():
        data = filtered_df[filtered_df['tic'] == company]
        ax.plot(data['fyear'], data[metric], 'o-', linewidth=2, markersize=6, label=company)
    ax.plot(industry_avg_all.index, industry_avg_all[metric], 'k--', linewidth=3, label='Industry Avg')
    ax.set_title(title, fontsize=12)
    ax.set_xlabel('Year')
    ax.set_ylabel(metric.replace('_', ' ').title())
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)
plt.tight_layout()
st.pyplot(fig2)

# ==================== 图表3：ROE vs ROA 柱状图（最新年份） ====================
import plotly.express as px

st.header("ROE vs ROA Comparison (Latest Year)")

latest_year = df['fyear'].max()
latest_data = df[df['fyear'] == latest_year].sort_values('roe', ascending=False)

# 准备数据
bar_df = latest_data.melt(
    id_vars=['tic'], 
    value_vars=['roe', 'roa'], 
    var_name='metric', 
    value_name='value'
)

# 用 Plotly 画柱状图
fig = px.bar(
    bar_df, 
    x='tic', 
    y='value', 
    color='metric',
    barmode='group',
    title=f'ROE vs ROA by Company ({latest_year})',
    labels={'tic': 'Company', 'value': 'Value', 'metric': 'Metric'},
    text='value'
)
fig.update_traces(texttemplate='%{text:.3f}', textposition='outside')
fig.update_layout(height=500)
st.plotly_chart(fig, use_container_width=True)

# ==================== 图表4：波动率分析 ====================
st.header("⚠️ Risk Analysis (ROE Volatility)")
volatility = df.groupby('tic')['roe'].std().sort_values()
fig4, ax4 = plt.subplots(figsize=(10, 6))
volatility.plot(kind='bar', ax=ax4, color='coral', edgecolor='black')
ax4.set_title('ROE Volatility (Lower = More Stable)', fontsize=14)
ax4.set_xlabel('Company')
ax4.set_ylabel('Standard Deviation of ROE')
ax4.set_xticklabels(volatility.index, rotation=0)
ax4.grid(True, alpha=0.3, axis='y')
st.pyplot(fig4)

# ==================== 图表5：雷达图 ====================
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
    fig_radar.add_trace(go.Scatterpolar(
        r=values,
        theta=[m.replace('_', ' ').title() for m in metrics_radar],
        fill='toself',
        name=row['tic']
    ))
fig_radar.update_layout(
    polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
    showlegend=True,
    title=f"Company Capability Radar Chart ({latest_year})"
)
st.plotly_chart(fig_radar, use_container_width=True)

# ==================== 图表6：股票收益率对比 ====================
import plotly.express as px

st.header("Stock Performance (Cumulative Returns)")

try:
    stock_raw = pd.read_csv("data/five_retailers_stock_clean.csv")
    stock_raw['date'] = pd.to_datetime(stock_raw['date'])
    stock_raw = stock_raw.sort_values(['ticker', 'date'])
    
    # 计算累计收益率
    stock_raw['cumulative_return'] = stock_raw.groupby('ticker')['ret'].transform(
        lambda x: (1 + x).cumprod() - 1
    )
    stock_raw['cumulative_return_pct'] = stock_raw['cumulative_return'] * 100
    
    # 用 Plotly 画图
    fig = px.line(
        stock_raw,
        x='date',
        y='cumulative_return_pct',
        color='ticker',
        title='Cumulative Stock Returns: 5 Retailers (2020-2025)',
        labels={'date': 'Date', 'cumulative_return_pct': 'Cumulative Return (%)', 'ticker': 'Company'}
    )
    fig.update_layout(hovermode='x unified', height=500)
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
    st.plotly_chart(fig, use_container_width=True)
    
except Exception as e:
    st.info(f"Stock data not available: {e}")
# ==================== 相关系数分析 ====================
st.header("🔗 Correlation: Profitability vs Stock Returns")

try:
    # 加载股票数据
    stock_raw = pd.read_csv("data/five_retailers_stock_clean.csv")
    stock_raw['date'] = pd.to_datetime(stock_raw['date'])
    stock_raw['year'] = stock_raw['date'].dt.year
    
    # 计算年度股票回报
    annual_return = stock_raw.groupby(['ticker', 'year'])['ret'].apply(
        lambda x: (1 + x).prod() - 1
    ).reset_index()
    annual_return.columns = ['tic', 'fyear', 'annual_return']
    
    # 合并财务数据
    df_corr = df.merge(annual_return, on=['tic', 'fyear'], how='inner')
    
    # 计算相关系数
    corr_roa = df_corr['roa'].corr(df_corr['annual_return'])
    corr_roe = df_corr['roe'].corr(df_corr['annual_return'])
    corr_netmargin = df_corr['net_margin'].corr(df_corr['annual_return'])
    
    # 显示结果
    col1, col2, col3 = st.columns(3)
    col1.metric("ROA vs Stock Return", f"{corr_roa:.3f}")
    col2.metric("ROE vs Stock Return", f"{corr_roe:.3f}")
    col3.metric("Net Margin vs Stock Return", f"{corr_netmargin:.3f}")
    
    # 解释
    if corr_roa > 0.3:
        interpretation = "✅ Moderate positive correlation: Higher profitability tends to lead to higher stock returns."
    elif corr_roa > 0:
        interpretation = "📈 Weak positive correlation: Profitability and returns are somewhat related."
    else:
        interpretation = "⚠️ Negative or no correlation: Profitability alone may not explain stock returns."
    
    st.info(interpretation)
    
    # 散点图
    fig_corr, ax_corr = plt.subplots(figsize=(10, 6))
    for company in df_corr['tic'].unique():
        subset = df_corr[df_corr['tic'] == company]
        ax_corr.scatter(subset['roa'], subset['annual_return'], 
                        label=company, s=100, alpha=0.7)
    ax_corr.set_xlabel('ROA (Return on Assets)')
    ax_corr.set_ylabel('Annual Stock Return')
    ax_corr.set_title('ROA vs Stock Return (2020-2025)')
    ax_corr.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    ax_corr.axvline(x=0, color='gray', linestyle='--', alpha=0.5)
    ax_corr.legend()
    ax_corr.grid(True, alpha=0.3)
    st.pyplot(fig_corr)
    
except Exception as e:
    st.info(f"Correlation analysis not available: {e}")


# ==================== 图表7：综合评分卡 ====================
st.header("📋 Company Scorecard")
# ==================== 功能1：公司排名表 ====================
# ==================== 关键数字卡片 ====================
st.header("📊 Key Metrics at a Glance")

latest_year = df['fyear'].max()
latest = df[df['fyear'] == latest_year].copy()

avg_roe = latest['roe'].mean()
avg_margin = latest['net_margin'].mean()
best_roe = latest.loc[latest['roe'].idxmax(), 'tic']
best_margin = latest.loc[latest['net_margin'].idxmax(), 'tic']

col1, col2, col3, col4 = st.columns(4)
col1.metric("Avg ROE", f"{avg_roe:.1%}")
col2.metric("Avg Net Margin", f"{avg_margin:.1%}")
col3.metric("ROE Leader", best_roe)
col4.metric("Margin Leader", best_margin)
# ==================== 风险评级 ====================
st.header("⚠️ Risk Rating")

volatility = df.groupby('tic')['roe'].std().sort_values()

def risk_rating(std_val):
    if std_val < volatility.quantile(0.33):
        return "🟢 Low Risk"
    elif std_val < volatility.quantile(0.67):
        return "🟡 Medium Risk"
    else:
        return "🔴 High Risk"

risk_df = pd.DataFrame({
    "Company": volatility.index,
    "ROE Volatility": volatility.values.round(4),
    "Risk Rating": [risk_rating(v) for v in volatility.values]
}).sort_values("ROE Volatility")

st.dataframe(risk_df, use_container_width=True)
st.caption("Lower volatility = more stable earnings")

# ==================== 投资建议总结 ====================
st.header("💼 Investment Summary")

most_stable = volatility.idxmin()
best_roe_company = latest.loc[latest['roe'].idxmax(), 'tic']

st.markdown(f"""
| Investor Type | Recommended | Reason |
|---------------|-------------|--------|
| 🚀 **Growth** | {best_roe_company} | Highest ROE, strong profitability |
| 🛡️ **Stable** | {most_stable} | Lowest ROE volatility, most predictable |
| 💰 **Value** | DLTR | Discount retailer, potential undervalued |
| 🛒 **Leader** | WMT | Largest scale, operational efficiency |

### ⚠️ Risk Disclaimer
- Past performance does not guarantee future results
- Retail sector is sensitive to inflation and consumer sentiment
- TGT offers high returns but with higher volatility
""")

# ==================== 公司简介 ====================
st.header("🏢 Company Quick Facts")

info_df = pd.DataFrame({
    "Company": ["WMT", "TGT", "COST", "KR", "DLTR"],
    "Description": [
        "World's largest retailer. Known for low prices and supply chain excellence.",
        "Upscale discount retailer. Strong private label brands.",
        "Membership-based warehouse club. High volume, low margin.",
        "Traditional supermarket chain. Largest pure-play grocery retailer.",
        "Deep discount retailer. Fixed price point model ($1.25)."
    ],
    "Strengths": [
        "Supply chain, scale, Everyday Low Price",
        "Brand strength, store experience, digital growth",
        "Membership model, customer loyalty, low prices",
        "Grocery focus, regional dominance",
        "Low cost structure, value-conscious consumers"
    ]
})
st.dataframe(info_df, use_container_width=True)

# ==================== 图表导出功能 ====================
st.header("📸 Export Charts")

def download_chart(fig, filename):
    from io import BytesIO
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    buf.seek(0)
    return buf

# 让用户选择要导出的图表
chart_option = st.selectbox(
    "Select a chart to export as PNG",
    options=["Gross Margin Trend", "ROA Trend", "ROE Trend", "Four-Key Metrics", "ROE vs ROA Bar Chart"]
)

if chart_option == "Gross Margin Trend":
    fig, ax = plt.subplots(figsize=(10, 6))
    for company in filtered_df['tic'].unique():
        data = filtered_df[filtered_df['tic'] == company]
        ax.plot(data['fyear'], data['gross_margin'], 'o-', linewidth=2, label=company)
    industry_avg = df.groupby('fyear')['gross_margin'].mean()
    ax.plot(industry_avg.index, industry_avg.values, 'k--', linewidth=3, label='Industry Average')
    ax.set_xlabel('Year')
    ax.set_ylabel('Gross Margin')
    ax.legend()
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)
    buf = download_chart(fig, "gross_margin.png")
    st.download_button("Download PNG", buf, "gross_margin.png", "image/png")

elif chart_option == "ROA Trend":
    fig, ax = plt.subplots(figsize=(10, 6))
    for company in filtered_df['tic'].unique():
        data = filtered_df[filtered_df['tic'] == company]
        ax.plot(data['fyear'], data['roa'], 'o-', linewidth=2, label=company)
    industry_avg = df.groupby('fyear')['roa'].mean()
    ax.plot(industry_avg.index, industry_avg.values, 'k--', linewidth=3, label='Industry Average')
    ax.set_xlabel('Year')
    ax.set_ylabel('ROA')
    ax.legend()
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)
    buf = download_chart(fig, "roa_trend.png")
    st.download_button("Download PNG", buf, "roa_trend.png", "image/png")

elif chart_option == "ROE Trend":
    fig, ax = plt.subplots(figsize=(10, 6))
    for company in filtered_df['tic'].unique():
        data = filtered_df[filtered_df['tic'] == company]
        ax.plot(data['fyear'], data['roe'], 'o-', linewidth=2, label=company)
    industry_avg = df.groupby('fyear')['roe'].mean()
    ax.plot(industry_avg.index, industry_avg.values, 'k--', linewidth=3, label='Industry Average')
    ax.set_xlabel('Year')
    ax.set_ylabel('ROE')
    ax.legend()
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)
    buf = download_chart(fig, "roe_trend.png")
    st.download_button("Download PNG", buf, "roe_trend.png", "image/png")

elif chart_option == "Four-Key Metrics":
    fig2, axes = plt.subplots(2, 2, figsize=(14, 10))
    metrics4 = ['gross_margin', 'net_margin', 'roa', 'roe']
    titles4 = ['Gross Margin', 'Net Margin', 'ROA', 'ROE']
    industry_avg_all = df.groupby('fyear')[metrics4].mean()
    for i, (metric, title) in enumerate(zip(metrics4, titles4)):
        ax = axes[i//2, i%2]
        for company in filtered_df['tic'].unique():
            data = filtered_df[filtered_df['tic'] == company]
            ax.plot(data['fyear'], data[metric], 'o-', linewidth=2, label=company)
        ax.plot(industry_avg_all.index, industry_avg_all[metric], 'k--', linewidth=3, label='Industry Avg')
        ax.set_title(title)
        ax.set_xlabel('Year')
        ax.legend()
        ax.grid(True, alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig2)
    buf = download_chart(fig2, "four_metrics.png")
    st.download_button("Download PNG", buf, "four_metrics.png", "image/png")

elif chart_option == "ROE vs ROA Bar Chart":
    fig3, ax3 = plt.subplots(figsize=(12, 6))
    x = np.arange(len(latest))
    width = 0.35
    ax3.bar(x - width/2, latest['roe'], width, label='ROE', color='steelblue')
    ax3.bar(x + width/2, latest['roa'], width, label='ROA', color='coral')
    ax3.set_xlabel('Company')
    ax3.set_ylabel('Value')
    ax3.set_title(f'ROE vs ROA by Company ({latest_year})')
    ax3.set_xticks(x)
    ax3.set_xticklabels(latest['tic'])
    ax3.legend()
    ax3.grid(True, alpha=0.3, axis='y')
    st.pyplot(fig3)
    buf = download_chart(fig3, "roe_roa_bar.png")
    st.download_button("Download PNG", buf, "roe_roa_bar.png", "image/png")
st.header("🏆 Company Rankings (Latest Year)")
latest_year = df['fyear'].max()
latest = df[df['fyear'] == latest_year].copy()

ranking_data = latest[['tic', 'roe', 'net_margin', 'inventory_turnover']].copy()
for col in ['roe', 'net_margin', 'inventory_turnover']:
    ranking_data[f'{col}_rank'] = ranking_data[col].rank(ascending=False).astype(int)

# 显示排名表
st.dataframe(ranking_data, use_container_width=True)

# 显示冠军
best_roe = ranking_data.loc[ranking_data['roe'].idxmax(), 'tic']
best_margin = ranking_data.loc[ranking_data['net_margin'].idxmax(), 'tic']
best_turnover = ranking_data.loc[ranking_data['inventory_turnover'].idxmax(), 'tic']

st.success(f"🏅 **ROE Champion**: {best_roe} | 🏅 **Net Margin Champion**: {best_margin} | 🏅 **Inventory Turnover Champion**: {best_turnover}")

# ==================== 功能2：同比变化率 ====================
st.header("📈 Year-over-Year Change (Latest vs Previous Year)")

prev_year = df[df['fyear'] == latest_year - 1][['tic', 'roe', 'net_margin', 'inventory_turnover']].rename(
    columns={'roe': 'roe_prev', 'net_margin': 'net_margin_prev', 'inventory_turnover': 'turnover_prev'}
)
current = df[df['fyear'] == latest_year][['tic', 'roe', 'net_margin', 'inventory_turnover']]

yoy_data = current.merge(prev_year, on='tic')
yoy_data['roe_change'] = ((yoy_data['roe'] - yoy_data['roe_prev']) / yoy_data['roe_prev'] * 100).round(1)
yoy_data['net_margin_change'] = ((yoy_data['net_margin'] - yoy_data['net_margin_prev']) / yoy_data['net_margin_prev'] * 100).round(1)
yoy_data['turnover_change'] = ((yoy_data['inventory_turnover'] - yoy_data['turnover_prev']) / yoy_data['turnover_prev'] * 100).round(1)

# 显示同比变化
yoy_display = yoy_data[['tic', 'roe_change', 'net_margin_change', 'turnover_change']]
st.dataframe(yoy_display, use_container_width=True)

# 找出改善最大的公司
best_improvement = yoy_data.loc[yoy_data['roe_change'].idxmax(), 'tic']
st.info(f"📈 **Most Improved (ROE)**: {best_improvement} with +{yoy_data['roe_change'].max():.1f}% change")

# ==================== 功能3：公司简介卡片 ====================
st.header("🏢 Company Quick Facts")

# 在侧边栏添加公司简介
st.sidebar.header("🏢 Company Info")
company_info = {
    "WMT": "**Walmart** - World's largest retailer. Known for low prices, supply chain excellence, and Everyday Low Price strategy.",
    "TGT": "**Target** - Upscale discount retailer. Strong private label brands (Good & Gather, Cat & Jack).",
    "COST": "**Costco** - Membership-based warehouse club. High volume, low margin, customer loyalty through low prices.",
    "KR": "**Kroger** - Traditional supermarket chain. Largest pure-play grocery retailer in the US.",
    "DLTR": "**Dollar Tree** - Deep discount retailer. Fixed price point model ($1.25), focuses on value-conscious consumers."
}

selected_company = st.sidebar.selectbox("Select a company to learn more", list(company_info.keys()))
st.sidebar.markdown(company_info[selected_company])
st.sidebar.markdown("---")
metrics_score = ['roe', 'net_margin', 'inventory_turnover']
latest = df[df['fyear'] == latest_year].copy()
for m in metrics_score:
    min_val = latest[m].min()
    max_val = latest[m].max()
    if max_val != min_val:
        latest[m + '_score'] = (latest[m] - min_val) / (max_val - min_val) * 100
    else:
        latest[m + '_score'] = 50
latest['total_score'] = latest[[m+'_score' for m in metrics_score]].mean(axis=1)
scorecard = latest[['tic', 'roe', 'net_margin', 'inventory_turnover', 'total_score']].sort_values('total_score', ascending=False)
st.dataframe(scorecard.round(2), use_container_width=True)

# ==================== 行业洞察文字 ====================
st.header("💡 Industry Insights")
trend_roe = df.groupby('fyear')['roe'].mean()
if trend_roe.iloc[-1] > trend_roe.iloc[0]:
    trend_msg = "✅ ROE has improved overall, indicating better profitability."
else:
    trend_msg = "⚠️ ROE has slightly declined, facing margin pressure."

most_stable = volatility.idxmin()
most_profitable = df.groupby('tic')['roe'].mean().idxmax()

st.write(f"- {trend_msg}")
st.write(f"- **Most stable company**: {most_stable} (lowest ROE volatility)")
st.write(f"- **Most profitable company**: {most_profitable} (highest average ROE)")
st.write("- Costco and Walmart showed stronger resilience during inflation (2021-2023).")
st.write("- Target (TGT) shows high profitability but also higher volatility.")

# ==================== 下载按钮 ====================
st.header("📥 Download Data")
csv = df.to_csv(index=False).encode('utf-8')
st.download_button("Download Full Data (CSV)", csv, "retail_data.csv", "text/csv")

st.markdown("---")
st.caption("Data source: WRDS Compustat | Analysis by Jin Zichun | ACC102 Mini Assignment")