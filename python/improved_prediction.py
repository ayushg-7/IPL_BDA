import json
import os
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score


DATA_FOLDER = "data"
OUTPUT_FOLDER = "output"


# ============================================================
# 1. LOAD IPL MATCHES
# ============================================================

def load_matches():

    matches = []

    for filename in os.listdir(DATA_FOLDER):

        if not filename.endswith(".json"):
            continue

        filepath = os.path.join(DATA_FOLDER, filename)

        try:

            with open(filepath, "r", encoding="utf-8") as file:
                match = json.load(file)

            matches.append(match)

        except Exception as e:

            print("Error reading:", filename)
            print(e)

    return matches


# ============================================================
# 2. CREATE HISTORICAL FEATURES
# ============================================================

def create_features(matches):

    team_history = {}

    records = []

    # Sort matches by date
    matches = sorted(
        matches,
        key=lambda x: str(
            x["info"].get("dates", [""])[0]
        )
    )

    for match in matches:

        info = match["info"]

        teams = info.get("teams", [])

        if len(teams) != 2:
            continue

        outcome = info.get("outcome", {})

        winner = outcome.get("winner")

        if winner not in teams:
            continue

        team1 = teams[0]
        team2 = teams[1]

        # ----------------------------------------------------
        # Initialize teams
        # ----------------------------------------------------

        for team in teams:

            if team not in team_history:

                team_history[team] = {
                    "matches": 0,
                    "wins": 0
                }

        # ----------------------------------------------------
        # Historical performance BEFORE this match
        # ----------------------------------------------------

        team1_matches = team_history[team1]["matches"]
        team1_wins = team_history[team1]["wins"]

        team2_matches = team_history[team2]["matches"]
        team2_wins = team_history[team2]["wins"]

        if team1_matches > 0:
            team1_win_rate = (
                team1_wins / team1_matches
            )
        else:
            team1_win_rate = 0.5

        if team2_matches > 0:
            team2_win_rate = (
                team2_wins / team2_matches
            )
        else:
            team2_win_rate = 0.5

        # ----------------------------------------------------
        # Toss information
        # ----------------------------------------------------

        toss = info.get("toss", {})

        toss_winner = toss.get("winner")

        toss_decision = toss.get("decision")

        team1_toss = 1 if toss_winner == team1 else 0

        toss_bat = 1 if toss_decision == "bat" else 0

        # ----------------------------------------------------
        # Target
        # ----------------------------------------------------

        target = 1 if winner == team1 else 0

        records.append({

            "team1": team1,
            "team2": team2,

            "team1_win_rate": team1_win_rate,
            "team2_win_rate": team2_win_rate,

            "team1_toss": team1_toss,
            "toss_bat": toss_bat,

            "target": target
        })

        # ----------------------------------------------------
        # Update team history AFTER the match
        # ----------------------------------------------------

        team_history[team1]["matches"] += 1
        team_history[team2]["matches"] += 1

        if winner == team1:

            team_history[team1]["wins"] += 1

        else:

            team_history[team2]["wins"] += 1

    return pd.DataFrame(records)


# ============================================================
# 3. ENCODE TEAMS
# ============================================================

def encode_teams(df):

    teams = sorted(
        set(df["team1"]) |
        set(df["team2"])
    )

    team_encoding = {}

    for index, team in enumerate(teams):

        team_encoding[team] = index

    df["team1_code"] = df["team1"].map(
        team_encoding
    )

    df["team2_code"] = df["team2"].map(
        team_encoding
    )

    return df, team_encoding


# ============================================================
# 4. TRAIN RANDOM FOREST MODEL
# ============================================================

def train_model(df):

    features = [

        "team1_code",

        "team2_code",

        "team1_win_rate",

        "team2_win_rate",

        "team1_toss",

        "toss_bat"

    ]

    X = df[features]

    y = df["target"]

    # Split historical data
    X_train, X_test, y_train, y_test = train_test_split(

        X,

        y,

        test_size=0.20,

        random_state=42,

        stratify=y
    )

    print("\nTraining Random Forest model...")

    model = RandomForestClassifier(

        n_estimators=200,

        max_depth=10,

        random_state=42
    )

    model.fit(
        X_train,
        y_train
    )

    # Test model
    predictions = model.predict(
        X_test
    )

    accuracy = accuracy_score(
        y_test,
        predictions
    )

    print(
        "\nModel Accuracy:",
        round(accuracy * 100, 2),
        "%"
    )

    return model


# ============================================================
# 5. PREDICT MATCH
# ============================================================

def predict_match(

    model,

    df,

    team_encoding,

    team1,

    team2,

    toss_winner,

    toss_decision

):

    # Check teams
    if team1 not in team_encoding:

        print(
            "Team 1 not found:",
            team1
        )

        return

    if team2 not in team_encoding:

        print(
            "Team 2 not found:",
            team2
        )

        return

    # --------------------------------------------------------
    # Get latest historical win rate
    # --------------------------------------------------------

    team1_data = df[
        df["team1"] == team1
    ]

    team1_data_2 = df[
        df["team2"] == team1
    ]

    team1_wins = (

        team1_data[
            "target"
        ].sum()

        +

        (
            len(team1_data_2)

            -

            team1_data_2[
                "target"
            ].sum()
        )
    )

    team1_matches = (
        len(team1_data)
        +
        len(team1_data_2)
    )

    team2_data = df[
        df["team1"] == team2
    ]

    team2_data_2 = df[
        df["team2"] == team2
    ]

    team2_wins = (

        team2_data[
            "target"
        ].sum()

        +

        (
            len(team2_data_2)

            -

            team2_data_2[
                "target"
            ].sum()
        )
    )

    team2_matches = (
        len(team2_data)
        +
        len(team2_data_2)
    )

    team1_win_rate = (
        team1_wins / team1_matches
        if team1_matches > 0
        else 0.5
    )

    team2_win_rate = (
        team2_wins / team2_matches
        if team2_matches > 0
        else 0.5
    )

    # --------------------------------------------------------
    # Toss features
    # --------------------------------------------------------

    team1_toss = (
        1
        if toss_winner == team1
        else 0
    )

    toss_bat = (
        1
        if toss_decision == "bat"
        else 0
    )

    # --------------------------------------------------------
    # Create input
    # --------------------------------------------------------

    input_data = pd.DataFrame([{

        "team1_code":
            team_encoding[team1],

        "team2_code":
            team_encoding[team2],

        "team1_win_rate":
            team1_win_rate,

        "team2_win_rate":
            team2_win_rate,

        "team1_toss":
            team1_toss,

        "toss_bat":
            toss_bat
    }])

    # --------------------------------------------------------
    # Prediction
    # --------------------------------------------------------

    probabilities = model.predict_proba(
        input_data
    )[0]

    # Class 0 = Team 2 wins
    # Class 1 = Team 1 wins

    team2_probability = (
        probabilities[0] * 100
    )

    team1_probability = (
        probabilities[1] * 100
    )

    # --------------------------------------------------------
    # Display
    # --------------------------------------------------------

    print("\n")
    print("=" * 50)

    print(
        "          IPL MATCH PREDICTION"
    )

    print("=" * 50)

    print(
        "\nTeam 1:",
        team1
    )

    print(
        "Team 2:",
        team2
    )

    print(
        "\nHistorical Win Rate:"
    )

    print(
        team1,
        ":",
        round(team1_win_rate * 100, 2),
        "%"
    )

    print(
        team2,
        ":",
        round(team2_win_rate * 100, 2),
        "%"
    )

    print(
        "\nToss Winner:",
        toss_winner
    )

    print(
        "Toss Decision:",
        toss_decision
    )

    print(
        "\nPredicted Win Probability:"
    )

    print(
        team1,
        ":",
        round(team1_probability, 2),
        "%"
    )

    print(
        team2,
        ":",
        round(team2_probability, 2),
        "%"
    )

    print("=" * 50)


# ============================================================
# 6. MAIN PROGRAM
# ============================================================

if __name__ == "__main__":

    print(
        "Loading IPL matches..."
    )

    matches = load_matches()

    print(
        "Total matches loaded:",
        len(matches)
    )

    print(
        "\nCreating historical features..."
    )

    df = create_features(
        matches
    )

    print(
        "Usable matches:",
        len(df)
    )

    # Encode teams
    df, team_encoding = encode_teams(
        df
    )

    # Save feature data
    os.makedirs(
        OUTPUT_FOLDER,
        exist_ok=True
    )

    df.to_csv(
        "output/prediction_features.csv",
        index=False
    )

    print(
        "\nPrediction feature dataset saved."
    )

    # Train model
    model = train_model(
        df
    )

    # --------------------------------------------------------
    # Example prediction
    # --------------------------------------------------------

    available_teams = list(
        team_encoding.keys()
    )

    print(
        "\nAvailable teams:"
    )

    for team in available_teams:

        print(
            "-",
            team
        )

    # Example using first two teams
    team1 = available_teams[0]

    team2 = available_teams[1]

    predict_match(

        model,

        df,

        team_encoding,

        team1,

        team2,

        team1,

        "bat"
    )