from pathlib import Path

import pytest

from finsight.spark.output_validation import (
    validate_company_output,
    validate_financial_metrics_output,
    validate_industry_output,
)


def test_financial_output_validation(
    spark,
):
    data = [
        (
            1,
            1,
            2021,
            1000.0,
            10.0,
            5.0,
            10.0,
        ),
        (
            2,
            1,
            2021,
            1100.0,
            11.0,
            10.0,
            10.0,
        ),
    ]

    columns = [
        "financial_id",
        "company_id",
        "fiscal_year",
        "revenue",
        "net_profit_margin_pct",
        "revenue_growth_qoq_pct",
        "revenue_growth_yoy_pct",
    ]

    dataframe = spark.createDataFrame(
        data,
        columns,
    )

    result = validate_financial_metrics_output(
        dataframe,
        expected_records=2,
    )

    assert result["records"] == 2
    assert result["duplicate_financial_ids"] == 0


def test_industry_output_validation(
    spark,
):
    dataframe = spark.createDataFrame(
        [
            ("Technology", 10),
            ("Energy", 8),
        ],
        [
            "industry_name",
            "company_count",
        ],
    )

    result = validate_industry_output(
        dataframe,
        expected_industries=2,
    )

    assert result["records"] == 2


def test_company_output_validation(
    spark,
):
    dataframe = spark.createDataFrame(
        [
            (1, "Company A"),
            (2, "Company B"),
        ],
        [
            "company_id",
            "company_name",
        ],
    )

    result = validate_company_output(
        dataframe,
        expected_companies=2,
    )

    assert result["records"] == 2
    assert result["duplicate_companies"] == 0


def test_financial_output_rejects_wrong_count(
    spark,
):
    dataframe = spark.createDataFrame(
        [
            (1, 1, 2021),
        ],
        [
            "financial_id",
            "company_id",
            "fiscal_year",
        ],
    )

    with pytest.raises(ValueError):
        validate_financial_metrics_output(
            dataframe,
            expected_records=2,
        )