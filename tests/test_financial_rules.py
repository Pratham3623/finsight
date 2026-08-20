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
    result = validate_financial_rules(
        valid_dataframe()
    )

    assert result.valid_mask.all()
    assert result.rejection_reasons.eq("").all()


def test_debt_equal_to_liabilities_is_valid():
    dataframe = valid_dataframe()

    dataframe.loc[0, "total_debt"] = (
        dataframe.loc[0, "total_liabilities"]
    )

    result = validate_financial_rules(dataframe)

    assert result.valid_mask.iloc[0]


def test_liabilities_equal_to_assets_is_valid():
    dataframe = valid_dataframe()

    dataframe.loc[0, "total_liabilities"] = (
        dataframe.loc[0, "total_assets"]
    )

    result = validate_financial_rules(dataframe)

    assert result.valid_mask.iloc[0]


def test_net_income_equal_to_revenue_is_valid():
    dataframe = valid_dataframe()

    dataframe.loc[0, "net_income"] = (
        dataframe.loc[0, "revenue"]
    )

    result = validate_financial_rules(dataframe)

    assert result.valid_mask.iloc[0]


def test_debt_exceeding_liabilities_is_rejected():
    dataframe = valid_dataframe()
    dataframe.loc[0, "total_debt"] = 150.0

    result = validate_financial_rules(dataframe)

    assert not result.valid_mask.iloc[0]
    assert result.rejection_reasons.iloc[0] == (
        "debt_exceeds_liabilities"
    )


def test_liabilities_exceeding_assets_is_rejected():
    dataframe = valid_dataframe()
    dataframe.loc[0, "total_liabilities"] = 250.0

    result = validate_financial_rules(dataframe)

    assert not result.valid_mask.iloc[0]
    assert result.rejection_reasons.iloc[0] == (
        "liabilities_exceed_assets"
    )


def test_net_income_exceeding_revenue_is_rejected():
    dataframe = valid_dataframe()
    dataframe.loc[0, "net_income"] = 150.0

    result = validate_financial_rules(dataframe)

    assert not result.valid_mask.iloc[0]
    assert result.rejection_reasons.iloc[0] == (
        "net_income_exceeds_revenue"
    )


def test_invalid_financial_id_is_rejected():
    dataframe = valid_dataframe()

    dataframe.loc[0, "financial_id"] = 0

    result = validate_financial_rules(dataframe)

    assert not result.valid_mask.iloc[0]
    assert result.rejection_reasons.iloc[0] == (
        "invalid_financial_id"
    )


def test_negative_financial_id_is_rejected():
    dataframe = valid_dataframe()

    dataframe.loc[0, "financial_id"] = -1

    result = validate_financial_rules(dataframe)

    assert not result.valid_mask.iloc[0]
    assert result.rejection_reasons.iloc[0] == (
        "invalid_financial_id"
    )


def test_invalid_company_id_is_rejected():
    dataframe = valid_dataframe()

    dataframe.loc[0, "company_id"] = 0

    result = validate_financial_rules(dataframe)

    assert not result.valid_mask.iloc[0]
    assert result.rejection_reasons.iloc[0] == (
        "invalid_company_id"
    )


def test_invalid_fiscal_year_is_rejected():
    dataframe = valid_dataframe()

    dataframe.loc[0, "fiscal_year"] = 1999

    result = validate_financial_rules(dataframe)

    assert not result.valid_mask.iloc[0]
    assert result.rejection_reasons.iloc[0] == (
        "invalid_fiscal_year"
    )


def test_boundary_fiscal_year_is_valid():
    dataframe = valid_dataframe()

    dataframe.loc[0, "fiscal_year"] = 2000

    result = validate_financial_rules(dataframe)

    assert result.valid_mask.iloc[0]


def test_invalid_quarter_is_rejected():
    dataframe = valid_dataframe()

    dataframe.loc[0, "fiscal_quarter"] = 5

    result = validate_financial_rules(dataframe)

    assert not result.valid_mask.iloc[0]
    assert result.rejection_reasons.iloc[0] == (
        "invalid_fiscal_quarter"
    )


def test_zero_quarter_is_rejected():
    dataframe = valid_dataframe()

    dataframe.loc[0, "fiscal_quarter"] = 0

    result = validate_financial_rules(dataframe)

    assert not result.valid_mask.iloc[0]
    assert result.rejection_reasons.iloc[0] == (
        "invalid_fiscal_quarter"
    )


def test_all_valid_quarters_are_accepted():
    dataframe = valid_dataframe()

    dataframe.loc[0, "fiscal_quarter"] = 1
    dataframe.loc[1, "fiscal_quarter"] = 2
    dataframe.loc[2, "fiscal_quarter"] = 4

    result = validate_financial_rules(dataframe)

    assert result.valid_mask.all()


def test_invalid_period_end_date_is_rejected():
    dataframe = valid_dataframe()

    dataframe.loc[0, "period_end_date"] = (
        "not-a-date"
    )

    result = validate_financial_rules(dataframe)

    assert not result.valid_mask.iloc[0]
    assert result.rejection_reasons.iloc[0] == (
        "invalid_period_end_date"
    )


def test_missing_required_value_is_rejected():
    dataframe = valid_dataframe()

    dataframe.loc[0, "revenue"] = None

    result = validate_financial_rules(dataframe)

    assert not result.valid_mask.iloc[0]
    assert result.rejection_reasons.iloc[0] == (
        "missing_required_value"
    )


def test_negative_revenue_is_rejected():
    dataframe = valid_dataframe()

    dataframe.loc[0, "revenue"] = -1.0

    result = validate_financial_rules(dataframe)

    assert not result.valid_mask.iloc[0]
    assert result.rejection_reasons.iloc[0] == (
        "invalid_revenue"
    )


def test_negative_operating_expenses_are_rejected():
    dataframe = valid_dataframe()

    dataframe.loc[0, "operating_expenses"] = -1.0

    result = validate_financial_rules(dataframe)

    assert not result.valid_mask.iloc[0]
    assert result.rejection_reasons.iloc[0] == (
        "invalid_operating_expenses"
    )


def test_negative_assets_are_rejected():
    dataframe = valid_dataframe()

    dataframe.loc[0, "total_assets"] = -1.0

    result = validate_financial_rules(dataframe)

    assert not result.valid_mask.iloc[0]
    assert result.rejection_reasons.iloc[0] == (
        "invalid_total_assets"
    )


def test_negative_liabilities_are_rejected():
    dataframe = valid_dataframe()

    dataframe.loc[0, "total_liabilities"] = -1.0

    result = validate_financial_rules(dataframe)

    assert not result.valid_mask.iloc[0]
    assert result.rejection_reasons.iloc[0] == (
        "invalid_total_liabilities"
    )


def test_negative_debt_is_rejected():
    dataframe = valid_dataframe()

    dataframe.loc[0, "total_debt"] = -1.0

    result = validate_financial_rules(dataframe)

    assert not result.valid_mask.iloc[0]
    assert result.rejection_reasons.iloc[0] == (
        "invalid_total_debt"
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


def test_duplicate_business_grain_is_rejected():
    dataframe = valid_dataframe()

    dataframe.loc[1, "company_id"] = (
        dataframe.loc[0, "company_id"]
    )
    dataframe.loc[1, "fiscal_year"] = (
        dataframe.loc[0, "fiscal_year"]
    )
    dataframe.loc[1, "fiscal_quarter"] = (
        dataframe.loc[0, "fiscal_quarter"]
    )

    result = validate_financial_rules(dataframe)

    assert not result.valid_mask.iloc[0]
    assert not result.valid_mask.iloc[1]

    assert result.rejection_reasons.iloc[0] == (
        "duplicate_financial_grain"
    )

    assert result.rejection_reasons.iloc[1] == (
        "duplicate_financial_grain"
    )


def test_first_rejection_reason_wins():
    dataframe = valid_dataframe()

    dataframe.loc[0, "financial_id"] = 0
    dataframe.loc[0, "company_id"] = 0
    dataframe.loc[0, "revenue"] = -100.0

    result = validate_financial_rules(dataframe)

    assert result.rejection_reasons.iloc[0] == (
        "invalid_financial_id"
    )
