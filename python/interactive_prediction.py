import pandas as pd
import numpy as np

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score


# =========================================================
# 1. LOAD CLEAN FEATURE DATA
# =========================================================

FILE_PATH = "output/advanced_prediction_features.csv"

df = pd.read_csv(FILE_PATH)

print("\n==========================================")
print("       IPL INTERACTIVE PREDICTION")
print("==========================================")

print(f"\nTotal historical matches: {len(df)}")


# =========================================================
# 2. TEAM AND VENUE LISTS
# =========================================================

teams = sorted(
    set(df["team1"]).union(
        set(df["team2"])
    )
)

venues = sorted(
    df["venue"].dropna().unique()
)


# =========================================================
# 3. CREATE ENCODINGS
# =========================================================

team_mapping = {
    team: i
    for i, team in enumerate(teams)
}

venue_mapping = {
    venue: i
    for i, venue in enumerate(venues)
}


df["team1_code"] = df["team1"].map(
    team_mapping
)

df["team2_code"] = df["team2"].map(
    team_mapping
)

df["venue_code"] = df["venue"].map(
    venue_mapping
)


# =========================================================
# 4. MODEL FEATURES
# =========================================================

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


# =========================================================
# 5. TRAIN / TEST SPLIT
# =========================================================

X_train, X_test, y_train, y_test = train_test_split(

    X,
    y,

    test_size=0.20,

    random_state=42,

    stratify=y
)


# =========================================================
# 6. TRAIN RANDOM FOREST
# =========================================================

model = RandomForestClassifier(

    n_estimators=300,

    max_depth=12,

    random_state=42
)


model.fit(
    X_train,
    y_train
)


# =========================================================
# 7. MODEL ACCURACY
# =========================================================

test_prediction = model.predict(
    X_test
)


accuracy = accuracy_score(
    y_test,
    test_prediction
)


print("\n==========================================")
print("MODEL PERFORMANCE")
print("==========================================")

print(
    f"\nModel Accuracy: "
    f"{accuracy * 100:.2f}%"
)


# =========================================================
# 8. SHOW TEAMS
# =========================================================

print("\n==========================================")
print("AVAILABLE TEAMS")
print("==========================================")

for i, team in enumerate(
    teams,
    start=1
):

    print(
        f"{i}. {team}"
    )


# =========================================================
# 9. TEAM 1
# =========================================================

while True:

    try:

        choice = int(
            input(
                "\nEnter Team 1 number: "
            )
        )

        if 1 <= choice <= len(teams):

            team1 = teams[
                choice - 1
            ]

            break

        print(
            "Invalid team number."
        )

    except ValueError:

        print(
            "Please enter a number."
        )


# =========================================================
# 10. TEAM 2
# =========================================================

while True:

    try:

        choice = int(
            input(
                "Enter Team 2 number: "
            )
        )

        if 1 <= choice <= len(teams):

            team2 = teams[
                choice - 1
            ]

            if team2 == team1:

                print(
                    "Team 1 and Team 2 "
                    "cannot be the same."
                )

            else:

                break

        else:

            print(
                "Invalid team number."
            )

    except ValueError:

        print(
            "Please enter a number."
        )


# =========================================================
# 11. VENUE
# =========================================================

print("\n==========================================")
print("AVAILABLE VENUES")
print("==========================================")

for i, venue in enumerate(
    venues,
    start=1
):

    print(
        f"{i}. {venue}"
    )


while True:

    try:

        choice = int(
            input(
                "\nEnter Venue number: "
            )
        )

        if 1 <= choice <= len(venues):

            venue = venues[
                choice - 1
            ]

            break

        print(
            "Invalid venue number."
        )

    except ValueError:

        print(
            "Please enter a number."
        )


# =========================================================
# 12. TOSS WINNER
# =========================================================

print("\n==========================================")
print("TOSS WINNER")
print("==========================================")

print(
    f"1. {team1}"
)

print(
    f"2. {team2}"
)


while True:

    try:

        choice = int(
            input(
                "\nWho won the toss? (1/2): "
            )
        )

        if choice == 1:

            toss_winner = team1

            break

        elif choice == 2:

            toss_winner = team2

            break

        else:

            print(
                "Enter 1 or 2."
            )

    except ValueError:

        print(
            "Please enter 1 or 2."
        )


# =========================================================
# 13. TOSS DECISION
# =========================================================

print("\n==========================================")
print("TOSS DECISION")
print("==========================================")

print("1. Bat")
print("2. Field")


while True:

    try:

        choice = int(
            input(
                "\nEnter toss decision (1/2): "
            )
        )

        if choice == 1:

            toss_decision = "bat"

            break

        elif choice == 2:

            toss_decision = "field"

            break

        else:

            print(
                "Enter 1 or 2."
            )

    except ValueError:

        print(
            "Please enter 1 or 2."
        )


# =========================================================
# 14. TEAM WIN RATE
# =========================================================

def calculate_win_rate(team):

    data = df[
        (df["team1"] == team) |
        (df["team2"] == team)
    ]

    if len(data) == 0:

        return 0.5

    wins = 0

    for _, row in data.iterrows():

        if row["team1"] == team:

            if row["target"] == 1:
                wins += 1

        elif row["team2"] == team:

            if row["target"] == 0:
                wins += 1

    return wins / len(data)


team1_win_rate = calculate_win_rate(
    team1
)

team2_win_rate = calculate_win_rate(
    team2
)


# =========================================================
# 15. RECENT FORM
# =========================================================

def calculate_recent_form(team):

    data = df[
        (df["team1"] == team) |
        (df["team2"] == team)
    ]

    # Last 5 historical matches
    data = data.tail(5)

    if len(data) == 0:

        return 0.5

    results = []

    for _, row in data.iterrows():

        if row["team1"] == team:

            results.append(
                1 if row["target"] == 1
                else 0
            )

        else:

            results.append(
                1 if row["target"] == 0
                else 0
            )

    return np.mean(results)


team1_recent_form = calculate_recent_form(
    team1
)

team2_recent_form = calculate_recent_form(
    team2
)


# =========================================================
# 16. VENUE PERFORMANCE
# =========================================================

def calculate_venue_form(
    team,
    selected_venue
):

    data = df[
        (df["venue"] == selected_venue)
        &
        (
            (df["team1"] == team)
            |
            (df["team2"] == team)
        )
    ]

    if len(data) == 0:

        return 0.5

    wins = 0

    for _, row in data.iterrows():

        if (
            row["team1"] == team
            and row["target"] == 1
        ):

            wins += 1

        elif (
            row["team2"] == team
            and row["target"] == 0
        ):

            wins += 1

    return wins / len(data)


team1_venue_rate = calculate_venue_form(
    team1,
    venue
)

team2_venue_rate = calculate_venue_form(
    team2,
    venue
)


# =========================================================
# 17. HEAD-TO-HEAD
# =========================================================

h2h = df[
    (
        (df["team1"] == team1)
        &
        (df["team2"] == team2)
    )
    |
    (
        (df["team1"] == team2)
        &
        (df["team2"] == team1)
    )
]


if len(h2h) == 0:

    h2h_team1_rate = 0.5

else:

    team1_wins = 0

    for _, row in h2h.iterrows():

        if (
            row["team1"] == team1
            and row["target"] == 1
        ):

            team1_wins += 1

        elif (
            row["team2"] == team1
            and row["target"] == 0
        ):

            team1_wins += 1

    h2h_team1_rate = (
        team1_wins / len(h2h)
    )


# =========================================================
# 18. TOSS FEATURES
# =========================================================

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


# =========================================================
# 19. CREATE PREDICTION INPUT
# =========================================================

input_data = pd.DataFrame([{

    "team1_code":
        team_mapping[team1],

    "team2_code":
        team_mapping[team2],

    "venue_code":
        venue_mapping[venue],

    "team1_win_rate":
        team1_win_rate,

    "team2_win_rate":
        team2_win_rate,

    "team1_recent_form":
        team1_recent_form,

    "team2_recent_form":
        team2_recent_form,

    "team1_venue_rate":
        team1_venue_rate,

    "team2_venue_rate":
        team2_venue_rate,

    "h2h_team1_rate":
        h2h_team1_rate,

    "team1_toss":
        team1_toss,

    "toss_bat":
        toss_bat
}])


# =========================================================
# 20. PREDICT
# =========================================================

prediction = model.predict(
    input_data
)[0]


probability = model.predict_proba(
    input_data
)[0]


if prediction == 1:

    predicted_winner = team1

    team1_probability = (
        probability[1] * 100
    )

    team2_probability = (
        probability[0] * 100
    )

else:

    predicted_winner = team2

    team1_probability = (
        probability[1] * 100
    )

    team2_probability = (
        probability[0] * 100
    )


# =========================================================
# 21. FINAL OUTPUT
# =========================================================

print("\n\n==========================================")
print("             IPL MATCH")
print("==========================================")

print(
    f"\nTeam 1        : {team1}"
)

print(
    f"Team 2        : {team2}"
)

print(
    f"Venue         : {venue}"
)

print(
    f"Toss Winner   : {toss_winner}"
)

print(
    f"Toss Decision : {toss_decision}"
)


print("\n------------------------------------------")
print("          HISTORICAL ANALYSIS")
print("------------------------------------------")


print(
    f"\n{team1} Overall Win Rate : "
    f"{team1_win_rate * 100:.2f}%"
)

print(
    f"{team2} Overall Win Rate : "
    f"{team2_win_rate * 100:.2f}%"
)


print(
    f"\n{team1} Recent Form : "
    f"{team1_recent_form * 100:.2f}%"
)

print(
    f"{team2} Recent Form : "
    f"{team2_recent_form * 100:.2f}%"
)


print(
    f"\n{team1} Venue Record : "
    f"{team1_venue_rate * 100:.2f}%"
)

print(
    f"{team2} Venue Record : "
    f"{team2_venue_rate * 100:.2f}%"
)


print(
    f"\nHead-to-Head "
    f"({team1}) : "
    f"{h2h_team1_rate * 100:.2f}%"
)


# =========================================================
# 22. FINAL PREDICTION
# =========================================================

print("\n==========================================")
print("             FINAL PREDICTION")
print("==========================================")


print(
    f"\n{team1} Win Probability : "
    f"{team1_probability:.2f}%"
)


print(
    f"{team2} Win Probability : "
    f"{team2_probability:.2f}%"
)


print(
    f"\nPredicted Winner : "
    f"{predicted_winner}"
)


print(
    f"Confidence       : "
    f"{max(team1_probability, team2_probability):.2f}%"
)


print("\n==========================================")
print("          PREDICTION COMPLETE")
print("==========================================")