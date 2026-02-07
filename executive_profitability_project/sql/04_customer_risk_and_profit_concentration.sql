-- 04_customer_risk_and_profit_concentration.sql
-- Purpose:
-- 1) Identify unprofitable customers (customer risk).
-- 2) Prepare product profit table for Pareto / concentration analysis.

-- A) Worst customers by total profit (customer risk list)
SELECT
  "Customer ID",
  ROUND(SUM(sales_num), 2)  AS revenue,
  ROUND(SUM(profit_num), 2) AS profit,
  COUNT(DISTINCT "Order ID") AS orders,
  ROUND(100.0 * SUM(profit_num) / NULLIF(SUM(sales_num), 0), 2) AS margin_pct,
  ROUND(AVG(discount_num), 4) AS avg_discount
FROM clean_orders_num
GROUP BY "Customer ID"
HAVING profit < 0
ORDER BY profit ASC
LIMIT 20;

-- B) Product profitability table (input for Python Pareto curve)
SELECT
  "Product Name",
  ROUND(SUM(sales_num), 2)  AS revenue,
  ROUND(SUM(profit_num), 2) AS profit
FROM clean_orders_num
GROUP BY "Product Name"
ORDER BY profit DESC;
