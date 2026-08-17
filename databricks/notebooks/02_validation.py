from pyspark.sql import functions as F

print("FinSight — Databricks Data Validation")
print("=" * 50)

BRONZE_PATH = "/Volumes/workspace/default/finsight_data/bronze/financials"

financials = (
    spark.read
    .format("delta")
    .load(BRONZE_PATH)
)

total_records = financials.count()

print(f"Records: {total_records:,}")

# ---------------------------------------------------------
# 1. Null validation
# ---------------------------------------------------------

print("\n1. Null validation")

null_report = financials.select(
    [
        F.count(
            F.when(F.col(column).isNull(), column)
        ).alias(column)
        for column in financials.columns
    ]
)

display(null_report)

# ---------------------------------------------------------
# 2. Duplicate financial IDs
# ---------------------------------------------------------

print("\n2. Duplicate financial IDs")

duplicate_ids = (
    financials
    .groupBy("financial_id")
    .count()
    .filter(F.col("count") > 1)
)

duplicate_count = duplicate_ids.count()

print(f"Duplicate financial IDs: {duplicate_count:,}")

display(duplicate_ids.limit(20))

# ---------------------------------------------------------
# 3. Invalid fiscal quarters
# ---------------------------------------------------------

print("\n3. Invalid fiscal quarters")

invalid_quarters = financials.filter(
    ~F.col("fiscal_quarter").between(1, 4)
)

invalid_quarter_count = invalid_quarters.count()

print(f"Invalid fiscal quarters: {invalid_quarter_count:,}")

# ---------------------------------------------------------
# 4. Invalid financial values
# ---------------------------------------------------------

print("\n4. Invalid financial values")

invalid_financials = financials.filter(
    (F.col("revenue") < 0)
    | (F.col("total_assets") < 0)
    | (F.col("total_liabilities") < 0)
    | (F.col("total_debt") < 0)
)

invalid_financial_count = invalid_financials.count()

print(
    f"Records with invalid financial values: "
    f"{invalid_financial_count:,}"
)

# ---------------------------------------------------------
# 5. Balance-sheet consistency
# ---------------------------------------------------------

print("\n5. Balance-sheet consistency")

invalid_balance = financials.filter(
    (F.col("total_liabilities") > F.col("total_assets"))
    | (F.col("total_debt") > F.col("total_liabilities"))
)

invalid_balance_count = invalid_balance.count()

print(
    f"Balance-sheet violations: "
    f"{invalid_balance_count:,}"
)

# ---------------------------------------------------------
# 6. Date validation
# ---------------------------------------------------------

print("\n6. Date validation")

invalid_dates = financials.filter(
    F.col("period_end_date").isNull()
)

invalid_date_count = invalid_dates.count()

print(f"Invalid/missing dates: {invalid_date_count:,}")

# ---------------------------------------------------------
# 7. Validation summary
# ---------------------------------------------------------

checks = [
    ("Total records", total_records),
    ("Duplicate financial IDs", duplicate_count),
    ("Invalid fiscal quarters", invalid_quarter_count),
    ("Invalid financial values", invalid_financial_count),
    ("Balance-sheet violations", invalid_balance_count),
    ("Invalid/missing dates", invalid_date_count),
]

validation_summary = spark.createDataFrame(
    checks,
    ["check", "count"],
)

print("\nValidation summary:")
display(validation_summary)

print("\nValidation completed successfully.")