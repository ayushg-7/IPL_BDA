import json
import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

DATA_FOLDER = "../data"


# ---------------------------------------
# 1. Create match dataset
# ---------------------------------------

def create_match_dataset():

    records = []

    for filename in os.listdir(DATA_FOLDER):

        if not filename.endswith(".json"):
            continue

        filepath = os.path.join(DATA_FOLDER, filename)

        with open(filepath, "r", encoding="utf-8") as file:
            match = json.load(file)

        info = match["info"]

        teams = info.get("teams", [])

        if len(teams) != 2:
            continue

        outcome = info.get("outcome", {})
        winner = outcome.get("winner")

        # Ignore matches without a winner
        if winner not in teams:
            continue

        toss = info.get("toss", {})

        team1 = teams[0]
        team2 = teams[1]

        # Features
        team1_win = 1 if winner == team1 else 0

        toss_winner = toss.get("winner")

        team1_toss = 1 if toss_winner == team1 else 0

        # Toss decision
        decision = toss.get("decision")

        if decision == "bat":
            toss_bat = 1
        else:
            toss_bat = 0

        records.append({
            "team1": team1,
            "team2": team2,
            "team1_toss": team1_toss,
            "toss_bat": toss_bat,
            "target": team1_win
        })

    return pd.DataFrame(records)


# ---------------------------------------
# 2. Train prediction model
# ---------------------------------------

def train_model(df):

    # Convert team names into numerical values
    teams = sorted(
        set(df["team1"]) | set(df["team2"])
    )

    team_encoding = {
        team: index
        for index, team in enumerate(teams)
    }

    df["team1_code"] = df["team1"].map(team_encoding)
    df["team2_code"] = df["team2"].map(team_encoding)

    features = [
        "team1_code",
        "team2_code",
        "team1_toss",
        "toss_bat"
    ]

    X = df[features]
    y = df["target"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42
    )

    model = RandomForestClassifier(
        n_estimators=100,
        random_state=42
    )

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    accuracy = accuracy_score(
        y_test,
        predictions
    )

    print("\nModel Accuracy:", round(accuracy * 100, 2), "%")

    return model, team_encoding


# ---------------------------------------
# 3. Predict a new match
# ---------------------------------------

def predict_match(
    model,
    team_encoding,
    team1,
    team2,
    toss_winner,
    toss_decision
):

    team1_code = team_encoding.get(team1)
    team2_code = team_encoding.get(team2)

    if team1_code is None or team2_code is None:
        print("Team not found in dataset.")
        return

    team1_toss = 1 if toss_winner == team1 else 0

    toss_bat = 1 if toss_decision == "bat" else 0

    input_data = pd.DataFrame([{
        "team1_code": team1_code,
        "team2_code": team2_code,
        "team1_toss": team1_toss,
        "toss_bat": toss_bat
    }])

    probabilities = model.predict_proba(input_data)[0]

    team2_probability = probabilities[0] * 100
    team1_probability = probabilities[1] * 100

    print("\n================================")
    print("       IPL MATCH PREDICTION")
    print("================================")

    print("\nTeam 1:", team1)
    print("Team 2:", team2)

    print("\nPredicted Win Probability:")

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


# ---------------------------------------
# 4. Main program
# ---------------------------------------

if __name__ == "__main__":

    print("Loading IPL match data...")

    df = create_match_dataset()

    print("Total matches used:", len(df))

    model, team_encoding = train_model(df)

    # Example match
    teams_available = list(team_encoding.keys())

    print("\nAvailable teams:")
    for team in teams_available:
        print("-", team)

    # Example using first two teams
    team1 = teams_available[0]
    team2 = teams_available[1]

    predict_match(
        model,
        team_encoding,
        team1,
        team2,
        team1,
        "bat"
    )