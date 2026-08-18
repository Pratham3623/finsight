from pyspark.sql import functions as F
from pyspark.sql.window import Window

print("FinSight — Databricks BI Analytics")
print("=" * 50)

GOLD_PATH = "/Volumes/workspace/default/finsight_data/gold/financial_metrics"

BI_COMPANY_PATH = "/Volumes/workspace/default/finsight_data/bi/company_performance"
BI_INDUSTRY_PATH = "/Volumes/workspace/default/finsight_data/bi/industry_performance"
BI_RANKINGS_PATH = "/Volumes/workspace/default/finsight_data/bi/company_rankings"

df = (
    spark.read
    .format("delta")
    .load(GOLD_PATH)
)

print(f"Gold records: {df.count():,}")

# =========================================================
# 1. COMPANY PERFORMANCE
# =========================================================

company_performance = (
    df
    .groupBy("company_id", "fiscal_year", "fiscal_quarter")
    .agg(
        F.sum("revenue").alias("revenue"),
        F.sum("operating_expenses").alias("operating_expenses"),
        F.sum("net_income").alias("net_income"),
        F.sum("total_assets").alias("total_assets"),
        F.sum("total_liabilities").alias("total_liabilities"),
        F.sum("total_debt").alias("total_debt"),
        F.sum("operating_cash_flow").alias("operating_cash_flow"),
        F.sum("investing_cash_flow").alias("investing_cash_flow"),
        F.sum("financing_cash_flow").alias("financing_cash_flow"),

        F.round(
            F.avg("net_profit_margin_pct"), 2
        ).alias("net_profit_margin_pct"),

        F.round(
            F.avg("operating_margin_pct"), 2
        ).alias("operating_margin_pct"),

        F.round(
            F.avg("debt_to_assets_pct"), 2
        ).alias("debt_to_assets_pct"),

        F.round(
            F.avg("debt_to_equity_pct"), 2
        ).alias("debt_to_equity_pct"),

        F.round(
            F.avg("roa_pct"), 2
        ).alias("roa_pct"),

        F.round(
            F.avg("operating_cash_flow_margin_pct"), 2
        ).alias("operating_cash_flow_margin_pct"),

        F.round(
            F.avg("revenue_growth_yoy_pct"), 2
        ).alias("revenue_growth_yoy_pct"),
    )
)

(
    company_performance.write
    .format("delta")
    .mode("overwrite")
    .partitionBy("fiscal_year")
    .save(BI_COMPANY_PATH)
)

print(f"Company BI records: {company_performance.count():,}")


# =========================================================
# 2. INDUSTRY PERFORMANCE
# =========================================================

industry_performance = (
    df
    .groupBy("industry_id", "fiscal_year", "fiscal_quarter")
    .agg(
        F.countDistinct("company_id").alias("company_count"),

        F.sum("revenue").alias("total_revenue"),
        F.sum("operating_expenses").alias("total_operating_expenses"),
        F.sum("net_income").alias("total_net_income"),
        F.sum("total_assets").alias("total_assets"),
        F.sum("total_liabilities").alias("total_liabilities"),
        F.sum("total_debt").alias("total_debt"),
        F.sum("operating_cash_flow").alias(
            "total_operating_cash_flow"
        ),

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
            F.avg("debt_to_equity_pct"), 2
        ).alias("avg_debt_to_equity_pct"),

        F.round(
            F.avg("roa_pct"), 2
        ).alias("avg_roa_pct"),

        F.round(
            F.avg("operating_cash_flow_margin_pct"), 2
        ).alias(
            "avg_operating_cash_flow_margin_pct"
        ),

        F.round(
            F.avg("revenue_growth_yoy_pct"), 2
        ).alias("avg_revenue_growth_yoy_pct"),
    )
)

(
    industry_performance.write
    .format("delta")
    .mode("overwrite")
    .partitionBy("fiscal_year")
    .save(BI_INDUSTRY_PATH)
)

print(
    f"Industry BI records: "
    f"{industry_performance.count():,}"
)


# =========================================================
# 3. COMPANY RANKINGS
# =========================================================

ranking_window = Window.partitionBy(
    "fiscal_year",
    "fiscal_quarter"
)

company_rankings = (
    company_performance
    .withColumn(
        "roa_rank",
        F.rank().over(
            ranking_window.orderBy(
                F.col("roa_pct").desc_nulls_last()
            )
        ),
    )
    .withColumn(
        "revenue_rank",
        F.rank().over(
            ranking_window.orderBy(
                F.col("revenue").desc_nulls_last()
            )
        ),
    )
)

(
    company_rankings.write
    .format("delta")
    .mode("overwrite")
    .partitionBy("fiscal_year")
    .save(BI_RANKINGS_PATH)
)

print(
    f"Ranking BI records: "
    f"{company_rankings.count():,}"
)


# =========================================================
# 4. VERIFICATION
# =========================================================

print("\nBI layer verification:")

print(
    f"Company performance: "
    f"{spark.read.format('delta').load(BI_COMPANY_PATH).count():,}"
)

print(
    f"Industry performance: "
    f"{spark.read.format('delta').load(BI_INDUSTRY_PATH).count():,}"
)

print(
    f"Company rankings: "
    f"{spark.read.format('delta').load(BI_RANKINGS_PATH).count():,}"
)


print("\nTop companies by ROA:")

display(
    company_rankings
    .select(
        "company_id",
        "fiscal_year",
        "fiscal_quarter",
        "roa_pct",
        "roa_rank",
        "revenue",
        "revenue_rank",
    )
    .orderBy(
        F.col("roa_rank").asc(),
        F.col("fiscal_year").desc(),
        F.col("fiscal_quarter").desc(),
    )
    .limit(10)
)

print("\nTop industries by ROA:")

display(
    industry_performance
    .select(
        "industry_id",
        "fiscal_year",
        "fiscal_quarter",
        "avg_roa_pct",
        "company_count",
        "total_revenue",
    )
    .orderBy(
        F.col("avg_roa_pct").desc()
    )
    .limit(10)
)

print("\nDatabricks BI analytics completed successfully.")