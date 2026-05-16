import os
import time
import psycopg2
from dagster import asset, Definitions, materialize, get_dagster_logger
from nba_api.stats.endpoints import leagueleaders

SEASONS = ['2018-19', '2019-20', '2020-21', '2021-22', '2022-23', '2023-24']


def get_conn():
    url = os.getenv("DATABASE_URL", "postgresql://zain@localhost:5432/nba_analytics")
    return psycopg2.connect(url)


@asset
def season_map() -> dict:
    """Fetch season ID mappings from dim_seasons."""
    logger = get_dagster_logger()
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT season_id, season FROM dim_seasons")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    mapping = {row[1]: row[0] for row in rows}
    logger.info(f"Loaded {len(mapping)} seasons: {list(mapping.keys())}")
    return mapping


@asset
def valid_team_ids() -> set:
    """Fetch valid team IDs from dim_teams."""
    logger = get_dagster_logger()
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT team_id FROM dim_teams")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    ids = set(row[0] for row in rows)
    logger.info(f"Loaded {len(ids)} valid team IDs")
    return ids


@asset
def raw_player_stats(season_map: dict, valid_team_ids: set) -> dict:
    """Fetch raw player stats from NBA API for all seasons."""
    logger = get_dagster_logger()
    all_data = {}

    for season in SEASONS:
        logger.info(f"Fetching {season}...")
        try:
            leaders = leagueleaders.LeagueLeaders(
                season=season,
                stat_category_abbreviation='PTS',
                per_mode48='PerGame',
                scope='S',
                season_type_all_star='Regular Season'
            )
            time.sleep(1)
            rows = leaders.get_normalized_dict()['LeagueLeaders']
            filtered = [
                r for r in rows
                if r.get('PLAYER_ID')
                and r.get('TEAM_ID') in valid_team_ids
                and (r.get('GP') or 0) >= 10
            ]
            all_data[season] = filtered
            logger.info(f"  {len(filtered)} valid players for {season}")
        except Exception as e:
            logger.error(f"  Error fetching {season}: {e}")
            all_data[season] = []

    return all_data


@asset
def loaded_player_stats(raw_player_stats: dict, season_map: dict) -> dict:
    """Insert player stats into PostgreSQL."""
    logger = get_dagster_logger()
    summary = {}

    conn = get_conn()
    cur = conn.cursor()

    for season, rows in raw_player_stats.items():
        if season not in season_map:
            logger.warning(f"Season {season} not in season_map, skipping")
            continue

        inserted = 0
        for row in rows:
            player_id = row.get('PLAYER_ID')
            team_id = row.get('TEAM_ID')
            gp = row.get('GP') or 0

            def pg(key):
                return round((row.get(key) or 0), 2)

            try:
                cur.execute("""
                    INSERT INTO dim_players
                      (player_id, full_name, position, height, weight, country,
                       draft_year, draft_round, draft_number)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (player_id) DO NOTHING
                """, (
                    player_id,
                    row.get('PLAYER', ''),
                    '', '', 0, '', None, None, None
                ))

                cur.execute("""
                    INSERT INTO fact_player_stats
                      (player_id, team_id, season_id, games_played, games_started,
                       minutes_pg, points_pg, rebounds_pg, assists_pg, steals_pg,
                       blocks_pg, fg_pct, fg3_pct, ft_pct, turnovers_pg, plus_minus)
                    VALUES (%s,%s,%s,%s,%s, %s,%s,%s,%s,%s, %s,%s,%s,%s,%s,%s)
                    ON CONFLICT DO NOTHING
                """, (
                    player_id, team_id, season_map[season],
                    gp, 0,
                    pg('MIN'), pg('PTS'), pg('REB'), pg('AST'),
                    pg('STL'), pg('BLK'),
                    row.get('FG_PCT') or 0,
                    row.get('FG3_PCT') or 0,
                    row.get('FT_PCT') or 0,
                    pg('TOV'), pg('EFF')
                ))
                inserted += 1

            except Exception as e:
                logger.error(f"Error inserting player {player_id} for {season}: {e}")
                conn.rollback()
                continue

        conn.commit()
        summary[season] = inserted
        logger.info(f"  Committed {inserted} players for {season}")

    cur.close()
    conn.close()
    return summary


defs = Definitions(
    assets=[season_map, valid_team_ids, raw_player_stats, loaded_player_stats]
)


if __name__ == "__main__":
    materialize([season_map, valid_team_ids, raw_player_stats, loaded_player_stats])