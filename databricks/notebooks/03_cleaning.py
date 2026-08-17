from pyspark.sql import functions as F

print("FinSight — Databricks Cleaning")
print("=" * 50)

BRONZE_PATH = "/Volumes/workspace/default/finsight_data/bronze/financials"
SILVER_PATH = "/Volumes/workspace/default/finsight_data/silver/financials"

df = spark.read.format("delta").load(BRONZE_PATH)

before = df.count()

print(f"Bronze records: {before:,}")

# Standardize column names
df = df.toDF(*[column.lower().strip() for column in df.columns])

# Cast numeric fields explicitly
numeric_columns = [
    "financial_id",
    "company_id",
    "fiscal_year",
    "fiscal_quarter",
    "revenue",
    "operating_expenses",
    "net_income",
    "total_assets",
    "total_liabilities",
    "total_debt",
    "operating_cash_flow",
    "investing_cash_flow",
    "financing_cash_flow",
]

for column in numeric_columns:
    df = df.withColumn(column, F.col(column).cast("double"))

df = df.withColumn(
    "period_end_date",
    F.to_date("period_end_date")
)

# Remove exact duplicate records
df = df.dropDuplicates()

# Remove duplicate financial IDs while keeping the first record
df = (
    df
    .dropDuplicates(["financial_id"])
)

# Apply core financial consistency rules
df = df.filter(
    F.col("fiscal_quarter").between(1, 4)
)

df = df.filter(
    (F.col("revenue") >= 0)
    & (F.col("total_assets") >= 0)
    & (F.col("total_liabilities") >= 0)
    & (F.col("total_debt") >= 0)
)

df = df.filter(
    F.col("total_liabilities") <= F.col("total_assets")
)

df = df.filter(
    F.col("total_debt") <= F.col("total_liabilities")
)

df = df.filter(
    F.col("period_end_date").isNotNull()
)

after = df.count()

(
    df.write
    .format("delta")
    .mode("overwrite")
    .save(SILVER_PATH)
)

print(f"Silver records: {after:,}")
print(f"Records removed: {before - after:,}")
print(f"Silver path: {SILVER_PATH}")
print("\nCleaning completed successfully.")