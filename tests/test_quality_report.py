import pandas as pd

from finsight.quality.report import calculate_quality_report
from finsight.validation.financial_rules import (
    validate_financial_rules,
)


def valid_dataframe() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "financial_id": [1, 2, 3],
            "company_id": [1, 2, 3],
            "fiscal_year": [2021, 2021, 2021],
            "fiscal_quarter": [1, 2, 3],
            "period_end_date": [
                "2021-03-31",
                "2021-06-30",
                "2021-09-30",
            ],
            "revenue": [100.0, 200.0, 300.0],
            "operating_expenses": [70.0, 140.0, 210.0],
            "net_income": [20.0, 30.0, 40.0],
            "total_assets": [200.0, 300.0, 400.0],
            "total_liabilities": [100.0, 150.0, 200.0],
            "total_debt": [50.0, 75.0, 100.0],
            "operating_cash_flow": [20.0, 30.0, 40.0],
            "investing_cash_flow": [-10.0, -20.0, -30.0],
            "financing_cash_flow": [5.0, 10.0, 15.0],
        }
    )


def test_clean_dataset_gets_perfect_quality_score():
    dataframe = valid_dataframe()

    validation = validate_financial_rules(dataframe)
    report = calculate_quality_report(
        dataframe,
        validation,
    )

    assert report.records_extracted == 3
    assert report.records_valid == 3
    assert report.records_rejected == 0

    assert report.completeness_score == 100.0
    assert report.validity_score == 100.0
    assert report.uniqueness_score == 100.0
    assert report.consistency_score == 100.0
    assert report.overall_quality_score == 100.0


def test_invalid_record_reduces_quality_score():
    dataframe = valid_dataframe()

    dataframe.loc[0, "total_debt"] = 250.0

    validation = validate_financial_rules(dataframe)
    report = calculate_quality_report(
        dataframe,
        validation,
    )

    assert report.records_extracted == 3
    assert report.records_valid == 2
    assert report.records_rejected == 1

    assert report.validity_score < 100.0
    assert report.consistency_score < 100.0
    assert report.overall_quality_score < 100.0

    assert report.rejection_counts == {
        "debt_exceeds_liabilities": 1,
    }


def test_duplicate_id_reduces_uniqueness():
    dataframe = valid_dataframe()

    dataframe.loc[2, "financial_id"] = 1

    validation = validate_financial_rules(dataframe)
    report = calculate_quality_report(
        dataframe,
        validation,
    )

    assert report.uniqueness_score < 100.0


def test_missing_value_reduces_completeness():
    dataframe = valid_dataframe()

    dataframe.loc[0, "revenue"] = None

    validation = validate_financial_rules(dataframe)
    report = calculate_quality_report(
        dataframe,
        validation,
    )

    assert report.completeness_score < 100.0