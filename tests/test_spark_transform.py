import pytest
from pyspark.sql import SparkSession

from finsight.spark.analytics import (
    build_company_analytics,
    build_industry_analytics,
)
from finsight.spark.financial_transform import (
    calculate_financial_metrics,
    calculate_growth_metrics,
)
from finsight.spark.quality import validate_financial_data


@pytest.fixture(scope="module")
def spark():
    session = (
        SparkSession.builder
        .appName("FinSightTests")
        .master("local[2]")
        .getOrCreate()
    )

    yield session

    session.stop()


@pytest.fixture
def financial_dataframe(spark):
    data = [
        (
            1, 1, "Company A", "FS0001", "Technology",
            2021, 1, "2021-03-31",
            1000.0, 600.0, 100.0,
            2000.0, 1000.0, 500.0, 120.0,
        ),
        (
            2, 1, "Company A", "FS0001", "Technology",
            2021, 2, "2021-06-30",
            1100.0, 620.0, 120.0,
            2100.0, 1050.0, 520.0, 130.0,
        ),
        (
            3, 1, "Company A", "FS0001", "Technology",
            2022, 1, "2022-03-31",
            1250.0, 680.0, 140.0,
            2300.0, 1100.0, 550.0, 150.0,
        ),
        (
            4, 2, "Company B", "FS0002", "Energy",
            2021, 1, "2021-03-31",
            2000.0, 1300.0, 200.0,
            4000.0, 2200.0, 1000.0, 250.0,
        ),
    ]

    columns = [
        "financial_id",
        "company_id",
        "company_name",
        "ticker",
        "industry_name",
        "fiscal_year",
        "fiscal_quarter",
        "period_end_date",
        "revenue",
        "operating_expenses",
        "net_income",
        "total_assets",
        "total_liabilities",
        "total_debt",
        "operating_cash_flow",
    ]

    return (
        spark.createDataFrame(data, columns)
        .withColumn(
            "period_end_date",
            __import__(
                "pyspark.sql.functions",
                fromlist=["to_date"],
            ).to_date("period_end_date"),
        )
    )


def test_financial_metrics(
    financial_dataframe,
):
    result = calculate_financial_metrics(
        financial_dataframe
    )

    row = (
        result
        .filter("financial_id = 1")
        .first()
    )

    assert row.net_profit_margin_pct == 10.0
    assert row.debt_to_assets_pct == 25.0
    assert row.return_on_assets_pct == 5.0


def test_growth_metrics(
    financial_dataframe,
):
    metrics = calculate_financial_metrics(
        financial_dataframe
    )

    result = calculate_growth_metrics(metrics)

    row = (
        result
        .filter("financial_id = 2")
        .first()
    )

    assert row.revenue_growth_qoq_pct == 10.0


def test_industry_analytics(
    financial_dataframe,
):
    metrics = calculate_financial_metrics(
        financial_dataframe
    )

    metrics = calculate_growth_metrics(metrics)

    result = build_industry_analytics(metrics)

    assert result.count() == 2

    technology = (
        result
        .filter("industry_name = 'Technology'")
        .first()
    )

    assert technology.company_count == 1


def test_company_analytics(
    financial_dataframe,
):
    metrics = calculate_financial_metrics(
        financial_dataframe
    )

    metrics = calculate_growth_metrics(metrics)

    result = build_company_analytics(metrics)

    assert result.count() == 2

    company = (
        result
        .filter("company_id = 1")
        .first()
    )

    assert company.rank_by_roa >= 1


def test_quality_validation(
    financial_dataframe,
):
    result = validate_financial_data(
        financial_dataframe
    )

    assert result["records"] == 4
    assert result["duplicate_financial_ids"] == 0
    assert result["invalid_revenue"] == 0


def test_quality_rejects_invalid_data(
    spark,
):
    data = [
        (
            1, 1, "Company A", "FS0001", "Technology",
            2021, 1, "2021-03-31",
            -100.0, 50.0, 10.0,
            1000.0, 600.0, 300.0, 20.0,
        )
    ]

    columns = [
        "financial_id",
        "company_id",
        "company_name",
        "ticker",
        "industry_name",
        "fiscal_year",
        "fiscal_quarter",
        "period_end_date",
        "revenue",
        "operating_expenses",
        "net_income",
        "total_assets",
        "total_liabilities",
        "total_debt",
        "operating_cash_flow",
    ]

    dataframe = spark.createDataFrame(
        data,
        columns,
    )

    with pytest.raises(ValueError):
        validate_financial_data(dataframe)