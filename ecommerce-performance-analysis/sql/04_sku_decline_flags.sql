/*
04_sku_decline_flags.sql

Purpose:
Flag SKUs with declining recent performance by comparing:
- Historical average monthly revenue
vs
- Average monthly revenue over the most recent 3 months

This produces an explainable "risk flag" view that can support
merchandising and inventory monitoring decisions.
*/

WITH monthly_sku_revenue AS (
  SELECT
    sku,
    DATE_TRUNC(DATE(invoice_datetime), MONTH) AS month,
    SUM(revenue) AS monthly_revenue
  FROM `tk-bigquery.portfolio_retail.online_retail_clean`
  WHERE
    -- Exclude non-merchandise revenue entries
    UPPER(product_description) NOT IN ('POSTAGE', 'DOTCOM POSTAGE', 'MANUAL')
    AND sku NOT IN ('POST', 'DOT', 'M')
  GROUP BY
    sku,
    month
),

ranked_months AS (
  SELECT
    sku,
    month,
    monthly_revenue,
    ROW_NUMBER() OVER (PARTITION BY sku ORDER BY month DESC) AS month_rank,
    COUNT(*) OVER (PARTITION BY sku) AS months_active,
    AVG(monthly_revenue) OVER (PARTITION BY sku) AS avg_monthly_revenue
  FROM monthly_sku_revenue
),

recent_vs_avg AS (
  SELECT
    sku,
    months_active,
    avg_monthly_revenue,
    AVG(CASE WHEN month_rank <= 3 THEN monthly_revenue END) AS recent_3_month_avg
  FROM ranked_months
  GROUP BY
    sku,
    months_active,
    avg_monthly_revenue
)

SELECT
  sku,
  months_active,
  ROUND(avg_monthly_revenue, 2) AS avg_monthly_revenue,
  ROUND(recent_3_month_avg, 2) AS recent_3_month_avg,
  ROUND(recent_3_month_avg - avg_monthly_revenue, 2) AS recent_vs_historical_diff
FROM recent_vs_avg
WHERE
  months_active >= 6
  AND recent_3_month_avg < avg_monthly_revenue
ORDER BY recent_vs_historical_diff ASC
LIMIT 20;
