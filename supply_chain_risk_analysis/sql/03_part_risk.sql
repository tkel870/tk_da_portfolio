.echo on
SELECT 'RUNNING PART RISK ANALYSIS' AS status;
.headers on
.mode column

-- =========================================================
-- PART RISK SCORECARD
-- Goal: identify parts driving downtime + defects + cost
-- =========================================================

WITH part_prod AS (
  SELECT
    pr.part_id,
    COUNT(*) AS production_rows,
    SUM(pr.units_produced) AS total_units,
    SUM(pr.downtime_minutes) AS total_downtime,
    ROUND(AVG(pr.downtime_minutes), 2) AS avg_downtime,
    SUM(pr.defects) AS total_defects,
    ROUND(1.0 * SUM(pr.defects) / NULLIF(SUM(pr.units_produced),0), 4) AS defect_rate
  FROM production pr
  GROUP BY pr.part_id
),

part_ship AS (
  SELECT
    sh.part_id,
    COUNT(*) AS shipments,
    ROUND(AVG(julianday(sh.arrival_date) - julianday(sh.ship_date)), 2) AS avg_transit_days,
    ROUND(SUM(sh.shipping_cost), 2) AS total_shipping_cost
  FROM shipments sh
  GROUP BY sh.part_id
)

SELECT
  p.part_id,
  p.part_name,
  p.category,
  p.unit_cost,
  s.supplier_name,
  s.region,

  ps.shipments,
  ps.avg_transit_days,
  ps.total_shipping_cost,

  pp.production_rows,
  pp.total_units,
  pp.total_downtime,
  pp.avg_downtime,
  pp.total_defects,
  pp.defect_rate

FROM parts p
JOIN suppliers s ON p.supplier_id = s.supplier_id
LEFT JOIN part_ship ps ON p.part_id = ps.part_id
LEFT JOIN part_prod pp ON p.part_id = pp.part_id

-- Focus on meaningful parts (avoid tiny/noise)
WHERE pp.production_rows >= 10

ORDER BY
  pp.total_downtime DESC,
  pp.defect_rate DESC,
  ps.avg_transit_days DESC
LIMIT 20;
