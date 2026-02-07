-- 03_loss_drivers_category_and_subcategory.sql
-- Purpose: Identify where profitability breaks down.
-- Output: Category and Sub-Category profitability ranking.

-- A) Profitability by Category
SELECT
  Category,
  ROUND(SUM(sales_num), 2)  AS revenue,
  ROUND(SUM(profit_num), 2) AS profit,
  ROUND(100.0 * SUM(profit_num) / NULLIF(SUM(sales_num), 0), 2) AS margin_pct
FROM clean_orders_num
GROUP BY Category
ORDER BY profit ASC;

-- B) Profitability by Sub-Category (find the true loss drivers)
SELECT
  "Sub-Category",
  ROUND(SUM(sales_num), 2)  AS revenue,
  ROUND(SUM(profit_num), 2) AS profit,
  ROUND(100.0 * SUM(profit_num) / NULLIF(SUM(sales_num), 0), 2) AS margin_pct
FROM clean_orders_num
GROUP BY "Sub-Category"
ORDER BY profit ASC;

-- Optional: focus on the worst offenders only
-- SELECT * FROM (
--   SELECT
--     "Sub-Category",
--     ROUND(SUM(sales_num), 2)  AS revenue,
--     ROUND(SUM(profit_num), 2) AS profit,
--     ROUND(100.0 * SUM(profit_num) / NULLIF(SUM(sales_num), 0), 2) AS margin_pct
--   FROM clean_orders_num
--   GROUP BY "Sub-Category"
-- )
-- WHERE profit < 0
-- ORDER BY profit ASC;
