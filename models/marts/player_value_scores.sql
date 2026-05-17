-- models/marts/player_value_scores.sql
-- Final PVS model — joins staged layers and computes composite Player Value Score
-- Replaces the raw CREATE VIEW in value_model.sql

WITH raw_scores AS (
    SELECT
        s.player_id,
        s.full_name,
        s.team,
        s.conference,
        s.division,
        s.season,
        s.games_played,
        s.minutes_pg,
        s.points_pg,
        s.rebounds_pg,
        s.assists_pg,
        s.steals_pg,
        s.blocks_pg,
        s.turnovers_pg,
        s.fg_pct,
        s.fg3_pct,
        s.ft_pct,
        s.plus_minus,

        -- SCORING EFFICIENCY
        (s.points_pg - la.avg_pts)
            * GREATEST(s.fg_pct / NULLIF(la.avg_fg, 0), 0.5)
            AS scoring_value,

        -- PLAYMAKING
        (s.assists_pg - la.avg_ast)
            - GREATEST(s.turnovers_pg - la.avg_tov, 0)
            AS playmaking_value,

        -- DEFENSE
        ((s.steals_pg - la.avg_stl) * 1.5)
            + ((s.blocks_pg - la.avg_blk) * 1.2)
            AS defensive_value,

        -- REBOUNDING
        (s.rebounds_pg - la.avg_reb) AS rebounding_value,

        -- CLUTCH PROXY
        GREATEST(s.ft_pct - la.avg_ft, 0) * s.points_pg * 0.1
            AS clutch_proxy,

        -- USAGE EFFICIENCY
        ((s.points_pg / NULLIF(s.minutes_pg, 0))
            - (la.avg_pts / NULLIF(la.avg_min, 0)))
            * (1.0 - LEAST(s.turnovers_pg / NULLIF(s.points_pg, 1), 0.3))
            AS usage_efficiency,

        s.games_played / 82.0  AS season_durability,
        s.minutes_pg   / 48.0  AS minutes_share,

        pc.consistency_score,
        pc.availability_rate,
        pc.seasons_in_data,
        pc.career_avg_pts

    FROM {{ ref('stg_player_stats') }} s
    JOIN {{ ref('stg_league_averages') }} la   ON s.season_id  = la.season_id
    JOIN {{ ref('stg_player_consistency') }} pc ON s.player_id = pc.player_id
)

SELECT
    full_name,
    team,
    conference,
    division,
    season,
    games_played,
    ROUND(minutes_pg::numeric,     2) AS minutes_pg,
    ROUND(points_pg::numeric,      2) AS points_pg,
    ROUND(rebounds_pg::numeric,    2) AS rebounds_pg,
    ROUND(assists_pg::numeric,     2) AS assists_pg,
    ROUND(steals_pg::numeric,      2) AS steals_pg,
    ROUND(blocks_pg::numeric,      2) AS blocks_pg,
    ROUND(turnovers_pg::numeric,   2) AS turnovers_pg,
    ROUND(fg_pct::numeric,         3) AS fg_pct,
    ROUND(fg3_pct::numeric,        3) AS fg3_pct,
    ROUND(ft_pct::numeric,         3) AS ft_pct,
    seasons_in_data,
    ROUND(career_avg_pts::numeric, 2) AS career_avg_pts,
    ROUND(scoring_value::numeric,    3) AS scoring_value,
    ROUND(playmaking_value::numeric, 3) AS playmaking_value,
    ROUND(defensive_value::numeric,  3) AS defensive_value,
    ROUND(rebounding_value::numeric, 3) AS rebounding_value,
    ROUND(clutch_proxy::numeric,     3) AS clutch_proxy,
    ROUND(usage_efficiency::numeric, 3) AS usage_efficiency,
    ROUND(consistency_score::numeric,3) AS consistency_score,
    ROUND(availability_rate::numeric,3) AS availability_rate,
    ROUND(season_durability::numeric,3) AS season_durability,

    ROUND((
        (scoring_value    * 0.30) +
        (playmaking_value * 0.20) +
        (defensive_value  * 0.20) +
        (rebounding_value * 0.15) +
        (clutch_proxy     * 0.08) +
        (usage_efficiency * 0.07)
    )
    * (0.7 + (availability_rate * 0.3))
    * (0.8 + (consistency_score * 0.2))
    * (1.0 + (minutes_share     * 0.5))
    ::numeric, 3) AS pvs

FROM raw_scores
ORDER BY pvs DESC
