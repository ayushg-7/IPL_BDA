# IPL Big Data Analytics

An interactive dashboard for exploring IPL match history, player and team performance, match predictions, fantasy recommendations, and big-data analytics.

## Screenshots

### IPL Analytics Dashboard
An overview of the project, match dataset, seasons, and technologies.

![IPL Big Data Analytics dashboard](docs/images/dashboard.png)

### Team Performance
Compare team match records, wins, losses, and win percentages.

![Team performance table and chart](docs/images/team-analytics.png)

### Top IPL Players
Explore leading players by runs, with additional performance statistics.

![Top IPL players by runs](docs/images/top-players.png)

### Player Career Analytics
View a player's career totals, records, and season-by-season performance.

![Player career statistics](docs/images/player-career.png)

### Match Winner Prediction
Choose teams and match conditions to see the predicted win probabilities.

![IPL match winner prediction](docs/images/match-prediction.png)

### MapReduce Visualization
Visualize season-wise player performance from the MapReduce output.

![Virat Kohli season-wise IPL runs](docs/images/mapreduce-visualization.png)

## About the Project

This project turns ball-by-ball IPL match records into an interactive way to explore the tournament. The match data is read from Cricsheet JSON files, processed into player and team statistics, and presented alongside visualizations and prediction/recommendation features. It brings together data analysis, machine learning concepts, and big-data tools in one project.

## Dashboard Modules

- **Dashboard:** A quick introduction and overview of the dataset and technologies.
- **Team Analytics:** Compare team match counts, wins, losses, and win percentages.
- **Player Analytics:** Search for a player and explore career totals and season-by-season performance.
- **Match Winner Prediction:** Select teams, venue, and toss conditions to view estimated win probabilities.
- **Fantasy Recommendations:** Browse player recommendations and a suggested fantasy XI when the generated results are available.
- **Big Data Analytics:** Explore PySpark and MapReduce result tables.
- **Visualizations:** View charts of player, bowling, team, and fantasy performance.

## Analytics Workflow

1. Match JSON files in `data/` provide match information and ball-by-ball deliveries.
2. Python scripts in `python/` process the data into team and player statistics, prediction inputs, and fantasy recommendation outputs.
3. PySpark and MapReduce workflows provide additional big-data processing results.
4. R scripts in `r/` generate charts from analytics data.
5. The Streamlit app in `app.py` displays the available data and results.

Generated tables and charts are stored in `output/`. Some dashboard sections depend on those output files, so they may show a notice until the corresponding analytics have been run.

## Features

- Interactive Streamlit dashboard with team and player analytics.
- Match winner estimates based on selected match details and historical IPL results.
- Fantasy player recommendations, including player similarity and a suggested XI.
- Big-data analytics views for PySpark and MapReduce results.
- Performance visualizations, including R-generated charts.
- Historical match data in JSON format.

> **Note:** Predictions and recommendations are data-driven estimates for exploration and learning; they are not guarantees of real match outcomes.

## Technologies

- Python, Streamlit, and Pandas
- Scikit-learn and NumPy for analytics scripts
- PySpark for distributed data processing
- R, ggplot2, dplyr, and readr for visualizations

## Project Structure

```text
.
├── app.py                 # Streamlit dashboard
├── data/                  # IPL match data in JSON format
├── docs/images/           # Screenshots used in this README
├── output/                # Analytics results and generated charts
├── python/                # Data processing, analytics, and recommendation scripts
└── r/                     # R visualization scripts
```

## Run the Dashboard

The dashboard uses the JSON match files in `data/` and reads available analytics results from `output/`.

1. Install Python 3 and open a terminal in the project folder.
2. Create and activate a virtual environment (PowerShell):

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Install the dashboard dependencies:

   ```powershell
   python -m pip install streamlit pandas
   ```

4. Start the dashboard:

   ```powershell
   streamlit run app.py
   ```

Streamlit will print a local URL (usually `http://localhost:8501`) to open in your browser.

> Some analytics scripts in `python/` and `r/` require additional packages and, depending on the script, a configured PySpark/Hadoop environment.

## Data

The `data/` folder contains 1,243 IPL match files in Cricsheet JSON format. See [`data/README.txt`](data/README.txt) for dataset notes. Cricsheet provides the [format documentation](https://cricsheet.org/format/json/) and [available downloads](https://cricsheet.org/downloads/).
