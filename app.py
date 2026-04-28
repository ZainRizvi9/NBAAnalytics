import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import psycopg2

st.set_page_config(
    page_title="Court Vision — NBA Analytics",
    page_icon="🏀",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@300;400;600;700;800;900&family=Barlow:wght@300;400;500;600&family=JetBrains+Mono:wght@300;400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body, [class*="css"] { font-family: 'Barlow', sans-serif; background-color: #0a0a0f; color: #e8e8f0; }
.stApp { background: #0a0a0f; }
.block-container { padding: 1.5rem 2rem 3rem !important; max-width: 100% !important; }
section[data-testid="stSidebar"] { background: #0f0f1a !important; border-right: 1px solid #1c1c2e; }
section[data-testid="stSidebar"] > div { padding: 1.5rem 1rem; }
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

.cv-logo { font-family:'Barlow Condensed',sans-serif; font-size:1.5rem; font-weight:900; letter-spacing:0.05em; text-transform:uppercase; color:#fff; margin-bottom:0.2rem; }
.cv-logo span { color:#C9082A; }
.cv-tagline { font-family:'JetBrains Mono',monospace; font-size:0.6rem; color:#3a3a5c; letter-spacing:0.15em; text-transform:uppercase; margin-bottom:1.5rem; }

.stat-card { background:#0f0f1a; padding:1.2rem 1.5rem; position:relative; overflow:hidden; border:1px solid #1c1c2e; border-radius:8px; }
.stat-card::before { content:''; position:absolute; top:0; left:0; right:0; height:2px; background:linear-gradient(90deg,#C9082A,transparent); }
.stat-label { font-family:'JetBrains Mono',monospace; font-size:0.6rem; color:#3a3a5c; letter-spacing:0.15em; text-transform:uppercase; margin-bottom:0.4rem; }
.stat-value { font-family:'Barlow Condensed',sans-serif; font-size:2.2rem; font-weight:800; color:#fff; line-height:1; }
.stat-value.orange { color:#C9082A; }
.stat-sub { font-size:0.75rem; color:#3a3a5c; margin-top:0.3rem; }

.podium-card { background:#0f0f1a; padding:1.5rem; position:relative; overflow:hidden; }
.podium-card.gold { background:linear-gradient(135deg,#0f0f1a 0%,#0a0010 100%); }
.podium-card.gold::after { content:''; position:absolute; top:0; left:0; right:0; height:3px; background:linear-gradient(90deg,#f5c518,#ff9500); }
.podium-card.silver::after { content:''; position:absolute; top:0; left:0; right:0; height:3px; background:linear-gradient(90deg,#c0c0c0,#8a8a8a); }
.podium-card.bronze::after { content:''; position:absolute; top:0; left:0; right:0; height:3px; background:linear-gradient(90deg,#cd7f32,#8b4513); }
.podium-rank { font-family:'Barlow Condensed',sans-serif; font-size:3.5rem; font-weight:900; color:#1c1c2e; position:absolute; right:1rem; top:0.5rem; line-height:1; }
.podium-name { font-family:'Barlow Condensed',sans-serif; font-size:1.4rem; font-weight:800; color:#fff; text-transform:uppercase; letter-spacing:0.03em; margin-bottom:0.2rem; }
.podium-team { font-family:'JetBrains Mono',monospace; font-size:0.65rem; color:#5a5a7a; letter-spacing:0.1em; margin-bottom:0.8rem; }
.podium-pvs { font-family:'Barlow Condensed',sans-serif; font-size:2.8rem; font-weight:900; color:#C9082A; line-height:1; }
.podium-pvs-label { font-family:'JetBrains Mono',monospace; font-size:0.55rem; color:#3a3a5c; letter-spacing:0.15em; text-transform:uppercase; }
.podium-stats { margin-top:0.8rem; display:flex; gap:0.8rem; }
.podium-stat { font-family:'Barlow Condensed',sans-serif; font-size:0.85rem; color:#5a5a7a; }
.podium-stat b { color:#c0c0d0; }

.page-header { margin-bottom:2rem; padding-bottom:1.2rem; border-bottom:1px solid #181828; }
.page-title { font-family:'Barlow Condensed',sans-serif; font-size:3rem; font-weight:900; letter-spacing:-0.02em; text-transform:uppercase; color:#fff; line-height:1; }
.page-title span { color:#C9082A; }
.page-sub { font-family:'JetBrains Mono',monospace; font-size:0.65rem; color:#3a3a5c; letter-spacing:0.15em; text-transform:uppercase; margin-top:0.4rem; }

.section-head { font-family:'Barlow Condensed',sans-serif; font-size:1.3rem; font-weight:800; text-transform:uppercase; letter-spacing:0.06em; color:#fff; margin:2rem 0 1rem; display:flex; align-items:center; gap:0.8rem; }
.section-head::after { content:''; flex:1; height:1px; background:#1c1c2e; }

.vs-badge { font-family:'Barlow Condensed',sans-serif; font-size:2rem; font-weight:900; color:#2a2a3e; text-align:center; padding-top:2.5rem; }

.winner-banner { background:linear-gradient(135deg,rgba(201,8,42,0.1),rgba(201,8,42,0.05)); border:1px solid rgba(201,8,42,0.3); border-radius:10px; padding:1rem 1.5rem; margin-bottom:1.5rem; }
.winner-label { font-family:'JetBrains Mono',monospace; font-size:0.6rem; color:#C9082A; letter-spacing:0.15em; text-transform:uppercase; }
.winner-name { font-family:'Barlow Condensed',sans-serif; font-size:1.6rem; font-weight:900; color:#fff; text-transform:uppercase; }
.winner-margin { font-family:'JetBrains Mono',monospace; font-size:0.75rem; color:#5a5a7a; }

.weights-box { background:#0f0f1a; border:1px solid #1c1c2e; border-radius:8px; padding:1rem; margin-top:1rem; }
.weights-row { display:flex; justify-content:space-between; align-items:center; padding:0.3rem 0; border-bottom:1px solid #181828; }
.weights-row:last-child { border-bottom:none; }
.weights-label { font-family:'JetBrains Mono',monospace; font-size:0.65rem; color:#5a5a7a; letter-spacing:0.08em; }
.weights-val { font-family:'Barlow Condensed',sans-serif; font-size:0.95rem; font-weight:700; color:#C9082A; }

.stSelectbox > div > div { background:#0f0f1a !important; border-color:#1c1c2e !important; color:#e8e8f0 !important; }
hr { border-color:#1c1c2e !important; }
</style>
""", unsafe_allow_html=True)

# ── DB ────────────────────────────────────────────────────────────────────────
@st.cache_resource
def get_conn():
    import os
    from dotenv import load_dotenv
    load_dotenv()
    url = os.getenv("DATABASE_URL", "postgresql://zain@localhost:5432/nba_analytics")
    return psycopg2.connect(url)

@st.cache_data(ttl=300)
def q(sql):
    return pd.read_sql(sql, get_conn())

SEASONS = ['2018-19', '2019-20', '2020-21', '2021-22', '2022-23', '2023-24']

def base_layout(**extra):
    layout = dict(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Barlow, sans-serif', color='#5a5a7a', size=11),
        margin=dict(l=0, r=0, t=30, b=0),
    )
    layout.update(extra)
    return layout

def ax():
    return dict(gridcolor='#181828', zeroline=False, linecolor='#1c1c2e', tickfont=dict(color='#5a5a7a'))

def chart(fig, height=350):
    fig.update_layout(height=height)
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="cv-logo">Court<span>Vision</span></div>
    <div class="cv-tagline">NBA Player Analytics Engine</div>
    """, unsafe_allow_html=True)

    page = st.radio("", [
        "League Rankings",
        "Player Deep Dive",
        "Season Trends",
        "Conference Battle",
        "Trade Analyzer"
    ], label_visibility="collapsed")

    st.markdown("""
    <div style="margin-top:1.5rem">
    <div class="weights-box">
    <div class="weights-row"><span class="weights-label">Scoring Efficiency</span><span class="weights-val">30%</span></div>
    <div class="weights-row"><span class="weights-label">Defense</span><span class="weights-val">20%</span></div>
    <div class="weights-row"><span class="weights-label">Playmaking</span><span class="weights-val">20%</span></div>
    <div class="weights-row"><span class="weights-label">Rebounding</span><span class="weights-val">15%</span></div>
    <div class="weights-row"><span class="weights-label">Clutch Proxy</span><span class="weights-val">8%</span></div>
    <div class="weights-row"><span class="weights-label">Usage Efficiency</span><span class="weights-val">7%</span></div>
    </div>
    <div style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;color:#2a2a40;margin-top:0.8rem;letter-spacing:0.1em">
    × AVAILABILITY × CONSISTENCY × MINUTES SHARE
    </div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# PAGE 1 — LEAGUE RANKINGS
# ─────────────────────────────────────────────────────────────────────────────
if page == "League Rankings":
    st.markdown("""
    <div class="page-header">
        <div class="page-title">League <span>Rankings</span></div>
        <div class="page-sub">Player Value Score — composite metric across 1,400+ players · 6 seasons</div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns([2, 2, 3])
    with c1:
        season = st.selectbox("Season", SEASONS[::-1])
    with c2:
        conf = st.selectbox("Conference", ["All", "East", "West"])
    with c3:
        top_n = st.slider("Players shown", 10, 50, 20)

    where = f"season = '{season}'"
    if conf != "All":
        where += f" AND conference = '{conf}'"

    df = q(f"""
        SELECT full_name, team, conference, pvs,
               scoring_value, defensive_value, playmaking_value,
               rebounding_value, clutch_proxy, consistency_score,
               availability_rate, points_pg, assists_pg, rebounds_pg,
               steals_pg, blocks_pg, games_played, minutes_pg, fg_pct
        FROM player_value_scores WHERE {where}
        ORDER BY pvs DESC LIMIT {top_n}
    """)

    if df.empty:
        st.warning("No data for this selection.")
    else:
        # Podium
        st.markdown('<div class="section-head">Top 3 This Season</div>', unsafe_allow_html=True)
        podium_grid = '<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:1px;background:#1c1c2e;border-radius:12px;overflow:hidden;margin-bottom:2rem">'
        classes = ['gold', 'silver', 'bronze']
        ranks = ['01', '02', '03']
        for i in range(min(3, len(df))):
            r = df.iloc[i]
            podium_grid += f"""
            <div class="podium-card {classes[i]}">
                <div class="podium-rank">{ranks[i]}</div>
                <div class="podium-name">{r['full_name']}</div>
                <div class="podium-team">{r['team']} · {r['conference']}ERN CONF</div>
                <div class="podium-pvs">{r['pvs']:.2f}</div>
                <div class="podium-pvs-label">Player Value Score</div>
                <div class="podium-stats">
                    <div class="podium-stat"><b>{r['points_pg']:.1f}</b> PTS</div>
                    <div class="podium-stat"><b>{r['assists_pg']:.1f}</b> AST</div>
                    <div class="podium-stat"><b>{r['rebounds_pg']:.1f}</b> REB</div>
                    <div class="podium-stat"><b>{r['games_played']}</b> GP</div>
                </div>
            </div>"""
        podium_grid += '</div>'
        st.markdown(podium_grid, unsafe_allow_html=True)

        # Bar chart
        st.markdown('<div class="section-head">Full Rankings</div>', unsafe_allow_html=True)
        fig = go.Figure(go.Bar(
            x=df['pvs'], y=df['full_name'], orientation='h',
            marker=dict(
                color=df['pvs'],
                colorscale=[[0,'#1c1c2e'],[0.5,'#8B0000'],[1,'#C9082A']],
                line=dict(width=0)
            ),
            text=[f"<b>{v:.2f}</b>" for v in df['pvs']],
            textposition='outside',
            textfont=dict(color='#5a5a7a', size=10)
        ))
        fig.update_layout(
            **base_layout(),
            height=max(400, top_n * 22),
            yaxis=dict(autorange='reversed', gridcolor='#181828', tickfont=dict(color='#c0c0d0', size=11), zeroline=False, linecolor='#1c1c2e'),
            xaxis=dict(gridcolor='#181828', zeroline=False, linecolor='#1c1c2e', tickfont=dict(color='#5a5a7a')),
            bargap=0.3
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

        # Radar
        st.markdown('<div class="section-head">Component DNA — Top 5</div>', unsafe_allow_html=True)
        top5 = df.head(5)
        cats = ['Scoring', 'Defense', 'Playmaking', 'Rebounding', 'Clutch']
        colors = ['#C9082A', '#17408B', '#50c878', '#f5c518', '#c084fc']
        fills = ['rgba(201,8,42,0.12)', 'rgba(23,64,139,0.12)', 'rgba(80,200,120,0.12)', 'rgba(245,197,24,0.12)', 'rgba(192,132,252,0.12)']
        fig2 = go.Figure()
        for idx, (_, row) in enumerate(top5.iterrows()):
            vals = [max(float(row[c]), 0) for c in ['scoring_value','defensive_value','playmaking_value','rebounding_value','clutch_proxy']]
            fig2.add_trace(go.Scatterpolar(
                r=vals + [vals[0]], theta=cats + [cats[0]],
                fill='toself', name=row['full_name'],
                line=dict(color=colors[idx], width=2),
                fillcolor=fills[idx]
            ))
        fig2.update_layout(
            **base_layout(),
            height=420,
            polar=dict(
                bgcolor='rgba(0,0,0,0)',
                radialaxis=dict(visible=True, gridcolor='#1c1c2e', tickfont=dict(color='#3a3a5c', size=9), linecolor='#1c1c2e'),
                angularaxis=dict(gridcolor='#1c1c2e', linecolor='#1c1c2e', tickfont=dict(color='#8888aa', size=11))
            ),
            legend=dict(orientation='h', y=-0.15, font=dict(color='#8888aa', size=10))
        )
        st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})

        # Table
        st.markdown('<div class="section-head">Full Data Table</div>', unsafe_allow_html=True)
        tbl = df[['full_name','team','conference','pvs','points_pg','assists_pg',
                  'rebounds_pg','steals_pg','blocks_pg','fg_pct','games_played',
                  'consistency_score','availability_rate']].copy()
        tbl.columns = ['Player','Team','Conf','PVS','PPG','APG','RPG','STL','BLK','FG%','GP','Consistency','Availability']
        tbl = tbl.reset_index(drop=True)
        tbl.index += 1
        tbl['FG%'] = tbl['FG%'].apply(lambda x: f"{x:.1%}")
        tbl['Consistency'] = tbl['Consistency'].apply(lambda x: f"{x:.2f}")
        tbl['Availability'] = tbl['Availability'].apply(lambda x: f"{x:.1%}")
        tbl['PVS'] = tbl['PVS'].apply(lambda x: f"{x:.2f}")
        st.dataframe(tbl, use_container_width=True, height=400)

# ─────────────────────────────────────────────────────────────────────────────
# PAGE 2 — PLAYER DEEP DIVE
# ─────────────────────────────────────────────────────────────────────────────
elif page == "Player Deep Dive":
    st.markdown("""
    <div class="page-header">
        <div class="page-title">Player <span>Deep Dive</span></div>
        <div class="page-sub">Career trajectory · Value breakdown · Season-by-season analysis</div>
    </div>
    """, unsafe_allow_html=True)

    players = q("SELECT DISTINCT full_name FROM player_value_scores ORDER BY full_name")
    player = st.selectbox("Select Player", players['full_name'].tolist())

    df = q(f"SELECT * FROM player_value_scores WHERE full_name = '{player}' ORDER BY season")

    if df.empty:
        st.warning("No data found.")
    else:
        latest = df.iloc[-1]

        stats = [
            ("PVS Score", f"{latest['pvs']:.2f}", "orange"),
            ("PPG", f"{latest['points_pg']:.1f}", ""),
            ("APG", f"{latest['assists_pg']:.1f}", ""),
            ("RPG", f"{latest['rebounds_pg']:.1f}", ""),
            ("STL", f"{latest['steals_pg']:.1f}", ""),
            ("BLK", f"{latest['blocks_pg']:.1f}", ""),
            ("GP", f"{latest['games_played']}", ""),
            ("Avail.", f"{latest['availability_rate']:.0%}", ""),
            ("Consist.", f"{latest['consistency_score']:.2f}", ""),
        ]
        cols = st.columns(len(stats))
        for col, (label, val, cls) in zip(cols, stats):
            with col:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-label">{label}</div>
                    <div class="stat-value {cls}">{val}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        col_l, col_r = st.columns(2)

        with col_l:
            st.markdown('<div class="section-head">PVS Career Arc</div>', unsafe_allow_html=True)
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df['season'], y=df['pvs'], mode='lines+markers',
                line=dict(color='#C9082A', width=3),
                marker=dict(size=8, color='#C9082A', line=dict(color='#0a0a0f', width=2)),
                fill='tozeroy', fillcolor='rgba(201,8,42,0.08)', name='PVS'
            ))
            fig.update_layout(
                **base_layout(),
                height=280,
                xaxis=dict(**ax()),
                yaxis=dict(**ax())
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

        with col_r:
            st.markdown('<div class="section-head">Scoring Profile</div>', unsafe_allow_html=True)
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(x=df['season'], y=df['points_pg'], marker_color='rgba(201,8,42,0.7)', name='PPG'))
            fig2.add_trace(go.Scatter(x=df['season'], y=df['assists_pg'], mode='lines+markers', line=dict(color='#17408B', width=2), marker=dict(size=6), name='APG'))
            fig2.add_trace(go.Scatter(x=df['season'], y=df['rebounds_pg'], mode='lines+markers', line=dict(color='#50c878', width=2), marker=dict(size=6), name='RPG'))
            fig2.update_layout(
                **base_layout(),
                height=280,
                xaxis=dict(**ax()),
                yaxis=dict(**ax()),
                legend=dict(orientation='h', y=1.15, font=dict(color='#8888aa', size=10))
            )
            st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})

        st.markdown('<div class="section-head">Value Breakdown by Season</div>', unsafe_allow_html=True)
        comps = ['scoring_value','playmaking_value','defensive_value','rebounding_value','clutch_proxy']
        labels = ['Scoring','Playmaking','Defense','Rebounding','Clutch']
        colors_comp = ['#C9082A','#17408B','#e74c3c','#50c878','#c084fc']
        fig3 = go.Figure()
        for comp, label, color in zip(comps, labels, colors_comp):
            fig3.add_trace(go.Bar(name=label, x=df['season'], y=df[comp].clip(lower=0), marker_color=color, marker_line_width=0))
        fig3.update_layout(
            **base_layout(),
            barmode='stack',
            height=300,
            xaxis=dict(**ax()),
            yaxis=dict(**ax()),
            legend=dict(orientation='h', y=1.12, font=dict(color='#8888aa', size=10))
        )
        st.plotly_chart(fig3, use_container_width=True, config={'displayModeBar': False})

        st.markdown('<div class="section-head">Season-by-Season Stats</div>', unsafe_allow_html=True)
        tbl = df[['season','team','pvs','points_pg','assists_pg','rebounds_pg','steals_pg','blocks_pg','fg_pct','ft_pct','games_played']].copy()
        tbl.columns = ['Season','Team','PVS','PPG','APG','RPG','STL','BLK','FG%','FT%','GP']
        tbl['FG%'] = tbl['FG%'].apply(lambda x: f"{x:.1%}")
        tbl['FT%'] = tbl['FT%'].apply(lambda x: f"{x:.1%}")
        tbl['PVS'] = tbl['PVS'].apply(lambda x: f"{x:.2f}")
        st.dataframe(tbl.reset_index(drop=True), use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# PAGE 3 — SEASON TRENDS
# ─────────────────────────────────────────────────────────────────────────────
elif page == "Season Trends":
    st.markdown("""
    <div class="page-header">
        <div class="page-title">Season <span>Trends</span></div>
        <div class="page-sub">League evolution · Most improved · Biggest declines</div>
    </div>
    """, unsafe_allow_html=True)

    league = q("""
        SELECT season, AVG(pvs) AS avg_pvs, AVG(points_pg) AS avg_ppg,
               AVG(assists_pg) AS avg_apg, AVG(rebounds_pg) AS avg_rpg,
               AVG(defensive_value) AS avg_def, COUNT(*) AS players
        FROM player_value_scores GROUP BY season ORDER BY season
    """)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-head">Average PVS by Season</div>', unsafe_allow_html=True)
        fig = go.Figure(go.Scatter(
            x=league['season'], y=league['avg_pvs'], mode='lines+markers',
            line=dict(color='#C9082A', width=3),
            marker=dict(size=8, color='#C9082A', line=dict(color='#0a0a0f', width=2)),
            fill='tozeroy', fillcolor='rgba(201,8,42,0.06)'
        ))
        fig.update_layout(**base_layout(), height=260, xaxis=dict(**ax()), yaxis=dict(**ax()))
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    with c2:
        st.markdown('<div class="section-head">League Scoring Trends</div>', unsafe_allow_html=True)
        fig2 = go.Figure()
        for col, label, color in [('avg_ppg','PPG','#C9082A'),('avg_apg','APG','#17408B'),('avg_rpg','RPG','#50c878')]:
            fig2.add_trace(go.Scatter(x=league['season'], y=league[col], mode='lines+markers', name=label, line=dict(color=color, width=2), marker=dict(size=6)))
        fig2.update_layout(
            **base_layout(), height=260,
            xaxis=dict(**ax()), yaxis=dict(**ax()),
            legend=dict(orientation='h', y=1.15, font=dict(color='#8888aa', size=10))
        )
        st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})

    st.markdown('<div class="section-head">Most Improved — 2022-23 to 2023-24</div>', unsafe_allow_html=True)
    improved = q("""
        SELECT a.full_name, a.team,
               ROUND(b.pvs::numeric,2) AS pvs_prev,
               ROUND(a.pvs::numeric,2) AS pvs_curr,
               ROUND((a.pvs-b.pvs)::numeric,2) AS gain
        FROM player_value_scores a
        JOIN player_value_scores b ON a.full_name=b.full_name
        WHERE a.season='2023-24' AND b.season='2022-23' AND a.games_played>=30
        ORDER BY gain DESC LIMIT 15
    """)
    fig3 = go.Figure(go.Bar(
        x=improved['gain'], y=improved['full_name'], orientation='h',
        marker=dict(color=improved['gain'], colorscale=[[0,'#1a2a1a'],[1,'#50c878']], line=dict(width=0)),
        text=[f"+{v:.2f}" for v in improved['gain']],
        textposition='outside', textfont=dict(color='#50c878', size=10)
    ))
    fig3.update_layout(
        **base_layout(), height=420,
        yaxis=dict(autorange='reversed', gridcolor='#181828', tickfont=dict(color='#c0c0d0', size=11), zeroline=False, linecolor='#1c1c2e'),
        xaxis=dict(**ax()),
        bargap=0.3
    )
    st.plotly_chart(fig3, use_container_width=True, config={'displayModeBar': False})

    st.markdown('<div class="section-head">Biggest Declines — 2022-23 to 2023-24</div>', unsafe_allow_html=True)
    declined = q("""
        SELECT a.full_name, a.team,
               ROUND(b.pvs::numeric,2) AS pvs_prev,
               ROUND(a.pvs::numeric,2) AS pvs_curr,
               ROUND((a.pvs-b.pvs)::numeric,2) AS change
        FROM player_value_scores a
        JOIN player_value_scores b ON a.full_name=b.full_name
        WHERE a.season='2023-24' AND b.season='2022-23' AND a.games_played>=30
        ORDER BY change ASC LIMIT 10
    """)
    st.dataframe(declined.reset_index(drop=True), use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# PAGE 4 — CONFERENCE BATTLE
# ─────────────────────────────────────────────────────────────────────────────
elif page == "Conference Battle":
    st.markdown("""
    <div class="page-header">
        <div class="page-title">Conference <span>Battle</span></div>
        <div class="page-sub">East vs West · Who dominates the value model?</div>
    </div>
    """, unsafe_allow_html=True)

    conf_df = q("""
        SELECT conference, season,
               ROUND(AVG(pvs)::numeric,3) AS avg_pvs,
               ROUND(AVG(points_pg)::numeric,2) AS avg_ppg,
               ROUND(AVG(defensive_value)::numeric,3) AS avg_def,
               COUNT(*) AS players
        FROM player_value_scores
        WHERE conference IN ('East','West')
        GROUP BY conference, season ORDER BY season, conference
    """)

    fig = go.Figure()
    for conf, color in [('East','#17408B'),('West','#C9082A')]:
        sub = conf_df[conf_df['conference']==conf]
        fig.add_trace(go.Scatter(
            x=sub['season'], y=sub['avg_pvs'], mode='lines+markers', name=conf,
            line=dict(color=color, width=3),
            marker=dict(size=8, color=color, line=dict(color='#0a0a0f', width=2))
        ))
    fig.update_layout(
        **base_layout(), height=320,
        xaxis=dict(**ax()), yaxis=dict(**ax()),
        legend=dict(orientation='h', y=1.12, font=dict(color='#8888aa', size=12))
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    c1, c2 = st.columns(2)
    for col, metric, label in [(c1,'avg_ppg','Scoring (PPG)'),(c2,'avg_def','Defensive Value')]:
        with col:
            st.markdown(f'<div class="section-head">{label}</div>', unsafe_allow_html=True)
            fig2 = go.Figure()
            for conf, color in [('East','#17408B'),('West','#C9082A')]:
                sub = conf_df[conf_df['conference']==conf]
                fig2.add_trace(go.Bar(x=sub['season'], y=sub[metric], name=conf, marker_color=color, marker_line_width=0))
            fig2.update_layout(
                **base_layout(), barmode='group', height=280,
                xaxis=dict(**ax()), yaxis=dict(**ax()),
                legend=dict(orientation='h', y=1.15, font=dict(color='#8888aa', size=10))
            )
            st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})

    season_pick = st.selectbox("Top players for season", SEASONS[::-1])
    c1, c2 = st.columns(2)
    for col, conf in [(c1,'East'),(c2,'West')]:
        with col:
            st.markdown(f'<div class="section-head">{conf}ern Conference</div>', unsafe_allow_html=True)
            top = q(f"""
                SELECT full_name, team, pvs, points_pg, assists_pg, rebounds_pg, games_played
                FROM player_value_scores
                WHERE conference='{conf}' AND season='{season_pick}'
                ORDER BY pvs DESC LIMIT 8
            """)
            top['pvs'] = top['pvs'].apply(lambda x: f"{x:.2f}")
            st.dataframe(top.reset_index(drop=True), use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# PAGE 5 — TRADE ANALYZER
# ─────────────────────────────────────────────────────────────────────────────
elif page == "Trade Analyzer":
    st.markdown("""
    <div class="page-header">
        <div class="page-title">Trade <span>Analyzer</span></div>
        <div class="page-sub">Head-to-head PVS comparison · Who wins the trade?</div>
    </div>
    """, unsafe_allow_html=True)

    all_p = q("SELECT DISTINCT full_name FROM player_value_scores ORDER BY full_name")['full_name'].tolist()

    c1, c2, c3 = st.columns([5, 1, 5])
    with c1:
        pa = st.selectbox("Player A", all_p, index=all_p.index('LeBron James') if 'LeBron James' in all_p else 0)
    with c2:
        st.markdown('<div class="vs-badge">VS</div>', unsafe_allow_html=True)
    with c3:
        pb = st.selectbox("Player B", all_p, index=all_p.index('Nikola Jokić') if 'Nikola Jokić' in all_p else 1)

    season = st.selectbox("Season", SEASONS[::-1])

    da = q(f"SELECT * FROM player_value_scores WHERE full_name='{pa}' AND season='{season}'")
    db = q(f"SELECT * FROM player_value_scores WHERE full_name='{pb}' AND season='{season}'")

    if da.empty or db.empty:
        st.warning("One or both players have no data for this season.")
    else:
        a, b = da.iloc[0], db.iloc[0]
        winner = pa if float(a['pvs']) > float(b['pvs']) else pb
        margin = abs(float(a['pvs']) - float(b['pvs']))

        st.markdown(f"""
        <div class="winner-banner">
            <div>
                <div class="winner-label">Trade Winner</div>
                <div class="winner-name">{winner}</div>
                <div class="winner-margin">leads by {margin:.2f} PVS points in {season}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        metrics = [
            ("PVS", 'pvs'), ("PPG", 'points_pg'), ("APG", 'assists_pg'),
            ("RPG", 'rebounds_pg'), ("STL", 'steals_pg'), ("BLK", 'blocks_pg'),
            ("FG%", 'fg_pct'), ("GP", 'games_played'),
            ("Consistency", 'consistency_score'), ("Availability", 'availability_rate'),
        ]

        pct_cols = {'fg_pct', 'availability_rate'}
        dec2_cols = {'pvs', 'consistency_score'}

        def fmt_val(val, col):
            if col in pct_cols: return f"{float(val):.1%}"
            if col in dec2_cols: return f"{float(val):.2f}"
            return f"{float(val):.1f}"

        ma, mb = st.columns(2)
        with ma:
            st.markdown(f'<div class="section-head">{pa}</div>', unsafe_allow_html=True)
            for label, col in metrics:
                va, vb = float(a[col]), float(b[col])
                win = va >= vb
                color = '#50c878' if win else '#e74c3c'
                icon = '▲' if win else '▼'
                st.markdown(f"""
                <div style="display:flex;justify-content:space-between;align-items:center;padding:0.4rem 0;border-bottom:1px solid #181828">
                    <span style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;color:#3a3a5c;letter-spacing:0.1em">{label}</span>
                    <span style="font-family:'Barlow Condensed',sans-serif;font-size:1.1rem;font-weight:700;color:{color}">{icon} {fmt_val(va, col)}</span>
                </div>
                """, unsafe_allow_html=True)

        with mb:
            st.markdown(f'<div class="section-head">{pb}</div>', unsafe_allow_html=True)
            for label, col in metrics:
                va, vb = float(a[col]), float(b[col])
                win = vb >= va
                color = '#50c878' if win else '#e74c3c'
                icon = '▲' if win else '▼'
                st.markdown(f"""
                <div style="display:flex;justify-content:space-between;align-items:center;padding:0.4rem 0;border-bottom:1px solid #181828">
                    <span style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;color:#3a3a5c;letter-spacing:0.1em">{label}</span>
                    <span style="font-family:'Barlow Condensed',sans-serif;font-size:1.1rem;font-weight:700;color:{color}">{icon} {fmt_val(vb, col)}</span>
                </div>
                """, unsafe_allow_html=True)

        # Radar
        st.markdown('<div class="section-head">Head-to-Head Radar</div>', unsafe_allow_html=True)
        cats = ['Scoring','Defense','Playmaking','Rebounding','Clutch','Consistency']
        def player_vals(row):
            return [
                max(float(row['scoring_value']), 0),
                max(float(row['defensive_value']), 0),
                max(float(row['playmaking_value']), 0),
                max(float(row['rebounding_value']), 0),
                max(float(row['clutch_proxy']), 0),
                float(row['consistency_score']) * 10,
            ]
        fig = go.Figure()
        for name, row, color, fill in [(pa, a, '#C9082A', 'rgba(201,8,42,0.15)'), (pb, b, '#17408B', 'rgba(23,64,139,0.15)')]:
            vals = player_vals(row)
            fig.add_trace(go.Scatterpolar(
                r=vals+[vals[0]], theta=cats+[cats[0]],
                fill='toself', name=name,
                line=dict(color=color, width=2), fillcolor=fill
            ))
        fig.update_layout(
            **base_layout(), height=420,
            polar=dict(
                bgcolor='rgba(0,0,0,0)',
                radialaxis=dict(visible=True, gridcolor='#1c1c2e', tickfont=dict(color='#3a3a5c', size=9), linecolor='#1c1c2e'),
                angularaxis=dict(gridcolor='#1c1c2e', linecolor='#1c1c2e', tickfont=dict(color='#8888aa', size=11))
            ),
            legend=dict(orientation='h', y=-0.12, font=dict(color='#8888aa', size=11))
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

        # Career PVS
        st.markdown('<div class="section-head">Career PVS Comparison</div>', unsafe_allow_html=True)
        ca = q(f"SELECT season, pvs FROM player_value_scores WHERE full_name='{pa}' ORDER BY season")
        cb = q(f"SELECT season, pvs FROM player_value_scores WHERE full_name='{pb}' ORDER BY season")
        fig2 = go.Figure()
        for name, df_c, color in [(pa, ca, '#C9082A'), (pb, cb, '#17408B')]:
            fig2.add_trace(go.Scatter(
                x=df_c['season'], y=df_c['pvs'], mode='lines+markers', name=name,
                line=dict(color=color, width=3),
                marker=dict(size=8, color=color, line=dict(color='#0a0a0f', width=2))
            ))
        fig2.update_layout(
            **base_layout(), height=300,
            xaxis=dict(**ax()), yaxis=dict(**ax()),
            legend=dict(orientation='h', y=1.12, font=dict(color='#8888aa', size=11))
        )
        st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})