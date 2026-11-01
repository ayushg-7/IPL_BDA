import streamlit as st
import pandas as pd
import os
import glob
import json
import re
import subprocess
import sys


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="IPL Big Data Analytics",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get help": None,
        "Report a bug": None,
        "About": None
    }
)


# ============================================================
# PROJECT PATHS
# ============================================================

BASE = os.path.dirname(os.path.abspath(__file__))

DATA = os.path.join(BASE, "data")
OUTPUT = os.path.join(BASE, "output")
GRAPHS = os.path.join(OUTPUT, "graphs")
PYSPARK = os.path.join(OUTPUT, "pyspark")
MAPREDUCE = os.path.join(OUTPUT, "mapreduce")


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* ======================================================
       SIDEBAR
       ====================================================== */

    [data-testid="stSidebar"] {
        min-width: 285px !important;
        max-width: 285px !important;
    }

    [data-testid="stSidebar"] h1 {
        font-size: 27px !important;
        font-weight: 800 !important;
        margin-bottom: 30px !important;
    }

    [data-testid="stSidebar"] label {
        font-size: 18px !important;
        font-weight: 600 !important;
    }

    [data-testid="stSidebar"] .stRadio > div {
        gap: 14px !important;
    }

    [data-testid="stSidebar"] .stRadio label {
        padding: 6px 0px !important;
    }

    [data-testid="stSidebar"] [role="radiogroup"] {
        gap: 10px !important;
    }


    /* ======================================================
       HIDE STREAMLIT TOP-RIGHT TOOLBAR
       ====================================================== */

    [data-testid="stToolbar"] {
        display: none !important;
    }

    [data-testid="stDecoration"] {
        display: none !important;
    }

    [data-testid="stStatusWidget"] {
        display: none !important;
    }

    header[data-testid="stHeader"] {
        background: transparent !important;
    }

    header[data-testid="stHeader"] > div {
        display: none !important;
    }

    #MainMenu {
        display: none !important;
        visibility: hidden !important;
    }

    .stDeployButton {
        display: none !important;
        visibility: hidden !important;
    }


    /* ======================================================
       TITLES
       ====================================================== */

    h1 {
        font-weight: 800 !important;
    }

    h2 {
        font-weight: 750 !important;
    }

    h3 {
        font-weight: 700 !important;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def read_csv(path):

    try:

        if os.path.exists(path):

            return pd.read_csv(path)

        return None

    except Exception:

        return None


def show_dataframe(df):

    if df is None:

        st.warning("No data available.")

        return

    if df.empty:

        st.warning("No data available.")

        return

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# TEAM NAME NORMALIZATION
# ============================================================

def normalize_team(team):

    team = str(team).strip()

    mapping = {

        "Royal Challengers Bangalore":
            "Royal Challengers Bengaluru",

        "RCB":
            "Royal Challengers Bengaluru",

        "Delhi Daredevils":
            "Delhi Capitals",

        "Delhi":
            "Delhi Capitals",

        "Kings XI Punjab":
            "Punjab Kings",

        "Punjab":
            "Punjab Kings",

        "Rising Pune Supergiants":
            "Rising Pune Supergiant",

        "Pune Warriors":
            "Pune Warriors India"

    }

    return mapping.get(team, team)


# ============================================================
# IPL SEASON NORMALIZATION
# ============================================================

def normalize_season(season):

    """
    Converts dataset season labels into the display year.

    Examples:

        2007/08  -> 2008
        2009/10  -> 2010
        2020/21  -> 2020
        2009     -> 2009
        2021     -> 2021

    The 2020/21 label is mapped to 2020 because it represents
    the IPL 2020 season in the dataset used by this project.
    """

    season = str(season).strip()

    # Special case in this IPL dataset
    if season == "2020/21":
        return 2020

    # Seasons such as 2007/08, 2009/10
    if "/" in season:

        parts = season.split("/")

        if len(parts) == 2:

            try:

                first_year = int(parts[0])
                second_part = parts[1]

                if len(second_part) == 2:

                    century = (
                        first_year // 100
                    ) * 100

                    second_year = (
                        century
                        + int(second_part)
                    )

                    return second_year

                return int(second_part)

            except ValueError:

                pass

    # Normal numeric season
    match = re.search(
        r"\d{4}",
        season
    )

    if match:

        return int(
            match.group()
        )

    return None


# ============================================================
# COMPLETE PLAYER ANALYTICS
# ============================================================

@st.cache_data
def load_complete_player_analytics():

    json_files = glob.glob(
        os.path.join(
            DATA,
            "*.json"
        )
    )

    player_stats = {}

    yearly_stats = {}

    # ========================================================
    # READ ALL MATCH FILES
    # ========================================================

    for file_path in json_files:

        try:

            with open(
                file_path,
                "r",
                encoding="utf-8"
            ) as f:

                match = json.load(f)

        except Exception:

            continue

        info = match.get(
            "info",
            {}
        )

        raw_season = info.get(
            "season",
            ""
        )

        display_year = normalize_season(
            raw_season
        )

        if display_year is None:

            continue

        match_players = set()

        innings_list = match.get(
            "innings",
            []
        )

        # ====================================================
        # INNINGS
        # ====================================================

        for innings_data in innings_list:

            overs = innings_data.get(
                "overs",
                []
            )

            for over in overs:

                deliveries = over.get(
                    "deliveries",
                    []
                )

                for delivery in deliveries:

                    batter = delivery.get(
                        "batter",
                        ""
                    )

                    bowler = delivery.get(
                        "bowler",
                        ""
                    )

                    runs_data = delivery.get(
                        "runs",
                        {}
                    )

                    batter_runs = int(
                        runs_data.get(
                            "batter",
                            0
                        )
                    )

                    # =================================================
                    # BATTER
                    # =================================================

                    if batter:

                        match_players.add(
                            batter
                        )

                        if batter not in player_stats:

                            player_stats[batter] = {

                                "Runs": 0,

                                "Balls Faced": 0,

                                "Wickets": 0,

                                "Matches": set()

                            }

                        player_stats[batter][
                            "Runs"
                        ] += batter_runs

                        player_stats[batter][
                            "Balls Faced"
                        ] += 1

                        player_stats[batter][
                            "Matches"
                        ].add(
                            file_path
                        )

                        key = (
                            batter,
                            display_year
                        )

                        if key not in yearly_stats:

                            yearly_stats[key] = {

                                "Runs": 0,

                                "Balls Faced": 0,

                                "Wickets": 0

                            }

                        yearly_stats[key][
                            "Runs"
                        ] += batter_runs

                        yearly_stats[key][
                            "Balls Faced"
                        ] += 1

                    # =================================================
                    # BOWLER
                    # =================================================

                    if bowler:

                        match_players.add(
                            bowler
                        )

                        if bowler not in player_stats:

                            player_stats[bowler] = {

                                "Runs": 0,

                                "Balls Faced": 0,

                                "Wickets": 0,

                                "Matches": set()

                            }

                        player_stats[bowler][
                            "Matches"
                        ].add(
                            file_path
                        )

                        key = (
                            bowler,
                            display_year
                        )

                        if key not in yearly_stats:

                            yearly_stats[key] = {

                                "Runs": 0,

                                "Balls Faced": 0,

                                "Wickets": 0

                            }

                    # =================================================
                    # WICKETS
                    # =================================================

                    wickets = delivery.get(
                        "wickets",
                        []
                    )

                    for wicket in wickets:

                        kind = str(
                            wicket.get(
                                "kind",
                                ""
                            )
                        ).lower()

                        excluded_wickets = {

                            "run out",

                            "retired hurt",

                            "retired out",

                            "obstructing the field"

                        }

                        if (
                            kind
                            not in
                            excluded_wickets
                        ):

                            if bowler:

                                player_stats[
                                    bowler
                                ][
                                    "Wickets"
                                ] += 1

                                key = (
                                    bowler,
                                    display_year
                                )

                                if key not in yearly_stats:

                                    yearly_stats[key] = {

                                        "Runs": 0,

                                        "Balls Faced": 0,

                                        "Wickets": 0

                                    }

                                yearly_stats[key][
                                    "Wickets"
                                ] += 1

        # ====================================================
        # MATCH PARTICIPATION
        # ====================================================

        for player in match_players:

            if player not in player_stats:

                player_stats[player] = {

                    "Runs": 0,

                    "Balls Faced": 0,

                    "Wickets": 0,

                    "Matches": set()

                }

            player_stats[player][
                "Matches"
            ].add(
                file_path
            )

    # ========================================================
    # PLAYER NAME NORMALIZATION
    # ========================================================

    def normalize_player_name(name):

        name = str(
            name
        ).strip()

        name = re.sub(
            r"\s+",
            " ",
            name
        )

        parts = name.split()

        if not parts:

            return name

        if len(parts) == 1:

            return parts[0]

        first_initial = (
            parts[0][0].upper()
        )

        surname = parts[-1]

        return (
            first_initial
            + " "
            + surname
        )

    # ========================================================
    # COMBINE NAME VARIATIONS
    # ========================================================

    combined = {}

    for original_name, stats in player_stats.items():

        normalized_name = normalize_player_name(
            original_name
        )

        if normalized_name not in combined:

            combined[normalized_name] = {

                "Player":
                    normalized_name,

                "Runs":
                    0,

                "Balls Faced":
                    0,

                "Wickets":
                    0,

                "Matches Played":
                    set()

            }

        combined[
            normalized_name
        ][
            "Runs"
        ] += stats["Runs"]

        combined[
            normalized_name
        ][
            "Balls Faced"
        ] += stats["Balls Faced"]

        combined[
            normalized_name
        ][
            "Wickets"
        ] += stats["Wickets"]

        combined[
            normalized_name
        ][
            "Matches Played"
        ].update(
            stats["Matches"]
        )

    # ========================================================
    # OVERALL DATAFRAME
    # ========================================================

    overall_rows = []

    for player, stats in combined.items():

        balls = stats[
            "Balls Faced"
        ]

        if balls > 0:

            strike_rate = (
                stats["Runs"]
                /
                balls
            ) * 100

        else:

            strike_rate = 0

        overall_rows.append({

            "Player":
                player,

            "Matches Played":
                len(
                    stats[
                        "Matches Played"
                    ]
                ),

            "Runs":
                stats["Runs"],

            "Wickets":
                stats["Wickets"],

            "Balls Faced":
                balls,

            "Strike Rate":
                round(
                    strike_rate,
                    2
                )

        })

    overall_df = pd.DataFrame(
        overall_rows
    )

    if not overall_df.empty:

        overall_df = overall_df.sort_values(
            by=[
                "Runs",
                "Wickets"
            ],
            ascending=False
        ).reset_index(
            drop=True
        )

    # ========================================================
    # YEAR-WISE COMBINATION
    # ========================================================

    yearly_combined = {}

    for (
        original_player,
        season
    ), stats in yearly_stats.items():

        normalized_name = normalize_player_name(
            original_player
        )

        key = (
            normalized_name,
            season
        )

        if key not in yearly_combined:

            yearly_combined[key] = {

                "Runs": 0,

                "Balls Faced": 0,

                "Wickets": 0

            }

        yearly_combined[key][
            "Runs"
        ] += stats["Runs"]

        yearly_combined[key][
            "Balls Faced"
        ] += stats["Balls Faced"]

        yearly_combined[key][
            "Wickets"
        ] += stats["Wickets"]

    # ========================================================
    # YEARLY DATAFRAME
    # ========================================================

    yearly_rows = []

    for (
        key,
        stats
    ) in yearly_combined.items():

        player, season = key

        yearly_rows.append({

            "Season":
                int(season),

            "Player":
                player,

            "Runs":
                stats["Runs"],

            "Wickets":
                stats["Wickets"],

            "Balls Faced":
                stats["Balls Faced"]

        })

    yearly_df = pd.DataFrame(
        yearly_rows
    )

    if not yearly_df.empty:

        yearly_df = yearly_df.sort_values(
            [
                "Player",
                "Season"
            ]
        ).reset_index(
            drop=True
        )

    return (
        overall_df,
        yearly_df
    )


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.markdown(
    "## 🏏 IPL BIG DATA<br>ANALYTICS",
    unsafe_allow_html=True
)

st.sidebar.markdown(
    "---"
)

page = st.sidebar.radio(

    "Select Module",

    [

        "Dashboard",

        "Team Analytics",

        "Player Analytics",

        "Match Winner Prediction",

        "Overall Fantasy Recommendation",

        "Big Data Analytics",

        "Visualizations"

    ]

)


# ============================================================
# DASHBOARD
# ============================================================

if page == "Dashboard":

    st.title(
        "🏏 IPL Big Data Analytics Dashboard"
    )

    st.markdown(
        """
        ### Welcome to the IPL Big Data Analytics System

        This project analyzes historical IPL data using
        Big Data processing, machine learning,
        recommendation techniques and visualization.
        """
    )

    st.markdown("---")

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        st.metric(
            "🏏 IPL Matches",
            "1,243"
        )

    with c2:

        st.metric(
            "👥 Player Database",
            "Complete IPL Data"
        )

    with c3:

        st.metric(
            "📅 Seasons",
            "2008–2026"
        )

    with c4:

        st.metric(
            "⚙️ Analytics",
            "Big Data + ML"
        )

    st.markdown("---")

    st.subheader(
        "🔬 Technologies Used"
    )

    a, b, c = st.columns(3)

    with a:

        st.info(
                   "⚡ PySpark\n\n"
                   "Large-scale IPL analytics."
               )


        st.info(
                      "📊 R\n\n"
                      "Performance visualization."
                  )

    with b:


        st.info(
            "🤖 Random Forest\n\n"
            "Match winner prediction."
        )

    with c:

        st.info(
            "🎯 Cosine Similarity\n\n"
            "Fantasy recommendation."
        )



# ============================================================
# TEAM ANALYTICS
# ============================================================

elif page == "Team Analytics":

    st.title(
        "🏆 Team Analytics"
    )

    st.markdown(
        """
        Team-wise IPL performance based on historical matches.
        """
    )

    path = os.path.join(
        OUTPUT,
        "team_statistics.csv"
    )

    df = read_csv(
        path
    )

    if df is not None:

        show_dataframe(
            df
        )

        numeric_cols = df.select_dtypes(
            include="number"
        ).columns.tolist()

        if numeric_cols:

            st.subheader(
                "📊 Team Performance"
            )

            chart_col = numeric_cols[-1]

            chart_data = df[
                [
                    df.columns[0],
                    chart_col
                ]
            ].copy()

            chart_data = chart_data.set_index(
                df.columns[0]
            )

            st.bar_chart(
                chart_data
            )

    else:

        st.warning(
            "team_statistics.csv not found."
        )


# ============================================================
# PLAYER ANALYTICS
# ============================================================

elif page == "Player Analytics":

    st.title(
        "🏏 Player Analytics"
    )

    st.markdown(
        """
        ### Complete IPL Player Performance

        Search any player from the complete IPL ball-by-ball
        dataset.
        """
    )

    # ========================================================
    # LOAD COMPLETE DATA
    # ========================================================

    with st.spinner(
        "Loading complete IPL player database..."
    ):

        overall_df, yearly_df = (
            load_complete_player_analytics()
        )

    st.success(
        f"✅ Complete player database loaded: "
        f"{len(overall_df)} normalized players"
    )

    st.caption(
        "Source: 1,243 IPL match JSON files"
    )

    # ========================================================
    # SEARCH
    # ========================================================

    search = st.text_input(

        "🔎 Search Player",

        placeholder=(
            "Example: S Raina, SK Raina, "
            "V Kohli, MS Dhoni"
        )

    )

    # ========================================================
    # DEFAULT VIEW
    # ========================================================

    if not search.strip():

        st.subheader(
            "⭐ Top IPL Players by Runs"
        )

        show_dataframe(
            overall_df.head(20)
        )

    else:

        query = search.strip().lower()

        query_parts = query.split()

        # ====================================================
        # PLAYER MATCHING
        # ====================================================

        def matches_player(player_name):

            player = str(
                player_name
            ).lower().strip()

            player_parts = player.split()

            # Direct search
            if query in player:

                return True

            # Initial + surname matching
            if (
                len(query_parts) >= 2
                and
                len(player_parts) >= 2
            ):

                search_initial = (
                    query_parts[0][0]
                )

                search_surname = (
                    query_parts[-1]
                )

                player_initial = (
                    player_parts[0][0]
                )

                player_surname = (
                    player_parts[-1]
                )

                if (
                    search_initial
                    ==
                    player_initial
                    and
                    search_surname
                    ==
                    player_surname
                ):

                    return True

            return False

        result = overall_df[
            overall_df[
                "Player"
            ].apply(
                matches_player
            )
        ].copy()

        # ====================================================
        # PLAYER FOUND
        # ====================================================

        if not result.empty:

            player_name = result.iloc[0][
                "Player"
            ]

            player_row = result.iloc[0]

            st.success(
                f"✅ Player Found: {player_name}"
            )

            # =================================================
            # CAREER METRICS
            # =================================================

            st.subheader(
                "📊 Overall Career Statistics"
            )

            c1, c2, c3, c4, c5 = st.columns(5)

            with c1:

                st.metric(
                    "🏏 Matches",
                    int(
                        player_row[
                            "Matches Played"
                        ]
                    )
                )

            with c2:

                st.metric(
                    "🏃 Total Runs",
                    int(
                        player_row[
                            "Runs"
                        ]
                    )
                )

            with c3:

                st.metric(
                    "🎯 Total Wickets",
                    int(
                        player_row[
                            "Wickets"
                        ]
                    )
                )

            with c4:

                st.metric(
                    "⚡ Strike Rate",
                    f"{player_row['Strike Rate']:.2f}"
                )

            with c5:

                st.metric(
                    "🏏 Balls Faced",
                    int(
                        player_row[
                            "Balls Faced"
                        ]
                    )
                )

            # =================================================
            # OVERALL RECORD
            # =================================================

            st.subheader(
                "📋 Overall Record"
            )

            overall_display = pd.DataFrame({

                "Player": [
                    player_name
                ],

                "Matches Played": [
                    int(
                        player_row[
                            "Matches Played"
                        ]
                    )
                ],

                "Total Runs": [
                    int(
                        player_row[
                            "Runs"
                        ]
                    )
                ],

                "Total Wickets": [
                    int(
                        player_row[
                            "Wickets"
                        ]
                    )
                ],

                "Balls Faced": [
                    int(
                        player_row[
                            "Balls Faced"
                        ]
                    )
                ],

                "Strike Rate": [
                    player_row[
                        "Strike Rate"
                    ]
                ]

            })

            show_dataframe(
                overall_display
            )

            # =================================================
            # YEAR-WISE PERFORMANCE
            # =================================================

            st.subheader(
                "📅 Year-wise Performance"
            )

            player_yearly = yearly_df[
                yearly_df[
                    "Player"
                ]
                ==
                player_name
            ].copy()

            # =================================================
            # FORCE COMPLETE 2008-2026 TIMELINE
            # =================================================

            seasons = list(
                range(
                    2008,
                    2027
                )
            )

            # Keep only required columns
            player_yearly = player_yearly[
                [
                    "Season",
                    "Runs",
                    "Wickets"
                ]
            ]

            # =================================================
            # GROUP AGAIN
            # =================================================

            if not player_yearly.empty:

                player_yearly = (
                    player_yearly
                    .groupby(
                        "Season",
                        as_index=False
                    )[
                        [
                            "Runs",
                            "Wickets"
                        ]
                    ]
                    .sum()
                )

            # =================================================
            # CREATE EVERY YEAR
            # =================================================

            complete_yearly = pd.DataFrame({

                "Season":
                    seasons

            })

            # =================================================
            # MERGE PLAYER DATA
            # =================================================

            complete_yearly = complete_yearly.merge(

                player_yearly,

                on="Season",

                how="left"

            )

            # =================================================
            # VERY IMPORTANT:
            # EMPTY VALUES -> 0
            # =================================================

            complete_yearly[
                "Runs"
            ] = (
                pd.to_numeric(
                    complete_yearly[
                        "Runs"
                    ],
                    errors="coerce"
                )
                .fillna(0)
                .astype(int)
            )

            complete_yearly[
                "Wickets"
            ] = (
                pd.to_numeric(
                    complete_yearly[
                        "Wickets"
                    ],
                    errors="coerce"
                )
                .fillna(0)
                .astype(int)
            )

            # =================================================
            # DISPLAY TABLE
            # =================================================

            show_dataframe(
                complete_yearly
            )

            # =================================================
            # RUNS GRAPH
            # =================================================

            st.subheader(
                "📈 Runs by Season"
            )

            runs_chart = (
                complete_yearly[
                    [
                        "Season",
                        "Runs"
                    ]
                ]
                .set_index(
                    "Season"
                )
            )

            st.bar_chart(
                runs_chart
            )

            # =================================================
            # WICKETS GRAPH
            # =================================================

            st.subheader(
                "🎯 Wickets by Season"
            )

            wickets_chart = (
                complete_yearly[
                    [
                        "Season",
                        "Wickets"
                    ]
                ]
                .set_index(
                    "Season"
                )
            )

            st.bar_chart(
                wickets_chart
            )

        # ====================================================
        # PLAYER NOT FOUND
        # ====================================================

        else:

            st.warning(
                f"❌ Player not found: {search}"
            )

            st.info(
                "Try: S Raina, SK Raina, "
                "V Kohli, MS Dhoni or Rohit Sharma."
            )

# ============================================================
# MATCH WINNER PREDICTION
# ============================================================

elif page == "Match Winner Prediction":

    import os
    import glob
    import json
    import streamlit as st

    st.title("🏏 IPL Match Winner Prediction")
    st.write("Select the teams and match conditions to predict win probability.")

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_PATH = os.path.join(BASE_DIR, "data", "*.json")

    TEAM_ALIASES = {
        "Royal Challengers Bangalore": "Royal Challengers Bengaluru",
        "Royal Challengers Bengaluru": "Royal Challengers Bengaluru",
        "Delhi Daredevils": "Delhi Capitals",
        "Delhi Capitals": "Delhi Capitals",
        "Kings XI Punjab": "Punjab Kings",
        "Punjab Kings": "Punjab Kings",
        "Punjab": "Punjab Kings",
        "Pune Warriors": "Pune Warriors India",
        "Pune Warriors India": "Pune Warriors India",
        "Rising Pune Supergiants": "Rising Pune Supergiant",
        "Rising Pune Supergiant": "Rising Pune Supergiant",
    }

    def normalize_team(team):
        return TEAM_ALIASES.get(team, team)

    @st.cache_data(show_spinner="Loading IPL JSON match history...")
    def load_matches(path):
        matches = []

        for filename in sorted(glob.glob(path)):
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    data = json.load(f)

                info = data.get("info", {})
                teams = list({
                    normalize_team(t)
                    for t in info.get("teams", [])
                })

                winner = info.get("outcome", {}).get("winner")
                toss = info.get("toss", {})

                if not winner or len(teams) != 2:
                    continue

                winner = normalize_team(winner)

                if winner not in teams:
                    continue

                matches.append({
                    "teams": teams,
                    "winner": winner,
                    "venue": info.get("venue", "Unknown"),
                    "toss_winner": normalize_team(
                        toss.get("winner", "")
                    ),
                    "toss_decision": toss.get(
                        "decision", ""
                    ).lower(),
                })

            except (OSError, json.JSONDecodeError, TypeError):
                continue

        return matches

    matches = load_matches(DATA_PATH)

    if not matches:
        st.error("No usable IPL JSON match data found in the data folder.")
        st.stop()

    available_teams = sorted({
        team for match in matches for team in match["teams"]
    })

    available_venues = sorted({
        match["venue"]
        for match in matches
        if match["venue"] and match["venue"] != "Unknown"
    })

    st.subheader("Select Match Details")

    col1, col2 = st.columns(2)

    with col1:
        team1 = st.selectbox(
            "Select Team 1",
            available_teams,
            key="mw_team1"
        )

    team2_options = [
        team for team in available_teams
        if team != team1
    ]

    with col2:
        if st.session_state.get("mw_team2") not in team2_options:
            st.session_state["mw_team2"] = team2_options[0]

        team2 = st.selectbox(
            "Select Team 2",
            team2_options,
            key="mw_team2"
        )

    venue = st.selectbox(
        "Select Venue",
        available_venues,
        key="mw_venue"
    )

    toss_winner = st.selectbox(
        "Who Won the Toss?",
        options=[team1, team2],
        key=f"mw_toss_winner_{team1}_{team2}"
    )

    toss_decision = st.radio(
        "Toss Winner Chose to",
        options=["Bat", "Field"],
        horizontal=True,
        key="mw_toss_decision"
    )

    predict = st.button(
        "🔮 Predict Match Winner",
        type="primary",
        use_container_width=True
    )

    if predict:

        selected_teams = {team1, team2}

        h2h = [
            match for match in matches
            if set(match["teams"]) == selected_teams
        ]

        venue_matches = [
            match for match in h2h
            if match["venue"] == venue
        ]

        toss_matches = [
            match for match in h2h
            if match["toss_winner"] == toss_winner
            and match["toss_decision"] == toss_decision.lower()
        ]

        total_h2h = len(h2h)

        team1_h2h_wins = sum(
            match["winner"] == team1 for match in h2h
        )

        # Smoothed head-to-head estimate
        baseline = (
            (team1_h2h_wins + 1) / (total_h2h + 2)
            if total_h2h else 0.5
        )

        # Venue estimate
        venue_wins = sum(
            match["winner"] == team1
            for match in venue_matches
        )

        venue_rate = (
            (venue_wins + 5 * baseline) / (len(venue_matches) + 5)
            if venue_matches else baseline
        )

        # Toss winner and toss decision estimate
        toss_team1_wins = sum(
            match["winner"] == team1
            for match in toss_matches
        )

        toss_rate = (
            (toss_team1_wins + 5 * baseline) / (len(toss_matches) + 5)
            if toss_matches else baseline
        )

        # If Team 1 won the toss, favour the historical results
        # for that toss-winning team and decision.
        # If Team 2 won the toss, reverse the toss-specific signal.
        if toss_winner == team1:
            toss_signal = toss_rate
        else:
            toss_signal = 1 - toss_rate

        team1_probability = (
            0.60 * baseline
            + 0.25 * venue_rate
            + 0.15 * toss_signal
        )

        team1_probability = max(
            0.0, min(1.0, team1_probability)
        )

        team2_probability = 1 - team1_probability

        pct1 = round(team1_probability * 100, 2)
        pct2 = round(team2_probability * 100, 2)

        st.divider()
        st.subheader("📊 Match Winner Prediction")

        st.caption(
            f"{team1} vs {team2} | Venue: {venue} | "
            f"Toss Winner: {toss_winner} | "
            f"Decision: {toss_decision}"
        )

        c1, c2 = st.columns(2)

        with c1:
            st.metric(f"{team1} Win Probability", f"{pct1:.2f}%")
            st.progress(team1_probability)

        with c2:
            st.metric(f"{team2} Win Probability", f"{pct2:.2f}%")
            st.progress(team2_probability)

        if pct1 > pct2:
            st.success(f"🏆 Predicted Favourite: {team1}")
        elif pct2 > pct1:
            st.success(f"🏆 Predicted Favourite: {team2}")
        else:
            st.info("Both teams have equal estimated win probabilities.")

        st.subheader("Historical Data Used")

        a, b, c = st.columns(3)
        a.metric("Head-to-Head Matches", total_h2h)
        b.metric("Matches at Selected Venue", len(venue_matches))
        c.metric("Matching Toss Conditions", len(toss_matches))

        st.caption(
            "Probabilities are estimates based on historical head-to-head, "
            "venue and toss-condition results. They are not guaranteed "
            "outcomes or direct output from a trained ML model."
        )

        
# ============================================================
# OVERALL FANTASY
# ============================================================

elif page == "Overall Fantasy Recommendation":

    st.title(
        "🏆 Overall Fantasy Recommendation"
    )

    st.markdown(
        """
        Player recommendations based on historical performance,
        player similarity and fantasy scoring.
        """
    )

    path = os.path.join(
        OUTPUT,
        "fantasy_recommendations.csv"
    )

    df = read_csv(
        path
    )

    if df is not None:

        st.subheader(
            "⭐ Top Fantasy Players"
        )

        show_dataframe(
            df.head(20)
        )

        st.markdown("---")

        top11_path = os.path.join(
            OUTPUT,
            "fantasy_top_11.csv"
        )

        top11 = read_csv(
            top11_path
        )

        if top11 is not None:

            st.subheader(
                "🏏 Recommended Top 11"
            )

            show_dataframe(
                top11
            )

    else:

        st.warning(
            "fantasy_recommendations.csv not found."
        )


# ============================================================
# BIG DATA ANALYTICS
# ============================================================

elif page == "Big Data Analytics":

    st.title(
        "⚡ Big Data Analytics"
    )

    st.markdown(
        """
        ### Hadoop MapReduce and PySpark Results
        """
    )

    # --------------------------------------------------------
    # MAPREDUCE
    # --------------------------------------------------------

    st.subheader(
        "🗺️ Hadoop MapReduce"
    )

    path = os.path.join(
        MAPREDUCE,
        "season_player_performance.csv"
    )

    df = read_csv(
        path
    )

    if df is not None:

        st.success(
            f"MapReduce output loaded: "
            f"{len(df)} records"
        )

        show_dataframe(
            df.head(30)
        )

    else:

        st.warning(
            "MapReduce CSV not found."
        )

    st.markdown("---")

    # --------------------------------------------------------
    # PYSPARK PLAYER RUNS
    # --------------------------------------------------------

    st.subheader(
        "⚡ PySpark Player Runs"
    )

    path = os.path.join(
        PYSPARK,
        "player_runs.csv"
    )

    df = read_csv(
        path
    )

    if df is not None:

        show_dataframe(
            df.head(30)
        )

    else:

        st.warning(
            "PySpark player_runs.csv not found."
        )

    st.markdown("---")

    # --------------------------------------------------------
    # PYSPARK BOWLING
    # --------------------------------------------------------

    st.subheader(
        "🎯 PySpark Bowling Statistics"
    )

    path = os.path.join(
        PYSPARK,
        "bowling_statistics.csv"
    )

    df = read_csv(
        path
    )

    if df is not None:

        show_dataframe(
            df.head(30)
        )

    else:

        st.warning(
            "PySpark bowling_statistics.csv not found."
        )

    st.markdown("---")

    # --------------------------------------------------------
    # PYSPARK TEAM
    # --------------------------------------------------------

    st.subheader(
        "🏆 PySpark Team Statistics"
    )

    path = os.path.join(
        PYSPARK,
        "team_statistics.csv"
    )

    df = read_csv(
        path
    )

    if df is not None:

        show_dataframe(
            df.head(30)
        )

    else:

        st.warning(
            "PySpark team_statistics.csv not found."
        )


# ============================================================
# VISUALIZATIONS
# ============================================================

elif page == "Visualizations":

    st.title(
        "📊 IPL Visualizations"
    )

    st.markdown(
        """
        ### R and Big Data Analytics Visualizations
        """
    )

    if not os.path.exists(
        GRAPHS
    ):

        st.warning(
            "Graphs folder not found."
        )

    else:

        graph_files = sorted(
            glob.glob(
                os.path.join(
                    GRAPHS,
                    "*.png"
                )
            )
        )

        if not graph_files:

            st.warning(
                "No graphs found."
            )

        else:

            for graph_path in graph_files:

                graph_name = os.path.basename(
                    graph_path
                )

                title = (
                    graph_name
                    .replace(
                        ".png",
                        ""
                    )
                    .replace(
                        "_",
                        " "
                    )
                    .title()
                )

                st.subheader(
                    title
                )

                st.image(
                    graph_path,
                    use_container_width=True
                )

                st.markdown(
                    "---"
                )