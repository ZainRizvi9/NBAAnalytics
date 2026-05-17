-- models/staging/stg_league_averages.sql
-- Per-season league averages used as baselines for PVS component calculations

SELECT
    season_id,
    AVG(points_pg)    AS avg_pts,
    AVG(rebounds_pg)  AS avg_reb,
    AVG(assists_pg)   AS avg_ast,
    AVG(steals_pg)    AS avg_stl,
    AVG(blocks_pg)    AS avg_blk,
    AVG(turnovers_pg) AS avg_tov,
    AVG(fg_pct)       AS avg_fg,
    AVG(ft_pct)       AS avg_ft,
    AVG(minutes_pg)   AS avg_min,
    AVG(games_played) AS avg_gp,
    STDDEV(points_pg) AS std_pts
FROM fact_player_stats
WHERE games_played >= 20
GROUP BY season_id
