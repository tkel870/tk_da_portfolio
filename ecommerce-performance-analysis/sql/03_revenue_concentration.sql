/*
03_revenue_concentration.sql

Purpose:
Measure revenue concentration across SKUs by calculating:
- Total revenue across all products
- Revenue contributed by the top 10 SKUs
- Percent of total revenue from the top 10 SKUs

This is useful for understanding catalog concentration risk in an
Amazon-style eCommerce business.
*/

WITH product_revenue AS (
  SELECT
    sku,
    SUM(revenue) AS sku_revenue
  FROM `tk-bigquery.portfolio_retail.online_retail_clean`
  WHERE
    -- Exclude non-merchandise revenue entries
    UPPER(product_description) NOT IN ('POSTAGE', 'DOTCOM POSTAGE', 'MANUAL')
    AND sku NOT IN ('POST', 'DOT', 'M')
  GROUP BY sku
),

ranked AS (
  SELECT
    sku,
    sku_revenue,
    RANK() OVER (ORDER BY sku_revenue DESC) AS revenue_rank
  FROM product_revenue
)

SELECT
  ROUND(SUM(CASE WHEN revenue_rank <= 10 THEN sku_revenue END), 2) AS top_10_revenue,
  ROUND(SUM(sku_revenue), 2) AS total_revenue,
  ROUND(
    SUM(CASE WHEN revenue_rank <= 10 THEN sku_revenue END)
    / SUM(sku_revenue) * 100,
    2
  ) AS pct_revenue_top_10
FROM ranked;

/*
Expected output from this project:
- pct_revenue_top_10 ≈ 9.4%
*/
