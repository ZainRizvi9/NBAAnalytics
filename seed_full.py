import psycopg2
import time
from nba_api.stats.endpoints import leagueleaders, commonplayerinfo

conn = psycopg2.connect(
    dbname="nba_analytics",
    user="zain",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

cur.execute("SELECT season_id, season FROM dim_seasons")
season_map = {row[1]: row[0] for row in cur.fetchall()}

cur.execute("SELECT team_id FROM dim_teams")
valid_team_ids = set(row[0] for row in cur.fetchall())

SEASONS = ['2018-19', '2019-20', '2020-21', '2021-22', '2022-23', '2023-24']

for season in SEASONS:
    print(f"\nFetching {season}...")
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
        print(f"  {len(rows)} players found")

        for row in rows:
            player_id = row.get('PLAYER_ID')
            team_id   = row.get('TEAM_ID')
            gp        = row.get('GP') or 0

            if not player_id or not team_id or gp < 10:
                continue
            if team_id not in valid_team_ids:
                continue

            # Insert player if not exists (basic info only)
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

            def pg(key):
                return round((row.get(key) or 0), 2)

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

        conn.commit()
        print(f"  Committed {season}")

    except Exception as e:
        print(f"  Error on {season}: {e}")
        conn.rollback()

cur.close()
conn.close()
print("\nFull league seeding complete.")