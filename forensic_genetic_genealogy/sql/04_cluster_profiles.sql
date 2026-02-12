-- Cluster Profiles: match strength + surnames + Louisiana geography

DROP VIEW IF EXISTS v_cluster_match_strength;
CREATE VIEW v_cluster_match_strength AS
SELECT
  mc.cluster_id,
  mc.match_id,
  m.cm_total,
  m.segments,
  m.longest_segment,
  m.tree_confidence
FROM match_clusters mc
JOIN matches m ON m.match_id = mc.match_id;

-- Top matches per cluster (strongest DNA)
DROP VIEW IF EXISTS v_top_matches_by_cluster;
CREATE VIEW v_top_matches_by_cluster AS
SELECT *
FROM (
  SELECT
    cluster_id,
    match_id,
    cm_total,
    tree_confidence,
    ROW_NUMBER() OVER (PARTITION BY cluster_id ORDER BY cm_total DESC) AS rn
  FROM v_cluster_match_strength
)
WHERE rn <= 10;

-- Surname counts per cluster (from linked tree persons)
DROP VIEW IF EXISTS v_surnames_by_cluster;
CREATE VIEW v_surnames_by_cluster AS
SELECT
  mc.cluster_id,
  p.last_name,
  COUNT(*) AS surname_count,
  AVG(l.confidence_level) AS avg_link_conf
FROM match_clusters mc
JOIN match_tree_links l ON l.match_id = mc.match_id
JOIN persons p ON p.person_id = l.person_id
WHERE p.last_name IS NOT NULL AND TRIM(p.last_name) <> ''
GROUP BY mc.cluster_id, p.last_name;

-- Louisiana hotspot by cluster (birth parish/state)
DROP VIEW IF EXISTS v_geo_by_cluster;
CREATE VIEW v_geo_by_cluster AS
SELECT
  mc.cluster_id,
  pl.state,
  pl.parish_or_county,
  COUNT(*) AS people_count
FROM match_clusters mc
JOIN match_tree_links l ON l.match_id = mc.match_id
JOIN persons p ON p.person_id = l.person_id
JOIN places pl ON pl.place_id = p.place_id_birth
GROUP BY mc.cluster_id, pl.state, pl.parish_or_county;
