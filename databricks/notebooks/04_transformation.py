from pyspark.sql import functions as F
from pyspark.sql.window import Window

print("FinSight — Databricks Transformation")
print("=" * 50)

SILVER_PATH = "/Volumes/workspace/default/finsight_data/silver/financials"
COMPANIES_PATH = "/Volumes/workspace/default/finsight_data/companies.csv"
GOLD_PATH = "/Volumes/workspace/default/finsight_data/gold/financial_metrics"

# ---------------------------------------------------------
# 1. Read Silver financial data
# ---------------------------------------------------------

df = (
    spark.read
    .format("delta")
    .load(SILVER_PATH)
)

print(f"Silver records: {df.count():,}")

# ---------------------------------------------------------
# 2. Read company reference data
# ---------------------------------------------------------

companies = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .csv(COMPANIES_PATH)
    .select(
        "company_id",
        "company_name",
        "ticker",
        "industry_id",
        "industry_name",
    )
)

print(f"Company reference records: {companies.count():,}")

# ---------------------------------------------------------
# 3. Join financial data with company reference data
# ---------------------------------------------------------

df = (
    df.join(
        companies,
        on="company_id",
        how="left",
    )
)

# ---------------------------------------------------------
# 4. Financial metrics
# ---------------------------------------------------------

df = (
    df
    .withColumn(
        "net_profit_margin_pct",
        F.round(
            F.col("net_income")
            / F.nullif(F.col("revenue"), F.lit(0))
            * 100,
            2,
        ),
    )
    .withColumn(
        "operating_margin_pct",
        F.round(
            (
                F.col("revenue")
                - F.col("operating_expenses")
            )
            / F.nullif(F.col("revenue"), F.lit(0))
            * 100,
            2,
        ),
    )
    .withColumn(
        "debt_to_assets_pct",
        F.round(
            F.col("total_debt")
            / F.nullif(F.col("total_assets"), F.lit(0))
            * 100,
            2,
        ),
    )
    .withColumn(
        "debt_to_equity_pct",
        F.round(
            F.col("total_debt")
            / F.nullif(
                F.col("total_assets")
                - F.col("total_liabilities"),
                F.lit(0),
            )
            * 100,
            2,
        ),
    )
    .withColumn(
        "roa_pct",
        F.round(
            F.col("net_income")
            / F.nullif(F.col("total_assets"), F.lit(0))
            * 100,
            2,
        ),
    )
    .withColumn(
        "operating_cash_flow_margin_pct",
        F.round(
            F.col("operating_cash_flow")
            / F.nullif(F.col("revenue"), F.lit(0))
            * 100,
            2,
        ),
    )
)

# ---------------------------------------------------------
# 5. YoY revenue growth
# ---------------------------------------------------------

window = (
    Window
    .partitionBy("company_id")
    .orderBy("period_end_date")
)

df = (
    df
    .withColumn(
        "previous_year_revenue",
        F.lag("revenue", 4).over(window),
    )
    .withColumn(
        "revenue_growth_yoy_pct",
        F.round(
            (
                F.col("revenue")
                / F.nullif(
                    F.col("previous_year_revenue"),
                    F.lit(0),
                )
                - 1
            )
            * 100,
            2,
        ),
    )
    .drop("previous_year_revenue")
)

# ---------------------------------------------------------
# 6. Verify enrichment
# ---------------------------------------------------------

missing_company_metadata = (
    df
    .filter(
        F.col("company_name").isNull()
        | F.col("ticker").isNull()
        | F.col("industry_id").isNull()
        | F.col("industry_name").isNull()
    )
    .count()
)

print(
    f"Records missing company metadata: "
    f"{missing_company_metadata:,}"
)

if missing_company_metadata > 0:
    raise ValueError(
        "Gold transformation failed: "
        f"{missing_company_metadata:,} records are missing "
        "company reference data."
    )

# ---------------------------------------------------------
# 7. Write Gold Delta layer
# ---------------------------------------------------------

(
    df.write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .partitionBy("fiscal_year")
    .save(GOLD_PATH)
)

gold_count = df.count()

print(f"Gold records: {gold_count:,}")
print(f"Gold path: {GOLD_PATH}")

# ---------------------------------------------------------
# 8. Verify Gold schema
# ---------------------------------------------------------

print("\nGold schema:")
df.printSchema()

# ---------------------------------------------------------
# 9. Sample enriched records
# ---------------------------------------------------------

print("\nSample enriched records:")

display(
    df.select(
        "company_id",
        "company_name",
        "ticker",
        "industry_id",
        "industry_name",
        "fiscal_year",
        "fiscal_quarter",
        "revenue",
        "net_profit_margin_pct",
        "operating_margin_pct",
        "debt_to_assets_pct",
        "roa_pct",
        "operating_cash_flow_margin_pct",
        "revenue_growth_yoy_pct",
    )
    .limit(10)
)

print("\nTransformation completed successfully.")