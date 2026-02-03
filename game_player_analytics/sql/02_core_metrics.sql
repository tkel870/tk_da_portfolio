-- Project: Player Behavior & Game Performance Analytics
-- File: 02_core_metrics.sql
-- Purpose: Analyze core engagement and monetization metrics
-- Metrics: DAU, WAU, retention, ARPU, and A/B test comparison

-- 1) Daily Active Users (DAU)
SELECT
  session_date,
  COUNT(DISTINCT player_id) AS dau
FROM `tk-bigquery.game_analytics.sessions`
GROUP BY session_date
ORDER BY session_date;

-- 2) Weekly Active Users (WAU)
SELECT
  DATE_TRUNC(session_date, WEEK) AS week_start,
  COUNT(DISTINCT player_id) AS wau
FROM `tk-bigquery.game_analytics.sessions`
GROUP BY week_start
ORDER BY week_start;

-- 3) Retention: Day 1 / Day 7 / Day 30

WITH first_session AS (
  SELECT
    player_id,
    MIN(session_date) AS first_play_date
  FROM `tk-bigquery.game_analytics.sessions`
  GROUP BY player_id
),
activity AS (
  SELECT DISTINCT
    s.player_id,
    DATE_DIFF(s.session_date, f.first_play_date, DAY) AS days_since_first_play
  FROM `tk-bigquery.game_analytics.sessions` s
  JOIN first_session f
    ON s.player_id = f.player_id
)
SELECT
  COUNT(DISTINCT player_id) AS total_players,
  COUNT(DISTINCT IF(days_since_first_play = 1, player_id, NULL)) AS day_1_retained,
  COUNT(DISTINCT IF(days_since_first_play = 7, player_id, NULL)) AS day_7_retained,
  COUNT(DISTINCT IF(days_since_first_play = 30, player_id, NULL)) AS day_30_retained
FROM activity;

-- 4) Average Revenue Per User (ARPU)

WITH revenue_per_player AS (
  SELECT
    player_id,
    SUM(revenue) AS total_revenue
  FROM `tk-bigquery.game_analytics.purchases`
  GROUP BY player_id
)
SELECT
  ROUND(SUM(total_revenue) / COUNT(DISTINCT player_id), 2) AS arpu
FROM revenue_per_player;

-- 5) A/B Test: Control vs Variant (Engagement & Revenue)

WITH player_metrics AS (
  SELECT
    f.test_group,
    s.player_id,
    COUNT(s.session_id) AS sessions,
    SUM(s.session_length_min) AS total_minutes,
    SUM(pu.revenue) AS revenue
  FROM `tk-bigquery.game_analytics.feature_flags_clean` f
  LEFT JOIN `tk-bigquery.game_analytics.sessions` s
    ON f.player_id = s.player_id
  LEFT JOIN `tk-bigquery.game_analytics.purchases` pu
    ON f.player_id = pu.player_id
  GROUP BY f.test_group, s.player_id
)
SELECT
  test_group,
  COUNT(DISTINCT player_id) AS players,
  ROUND(AVG(sessions), 2) AS avg_sessions_per_player,
  ROUND(AVG(total_minutes), 2) AS avg_minutes_per_player,
  ROUND(AVG(IFNULL(revenue, 0)), 2) AS avg_revenue_per_player
FROM player_metrics
GROUP BY test_group;

-- Insight:
-- The Variant group outperformed Control across engagement and monetization metrics.
-- Variant players averaged more sessions (+9%), higher total playtime (+15%),
-- and higher revenue per player (+28%), suggesting the new feature
-- positively impacts both player experience and business outcomes.

