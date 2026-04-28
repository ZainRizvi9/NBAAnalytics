-- ─────────────────────────────────────────────────────────────────────────────
-- NBA Player Value Score (PVS) v2
-- Metrics: scoring efficiency, playmaking, defense, rebounding,
--          consistency, availability, usage efficiency, clutch proxy
-- ─────────────────────────────────────────────────────────────────────────────

CREATE OR REPLACE VIEW player_value_scores AS
WITH

-- Step 1: League averages per season (baseline for above/below average calc)
league_avg AS (
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
),

-- Step 2: Career consistency — stddev of points across seasons
--         Low stddev = consistent producer, high stddev = streaky
player_consistency AS (
    SELECT
        player_id,
        COUNT(*)                   AS seasons_in_data,
        AVG(points_pg)             AS career_avg_pts,
        STDDEV(points_pg)          AS pts_stddev,
        AVG(games_played)          AS avg_games,
        -- Consistency score: inverse of coefficient of variation
        -- Players with low variance relative to their mean score higher
        CASE
            WHEN AVG(points_pg) > 0
            THEN 1.0 - LEAST(STDDEV(points_pg) / NULLIF(AVG(points_pg), 0), 1.0)
            ELSE 0
        END AS consistency_score,
        -- Availability: average games played as fraction of 82
        AVG(games_played) / 82.0 AS availability_rate
    FROM fact_player_stats
    WHERE games_played >= 20
    GROUP BY player_id
),

-- Step 3: Per-season raw component scores
raw_scores AS (
    SELECT
        fps.player_id,
        p.full_name,
        t.abbreviation          AS team,
        t.conference,
        t.division,
        s.season,
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
        fps.plus_minus,

        -- SCORING EFFICIENCY
        -- Points above average, weighted by how efficiently they score
        -- FG% relative to league average penalizes volume scorers who are inefficient
        (fps.points_pg - la.avg_pts)
            * GREATEST(fps.fg_pct / NULLIF(la.avg_fg, 0), 0.5)
            AS scoring_value,

        -- PLAYMAKING
        -- Assists above average minus turnover burden above average
        (fps.assists_pg - la.avg_ast)
            - GREATEST(fps.turnovers_pg - la.avg_tov, 0)
            AS playmaking_value,

        -- DEFENSE
        -- Steals above average (weighted 1.5x — steals are high-impact plays)
        -- Blocks above average (weighted 1.2x)
        -- Rebounding defense component (half weight — rebounding is shared)
        ((fps.steals_pg - la.avg_stl) * 1.5)
            + ((fps.blocks_pg - la.avg_blk) * 1.2)
            AS defensive_value,

        -- REBOUNDING
        (fps.rebounds_pg - la.avg_reb) AS rebounding_value,

        -- CLUTCH PROXY
        -- FT rate (FT attempts implied from ft_pct and points) combined with
        -- FT% above average. High FT volume + high FT% = trusted in big moments.
        -- We use ft_pct above average as a proxy since we have no raw FTA
        GREATEST(fps.ft_pct - la.avg_ft, 0) * fps.points_pg * 0.1
            AS clutch_proxy,

        -- USAGE EFFICIENCY
        -- Points per minute above average, penalized by turnover rate
        -- Rewards players who produce a lot without needing excessive ball time
        ((fps.points_pg / NULLIF(fps.minutes_pg, 0))
            - (la.avg_pts / NULLIF(la.avg_min, 0)))
            * (1.0 - LEAST(fps.turnovers_pg / NULLIF(fps.points_pg, 1), 0.3))
            AS usage_efficiency,

        -- DURABILITY (this season)
        fps.games_played / 82.0 AS season_durability,

        -- MINUTES SHARE (how much of the game they play)
        fps.minutes_pg / 48.0 AS minutes_share,

        pc.consistency_score,
        pc.availability_rate,
        pc.seasons_in_data,
        pc.career_avg_pts

    FROM fact_player_stats fps
    JOIN dim_players p        ON fps.player_id = p.player_id
    JOIN dim_teams t          ON fps.team_id   = t.team_id
    JOIN dim_seasons s        ON fps.season_id = s.season_id
    JOIN league_avg la        ON fps.season_id = la.season_id
    JOIN player_consistency pc ON fps.player_id = pc.player_id
    WHERE fps.games_played >= 20
      AND fps.minutes_pg   >= 15
)

SELECT
    full_name,
    team,
    conference,
    division,
    season,
    games_played,
    ROUND(minutes_pg::numeric,    2) AS minutes_pg,
    ROUND(points_pg::numeric,     2) AS points_pg,
    ROUND(rebounds_pg::numeric,   2) AS rebounds_pg,
    ROUND(assists_pg::numeric,    2) AS assists_pg,
    ROUND(steals_pg::numeric,     2) AS steals_pg,
    ROUND(blocks_pg::numeric,     2) AS blocks_pg,
    ROUND(turnovers_pg::numeric,  2) AS turnovers_pg,
    ROUND(fg_pct::numeric,        3) AS fg_pct,
    ROUND(fg3_pct::numeric,       3) AS fg3_pct,
    ROUND(ft_pct::numeric,        3) AS ft_pct,
    seasons_in_data,
    ROUND(career_avg_pts::numeric, 2) AS career_avg_pts,

    -- Individual component scores (for transparency/breakdown in dashboard)
    ROUND(scoring_value::numeric,    3) AS scoring_value,
    ROUND(playmaking_value::numeric, 3) AS playmaking_value,
    ROUND(defensive_value::numeric,  3) AS defensive_value,
    ROUND(rebounding_value::numeric, 3) AS rebounding_value,
    ROUND(clutch_proxy::numeric,     3) AS clutch_proxy,
    ROUND(usage_efficiency::numeric, 3) AS usage_efficiency,
    ROUND(consistency_score::numeric,3) AS consistency_score,
    ROUND(availability_rate::numeric,3) AS availability_rate,
    ROUND(season_durability::numeric,3) AS season_durability,

    -- FINAL PVS FORMULA
    -- Base components weighted by basketball importance
    -- Multiplied by availability (penalizes players who miss games)
    -- Multiplied by consistency bonus (rewards sustained excellence)
    -- Multiplied by minutes share (more minutes = higher ceiling)
    ROUND((
        (scoring_value    * 0.30) +
        (playmaking_value * 0.20) +
        (defensive_value  * 0.20) +
        (rebounding_value * 0.15) +
        (clutch_proxy     * 0.08) +
        (usage_efficiency * 0.07)
    )
    * (0.7 + (availability_rate  * 0.3))   -- availability multiplier (0.7–1.0)
    * (0.8 + (consistency_score  * 0.2))   -- consistency multiplier (0.8–1.0)
    * (1.0 + (minutes_share      * 0.5))   -- minutes share boost
    ::numeric, 3) AS pvs

FROM raw_scores
ORDER BY pvs DESC;