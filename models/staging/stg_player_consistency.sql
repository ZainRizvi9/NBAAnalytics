-- models/staging/stg_player_consistency.sql
-- Career consistency and availability metrics per player

SELECT
    player_id,
    COUNT(*)          AS seasons_in_data,
    AVG(points_pg)    AS career_avg_pts,
    STDDEV(points_pg) AS pts_stddev,
    AVG(games_played) AS avg_games,
    CASE
        WHEN AVG(points_pg) > 0
        THEN 1.0 - LEAST(STDDEV(points_pg) / NULLIF(AVG(points_pg), 0), 1.0)
        ELSE 0
    END AS consistency_score,
    AVG(games_played) / 82.0 AS availability_rate
FROM fact_player_stats
WHERE games_played >= 20
GROUP BY player_id
