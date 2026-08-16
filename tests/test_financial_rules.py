import pandas as pd

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


def test_valid_records_pass():
    dataframe = valid_dataframe()

    result = validate_financial_rules(dataframe)

    assert result.valid_mask.all()
    assert result.rejection_reasons.eq("").all()


def test_debt_exceeding_liabilities_is_rejected():
    dataframe = valid_dataframe()

    dataframe.loc[0, "total_debt"] = 150.0

    result = validate_financial_rules(dataframe)

    assert not result.valid_mask.iloc[0]
    assert result.rejection_reasons.iloc[0] == (
        "debt_exceeds_liabilities"
    )


def test_invalid_quarter_is_rejected():
    dataframe = valid_dataframe()

    dataframe.loc[0, "fiscal_quarter"] = 5

    result = validate_financial_rules(dataframe)

    assert not result.valid_mask.iloc[0]
    assert result.rejection_reasons.iloc[0] == (
        "invalid_fiscal_quarter"
    )


def test_duplicate_financial_id_is_rejected():
    dataframe = valid_dataframe()

    dataframe.loc[1, "financial_id"] = 1

    result = validate_financial_rules(dataframe)

    assert not result.valid_mask.iloc[0]
    assert not result.valid_mask.iloc[1]

    assert result.rejection_reasons.iloc[0] == (
        "duplicate_financial_id"
    )

    assert result.rejection_reasons.iloc[1] == (
        "duplicate_financial_id"
    )


def test_liabilities_exceeding_assets_is_rejected():
    dataframe = valid_dataframe()

    dataframe.loc[0, "total_liabilities"] = 250.0

    result = validate_financial_rules(dataframe)

    assert not result.valid_mask.iloc[0]
    assert result.rejection_reasons.iloc[0] == (
        "liabilities_exceed_assets"
    )