-- models/staging/stg_player_stats.sql
-- Cleans and standardizes raw fact_player_stats for downstream models

SELECT
    fps.player_id,
    p.full_name,
    t.abbreviation      AS team,
    t.conference,
    t.division,
    s.season,
    fps.season_id,
    fps.team_id,
    fps.games_played,
    fps.minutes_pg,
    fps.points_pg,
    fps.rebounds_pg,
    fps.assists_pg,
    fps.steals_pg,
    fps.blocks_pg,
    fps.turnovers_pg,
    fps.fg_pct,
    fps.fg3_pct,
    fps.ft_pct,
    fps.plus_minus
FROM fact_player_stats fps
JOIN dim_players p  ON fps.player_id = p.player_id
JOIN dim_teams t    ON fps.team_id   = t.team_id
JOIN dim_seasons s  ON fps.season_id = s.season_id
WHERE fps.games_played >= 20
  AND fps.minutes_pg   >= 15
