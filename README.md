# Court Vision — NBA Analytics

A full-stack NBA analytics platform that ingests real player and game data, computes a custom Player Value Score (PVS) metric, and surfaces insights through an interactive Streamlit dashboard and a Tableau visualization layer.

**Live App:** [nbaanalytics9.streamlit.app](https://nbaanalytics9.streamlit.app)

---

## Demo

https://youtu.be/6sxuP4BoEio

---

## Dashboard Preview

<!-- Replace with your Streamlit app screenshot -->
![Court Vision Dashboard](assets/dashboard.png)

---

## Tableau Dashboard

<!-- Add your Tableau dashboard screenshot here -->
![NBA Player Analytics Tableau Dashboard](assets/tableau_dashboard.png)

---

## Overview

Court Vision pulls historical NBA data across 6 seasons (2018-19 through 2023-24) using the `nba_api` Python package, stores it in a PostgreSQL database with a star schema, and computes a composite Player Value Score for each player-season combination. The frontend is built with Streamlit and Plotly, and a separate Tableau workbook provides additional business intelligence views including player salary efficiency and team-level rankings.

---

## Features

- **League Rankings** — Full player leaderboard filterable by season and conference, with top 3 featured cards showing key stats
- **Career PVS Comparison** — Multi-player career trajectory charts comparing Player Value Score over time
- **Team Analysis** — Team-level breakdowns of average player value by roster
- **Salary vs. Value** — Scatter analysis of player salary against PVS to identify over and undervalued contracts
- **Tableau Dashboard** — Separate visualization layer with bar charts, scatter plots, and team rankings built on top of the live Supabase database

---

## Tech Stack

| Layer | Technology |
|---|---|
| Data Ingestion | Python, nba_api |
| Database | PostgreSQL (Supabase) |
| Data Model | Star schema (fact_player_stats, dim_players, dim_teams, dim_seasons) |
| Value Model | Custom SQL view (player_value_scores) |
| Frontend | Streamlit, Plotly |
| BI Layer | Tableau Desktop |
| Deployment | Streamlit Community Cloud |

---

## Data Model

The database follows a star schema with one central fact table and supporting dimension tables.

```
fact_player_stats
    player_id -> dim_players
    team_id   -> dim_teams
    season_id -> dim_seasons

player_value_scores (view)
    Computed from fact_player_stats
    Includes: pvs, scoring_value, defensive_value,
              playmaking_value, rebounding_value,
              clutch_proxy, consistency_score,
              availability_rate, season_durability
```

---

## Player Value Score (PVS)

PVS is a composite metric designed to measure overall player impact in a single number. It is computed from weighted sub-scores across five dimensions:

- **Scoring Value** — Points per game adjusted for efficiency (FG%, FT%, 3P%)
- **Defensive Value** — Blocks and steals per game
- **Playmaking Value** — Assists per game with a turnover penalty
- **Rebounding Value** — Total rebounds per game weighted by position
- **Clutch Proxy** — Performance consistency across high-leverage game situations

PVS is then scaled by an **Availability Rate** and **Season Durability** factor to reflect how much of the season the player was active and healthy.

---

## Project Structure

```
NBAAnalytics/
├── app.py              # Streamlit application
├── seed_full.py        # Data ingestion and seeding script
├── value_model.sql     # SQL view definition for player_value_scores
├── requirements.txt    # Python dependencies
└── .gitignore
```

---

## Running Locally

**Prerequisites:** Python 3.10+, PostgreSQL

```bash
# Clone the repo
git clone https://github.com/ZainRizvi9/NBAAnalytics.git
cd NBAAnalytics

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variable
echo 'DATABASE_URL=postgresql://your_user@localhost:5432/nba_analytics' > .env

# Seed the database
python seed_full.py

# Run the app
streamlit run app.py
```

---

## Environment Variables

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string (local or Supabase) |

For Streamlit Cloud deployment, set this in **App Settings > Secrets**.

---

## Acknowledgements

- [nba_api](https://github.com/swar/nba_api) for providing access to NBA stats data
- [Streamlit](https://streamlit.io) for the frontend framework
- [Supabase](https://supabase.com) for hosted PostgreSQL
- [Tableau](https://www.tableau.com) for the BI visualization layer
