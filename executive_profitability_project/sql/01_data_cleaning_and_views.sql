-- 01_data_cleaning_and_views.sql
-- Purpose: Keep raw data untouched, create reproducible analytical layers.
-- Notes:
-- - CSV import into SQLite often defaults columns to TEXT.
-- - Sales/Profit include currency symbols and commas (e.g., $1,234.56), so we clean + cast.
-- - We also remove rows with blank Sales/Profit to avoid corrupt calculations.

-- View 1: remove rows with blank Sales/Profit (e.g., corrupt profit-only row)
DROP VIEW IF EXISTS clean_orders;
CREATE VIEW clean_orders AS
SELECT *
FROM orders
WHERE TRIM(Sales) != ''
  AND TRIM(Profit) != '';

-- View 2: numbers-ready analytical view (casts currency strings to REAL)
DROP VIEW IF EXISTS clean_orders_num;
CREATE VIEW clean_orders_num AS
SELECT
  "Row ID",
  "Order ID",
  "Order Date",
  "Ship Date",
  "Ship Mode",
  "Customer ID",
  "Customer Name",
  Segment,
  "Country/Region",
  City,
  State,
  "Postal Code",
  Region,
  "Product ID",
  Category,
  "Sub-Category",
  "Product Name",

  -- Clean currency formatting and cast to REAL
  CAST(REPLACE(REPLACE(Sales,'$',''),',','')  AS REAL) AS sales_num,
  CAST(REPLACE(REPLACE(Profit,'$',''),',','') AS REAL) AS profit_num,

  -- Quantity/Discount imported as TEXT; cast to REAL for analysis
  CAST(REPLACE(REPLACE(Quantity,'$',''),',','') AS REAL) AS quantity_num,
  CAST(REPLACE(REPLACE(Discount,'$',''),',','') AS REAL) AS discount_num

FROM clean_orders;

-- Quick validation checks (run as needed)
-- SELECT COUNT(*) FROM orders;
-- SELECT COUNT(*) FROM clean_orders;
-- SELECT MIN(sales_num), MAX(sales_num), MIN(profit_num), MAX(profit_num) FROM clean_orders_num;
