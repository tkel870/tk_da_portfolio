Executive Profitability & Customer Risk Analysis
Overview

This project delivers a full-stack executive profitability and customer risk analysis using SQL, Python, spreadsheets, and Tableau.

The objective was to simulate a real-world business analytics engagement by identifying revenue drivers, loss-generating products, and high-risk customers across a multi-category retail dataset.

The analysis demonstrates an end-to-end workflow from raw data ingestion and cleaning through executive-level insight generation and visualization.

## Interactive Tableau Dashboard

View the live executive dashboard here:
🔗 https://public.tableau.com/app/profile/tricia.bleavins/viz/ExecutiveProfitabilityAnalysisDashboard/ExecutiveProfitabilityAnalysisDashboard

This interactive dashboard presents:
- Profitability by category and sub-category
- Customer risk and unprofitable accounts
- Revenue and profit performance overview
- Executive-level KPI summary

Tools & Technologies

SQL (SQLite) — data cleaning, transformation, KPI analysis
Python (pandas) — profitability modeling, Pareto analysis, customer risk scoring
Excel / Spreadsheets — executive summary modeling
Tableau — executive dashboard & visualization
GitHub — version control & portfolio presentation

Dataset

~9,994 cleaned transaction records

Multi-category retail sales dataset

Includes revenue, profit, discount, customer, and product data

Currency-formatted fields required cleaning and type conversion

Business Questions

Which product categories generate the most profit?

Which sub-categories are driving losses?

Are there high-revenue customers who are unprofitable?

How concentrated is profit across products?

Where should executives focus to improve margins?

Data Preparation (SQL)

Raw data contained:

Currency formatting ($ and commas)

Text-typed numeric fields

One corrupt row with profit but no sales

Cleaning steps:

Created SQL views to preserve raw data

Removed corrupt rows

Converted currency fields to numeric

Built clean analytical dataset for modeling

This mirrors real-world analyst workflows where raw data is preserved and cleaned views are used for analysis.

Executive KPI Snapshot

Total Revenue: $2.29M

Total Profit: $286K

Profit Margin: 12.47%

Orders: 5,009

Customers: 793

Products: 1,849

Key Findings
1. Category Profitability

Technology and Office Supplies show strong margins (~17%)

Furniture generates significant revenue but only ~2.5% margin

Furniture identified as primary profit risk category

2. Loss-Generating Subcategories

Major loss drivers:

Tables: −$17.7K profit

Supplies: −$11.8K profit

Bookcases: negative margin

These products significantly reduce overall profitability despite strong revenue.

3. Customer Risk Analysis

Multiple customers generated high revenue while producing net losses.

Example:

Customer produced $5.6K revenue but −$6.6K profit

This suggests discounting, shipping costs, or product mix issues creating hidden profitability risk.

4. Profit Concentration (Pareto Analysis)

Approximately 8.9% of products generate 80% of total profit, indicating strong profit concentration and opportunities for targeted growth and pricing optimization.

Project Structure
executive_profitability_project
│
├── README.md
├── sql/
│   ├── data_cleaning_and_views.sql
│   ├── executive_kpis.sql
│   ├── loss_driver_analysis.sql
│   └── customer_risk_analysis.sql
│
├── python/
│   └── python_analysis.py
│
├── data/
│   └── clean_orders_num.csv
│
├── outputs/
│   ├── customer_risk_table.csv
│   ├── top_50_products_by_profit.csv
│   └── worst_20_customers.csv
│
└── tableau/
    └── dashboard_link.txt

Business Impact

This analysis demonstrates how data analytics can:

Identify hidden loss drivers

Improve pricing and discount strategy

Highlight unprofitable customer relationships

Focus growth on high-margin products

Support executive decision-making with data

Author

Tricia Bleavins (tkel870)
Data Analytics | SQL | Python | Tableau | Business Intelligence
