-- Project: Player Behavior & Game Performance Analytics
-- File: 01_data_validation.sql
-- Purpose: Validate data integrity after loading into BigQuery
-- Checks: row counts, null checks, date ranges, join integrity, basic activity sanity checks

-- 1) Row counts (confirm ingestion)
SELECT
  (SELECT COUNT(*) FROM `tk-bigquery.game_analytics.players`) AS players,
  (SELECT COUNT(*) FROM `tk-bigquery.game_analytics.sessions`) AS sessions,
  (SELECT COUNT(*) FROM `tk-bigquery.game_analytics.purchases`) AS purchases,
  (SELECT COUNT(*) FROM `tk-bigquery.game_analytics.feature_flags`) AS feature_flags;

-- 2) Null checks (players)
SELECT
  COUNTIF(player_id IS NULL) AS null_player_id,
  COUNTIF(signup_date IS NULL) AS null_signup_date,
  COUNTIF(region IS NULL) AS null_region,
  COUNTIF(platform IS NULL) AS null_platform,
  COUNTIF(acquisition_channel IS NULL) AS null_acquisition_channel
FROM `tk-bigquery.game_analytics.players`;

-- 3) Date range checks

-- Players signup dates
SELECT
  MIN(signup_date) AS min_signup_date,
  MAX(signup_date) AS max_signup_date
FROM `tk-bigquery.game_analytics.players`;

-- Session dates
SELECT
  MIN(session_date) AS min_session_date,
  MAX(session_date) AS max_session_date
FROM `tk-bigquery.game_analytics.sessions`;

-- Purchase dates
SELECT
  MIN(purchase_date) AS min_purchase_date,
  MAX(purchase_date) AS max_purchase_date
FROM `tk-bigquery.game_analytics.purchases`;

-- NOTE:
-- feature_flags table included a header row imported as data
-- Created feature_flags_clean view to exclude the invalid record
-- All join integrity checks pass when using the cleaned view

-- 4) Join integrity checks (orphans)
-- Expect all orphan counts = 0
SELECT COUNT(*) AS orphan_sessions
FROM `tk-bigquery.game_analytics.sessions` s
LEFT JOIN `tk-bigquery.game_analytics.players` p
  ON s.player_id = p.player_id
WHERE p.player_id IS NULL;

SELECT COUNT(*) AS orphan_purchases
FROM `tk-bigquery.game_analytics.purchases` pu
LEFT JOIN `tk-bigquery.game_analytics.players` p
  ON pu.player_id = p.player_id
WHERE p.player_id IS NULL;

SELECT COUNT(*) AS orphan_feature_flags
FROM `tk-bigquery.game_analytics.feature_flags` f
LEFT JOIN `tk-bigquery.game_analytics.players` p
  ON f.player_id = p.player_id
WHERE p.player_id IS NULL;


-- 5) DAU sanity check
SELECT
  session_date,
  COUNT(DISTINCT player_id) AS dau
FROM `tk-bigquery.game_analytics.sessions`
GROUP BY session_date
ORDER BY session_date
LIMIT 15;



