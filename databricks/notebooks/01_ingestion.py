from pyspark.sql import functions as F

print("FinSight — Databricks Ingestion")
print("=" * 50)

SOURCE_PATH = "/Volumes/workspace/default/finsight_data/financials.csv"
TARGET_PATH = "/Volumes/workspace/default/finsight_data/bronze/financials"

print(f"Source: {SOURCE_PATH}")

# ---------------------------------------------------------
# 1. Extract
# ---------------------------------------------------------

financials = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .csv(SOURCE_PATH)
)

record_count = financials.count()

print(f"Records loaded: {record_count:,}")

# ---------------------------------------------------------
# 2. Inspect schema
# ---------------------------------------------------------

print("\nSchema:")
financials.printSchema()

# ---------------------------------------------------------
# 3. Basic inspection
# ---------------------------------------------------------

print("\nSample records:")
display(financials.limit(10))

# ---------------------------------------------------------
# 4. Dataset statistics
# ---------------------------------------------------------

print("\nDataset summary:")

display(
    financials.select(
        F.count("*").alias("record_count"),
        F.countDistinct("company_id").alias("company_count"),
        F.countDistinct("fiscal_year").alias("year_count"),
    )
)

# ---------------------------------------------------------
# 5. Financial year distribution
# ---------------------------------------------------------

print("\nFinancial years:")

display(
    financials
    .groupBy("fiscal_year")
    .count()
    .orderBy("fiscal_year")
)

# ---------------------------------------------------------
# 6. Write Bronze layer
# ---------------------------------------------------------

(
    financials.write
    .format("delta")
    .mode("overwrite")
    .save(TARGET_PATH)
)

print(f"\nBronze dataset written to: {TARGET_PATH}")

# ---------------------------------------------------------
# 7. Verify Bronze layer
# ---------------------------------------------------------

bronze = spark.read.format("delta").load(TARGET_PATH)

print(f"Bronze records: {bronze.count():,}")

print("\nIngestion completed successfully.")
