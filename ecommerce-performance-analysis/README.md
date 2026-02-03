# eCommerce Performance Analysis (Amazon-Style)

## Project Overview
This project analyzes eCommerce transaction data to evaluate product (SKU) performance,
identify revenue concentration, and flag potential product risks using an Amazon-style
analytics approach.

The analysis focuses on creating reliable, Excel- and SQL-driven insights that support
merchandising, inventory planning, and performance monitoring decisions.

---

## Dataset
- **Source:** Online Retail II (UCI / Kaggle)
- **Type:** Transaction-level eCommerce data
- **Time Period:** 2010–2011
- **Rows (after cleaning):** ~530,000
- **SKUs:** ~4,000

---

## Tools Used
- **SQL:** Google BigQuery
- **Data Cleaning & Analysis:** SQL (CTEs, window functions, aggregations)
- **Version Control:** Git & GitHub
- **Workflow:** VS Code + GitHub

---

## Key Business Questions
1. Which products generate the highest revenue?
2. How concentrated is revenue across top-performing SKUs?
3. Are there products showing signs of recent performance decline?
4. What risks or opportunities can be identified from SKU-level trends?

---

## Key Insights

### 1. Revenue Is Distributed Across a Broad Product Mix
The top 10 SKUs account for only **9.4% of total revenue**, indicating a highly diversified
catalog with low concentration risk.

### 2. Core Products Drive Consistent Performance
Several SKUs generate strong revenue through consistently high unit sales, making them
key merchandising and inventory priorities.

### 3. Premium, Low-Volume Items Show Higher Volatility
High-price, low-volume products generate meaningful revenue but exhibit sharper recent
declines, suggesting higher sensitivity to demand changes.

### 4. Multiple SKUs Show Recent Performance Declines
Comparing recent three-month performance to historical averages identified several SKUs
with declining revenue trends, signaling potential inventory or merchandising risk.

### 5. Even Top Products Require Monitoring
Some historically strong SKUs showed moderate recent softening, reinforcing the need
for ongoing performance tracking.

---

## Project Structure
ecommerce-performance-analysis/
├── README.md
├── sql/
│ ├── 01_data_cleaning.sql
│ ├── 02_top_skus.sql
│ ├── 03_revenue_concentration.sql
│ └── 04_sku_decline_flags.sql
└── insights/
└── summary.md


---

## Notes
This project emphasizes clear, explainable analysis over complex modeling to mirror
real-world junior analyst responsibilities in eCommerce and marketplace analytics roles.

