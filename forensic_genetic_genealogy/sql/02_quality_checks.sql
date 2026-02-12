-- match count
SELECT COUNT(*) AS total_matches FROM matches;

-- shared match count
SELECT COUNT(*) AS total_shared_edges FROM shared_matches;

-- persons count
SELECT COUNT(*) AS total_persons FROM persons;

-- check for null cm values
SELECT COUNT(*) AS null_cm
FROM matches
WHERE cm_total IS NULL;

-- top matches by cm
SELECT match_id, cm_total
FROM matches
ORDER BY cm_total DESC
LIMIT 10;
