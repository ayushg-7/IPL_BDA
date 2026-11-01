import json
import os
import pandas as pd

DATA_FOLDER = "../data"


def calculate_team_statistics():

    team_stats = {}

    # Read every IPL JSON file
    for filename in os.listdir(DATA_FOLDER):

        if not filename.endswith(".json"):
            continue

        filepath = os.path.join(DATA_FOLDER, filename)

        with open(filepath, "r", encoding="utf-8") as file:
            match = json.load(file)

        info = match["info"]

        teams = info.get("teams", [])
        winner = info.get("outcome", {}).get("winner")

        # Create statistics for both teams
        for team in teams:

            if team not in team_stats:

                team_stats[team] = {
                    "matches": 0,
                    "wins": 0,
                    "losses": 0
                }

            team_stats[team]["matches"] += 1

            if winner == team:
                team_stats[team]["wins"] += 1
            else:
                team_stats[team]["losses"] += 1

    # Convert dictionary into list
    records = []

    for team, stats in team_stats.items():

        matches = stats["matches"]
        wins = stats["wins"]
        losses = stats["losses"]

        # Calculate win percentage
        if matches > 0:
            win_percentage = (wins / matches) * 100
        else:
            win_percentage = 0

        records.append({
            "team": team,
            "matches": matches,
            "wins": wins,
            "losses": losses,
            "win_percentage": round(win_percentage, 2)
        })

    # Create DataFrame
    df = pd.DataFrame(records)

    return df


if __name__ == "__main__":

    print("Calculating team statistics...")

    df = calculate_team_statistics()

    # Sort by number of wins
    df = df.sort_values(
        by="wins",
        ascending=False
    )

    print("\n========== IPL TEAM ANALYTICS ==========\n")

    print(
        df.to_string(index=False)
    )

    # Create output folder if it doesn't exist
    os.makedirs("../output", exist_ok=True)

    # Save results
    df.to_csv(
        "../output/team_statistics.csv",
        index=False
    )

    print("\nTeam statistics saved successfully!")

    print("File: output/team_statistics.csv")