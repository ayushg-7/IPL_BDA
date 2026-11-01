import os

# ============================================================
# PYTHON CONFIGURATION
# ============================================================

os.environ["PYSPARK_PYTHON"] = r"C:\Python313\python.exe"
os.environ["PYSPARK_DRIVER_PYTHON"] = r"C:\Python313\python.exe"

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum, count, round, when, desc


# ============================================================
# SPARK SESSION
# ============================================================

spark = SparkSession.builder \
    .appName("IPL Big Data Analytics - HDFS") \
    .master("local[*]") \
    .config("spark.pyspark.python", r"C:\Python313\python.exe") \
    .config("spark.pyspark.driver.python", r"C:\Python313\python.exe") \
    .config("spark.hadoop.io.native.lib.available", "false") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")


# ============================================================
# HDFS INPUT
# ============================================================

HDFS_PATH = "hdfs://localhost:9000/ipl/data/*.json"

OUTPUT_FOLDER = r"C:\Users\Hp\Downloads\IPLBDAMP\output\pyspark"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)


print()
print("==========================================")
print(" IPL BIG DATA ANALYTICS - PYSPARK + HDFS")
print("==========================================")
print()

print("Reading IPL data from HDFS...")
print(HDFS_PATH)


# ============================================================
# READ JSON FROM HDFS
# ============================================================

df = spark.read \
    .option("multiLine", "true") \
    .json(HDFS_PATH)


print()
print("HDFS DATA READ SUCCESSFULLY!")
print()


# ============================================================
# FLATTEN IPL DATA
# ============================================================

from pyspark.sql.functions import explode

# Explode innings
innings_df = df.select(
    col("info.season").alias("season"),
    col("info.venue").alias("venue"),
    explode("innings").alias("innings")
)

# Get batting team and overs
overs_df = innings_df.select(
    "season",
    "venue",
    col("innings.team").alias("batting_team"),
    explode("innings.overs").alias("over")
)

# Get deliveries
deliveries_df = overs_df.select(
    "season",
    "venue",
    "batting_team",
    col("over.over").alias("over_number"),
    explode("over.deliveries").alias("delivery")
)


# ============================================================
# EXTRACT BALL-BY-BALL INFORMATION
# ============================================================

ball_df = deliveries_df.select(
    "season",
    "venue",
    "batting_team",
    "over_number",

    col("delivery.batter").alias("batter"),
    col("delivery.bowler").alias("bowler"),

    col("delivery.runs.batter").alias("batter_runs"),
    col("delivery.runs.total").alias("total_runs"),

    col("delivery.wickets").alias("wickets")
)


# ============================================================
# CALCULATE BOWLER WICKETS
# ============================================================

ball_df = ball_df.withColumn(
    "bowler_wickets",
    when(
        col("wickets").isNull(),
        0
    ).otherwise(
        count("*").over(
            __import__(
                "pyspark.sql.window",
                fromlist=["Window"]
            ).Window.partitionBy(
                "season",
                "venue",
                "batting_team",
                "over_number",
                "batter",
                "bowler",
                "batter_runs",
                "total_runs"
            )
        )
    )
)


# The above temporary calculation is replaced below
# with a simpler and more accurate wicket calculation.

from pyspark.sql.functions import size, expr

ball_df = ball_df.drop("bowler_wickets")

ball_df = ball_df.withColumn(
    "bowler_wickets",
    when(
        col("wickets").isNull(),
        0
    ).otherwise(
        expr("""
            aggregate(
                wickets,
                0,
                (acc, w) ->
                    acc +
                    CASE
                        WHEN w.kind IN (
                            'run out',
                            'retired hurt',
                            'retired out',
                            'obstructing the field'
                        )
                        THEN 0
                        ELSE 1
                    END
            )
        """)
    )
)


print("Ball-by-ball DataFrame created successfully.")
print()


# ============================================================
# 1. TOP 10 RUN SCORERS
# ============================================================

print("==========================================")
print(" TOP 10 RUN SCORERS")
print("==========================================")

player_runs = (
    ball_df
    .groupBy("batter")
    .agg(
        sum("batter_runs").alias("total_runs"),
        count("*").alias("balls_faced")
    )
    .withColumn(
        "strike_rate",
        round(
            (col("total_runs") / col("balls_faced")) * 100,
            2
        )
    )
    .orderBy(desc("total_runs"))
)

player_runs.show(10, truncate=False)

player_runs.toPandas().to_csv(
    os.path.join(
        OUTPUT_FOLDER,
        "player_runs.csv"
    ),
    index=False
)


# ============================================================
# 2. BOWLING STATISTICS
# ============================================================

print()
print("==========================================")
print(" TOP BOWLERS")
print("==========================================")

bowling_statistics = (
    ball_df
    .groupBy("bowler")
    .agg(
        count("*").alias("balls_bowled"),

        sum("total_runs").alias("runs_conceded"),

        sum("bowler_wickets").alias("wickets")
    )
    .withColumn(
        "overs",
        round(
            col("balls_bowled") / 6,
            2
        )
    )
    .withColumn(
        "economy",
        round(
            (col("runs_conceded") /
             col("balls_bowled")) * 6,
            2
        )
    )
    .orderBy(desc("wickets"))
)

bowling_statistics.show(
    10,
    truncate=False
)

bowling_statistics.toPandas().to_csv(
    os.path.join(
        OUTPUT_FOLDER,
        "bowling_statistics.csv"
    ),
    index=False
)


# ============================================================
# 3. TEAM STATISTICS
# ============================================================

print()
print("==========================================")
print(" TEAM STATISTICS")
print("==========================================")

team_statistics = (
    ball_df
    .groupBy("batting_team")
    .agg(
        sum("total_runs").alias("total_runs"),
        count("*").alias("balls_faced")
    )
    .withColumn(
        "runs_per_ball",
        round(
            col("total_runs") /
            col("balls_faced"),
            2
        )
    )
    .orderBy(desc("total_runs"))
)

team_statistics.show(
    truncate=False
)

team_statistics.toPandas().to_csv(
    os.path.join(
        OUTPUT_FOLDER,
        "team_statistics.csv"
    ),
    index=False
)


# ============================================================
# COMPLETED
# ============================================================

print()
print("==========================================")
print(" HDFS + PYSPARK ANALYTICS COMPLETED")
print("==========================================")

print()
print("Input:")
print(HDFS_PATH)

print()
print("Results:")
print(OUTPUT_FOLDER)

print()

spark.stop()