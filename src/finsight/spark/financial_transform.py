from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F


def load_financial_data(
    spark,
    path: str,
) -> DataFrame:
    return (
        spark.read
        .option("header", True)
        .option("inferSchema", True)
        .option("dateFormat", "yyyy-MM-dd")
        .csv(path)
    )


def calculate_financial_metrics(
    dataframe: DataFrame,
) -> DataFrame:
    return (
        dataframe
        .withColumn(
            "net_profit_margin_pct",
            F.round(
                F.when(
                    F.col("revenue") != 0,
                    F.col("net_income") / F.col("revenue") * 100,
                ),
                2,
            ),
        )
        .withColumn(
            "operating_margin_pct",
            F.round(
                F.when(
                    F.col("revenue") != 0,
                    (
                        F.col("revenue")
                        - F.col("operating_expenses")
                    )
                    / F.col("revenue")
                    * 100,
                ),
                2,
            ),
        )
        .withColumn(
            "debt_to_assets_pct",
            F.round(
                F.when(
                    F.col("total_assets") != 0,
                    F.col("total_debt")
                    / F.col("total_assets")
                    * 100,
                ),
                2,
            ),
        )
        .withColumn(
            "debt_to_equity_pct",
            F.round(
                F.when(
                    (
                        F.col("total_assets")
                        - F.col("total_liabilities")
                    ) != 0,
                    F.col("total_debt")
                    / (
                        F.col("total_assets")
                        - F.col("total_liabilities")
                    )
                    * 100,
                ),
                2,
            ),
        )
        .withColumn(
            "return_on_assets_pct",
            F.round(
                F.when(
                    F.col("total_assets") != 0,
                    F.col("net_income")
                    / F.col("total_assets")
                    * 100,
                ),
                2,
            ),
        )
        .withColumn(
            "operating_cash_flow_margin_pct",
            F.round(
                F.when(
                    F.col("revenue") != 0,
                    F.col("operating_cash_flow")
                    / F.col("revenue")
                    * 100,
                ),
                2,
            ),
        )
    )


def calculate_growth_metrics(
    dataframe: DataFrame,
) -> DataFrame:
    window = (
        Window
        .partitionBy("company_id")
        .orderBy("period_end_date")
    )

    return (
        dataframe
        .withColumn(
            "previous_revenue",
            F.lag("revenue", 1).over(window),
        )
        .withColumn(
            "previous_year_revenue",
            F.lag("revenue", 4).over(window),
        )
        .withColumn(
            "previous_net_income",
            F.lag("net_income", 1).over(window),
        )
        .withColumn(
            "previous_year_net_income",
            F.lag("net_income", 4).over(window),
        )
        .withColumn(
            "revenue_growth_qoq_pct",
            F.round(
                F.when(
                    F.col("previous_revenue") != 0,
                    (
                        F.col("revenue")
                        / F.col("previous_revenue")
                        - 1
                    )
                    * 100,
                ),
                2,
            ),
        )
        .withColumn(
            "revenue_growth_yoy_pct",
            F.round(
                F.when(
                    F.col("previous_year_revenue") != 0,
                    (
                        F.col("revenue")
                        / F.col("previous_year_revenue")
                        - 1
                    )
                    * 100,
                ),
                2,
            ),
        )
        .withColumn(
            "net_income_growth_qoq_pct",
            F.round(
                F.when(
                    F.col("previous_net_income") != 0,
                    (
                        F.col("net_income")
                        / F.col("previous_net_income")
                        - 1
                    )
                    * 100,
                ),
                2,
            ),
        )
        .withColumn(
            "net_income_growth_yoy_pct",
            F.round(
                F.when(
                    F.col("previous_year_net_income") != 0,
                    (
                        F.col("net_income")
                        / F.col("previous_year_net_income")
                        - 1
                    )
                    * 100,
                ),
                2,
            ),
        )
        .drop(
            "previous_revenue",
            "previous_year_revenue",
            "previous_net_income",
            "previous_year_net_income",
        )
    )
def load_reference_data(
    spark,
    companies_path: str,
    industries_path: str,
):
    companies = (
        spark.read
        .option("header", True)
        .option("inferSchema", True)
        .csv(companies_path)
    )

    industries = (
        spark.read
        .option("header", True)
        .option("inferSchema", True)
        .csv(industries_path)
    )

    return companies, industries


def enrich_financial_data(
    financials,
    companies,
    industries,
):
    return (
        financials
        .join(
            companies.select(
                "company_id",
                "company_name",
                "ticker",
                "industry_id",
            ),
            on="company_id",
            how="left",
        )
        .join(
            industries.select(
                "industry_id",
                "industry_name",
            ),
            on="industry_id",
            how="left",
        )
    )
