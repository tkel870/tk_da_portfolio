/*
02_top_skus.sql

Purpose:
Identify top-performing SKUs by revenue and units sold.

This script includes:
1) A raw top-SKU ranking (may include non-product entries like postage/manual)
2) A cleaned top-SKU ranking that excludes non-merchandise rows so results reflect
   true product performance (Amazon-style merchandising view).
*/

-- ------------------------------------------------------------
-- 1) Raw Top 20 SKUs by Revenue (includes non-product entries)
-- ------------------------------------------------------------
SELECT
  sku,
  product_description,
  SUM(quantity) AS units_sold,
  ROUND(SUM(revenue), 2) AS total_revenue
FROM `tk-bigquery.portfolio_retail.online_retail_clean`
GROUP BY
  sku,
  product_description
ORDER BY
  total_revenue DESC
LIMIT 20;


-- ------------------------------------------------------------
-- 2) Clean Top 20 Products by Revenue (excludes postage/manual)
-- ------------------------------------------------------------
SELECT
  sku,
  product_description,
  SUM(quantity) AS units_sold,
  ROUND(SUM(revenue), 2) AS total_revenue
FROM `tk-bigquery.portfolio_retail.online_retail_clean`
WHERE
  -- Exclude non-merchandise revenue entries
  UPPER(product_description) NOT IN ('POSTAGE', 'DOTCOM POSTAGE', 'MANUAL')
  AND sku NOT IN ('POST', 'DOT', 'M')
GROUP BY
  sku,
  product_description
ORDER BY
  total_revenue DESC
LIMIT 20;
