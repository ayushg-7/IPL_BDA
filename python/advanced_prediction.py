import json
import os
from collections import defaultdict, deque

import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report


# =========================================================
# SETTINGS
# =========================================================

DATA_FOLDER = "data"
OUTPUT_FOLDER = "output"


# =========================================================
# TEAM NORMALIZATION
# =========================================================

TEAM_NAME_MAP = {

    "Royal Challengers Bangalore":
        "Royal Challengers Bengaluru",

    "Royal Challengers Bengaluru":
        "Royal Challengers Bengaluru",

    "RCB":
        "Royal Challengers Bengaluru",

    "Delhi Daredevils":
        "Delhi Capitals",

    "Delhi Capitals":
        "Delhi Capitals",

    "Delhi":
        "Delhi Capitals",

    "Kings XI Punjab":
        "Punjab Kings",

    "Punjab Kings":
        "Punjab Kings",

    "Punjab":
        "Punjab Kings",

    "Chennai Super Kings":
        "Chennai Super Kings",

    "Mumbai Indians":
        "Mumbai Indians",

    "Kolkata Knight Riders":
        "Kolkata Knight Riders",

    "Rajasthan Royals":
        "Rajasthan Royals",

    "Sunrisers Hyderabad":
        "Sunrisers Hyderabad",

    "Deccan Chargers":
        "Deccan Chargers",

    "Gujarat Titans":
        "Gujarat Titans",

    "Gujarat Lions":
        "Gujarat Lions",

    "Rising Pune Supergiant":
        "Rising Pune Supergiant",

    "Rising Pune Supergiants":
        "Rising Pune Supergiant",

    "Pune Warriors":
        "Pune Warriors India",

    "Pune Warriors India":
        "Pune Warriors India",

    "Kochi Tuskers Kerala":
        "Kochi Tuskers Kerala",

    "Lucknow Super Giants":
        "Lucknow Super Giants"
}


def normalize_team(team):

    return TEAM_NAME_MAP.get(
        team,
        team
    )


# =========================================================
# VENUE NORMALIZATION
# =========================================================

def normalize_venue(venue):

    if venue is None:
        return "Unknown"

    venue = str(venue).strip()

    v = venue.lower()


    # Chennai
    if (
        "chidambaram" in v
        or "chepauk" in v
    ):
        return "M. A. Chidambaram Stadium, Chepauk"


    # Kolkata
    if "eden garden" in v:
        return "Eden Gardens"


    # Bangalore / Bengaluru
    if "chinnaswamy" in v:
        return "M. Chinnaswamy Stadium"


    # Mumbai - Wankhede
    if "wankhede" in v:
        return "Wankhede Stadium"


    # Mumbai - Brabourne
    if "brabourne" in v:
        return "Brabourne Stadium"


    # Mumbai - DY Patil
    if "dy patil" in v:
        return "Dr DY Patil Sports Academy"


    # Delhi
    if (
        "feroz shah kotla" in v
        or "arun jaitley" in v
    ):
        return "Arun Jaitley Stadium"


    # Hyderabad
    if (
        "rajiv gandhi" in v
        and (
            "stadium" in v
            or "cricket" in v
        )
    ):
        return "Rajiv Gandhi International Stadium"


    # Old Mohali / PCA
    if (
        "is bindra" in v
        or "punjab cricket association stadium" in v
        or "punjab cricket association is bindra" in v
        or "pca stadium" in v
    ):
        return "Punjab Cricket Association IS Bindra Stadium"


    # Mullanpur
    if (
        "mullanpur" in v
        or "maharaja yadavindra singh" in v
    ):
        return (
            "Maharaja Yadavindra Singh "
            "International Cricket Stadium"
        )


    # Jaipur
    if "sawai mansingh" in v:
        return "Sawai Mansingh Stadium"


    # Pune
    if (
        "maharashtra cricket association" in v
        or "mca stadium" in v
    ):
        return "Maharashtra Cricket Association Stadium"


    # Ahmedabad
    if (
        "narendra modi" in v
        or "sardar patel" in v
        or "motera" in v
    ):
        return "Narendra Modi Stadium"


    # Kanpur
    if "green park" in v:
        return "Green Park"


    # Raipur
    if "shaheed veer narayan singh" in v:
        return (
            "Shaheed Veer Narayan Singh "
            "International Stadium"
        )


    # Visakhapatnam
    if (
        "aca-vdca" in v
        or "aca vdca" in v
        or "rajasekhara reddy" in v
    ):
        return "ACA-VDCA Cricket Stadium"


    # Dharamsala
    if "himachal pradesh cricket association" in v:
        return "Himachal Pradesh Cricket Association Stadium"


    # Lucknow
    if (
        "ekana" in v
        or "atal bihari vajpayee" in v
    ):
        return (
            "Bharat Ratna Shri Atal Bihari Vajpayee "
            "Ekana Cricket Stadium"
        )


    return venue


# =========================================================
# LOAD MATCHES
# =========================================================

def load_matches():

    matches = []

    for filename in os.listdir(DATA_FOLDER):

        if not filename.endswith(".json"):
            continue

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

            teams = info.get(
                "teams",
                []
            )

            outcome = info.get(
                "outcome",
                {}
            )

            winner = outcome.get(
                "winner"
            )

            dates = info.get(
                "dates",
                []
            )

            if len(teams) != 2:
                continue

            if winner is None:
                continue

            if not dates:
                continue


            # Normalize teams immediately
            team1 = normalize_team(
                teams[0]
            )

            team2 = normalize_team(
                teams[1]
            )


            # Normalize winner
            winner = normalize_team(
                winner
            )


            # Normalize venue
            venue = normalize_venue(
                info.get(
                    "venue",
                    "Unknown"
                )
            )


            matches.append({

                "date": str(dates[0]),

                "team1": team1,

                "team2": team2,

                "venue": venue,

                "toss_winner":
                    normalize_team(
                        info.get(
                            "toss",
                            {}
                        ).get(
                            "winner"
                        )
                    ),

                "toss_decision":
                    info.get(
                        "toss",
                        {}
                    ).get(
                        "decision"
                    ),

                "winner": winner

            })

        except Exception as e:

            print(
                f"Error reading "
                f"{filename}: {e}"
            )


    matches.sort(
        key=lambda x: x["date"]
    )

    return matches


# =========================================================
# CREATE HISTORICAL FEATURES
# =========================================================

def create_features(matches):

    # Team statistics
    team_matches = defaultdict(int)

    team_wins = defaultdict(int)


    # Last 5 results
    recent_results = defaultdict(
        lambda: deque(
            maxlen=5
        )
    )


    # Venue statistics
    venue_matches = defaultdict(
        lambda: defaultdict(int)
    )

    venue_wins = defaultdict(
        lambda: defaultdict(int)
    )


    # Head-to-head
    h2h_matches = defaultdict(int)

    h2h_wins = defaultdict(int)


    records = []


    for match in matches:

        team1 = match["team1"]

        team2 = match["team2"]

        venue = match["venue"]


        # -------------------------------------------------
        # OVERALL WIN RATE
        # -------------------------------------------------

        team1_win_rate = (

            team_wins[team1]
            / team_matches[team1]

            if team_matches[team1] > 0

            else 0.5
        )


        team2_win_rate = (

            team_wins[team2]
            / team_matches[team2]

            if team_matches[team2] > 0

            else 0.5
        )


        # -------------------------------------------------
        # RECENT FORM
        # -------------------------------------------------

        team1_recent_form = (

            sum(recent_results[team1])
            / len(recent_results[team1])

            if recent_results[team1]

            else 0.5
        )


        team2_recent_form = (

            sum(recent_results[team2])
            / len(recent_results[team2])

            if recent_results[team2]

            else 0.5
        )


        # -------------------------------------------------
        # VENUE PERFORMANCE
        # -------------------------------------------------

        team1_venue_rate = (

            venue_wins[venue][team1]
            / venue_matches[venue][team1]

            if venue_matches[venue][team1] > 0

            else 0.5
        )


        team2_venue_rate = (

            venue_wins[venue][team2]
            / venue_matches[venue][team2]

            if venue_matches[venue][team2] > 0

            else 0.5
        )


        # -------------------------------------------------
        # HEAD TO HEAD
        # -------------------------------------------------

        h2h_key = (
            team1,
            team2
        )


        h2h_team1_rate = (

            h2h_wins[h2h_key]
            / h2h_matches[h2h_key]

            if h2h_matches[h2h_key] > 0

            else 0.5
        )


        # -------------------------------------------------
        # TOSS
        # -------------------------------------------------

        team1_toss = (

            1

            if match["toss_winner"] == team1

            else 0
        )


        toss_bat = (

            1

            if match["toss_decision"] == "bat"

            else 0
        )


        # -------------------------------------------------
        # TARGET
        # -------------------------------------------------

        target = (

            1

            if match["winner"] == team1

            else 0
        )


        # -------------------------------------------------
        # SAVE FEATURES
        # -------------------------------------------------

        records.append({

            "date":
                match["date"],

            "team1":
                team1,

            "team2":
                team2,

            "venue":
                venue,

            "team1_win_rate":
                round(
                    team1_win_rate,
                    4
                ),

            "team2_win_rate":
                round(
                    team2_win_rate,
                    4
                ),

            "team1_recent_form":
                round(
                    team1_recent_form,
                    4
                ),

            "team2_recent_form":
                round(
                    team2_recent_form,
                    4
                ),

            "team1_venue_rate":
                round(
                    team1_venue_rate,
                    4
                ),

            "team2_venue_rate":
                round(
                    team2_venue_rate,
                    4
                ),

            "h2h_team1_rate":
                round(
                    h2h_team1_rate,
                    4
                ),

            "team1_toss":
                team1_toss,

            "toss_bat":
                toss_bat,

            "target":
                target

        })


        # =================================================
        # UPDATE HISTORY AFTER MATCH
        # =================================================

        team_matches[team1] += 1

        team_matches[team2] += 1


        if match["winner"] == team1:

            team_wins[team1] += 1

            recent_results[
                team1
            ].append(1)

            recent_results[
                team2
            ].append(0)

        else:

            team_wins[team2] += 1

            recent_results[
                team1
            ].append(0)

            recent_results[
                team2
            ].append(1)


        # Venue
        venue_matches[
            venue
        ][team1] += 1

        venue_matches[
            venue
        ][team2] += 1


        if match["winner"] == team1:

            venue_wins[
                venue
            ][team1] += 1

        else:

            venue_wins[
                venue
            ][team2] += 1


        # Head-to-head
        h2h_matches[
            (team1, team2)
        ] += 1


        if match["winner"] == team1:

            h2h_wins[
                (team1, team2)
            ] += 1


    return pd.DataFrame(
        records
    )


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    print("\nLoading IPL matches...")

    matches = load_matches()

    print(
        f"Usable matches: "
        f"{len(matches)}"
    )


    print(
        "\nCreating normalized "
        "historical features..."
    )

    df = create_features(
        matches
    )


    # =====================================================
    # SAVE CLEAN FEATURES
    # =====================================================

    os.makedirs(
        OUTPUT_FOLDER,
        exist_ok=True
    )


    output_file = os.path.join(
        OUTPUT_FOLDER,
        "advanced_prediction_features.csv"
    )


    df.to_csv(
        output_file,
        index=False
    )


    print(
        "\nClean feature file created:"
    )

    print(
        output_file
    )


    # =====================================================
    # TEAM ENCODING
    # =====================================================

    teams = sorted(
        set(df["team1"]).union(
            set(df["team2"])
        )
    )


    venues = sorted(
        df["venue"].unique()
    )


    team_mapping = {

        team: i

        for i, team
        in enumerate(teams)
    }


    venue_mapping = {

        venue: i

        for i, venue
        in enumerate(venues)
    }


    df["team1_code"] = (
        df["team1"]
        .map(team_mapping)
    )


    df["team2_code"] = (
        df["team2"]
        .map(team_mapping)
    )


    df["venue_code"] = (
        df["venue"]
        .map(venue_mapping)
    )


    # =====================================================
    # MODEL FEATURES
    # =====================================================

    features = [

        "team1_code",

        "team2_code",

        "venue_code",

        "team1_win_rate",

        "team2_win_rate",

        "team1_recent_form",

        "team2_recent_form",

        "team1_venue_rate",

        "team2_venue_rate",

        "h2h_team1_rate",

        "team1_toss",

        "toss_bat"
    ]


    X = df[features]

    y = df["target"]


    # =====================================================
    # TRAIN / TEST
    # =====================================================

    X_train, X_test, y_train, y_test = train_test_split(

        X,

        y,

        test_size=0.20,

        random_state=42,

        stratify=y
    )


    # =====================================================
    # RANDOM FOREST
    # =====================================================

    model = RandomForestClassifier(

        n_estimators=300,

        max_depth=12,

        random_state=42
    )


    model.fit(
        X_train,
        y_train
    )


    # =====================================================
    # EVALUATION
    # =====================================================

    predictions = model.predict(
        X_test
    )


    accuracy = accuracy_score(
        y_test,
        predictions
    )


    print(
        "\n=========================================="
    )

    print(
        "ADVANCED IPL MODEL"
    )

    print(
        "=========================================="
    )


    print(
        f"\nTraining matches: "
        f"{len(X_train)}"
    )


    print(
        f"Testing matches: "
        f"{len(X_test)}"
    )


    print(
        f"\nAccuracy: "
        f"{accuracy * 100:.2f}%"
    )


    print(
        "\nClassification Report:"
    )


    print(
        classification_report(
            y_test,
            predictions
        )
    )


    # =====================================================
    # NORMALIZED TEAM LIST
    # =====================================================

    print(
        "\n=========================================="
    )

    print(
        "NORMALIZED TEAMS"
    )

    print(
        "=========================================="
    )


    for team in teams:

        print(
            "-",
            team
        )


    # =====================================================
    # NORMALIZED VENUE LIST
    # =====================================================

    print(
        "\n=========================================="
    )

    print(
        "NORMALIZED VENUES"
    )

    print(
        "=========================================="
    )


    for venue in venues:

        print(
            "-",
            venue
        )


    print(
        "\n=========================================="
    )

    print(
        "SUCCESS"
    )

    print(
        "=========================================="
    )

    print(
        "\nHistorical features are now"
    )

    print(
        "generated AFTER team and venue"
    )

    print(
        "normalization."
    )

    print(
        "\nNext step: Interactive prediction"
    )