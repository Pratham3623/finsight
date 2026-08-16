from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F


def build_industry_analytics(
    dataframe: DataFrame,
) -> DataFrame:
    return (
        dataframe
        .groupBy("industry_name")
        .agg(
            F.countDistinct("company_id").alias(
                "company_count"
            ),
            F.round(F.avg("revenue"), 2).alias(
                "avg_revenue"
            ),
            F.round(
                F.avg("net_profit_margin_pct"),
                2,
            ).alias(
                "avg_net_profit_margin_pct"
            ),
            F.round(
                F.avg("operating_margin_pct"),
                2,
            ).alias(
                "avg_operating_margin_pct"
            ),
            F.round(
                F.avg("debt_to_assets_pct"),
                2,
            ).alias(
                "avg_debt_to_assets_pct"
            ),
            F.round(
                F.avg("return_on_assets_pct"),
                2,
            ).alias(
                "avg_roa_pct"
            ),
            F.round(
                F.avg("revenue_growth_yoy_pct"),
                2,
            ).alias(
                "avg_revenue_growth_yoy_pct"
            ),
            F.round(
                F.avg("operating_cash_flow_margin_pct"),
                2,
            ).alias(
                "avg_operating_cash_flow_margin_pct"
            ),
        )
    )


def build_company_analytics(
    dataframe: DataFrame,
) -> DataFrame:
    company_metrics = (
        dataframe
        .groupBy(
            "company_id",
            "company_name",
            "ticker",
            "industry_name",
        )
        .agg(
            F.round(F.avg("revenue"), 2).alias(
                "avg_revenue"
            ),
            F.round(
                F.avg("net_profit_margin_pct"),
                2,
            ).alias(
                "avg_net_profit_margin_pct"
            ),
            F.round(
                F.avg("return_on_assets_pct"),
                2,
            ).alias(
                "avg_roa_pct"
            ),
            F.round(
                F.avg("revenue_growth_yoy_pct"),
                2,
            ).alias(
                "avg_revenue_growth_yoy_pct"
            ),
            F.round(
                F.avg("debt_to_assets_pct"),
                2,
            ).alias(
                "avg_debt_to_assets_pct"
            ),
            F.round(
                F.avg("operating_cash_flow_margin_pct"),
                2,
            ).alias(
                "avg_operating_cash_flow_margin_pct"
            ),
        )
    )

    # Global rankings are intentionally unpartitioned because
    # we want rankings across all companies.
    roa_window = Window.orderBy(
        F.col("avg_roa_pct").desc_nulls_last(),
        F.col("company_id").asc(),
    )

    revenue_window = Window.orderBy(
        F.col("avg_revenue").desc_nulls_last(),
        F.col("company_id").asc(),
    )

    return (
        company_metrics
        .withColumn(
            "rank_by_roa",
            F.dense_rank().over(roa_window),
        )
        .withColumn(
            "rank_by_revenue",
            F.dense_rank().over(revenue_window),
        )
    )