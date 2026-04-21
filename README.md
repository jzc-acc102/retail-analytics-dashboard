📊 Retail Financial Analysis Dashboard (2020-2025)

An interactive tool for comparing financial performance across five major US retailers: Walmart, Target, Costco, Kroger, and Dollar Tree.

🚀 Live Demo

[Streamlit link will be added here after deployment]

📌 Project Overview

This dashboard helps investors and analysts quickly compare the financial health of leading retail companies. Instead of manually pulling data from WRDS and calculating ratios in Excel, users can interact with an automated dashboard that updates dynamically.

The dashboard answers three key questions:
- Which company is most profitable? (ROE, net margin, ROA)
- Which company is most stable? (volatility analysis)
- Does profitability translate to stock returns? (correlation analysis)

👥 Target User

- Individual investors researching retail stocks for their portfolios
- Business students learning financial analysis with Python
- Analysts who need quick cross-company comparisons without Excel

✨ Key Features

🔍 Company filter: Select any subset of the 5 retailers to compare
📊 Metric selector: Choose between gross margin, net margin, ROA, ROE, or inventory turnover
📈 Industry average: Every chart includes a benchmark line for context
⚠️ Risk rating: ROE volatility calculated and classified as Low/Medium/High
🏅 Company rankings: See which company leads in ROE, net margin, and inventory turnover
📅 YoY change: Track how each company improved or declined from previous year
🎯 Radar chart: Multi-dimensional comparison of all 5 metrics at once
🔗 Correlation analysis: Quantifies the relationship between profitability and stock returns
📸 Chart export: Download any visualization as PNG
💾 CSV download: Export the full dataset for your own analysis

📁 Data Source

Database: WRDS (Wharton Research Data Services)
Financial data: Compustat (funda table) - annual statements 2020-2025
Stock data: CRSP (msf and msfhdr tables) - monthly returns
Access date: April 2026

Key variables used:

sale: Revenue
cogs: Cost of Goods Sold
ni: Net Income
at: Total Assets
invt: Inventory
teq: Shareholders' Equity
ret: Monthly stock return

🔧 Methodology

Step 1: Data Extraction
Connected to WRDS using Python's wrds library. Used parameterized SQL queries (f-strings) to extract data for all five companies from 2020 to 2025.

Step 2: Ratio Calculation
Calculated five financial ratios standard in retail analysis:
- Gross margin = (Revenue - COGS) / Revenue
- Net margin = Net Income / Revenue
- ROA = Net Income / Total Assets
- ROE = Net Income / Shareholders' Equity
- Inventory turnover = COGS / Inventory

Step 3: Stock Data Processing
Cleaned monthly returns, removed missing values, and calculated cumulative returns over the 6-year period.

Step 4: Visualization
Created 8+ chart types using matplotlib, seaborn, and plotly, including line charts with industry average benchmarks, bar charts, heatmaps, radar charts, and correlation scatter plots.

Step 5: Dashboard Development
Packaged everything into a Streamlit app with interactive widgets (multiselect, dropdowns, buttons) and deployed to Streamlit Cloud.

📈 Key Findings

After analyzing 6 years of financial data across 5 retailers, here are the most notable insights.

1. Profitability Leader: Target (TGT)
Target consistently delivered the highest ROE, ranging from 30% to 54% during 2020-2025. This suggests strong brand positioning and effective cost management compared to peers.

2. Operational Efficiency Leader: Walmart (WMT)
Walmart's inventory turnover (8-9x per year) significantly outperformed competitors (5-6x). This reflects Walmart's legendary supply chain management and scale advantages.

3. Most Stable: Costco (COST)
Costco had the lowest ROE volatility, meaning its earnings are more predictable. For risk-averse investors, Costco is the safest choice.

4. Industry Trend: Recovery After Inflation
All five companies experienced margin pressure during 2021-2022 due to inflation and supply chain disruptions. From 2023 onward, ROE recovered across the board, signaling successful cost management.

5. Correlation: Profitability Does Not Always Equal Stock Returns
The correlation between ROE and stock returns was moderate (around 0.3 to 0.4). This means profitable companies tend to have higher stock returns, but other factors like market sentiment and growth expectations also matter.

🛠️ How to Run Locally

Prerequisites:
- Python 3.8 or higher
- WRDS account (though CSV files are included)

Steps:

1. Clone the repository
git clone https://github.com/jzc-acc102/retail-analytics-dashboard.git
cd retail-analytics-dashboard

2. Install dependencies
pip install -r requirements.txt

3. Run the app
streamlit run app.py

The app will open at http://localhost:8501

📂 Repository Structure

retail-analytics-dashboard/
- app.py (main Streamlit application)
- requirements.txt (Python dependencies)
- data/ (folder containing CSV files)
  - five_retailers_ratios.csv
  - five_retailers_stock_clean.csv
- images/ (folder for saved visualizations, optional)
- README.md (this file)

👤 Author

Jin Zichun - ACC102 Mini Assignment (Track 4)
GitHub: jzc-acc102

📄 License

This project is for academic submission purposes only. Data remains property of WRDS and Compustat.
