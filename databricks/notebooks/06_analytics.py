from pyspark.sql import functions as F
from pyspark.sql.window import Window

print("FinSight — Databricks Analytics")
print("=" * 50)

GOLD_PATH = "/Volumes/workspace/default/finsight_data/gold/financial_metrics"

df = (
    spark.read
    .format("delta")
    .load(GOLD_PATH)
)

print(f"Gold records: {df.count():,}")

# ---------------------------------------------------------
# Company analytics
# ---------------------------------------------------------

company_analytics = (
    df
    .groupBy("company_id")
    .agg(
        F.round(F.avg("revenue"), 2).alias("avg_revenue"),
        F.round(
            F.avg("net_profit_margin_pct"), 2
        ).alias("avg_net_profit_margin_pct"),
        F.round(
            F.avg("roa_pct"), 2
        ).alias("avg_roa_pct"),
        F.round(
            F.avg("revenue_growth_yoy_pct"), 2
        ).alias("avg_revenue_growth_yoy_pct"),
    )
)

# ---------------------------------------------------------
# Company ROA ranking
# ---------------------------------------------------------

ranking_window = Window.orderBy(
    F.col("avg_roa_pct").desc()
)

company_analytics = (
    company_analytics
    .withColumn(
        "roa_rank",
        F.rank().over(ranking_window),
    )
)

print("\nTop companies by ROA:")

display(
    company_analytics
    .orderBy(F.col("avg_roa_pct").desc())
    .limit(10)
)

# ---------------------------------------------------------
# Industry analytics
# ---------------------------------------------------------

industry_analytics = (
    df
    .groupBy("industry_id")
    .agg(
        F.round(
            F.avg("revenue"), 2
        ).alias("avg_revenue"),
        F.round(
            F.avg("net_profit_margin_pct"), 2
        ).alias("avg_net_profit_margin_pct"),
        F.round(
            F.avg("operating_margin_pct"), 2
        ).alias("avg_operating_margin_pct"),
        F.round(
            F.avg("debt_to_assets_pct"), 2
        ).alias("avg_debt_to_assets_pct"),
        F.round(
            F.avg("roa_pct"), 2
        ).alias("avg_roa_pct"),
        F.countDistinct(
            "company_id"
        ).alias("company_count"),
    )
)

print("\nIndustry analytics:")

display(
    industry_analytics
    .orderBy(F.col("avg_roa_pct").desc())
)

print("\nDatabricks analytics completed successfully.")