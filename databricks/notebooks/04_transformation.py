from pyspark.sql import functions as F
from pyspark.sql.window import Window

print("FinSight — Databricks Transformation")
print("=" * 50)

SILVER_PATH = "/Volumes/workspace/default/finsight_data/silver/financials"
GOLD_PATH = "/Volumes/workspace/default/finsight_data/gold/financial_metrics"

df = spark.read.format("delta").load(SILVER_PATH)

# ---------------------------------------------------------
# Financial metrics
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
            (F.col("revenue") - F.col("operating_expenses"))
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
                F.col("total_assets") - F.col("total_liabilities"),
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
# YoY revenue growth
# ---------------------------------------------------------

window = Window.partitionBy("company_id").orderBy("period_end_date")

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
                / F.nullif(F.col("previous_year_revenue"), F.lit(0))
                - 1
            ) * 100,
            2,
        ),
    )
    .drop("previous_year_revenue")
)

(
    df.write
    .format("delta")
    .mode("overwrite")
    .partitionBy("fiscal_year")
    .save(GOLD_PATH)
)

print(f"Gold records: {df.count():,}")
print(f"Gold path: {GOLD_PATH}")

display(
    df.select(
        "company_id",
        "fiscal_year",
        "fiscal_quarter",
        "revenue",
        "net_profit_margin_pct",
        "operating_margin_pct",
        "debt_to_assets_pct",
        "roa_pct",
        "revenue_growth_yoy_pct",
    ).limit(10)
)

print("\nTransformation completed successfully.")