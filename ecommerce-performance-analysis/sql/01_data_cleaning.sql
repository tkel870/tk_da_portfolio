/*
01_data_cleaning.sql

Purpose:
Clean and prepare eCommerce transaction data for analysis by:
- Removing canceled and returned transactions
- Validating quantity and price fields
- Creating revenue and time-based reporting fields

This cleaning logic mirrors real-world eCommerce and Amazon-style
performance reporting practices.
*/

CREATE OR REPLACE TABLE `tk-bigquery.portfolio_retail.online_retail_clean` AS
WITH base AS (
  SELECT
    CAST(Invoice AS STRING) AS invoice_id,
    CAST(StockCode AS STRING) AS sku,
    CAST(Description AS STRING) AS product_description,
    SAFE_CAST(Quantity AS INT64) AS quantity,

    COALESCE(
      SAFE_CAST(InvoiceDate AS DATETIME),
      DATETIME(SAFE_CAST(InvoiceDate AS TIMESTAMP)),
      SAFE.PARSE_DATETIME('%Y-%m-%d %H:%M:%S', CAST(InvoiceDate AS STRING)),
      SAFE.PARSE_DATETIME('%m/%d/%Y %H:%M', CAST(InvoiceDate AS STRING))
    ) AS invoice_datetime,

    SAFE_CAST(Price AS NUMERIC) AS unit_price,
    SAFE_CAST(CustomerID AS INT64) AS customer_id,
    CAST(Country AS STRING) AS country
  FROM `tk-bigquery.portfolio_retail.online_retail_raw`
)

SELECT
  invoice_id,
  sku,
  product_description,
  quantity,
  invoice_datetime,
  unit_price,
  customer_id,
  country,

  -- Derived metrics
  (quantity * unit_price) AS revenue,
  EXTRACT(YEAR  FROM invoice_datetime) AS invoice_year,
  EXTRACT(MONTH FROM invoice_datetime) AS invoice_month

FROM base
WHERE
  quantity IS NOT NULL
  AND unit_price IS NOT NULL
  AND invoice_datetime IS NOT NULL

  -- Completed sales only
  AND quantity > 0
  AND unit_price > 0
  AND NOT STARTS_WITH(invoice_id, 'C');
