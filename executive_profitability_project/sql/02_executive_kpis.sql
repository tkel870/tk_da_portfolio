-- 02_executive_kpis.sql
-- Purpose: Executive-level KPI snapshot for revenue, profit, margin, and scale.

SELECT
  ROUND(SUM(sales_num), 2)  AS total_revenue,
  ROUND(SUM(profit_num), 2) AS total_profit,
  ROUND(100.0 * SUM(profit_num) / NULLIF(SUM(sales_num), 0), 2) AS profit_margin_pct,
  COUNT(DISTINCT "Order ID")    AS total_orders,
  COUNT(DISTINCT "Customer ID") AS total_customers,
  COUNT(DISTINCT "Product Name") AS total_products
FROM clean_orders_num;
