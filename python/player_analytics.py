import json
import os
import pandas as pd

DATA_FOLDER = "../data"


def calculate_player_statistics():

    player_stats = {}

    for filename in os.listdir(DATA_FOLDER):

        if not filename.endswith(".json"):
            continue

        filepath = os.path.join(DATA_FOLDER, filename)

        with open(filepath, "r", encoding="utf-8") as file:
            match = json.load(file)

        for innings in match["innings"]:

            for over in innings["overs"]:

                for delivery in over["deliveries"]:

                    batter = delivery["batter"]
                    bowler = delivery["bowler"]

                    runs = delivery["runs"]

                    batter_runs = runs.get("batter", 0)
                    total_runs = runs.get("total", 0)

                    # Create batter record
                    if batter not in player_stats:

                        player_stats[batter] = {
                            "runs": 0,
                            "balls_faced": 0,
                            "wickets": 0,
                            "balls_bowled": 0,
                            "runs_conceded": 0
                        }

                    player_stats[batter]["runs"] += batter_runs
                    player_stats[batter]["balls_faced"] += 1

                    # Create bowler record
                    if bowler not in player_stats:

                        player_stats[bowler] = {
                            "runs": 0,
                            "balls_faced": 0,
                            "wickets": 0,
                            "balls_bowled": 0,
                            "runs_conceded": 0
                        }

                    player_stats[bowler]["balls_bowled"] += 1
                    player_stats[bowler]["runs_conceded"] += total_runs

                    # Check wickets
                    wickets = delivery.get("wickets", [])

                    for wicket in wickets:

                        player_out = wicket.get("player_out")

                        kind = wicket.get("kind")

                        # Exclude run outs, retired hurt etc.
                        if kind not in [
                            "run out",
                            "retired hurt",
                            "retired out",
                            "obstructing the field"
                        ]:

                            player_stats[bowler]["wickets"] += 1

    records = []

    for player, stats in player_stats.items():

        runs = stats["runs"]
        balls = stats["balls_faced"]

        strike_rate = 0

        if balls > 0:
            strike_rate = (runs / balls) * 100

        balls_bowled = stats["balls_bowled"]
        runs_conceded = stats["runs_conceded"]
        wickets = stats["wickets"]

        economy = 0

        if balls_bowled > 0:
            economy = (runs_conceded / balls_bowled) * 6

        records.append({
            "player": player,
            "runs": runs,
            "balls_faced": balls,
            "strike_rate": round(strike_rate, 2),
            "wickets": wickets,
            "balls_bowled": balls_bowled,
            "runs_conceded": runs_conceded,
            "economy": round(economy, 2)
        })

    df = pd.DataFrame(records)

    return df


if __name__ == "__main__":

    print("Calculating player statistics...")

    df = calculate_player_statistics()

    # Sort according to runs
    top_batsmen = df.sort_values(
        by="runs",
        ascending=False
    ).head(20)

    print("\nTOP 20 RUN SCORERS")
    print(top_batsmen[
        ["player", "runs", "strike_rate"]
    ].to_string(index=False))

    # Top bowlers
    top_bowlers = df.sort_values(
        by="wickets",
        ascending=False
    ).head(20)

    print("\nTOP 20 WICKET TAKERS")
    print(top_bowlers[
        ["player", "wickets", "economy"]
    ].to_string(index=False))

    # Save complete statistics
    os.makedirs("../output", exist_ok=True)

    df.to_csv(
        "../output/player_statistics.csv",
        index=False
    )

    print("\nPlayer statistics saved to:")
    print("../output/player_statistics.csv")