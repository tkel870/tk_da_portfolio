SELECT 'RUNNING OVERVIEW FILE' AS status;

-- =========================================================
-- 01_data_overview.sql
-- Industrial Operations War Room — Data Overview + Health
-- =========================================================

PRAGMA foreign_keys = ON;

-- -------------------------
-- Row counts
-- -------------------------
SELECT 'suppliers' AS table_name, COUNT(*) AS rows FROM suppliers
UNION ALL SELECT 'parts', COUNT(*) FROM parts
UNION ALL SELECT 'shipments', COUNT(*) FROM shipments
UNION ALL SELECT 'inventory', COUNT(*) FROM inventory
UNION ALL SELECT 'production', COUNT(*) FROM production;

-- -------------------------
-- Date coverage (shipments + production)
-- -------------------------
SELECT
  'shipments' AS dataset,
  MIN(ship_date) AS min_date,
  MAX(ship_date) AS max_date,
  MIN(arrival_date) AS min_arrival,
  MAX(arrival_date) AS max_arrival
FROM shipments;

SELECT
  'production' AS dataset,
  MIN(production_date) AS min_date,
  MAX(production_date) AS max_date
FROM production;

-- -------------------------
-- Key null checks (should be 0)
-- -------------------------
SELECT 'shipments_null_keys' AS check_name,
       SUM(CASE WHEN shipment_id IS NULL THEN 1 ELSE 0 END) +
       SUM(CASE WHEN supplier_id IS NULL THEN 1 ELSE 0 END) +
       SUM(CASE WHEN part_id IS NULL THEN 1 ELSE 0 END) +
       SUM(CASE WHEN ship_date IS NULL THEN 1 ELSE 0 END) AS null_key_count
FROM shipments;

SELECT 'production_null_keys' AS check_name,
       SUM(CASE WHEN production_id IS NULL THEN 1 ELSE 0 END) +
       SUM(CASE WHEN part_id IS NULL THEN 1 ELSE 0 END) +
       SUM(CASE WHEN production_date IS NULL THEN 1 ELSE 0 END) AS null_key_count
FROM production;

-- -------------------------
-- Orphan checks (should be 0)
-- -------------------------
SELECT 'parts_missing_supplier' AS check_name, COUNT(*) AS issue_count
FROM parts p
LEFT JOIN suppliers s ON p.supplier_id = s.supplier_id
WHERE s.supplier_id IS NULL;

SELECT 'shipments_missing_part' AS check_name, COUNT(*) AS issue_count
FROM shipments sh
LEFT JOIN parts p ON sh.part_id = p.part_id
WHERE p.part_id IS NULL;

SELECT 'production_missing_part' AS check_name, COUNT(*) AS issue_count
FROM production pr
LEFT JOIN parts p ON pr.part_id = p.part_id
WHERE p.part_id IS NULL;

-- -------------------------
-- Quick business distributions
-- -------------------------
SELECT region, COUNT(*) AS suppliers
FROM suppliers
GROUP BY region
ORDER BY suppliers DESC;

SELECT category, COUNT(*) AS parts
FROM parts
GROUP BY category
ORDER BY parts DESC;

SELECT plant, COUNT(*) AS production_rows
FROM production
GROUP BY plant
ORDER BY production_rows DESC;

-- -------------------------
-- Delay summary (arrival - ship)
-- -------------------------
SELECT
  ROUND(AVG(julianday(arrival_date) - julianday(ship_date)), 2) AS avg_transit_days,
  ROUND(MIN(julianday(arrival_date) - julianday(ship_date)), 2) AS min_transit_days,
  ROUND(MAX(julianday(arrival_date) - julianday(ship_date)), 2) AS max_transit_days
FROM shipments;
