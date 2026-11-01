import json
import os
from collections import defaultdict

import numpy as np
import pandas as pd

from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity


# =========================================================
# SETTINGS
# =========================================================

DATA_FOLDER = "data"
OUTPUT_FOLDER = "output"

os.makedirs(
    OUTPUT_FOLDER,
    exist_ok=True
)


# =========================================================
# WICKET TYPES THAT ARE NOT BOWLER WICKETS
# =========================================================

NON_BOWLER_WICKETS = {

    "run out",
    "retired hurt",
    "retired out",
    "obstructing the field"
}


# =========================================================
# 1. BUILD MATCH-PLAYER PERFORMANCE DATA
# =========================================================

def build_player_match_data():

    records = []

    files = [
        f
        for f in os.listdir(DATA_FOLDER)
        if f.endswith(".json")
    ]

    print(
        f"Found {len(files)} IPL match files."
    )

    for file_number, filename in enumerate(
        files,
        start=1
    ):

        filepath = os.path.join(
            DATA_FOLDER,
            filename
        )

        try:

            with open(
                filepath,
                "r",
                encoding="utf-8"
            ) as file:

                match = json.load(file)


            info = match.get(
                "info",
                {}
            )

            match_date = str(
                info.get(
                    "dates",
                    ["Unknown"]
                )[0]
            )

            teams = info.get(
                "teams",
                []
            )


            # -------------------------------------------------
            # PLAYER STATISTICS FOR THIS MATCH
            # -------------------------------------------------

            player_stats = defaultdict(
                lambda: {

                    "runs": 0,

                    "balls_faced": 0,

                    "wickets": 0,

                    "balls_bowled": 0,

                    "runs_conceded": 0,

                    "fours": 0,

                    "sixes": 0
                }
            )


            # -------------------------------------------------
            # PROCESS BALL-BY-BALL DATA
            # -------------------------------------------------

            for innings in match.get(
                "innings",
                []
            ):

                for over in innings.get(
                    "overs",
                    []
                ):

                    for delivery in over.get(
                        "deliveries",
                        []
                    ):

                        batter = delivery.get(
                            "batter"
                        )

                        bowler = delivery.get(
                            "bowler"
                        )

                        runs = delivery.get(
                            "runs",
                            {}
                        )


                        batter_runs = runs.get(
                            "batter",
                            0
                        )

                        total_runs = runs.get(
                            "total",
                            0
                        )


                        # =====================================
                        # BATTING
                        # =====================================

                        if batter:

                            player_stats[
                                batter
                            ]["runs"] += batter_runs

                            player_stats[
                                batter
                            ]["balls_faced"] += 1


                            if batter_runs == 4:

                                player_stats[
                                    batter
                                ]["fours"] += 1


                            if batter_runs == 6:

                                player_stats[
                                    batter
                                ]["sixes"] += 1


                        # =====================================
                        # BOWLING
                        # =====================================

                        if bowler:

                            player_stats[
                                bowler
                            ]["balls_bowled"] += 1


                            # Extras such as byes and leg-byes
                            # should not be charged to bowler.

                            extras = delivery.get(
                                "extras",
                                {}
                            )

                            bowler_runs = (
                                total_runs
                                - extras.get(
                                    "byes",
                                    0
                                )
                                - extras.get(
                                    "legbyes",
                                    0
                                )
                            )


                            player_stats[
                                bowler
                            ]["runs_conceded"] += (
                                bowler_runs
                            )


                        # =====================================
                        # WICKETS
                        # =====================================

                        for wicket in delivery.get(
                            "wickets",
                            []
                        ):

                            kind = wicket.get(
                                "kind"
                            )


                            if (
                                bowler
                                and kind
                                not in NON_BOWLER_WICKETS
                            ):

                                player_stats[
                                    bowler
                                ]["wickets"] += 1


            # -------------------------------------------------
            # CALCULATE PLAYER PERFORMANCE
            # -------------------------------------------------

            for player, stats in player_stats.items():

                runs = stats["runs"]

                balls = stats["balls_faced"]

                wickets = stats["wickets"]

                balls_bowled = stats[
                    "balls_bowled"
                ]

                runs_conceded = stats[
                    "runs_conceded"
                ]


                strike_rate = (

                    runs / balls * 100

                    if balls > 0

                    else 0
                )


                economy = (

                    runs_conceded
                    / balls_bowled
                    * 6

                    if balls_bowled > 0

                    else 0
                )


                # -------------------------------------------------
                # FANTASY POINTS
                # -------------------------------------------------

                # Simple IPL-style analytical fantasy score.
                # This is NOT an official Dream11 scoring system.

                fantasy_points = (

                    runs

                    + stats["fours"] * 1

                    + stats["sixes"] * 2

                    + wickets * 25
                )


                records.append({

                    "match_id":
                        filename.replace(
                            ".json",
                            ""
                        ),

                    "date":
                        match_date,

                    "player":
                        player,

                    "runs":
                        runs,

                    "balls_faced":
                        balls,

                    "strike_rate":
                        strike_rate,

                    "wickets":
                        wickets,

                    "balls_bowled":
                        balls_bowled,

                    "runs_conceded":
                        runs_conceded,

                    "economy":
                        economy,

                    "fours":
                        stats["fours"],

                    "sixes":
                        stats["sixes"],

                    "fantasy_points":
                        fantasy_points

                })


        except Exception as e:

            print(
                f"Error processing {filename}: {e}"
            )


        if file_number % 100 == 0:

            print(
                f"Processed {file_number} matches..."
            )


    return pd.DataFrame(
        records
    )


# =========================================================
# 2. CREATE PLAYER PROFILE
# =========================================================

def create_player_profile(
    match_data
):

    profile = (
        match_data
        .groupby("player")
        .agg(

            matches=(
                "match_id",
                "nunique"
            ),

            runs=(
                "runs",
                "sum"
            ),

            balls_faced=(
                "balls_faced",
                "sum"
            ),

            wickets=(
                "wickets",
                "sum"
            ),

            balls_bowled=(
                "balls_bowled",
                "sum"
            ),

            runs_conceded=(
                "runs_conceded",
                "sum"
            ),

            fours=(
                "fours",
                "sum"
            ),

            sixes=(
                "sixes",
                "sum"
            ),

            total_fantasy_points=(
                "fantasy_points",
                "sum"
            ),

            average_fantasy_points=(
                "fantasy_points",
                "mean"
            ),

            fantasy_consistency=(
                "fantasy_points",
                "std"
            )
        )
        .reset_index()
    )


    # -----------------------------------------------------
    # DERIVED METRICS
    # -----------------------------------------------------

    profile["strike_rate"] = np.where(

        profile["balls_faced"] > 0,

        profile["runs"]
        / profile["balls_faced"]
        * 100,

        0
    )


    profile["economy"] = np.where(

        profile["balls_bowled"] > 0,

        profile["runs_conceded"]
        / profile["balls_bowled"]
        * 6,

        0
    )


    profile["fantasy_consistency"] = (
        profile[
            "fantasy_consistency"
        ]
        .fillna(0)
    )


    # -----------------------------------------------------
    # AVOID VERY SMALL SAMPLES
    # -----------------------------------------------------

    profile = profile[
        profile["matches"] >= 5
    ].copy()


    return profile


# =========================================================
# 3. BUILD MATCH-PLAYER MATRIX
# =========================================================

def build_performance_matrix(
    match_data
):

    matrix = match_data.pivot_table(

        index="match_id",

        columns="player",

        values="fantasy_points",

        aggfunc="sum",

        fill_value=0
    )


    return matrix


# =========================================================
# 4. PLAYER SIMILARITY
# =========================================================

def calculate_similarity(
    profile
):

    similarity_features = [

        "runs",

        "strike_rate",

        "wickets",

        "economy",

        "fours",

        "sixes",

        "average_fantasy_points"
    ]


    feature_data = profile[
        similarity_features
    ].copy()


    # Replace infinite values
    feature_data = (
        feature_data
        .replace(
            [np.inf, -np.inf],
            np.nan
        )
        .fillna(0)
    )


    # Standardize features
    scaler = StandardScaler()

    scaled_features = scaler.fit_transform(
        feature_data
    )


    similarity_matrix = cosine_similarity(
        scaled_features
    )


    similarity_df = pd.DataFrame(

        similarity_matrix,

        index=profile["player"],

        columns=profile["player"]
    )


    return similarity_df


# =========================================================
# 5. RECOMMEND SIMILAR PLAYERS
# =========================================================

def recommend_similar_players(

    player_name,

    similarity_df,

    profile,

    top_n=10
):

    if player_name not in similarity_df.index:

        return None


    similarities = (
        similarity_df[player_name]
        .drop(player_name)
        .sort_values(
            ascending=False
        )
    )


    recommendations = []

    for player, similarity in similarities.head(
        top_n
    ).items():

        player_data = profile[
            profile["player"] == player
        ].iloc[0]


        recommendations.append({

            "player":
                player,

            "similarity_score":
                round(
                    similarity,
                    4
                ),

            "matches":
                int(
                    player_data[
                        "matches"
                    ]
                ),

            "runs":
                int(
                    player_data[
                        "runs"
                    ]
                ),

            "wickets":
                int(
                    player_data[
                        "wickets"
                    ]
                ),

            "average_fantasy_points":
                round(
                    player_data[
                        "average_fantasy_points"
                    ],
                    2
                )
        })


    return pd.DataFrame(
        recommendations
    )


# =========================================================
# 6. CREATE FANTASY SCORE
# =========================================================

def create_fantasy_score(
    profile
):

    data = profile.copy()


    # -----------------------------------------------------
    # NORMALIZATION FUNCTION
    # -----------------------------------------------------

    def normalize_column(
        column
    ):

        minimum = data[
            column
        ].min()

        maximum = data[
            column
        ].max()


        if maximum == minimum:

            return pd.Series(
                0.5,
                index=data.index
            )


        return (
            data[column]
            - minimum
        ) / (
            maximum
            - minimum
        )


    data["runs_score"] = normalize_column(
        "runs"
    )


    data["strike_score"] = normalize_column(
        "strike_rate"
    )


    data["wicket_score"] = normalize_column(
        "wickets"
    )


    data["fantasy_score"] = normalize_column(
        "average_fantasy_points"
    )


    # Economy is better when LOWER
    data["economy_score"] = 1 - normalize_column(
        "economy"
    )


    # -----------------------------------------------------
    # COMBINED PERFORMANCE SCORE
    # -----------------------------------------------------

    data["performance_score"] = (

        0.30
        * data["runs_score"]

        +

        0.20
        * data["strike_score"]

        +

        0.25
        * data["wicket_score"]

        +

        0.15
        * data["economy_score"]

        +

        0.10
        * data["fantasy_score"]
    )


    # -----------------------------------------------------
    # CONSISTENCY
    # -----------------------------------------------------

    consistency = (

        1
        /
        (
            1
            +
            data[
                "fantasy_consistency"
            ]
        )
    )


    data["consistency_score"] = (
        consistency
        / consistency.max()
    )


    # -----------------------------------------------------
    # FINAL FANTASY RANKING
    # -----------------------------------------------------

    data["final_fantasy_score"] = (

        0.75
        * data["performance_score"]

        +

        0.25
        * data["consistency_score"]
    )


    data = data.sort_values(

        "final_fantasy_score",

        ascending=False
    )


    return data


# =========================================================
# 7. GENERATE FANTASY TOP 11
# =========================================================

def generate_fantasy_team(
    scored_profile
):

    # Top players based on performance
    # and consistency.

    top_players = scored_profile.head(
        11
    ).copy()


    top_players["rank"] = range(
        1,
        len(top_players) + 1
    )


    return top_players[[
        "rank",

        "player",

        "matches",

        "runs",

        "strike_rate",

        "wickets",

        "economy",

        "average_fantasy_points",

        "final_fantasy_score"
    ]]


# =========================================================
# 8. MAIN PROGRAM
# =========================================================

if __name__ == "__main__":

    print("\n==========================================")
    print(" IPL COLLABORATIVE FILTERING")
    print(" FANTASY PLAYER RECOMMENDATION")
    print("==========================================\n")


    # =====================================================
    # STEP 1 - PROCESS DATA
    # =====================================================

    print(
        "Step 1: Processing IPL ball-by-ball data..."
    )


    match_data = build_player_match_data()


    print(
        f"\nPlayer-match records created: "
        f"{len(match_data)}"
    )


    # Save detailed match-level data

    match_data.to_csv(

        os.path.join(
            OUTPUT_FOLDER,
            "player_match_performance.csv"
        ),

        index=False
    )


    print(
        "Saved:"
    )

    print(
        "output/player_match_performance.csv"
    )


    # =====================================================
    # STEP 2 - PLAYER PROFILE
    # =====================================================

    print(
        "\nStep 2: Creating player profiles..."
    )


    profile = create_player_profile(
        match_data
    )


    print(
        f"Players with at least 5 matches: "
        f"{len(profile)}"
    )


    # =====================================================
    # STEP 3 - PERFORMANCE MATRIX
    # =====================================================

    print(
        "\nStep 3: Building match-player matrix..."
    )


    performance_matrix = build_performance_matrix(
        match_data
    )


    performance_matrix.to_csv(

        os.path.join(
            OUTPUT_FOLDER,
            "player_match_matrix.csv"
        )
    )


    print(
        "Saved:"
    )

    print(
        "output/player_match_matrix.csv"
    )


    # =====================================================
    # STEP 4 - SIMILARITY
    # =====================================================

    print(
        "\nStep 4: Calculating player similarity..."
    )


    similarity_df = calculate_similarity(
        profile
    )


    similarity_df.to_csv(

        os.path.join(
            OUTPUT_FOLDER,
            "player_similarity_matrix.csv"
        )
    )


    print(
        "Saved:"
    )

    print(
        "output/player_similarity_matrix.csv"
    )


    # =====================================================
    # STEP 5 - FANTASY SCORING
    # =====================================================

    print(
        "\nStep 5: Calculating fantasy scores..."
    )


    scored_profile = create_fantasy_score(
        profile
    )


    # Save complete recommendation data

    scored_profile.to_csv(

        os.path.join(
            OUTPUT_FOLDER,
            "fantasy_recommendations.csv"
        ),

        index=False
    )


    # =====================================================
    # STEP 6 - TOP 11
    # =====================================================

    fantasy_team = generate_fantasy_team(
        scored_profile
    )


    print(
        "\n=========================================="
    )

    print(
        "          RECOMMENDED FANTASY XI"
    )

    print(
        "==========================================\n"
    )


    print(
        fantasy_team.to_string(
            index=False
        )
    )


    fantasy_team.to_csv(

        os.path.join(
            OUTPUT_FOLDER,
            "fantasy_top_11.csv"
        ),

        index=False
    )


    print(
        "\nSaved:"
    )

    print(
        "output/fantasy_top_11.csv"
    )


    # =====================================================
    # STEP 7 - INTERACTIVE PLAYER RECOMMENDATION
    # =====================================================

    print(
        "\n=========================================="
    )

    print(
        "       PLAYER SIMILARITY SEARCH"
    )

    print(
        "=========================================="
    )


    print(
        "\nEnter a player name to find similar players."
    )

    print(
        "Type 'skip' to finish."
    )


    while True:

        player_name = input(
            "\nPlayer name: "
        ).strip()


        if player_name.lower() == "skip":

            break


        # Case-insensitive matching

        matching_players = [

            player

            for player in similarity_df.index

            if player.lower()
            == player_name.lower()
        ]


        if not matching_players:

            print(
                "\nPlayer not found."
            )

            print(
                "\nExample players:"
            )

            for player in list(
                similarity_df.index
            )[:15]:

                print(
                    "-",
                    player
                )

            continue


        actual_player = matching_players[0]


        recommendations = (
            recommend_similar_players(

                actual_player,

                similarity_df,

                profile,

                top_n=10
            )
        )


        print(
            "\n=========================================="
        )

        print(
            f"PLAYERS SIMILAR TO "
            f"{actual_player}"
        )

        print(
            "==========================================\n"
        )


        print(
            recommendations.to_string(
                index=False
            )
        )


        # Save latest recommendation

        recommendations.to_csv(

            os.path.join(
                OUTPUT_FOLDER,
                "similar_player_recommendations.csv"
            ),

            index=False
        )


    # =====================================================
    # FINAL MESSAGE
    # =====================================================

    print(
        "\n=========================================="
    )

    print(
        " COLLABORATIVE FILTERING COMPLETE"
    )

    print(
        "=========================================="
    )

    print(
        "\nGenerated files:"
    )

    print(
        "1. output/player_match_performance.csv"
    )

    print(
        "2. output/player_match_matrix.csv"
    )

    print(
        "3. output/player_similarity_matrix.csv"
    )

    print(
        "4. output/fantasy_recommendations.csv"
    )

    print(
        "5. output/fantasy_top_11.csv"
    )

    print(
        "\nFantasy recommendation system completed!"
    )