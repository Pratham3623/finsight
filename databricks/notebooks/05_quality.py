from pyspark.sql import functions as F

print("FinSight — Databricks Quality")
print("=" * 50)

GOLD_PATH = "/Volumes/workspace/default/finsight_data/gold/financial_metrics"

df = spark.read.format("delta").load(GOLD_PATH)

total = df.count()

checks = []

def add_check(name, count):
    checks.append((name, int(count)))

# Null financial IDs
add_check(
    "Null financial IDs",
    df.filter(F.col("financial_id").isNull()).count(),
)

# Null company IDs
add_check(
    "Null company IDs",
    df.filter(F.col("company_id").isNull()).count(),
)

# Duplicate IDs
add_check(
    "Duplicate financial IDs",
    df.groupBy("financial_id")
      .count()
      .filter(F.col("count") > 1)
      .count(),
)

# Invalid margins
add_check(
    "Invalid ROA",
    df.filter(
        F.col("roa_pct").isNull()
        | F.isnan("roa_pct")
    ).count(),
)

# Missing dates
add_check(
    "Missing period dates",
    df.filter(F.col("period_end_date").isNull()).count(),
)

quality = spark.createDataFrame(
    checks,
    ["check", "failure_count"],
)

display(quality)

failures = quality.agg(
    F.sum("failure_count").alias("total_failures")
).collect()[0]["total_failures"]

print(f"Records evaluated: {total:,}")
print(f"Total quality failures: {failures:,}")

if failures == 0:
    print("QUALITY STATUS: PASS")
else:
    print("QUALITY STATUS: REVIEW")

print("\nQuality assessment completed.")