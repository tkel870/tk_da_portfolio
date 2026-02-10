.echo on
SELECT 'RUNNING VENDOR RISK ANALYSIS' AS status;
.headers on
.mode column

WITH ship_perf AS (
  SELECT
    sh.supplier_id,
    s.supplier_name,
    s.region,
    COUNT(*) AS shipments,
    ROUND(AVG(julianday(sh.arrival_date) - julianday(sh.ship_date)), 2) AS avg_transit_days,
    ROUND(SUM(sh.shipping_cost), 2) AS total_shipping_cost
  FROM shipments sh
  JOIN suppliers s ON sh.supplier_id = s.supplier_id
  GROUP BY sh.supplier_id
),

prod_impact AS (
  SELECT
    p.supplier_id,
    SUM(pr.downtime_minutes) AS total_downtime,
    ROUND(AVG(pr.downtime_minutes),2) AS avg_downtime,
    SUM(pr.defects) AS total_defects,
    ROUND(1.0 * SUM(pr.defects)/SUM(pr.units_produced),4) AS defect_rate
  FROM production pr
  JOIN parts p ON pr.part_id = p.part_id
  GROUP BY p.supplier_id
)

SELECT
  sp.supplier_id,
  sp.supplier_name,
  sp.region,
  sp.shipments,
  sp.avg_transit_days,
  sp.total_shipping_cost,
  pi.total_downtime,
  pi.avg_downtime,
  pi.total_defects,
  pi.defect_rate

FROM ship_perf sp
LEFT JOIN prod_impact pi
  ON sp.supplier_id = pi.supplier_id

ORDER BY avg_transit_days DESC,
         pi.avg_downtime DESC,
         pi.defect_rate DESC
LIMIT 15;
