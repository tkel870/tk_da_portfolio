-- Weight matches by strength
CREATE VIEW v_match_strength AS
SELECT
  match_id,
  cm_total,
  CASE
    WHEN cm_total >= 200 THEN 5
    WHEN cm_total >= 100 THEN 4
    WHEN cm_total >= 50 THEN 3
    WHEN cm_total >= 20 THEN 2
    ELSE 1
  END AS strength_score
FROM matches;

-- Connectivity count (cluster anchors)
CREATE VIEW v_match_connectivity AS
SELECT
  match_id_a AS match_id,
  COUNT(*) AS connections
FROM shared_matches
GROUP BY match_id_a
ORDER BY connections DESC;

-- Louisiana concentration
CREATE VIEW v_louisiana_roots AS
SELECT
  p.last_name,
  pl.state,
  COUNT(*) AS count_people
FROM persons p
JOIN places pl ON p.place_id_birth = pl.place_id
GROUP BY p.last_name, pl.state
ORDER BY count_people DESC;
