from pyspark.sql import functions as F

print("FinSight — Databricks Ingestion")
print("=" * 50)

SOURCE_PATH = "/Volumes/workspace/default/finsight_data/financials.csv"
TARGET_PATH = "/Volumes/workspace/default/finsight_data/bronze/financials"

print(f"Source: {SOURCE_PATH}")
