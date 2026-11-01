import os

os.environ["PYSPARK_PYTHON"] = r"C:\Python313\python.exe"
os.environ["PYSPARK_DRIVER_PYTHON"] = r"C:\Python313\python.exe"

from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("IPL HDFS Test") \
    .master("local[*]") \
    .config("spark.pyspark.python", r"C:\Python313\python.exe") \
    .config("spark.pyspark.driver.python", r"C:\Python313\python.exe") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

print()
print("==========================================")
print(" IPL HDFS + PYSPARK TEST")
print("==========================================")

HDFS_PATH = "hdfs://localhost:9000/ipl/data/*.json"

print()
print("Reading IPL data from HDFS...")

df = spark.read \
    .option("multiLine", "true") \
    .json(HDFS_PATH)

print()
print("HDFS DATA READ SUCCESSFULLY!")
print()

print("Columns detected:")
print(df.columns)

print()
print("Schema:")
df.printSchema()

print()
print("First record:")
df.show(1, truncate=False)

print()
print("==========================================")
print(" HDFS + PYSPARK TEST COMPLETED")
print("==========================================")

spark.stop()