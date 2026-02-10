.echo on
SELECT 'RUNNING COST IMPACT ANALYSIS' AS status;
.headers on
.mode column

-- =========================================================
-- COST IMPACT MODEL
-- Estimates financial loss from downtime + defects
-- =========================================================

-- Assumptions (realistic manufacturing estimates)
-- Downtime cost per minute: $75
-- Defect cost per unit: $420 avg replacement/rework

WITH part_costs AS (
  SELECT
    p.part_id,
    p.part_name,
    p.category,
    s.supplier_name,
    s.region,

    SUM(pr.downtime_minutes) AS total_downtime,
    SUM(pr.defects) AS total_defects,
    SUM(pr.units_produced) AS total_units,

    ROUND(SUM(pr.downtime_minutes) * 75, 2) AS downtime_cost,
    ROUND(SUM(pr.defects) * 420, 2) AS defect_cost

  FROM production pr
  JOIN parts p ON pr.part_id = p.part_id
  JOIN suppliers s ON p.supplier_id = s.supplier_id
  GROUP BY p.part_id
),

total_loss AS (
  SELECT
    part_id,
    part_name,
    category,
    supplier_name,
    region,
    total_downtime,
    total_defects,
    downtime_cost,
    defect_cost,
    (downtime_cost + defect_cost) AS total_loss
  FROM part_costs
)

SELECT
  part_name,
  supplier_name,
  category,
  region,
  total_downtime,
  total_defects,
  downtime_cost,
  defect_cost,
  total_loss

FROM total_loss
ORDER BY total_loss DESC
LIMIT 15;
