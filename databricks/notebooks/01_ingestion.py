from pyspark.sql import functions as F

print("FinSight — Databricks Ingestion")
print("=" * 50)

# Read the existing processed financial dataset from the repository.
# Databricks Git folders expose repository files through /Workspace.
source_path = "/Workspace" + dbutils.entry_point.getDbutils().notebook().getContext().notebookPath().get().rsplit("/", 3)[0] + "/data/processed/financials.csv"

print(f"Source: {source_path}")

financials = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .csv(source_path)
)

print(f"Records loaded: {financials.count():,}")

print("\nSchema:")
financials.printSchema()

print("\nSample records:")
display(financials.limit(10))

print("\nFinancial years:")
display(
    financials
    .groupBy("fiscal_year")
    .count()
    .orderBy("fiscal_year")
)

print("\nDataset summary:")
display(
    financials.select(
        F.count("*").alias("record_count"),
        F.countDistinct("company_id").alias("company_count"),
        F.countDistinct("fiscal_year").alias("year_count"),
    )
)

print("\nIngestion completed successfully.")
