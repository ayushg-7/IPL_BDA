import json
import os
import pandas as pd

DATA_FOLDER = "../data"


def load_matches():
    matches = []

    for filename in os.listdir(DATA_FOLDER):

        if filename.endswith(".json"):

            filepath = os.path.join(DATA_FOLDER, filename)

            try:
                with open(filepath, "r", encoding="utf-8") as file:
                    match = json.load(file)

                matches.append(match)

            except Exception as e:
                print(f"Error reading {filename}: {e}")

    return matches


def create_match_dataframe(matches):

    records = []

    for match in matches:

        info = match["info"]

        outcome = info.get("outcome", {})

        winner = outcome.get("winner", None)

        teams = info.get("teams", [])

        toss = info.get("toss", {})

        record = {
            "match_id": None,
            "season": info.get("season"),
            "date": info.get("dates", [None])[0],
            "city": info.get("city"),
            "venue": info.get("venue"),
            "team1": teams[0] if len(teams) > 0 else None,
            "team2": teams[1] if len(teams) > 1 else None,
            "toss_winner": toss.get("winner"),
            "toss_decision": toss.get("decision"),
            "winner": winner
        }

        records.append(record)

    return pd.DataFrame(records)


if __name__ == "__main__":

    print("Loading IPL dataset...")

    matches = load_matches()

    print("Total matches:", len(matches))

    df = create_match_dataframe(matches)

    print("\nFirst 5 matches:")
    print(df.head())

    print("\nDataset information:")
    print(df.info())
    