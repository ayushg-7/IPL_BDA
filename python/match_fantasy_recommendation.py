
import csv
import glob
import json
import os
import sys
from collections import defaultdict


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "*.json")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "match_fantasy_xi.csv")


# ============================================================
# TEAM NAME NORMALIZATION
# ============================================================

TEAM_ALIASES = {
    "Royal Challengers Bangalore": "Royal Challengers Bengaluru",
    "Royal Challengers Bengaluru": "Royal Challengers Bengaluru",
    "Delhi Daredevils": "Delhi Capitals",
    "Delhi Capitals": "Delhi Capitals",
    "Delhi": "Delhi Capitals",
    "Kings XI Punjab": "Punjab Kings",
    "Punjab Kings": "Punjab Kings",
    "Punjab": "Punjab Kings",
    "Chennai Super Kings": "Chennai Super Kings",
    "Mumbai Indians": "Mumbai Indians",
    "Kolkata Knight Riders": "Kolkata Knight Riders",
    "Rajasthan Royals": "Rajasthan Royals",
    "Sunrisers Hyderabad": "Sunrisers Hyderabad",
    "Deccan Chargers": "Deccan Chargers",
    "Gujarat Titans": "Gujarat Titans",
    "Gujarat Lions": "Gujarat Lions",
    "Kochi Tuskers Kerala": "Kochi Tuskers Kerala",
    "Lucknow Super Giants": "Lucknow Super Giants",
    "Rising Pune Supergiant": "Rising Pune Supergiant",
    "Rising Pune Supergiants": "Rising Pune Supergiant",
    "Pune Warriors": "Pune Warriors India",
    "Pune Warriors India": "Pune Warriors India",
}


def normalize_team(team):
    team = str(team).strip()
    return TEAM_ALIASES.get(team, team)


def credited_wicket(wicket):
    excluded = {
        "run out",
        "retired hurt",
        "retired out",
        "obstructing the field",
    }
    return str(wicket.get("kind", "")).lower() not in excluded


# ============================================================
# READ TEAM SELECTION
# ============================================================

files = sorted(glob.glob(DATA_PATH))

if not files:
    print(f"ERROR: No JSON files found at {DATA_PATH}", file=sys.stderr)
    sys.exit(1)

# Streamlit passes the selected team names as command-line arguments.
# This skips the initial scan used only to display the interactive menu.
if len(sys.argv) >= 3:
    TEAM1 = normalize_team(sys.argv[1])
    TEAM2 = normalize_team(sys.argv[2])

else:
    # Preserve standalone terminal usage.
    print("=" * 65)
    print("HEAD-TO-HEAD FANTASY XI")
    print("=" * 65)
    print(f"Found {len(files)} match files. Loading team list...")

    available_teams = set()

    for filepath in files:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                match = json.load(f)

            for team in match.get("info", {}).get("teams", []):
                available_teams.add(normalize_team(team))

        except (OSError, json.JSONDecodeError):
            continue

    available_teams = sorted(available_teams)

    for number, team in enumerate(available_teams, 1):
        print(f"{number}. {team}")

    while True:
        try:
            first = int(input("Enter Team 1 number: "))
            second = int(input("Enter Team 2 number: "))

            if not (1 <= first <= len(available_teams)):
                print("Invalid Team 1 number.")
                continue

            if not (1 <= second <= len(available_teams)):
                print("Invalid Team 2 number.")
                continue

            if first == second:
                print("Please select two different teams.")
                continue

            TEAM1 = available_teams[first - 1]
            TEAM2 = available_teams[second - 1]
            break

        except ValueError:
            print("Enter valid numbers.")

if TEAM1 == TEAM2:
    print("ERROR: Select two different teams.", file=sys.stderr)
    sys.exit(1)

SELECTED_TEAMS = {TEAM1, TEAM2}

print(f"\nHead-to-head analysis: {TEAM1} vs {TEAM2}")
print(f"Match files to inspect: {len(files)}")


# ============================================================
# PROCESS MATCHES IN ONE PASS
# ============================================================

players = defaultdict(lambda: {
    "matches": set(),
    "teams": set(),
    "runs": 0,
    "balls": 0,
    "wickets": 0,
    "balls_bowled": 0,
    "runs_conceded": 0,
    "fantasy_points": 0,
})

head_to_head_matches = 0

for index, filepath in enumerate(files, 1):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            match = json.load(f)
    except (OSError, json.JSONDecodeError):
        continue

    raw_teams = match.get("info", {}).get("teams", [])
    match_teams = {normalize_team(t) for t in raw_teams}

    # Only matches involving exactly the selected pair.
    if match_teams != SELECTED_TEAMS:
        continue

    head_to_head_matches += 1
    match_id = os.path.basename(filepath)

    for innings in match.get("innings", []):
        batting_team = normalize_team(innings.get("team", ""))

        if batting_team not in SELECTED_TEAMS:
            continue

        bowling_team = TEAM2 if batting_team == TEAM1 else TEAM1

        for over in innings.get("overs", []):
            for delivery in over.get("deliveries", []):
                batter = delivery.get("batter", "")
                bowler = delivery.get("bowler", "")
                runs = delivery.get("runs", {})
                extras = delivery.get("extras", {})

                batter_runs = int(runs.get("batter", 0))
                total_runs = int(runs.get("total", 0))

                # Batter statistics
                if batter:
                    p = players[batter]
                    p["matches"].add(match_id)
                    p["teams"].add(batting_team)
                    p["runs"] += batter_runs

                    # Do not count wides or no-balls as balls faced.
                    if "wides" not in extras and "noballs" not in extras:
                        p["balls"] += 1

                    # Project fantasy scoring: runs + boundary bonuses.
                    p["fantasy_points"] += batter_runs

                    if batter_runs == 4:
                        p["fantasy_points"] += 1

                    elif batter_runs == 6:
                        p["fantasy_points"] += 2

                # Bowler statistics
                if bowler:
                    p = players[bowler]
                    p["matches"].add(match_id)
                    p["teams"].add(bowling_team)

                    is_wide = "wides" in extras
                    is_no_ball = "noballs" in extras

                    if not is_wide and not is_no_ball:
                        p["balls_bowled"] += 1

                    conceded = (
                        total_runs
                        - int(extras.get("byes", 0))
                        - int(extras.get("legbyes", 0))
                        - int(extras.get("penalty", 0))
                    )
                    p["runs_conceded"] += conceded

                    for wicket in delivery.get("wickets", []):
                        if credited_wicket(wicket):
                            p["wickets"] += 1
                            p["fantasy_points"] += 25

    # Lightweight progress output for longer runs.
    if index % 200 == 0:
        print(f"Inspected {index}/{len(files)} files...")


print(f"\nHead-to-head matches found: {head_to_head_matches}")

if head_to_head_matches == 0:
    print("ERROR: No head-to-head matches found.", file=sys.stderr)
    sys.exit(1)


# ============================================================
# CALCULATE PLAYER RATINGS
# ============================================================

records = []

for player, data in players.items():
    matches_played = len(data["matches"])

    if matches_played == 0:
        continue

    runs = data["runs"]
    balls = data["balls"]
    wickets = data["wickets"]
    balls_bowled = data["balls_bowled"]
    runs_conceded = data["runs_conceded"]

    strike_rate = (runs / balls * 100) if balls else 0
    economy = (runs_conceded / balls_bowled * 6) if balls_bowled else 0
    average_fantasy = data["fantasy_points"] / matches_played

    consistency = min(matches_played / head_to_head_matches, 1)

    rating = (
        min(runs / 1000, 1) * 25
        + min(strike_rate / 150, 1) * 15
        + min(wickets / 40, 1) * 25
        + min(average_fantasy / 50, 1) * 25
        + consistency * 10
    )

    team_list = sorted(data["teams"])

    if TEAM1 in team_list:
        display_team = TEAM1
    elif TEAM2 in team_list:
        display_team = TEAM2
    else:
        display_team = team_list[0] if team_list else "Unknown"

    records.append({
        "player": player,
        "team": display_team,
        "matches": matches_played,
        "runs": runs,
        "wickets": wickets,
        "balls": balls,
        "strike_rate": strike_rate,
        "economy": economy,
        "average_fantasy": average_fantasy,
        "rating": rating,
    })


records.sort(key=lambda item: item["rating"], reverse=True)
top_11 = records[:11]

if not top_11:
    print("ERROR: No player performance found.", file=sys.stderr)
    sys.exit(1)

max_rating = max(player["rating"] for player in top_11)

# ============================================================
# SAVE CSV
# ============================================================

os.makedirs(OUTPUT_DIR, exist_ok=True)

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)

    writer.writerow([
        "Rank", "Player", "Team", "Matches", "Runs", "Wickets",
        "Strike_Rate", "Economy", "Average_Fantasy", "Rating_Out_of_10"
    ])

    for rank, player in enumerate(top_11, 1):
        rating_10 = (
            player["rating"] / max_rating * 10
            if max_rating else 0
        )

        writer.writerow([
            rank,
            player["player"],
            player["team"],
            player["matches"],
            player["runs"],
            player["wickets"],
            f"{player['strike_rate']:.2f}",
            f"{player['economy']:.2f}",
            f"{player['average_fantasy']:.2f}",
            f"{rating_10:.2f}",
        ])


# ============================================================
# DISPLAY RESULTS
# ============================================================

print("\n" + "=" * 100)
print(f"TOP 11 FANTASY PLAYERS — {TEAM1} VS {TEAM2}")
print("Based only on head-to-head performance")
print("=" * 100)

print(
    f"{'Rank':<6}{'Player':<24}{'Team':<34}"
    f"{'Matches':<10}{'Runs':<8}{'Wickets':<10}{'Rating /10'}"
)
print("-" * 100)

for rank, player in enumerate(top_11, 1):
    rating_10 = player["rating"] / max_rating * 10 if max_rating else 0

    print(
        f"{rank:<6}{player['player']:<24}{player['team']:<34}"
        f"{player['matches']:<10}{player['runs']:<8}"
        f"{player['wickets']:<10}{rating_10:.2f}"
    )

team1_count = sum(1 for p in top_11 if p["team"] == TEAM1)
team2_count = sum(1 for p in top_11 if p["team"] == TEAM2)

print(f"\n{TEAM1}: {team1_count} players")
print(f"{TEAM2}: {team2_count} players")
print(f"\nCSV saved to: {OUTPUT_FILE}")
print("Analysis completed successfully.")
