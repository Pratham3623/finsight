import pandas as pd

from finsight.validation.schema_validator import (
    validate_financial_schema,
)


EXPECTED_COLUMNS = [
    "financial_id",
    "company_id",
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
    "investing_cash_flow",
    "financing_cash_flow",
]


def valid_dataframe() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "financial_id": pd.Series([1], dtype="int64"),
            "company_id": pd.Series([1], dtype="int64"),
            "fiscal_year": pd.Series([2021], dtype="int64"),
            "fiscal_quarter": pd.Series([1], dtype="int64"),
            "period_end_date": pd.Series(["2021-03-31"], dtype="object"),
            "revenue": pd.Series([100.0], dtype="float64"),
            "operating_expenses": pd.Series([70.0], dtype="float64"),
            "net_income": pd.Series([20.0], dtype="float64"),
            "total_assets": pd.Series([200.0], dtype="float64"),
            "total_liabilities": pd.Series([100.0], dtype="float64"),
            "total_debt": pd.Series([50.0], dtype="float64"),
            "operating_cash_flow": pd.Series([25.0], dtype="float64"),
            "investing_cash_flow": pd.Series([-10.0], dtype="float64"),
            "financing_cash_flow": pd.Series([5.0], dtype="float64"),
        }
    )


def test_valid_financial_schema():
    dataframe = valid_dataframe()

    result = validate_financial_schema(dataframe)

    assert result.is_valid
    assert result.missing_columns == []
    assert result.unexpected_columns == []
    assert result.invalid_types == {}


def test_missing_column_is_detected():
    dataframe = valid_dataframe().drop(columns=["revenue"])

    result = validate_financial_schema(dataframe)

    assert not result.is_valid
    assert result.missing_columns == ["revenue"]


def test_unexpected_column_is_detected():
    dataframe = valid_dataframe()
    dataframe["unexpected_column"] = 123

    result = validate_financial_schema(dataframe)

    assert not result.is_valid
    assert result.unexpected_columns == ["unexpected_column"]


def test_invalid_type_is_detected():
    dataframe = valid_dataframe()
    dataframe["company_id"] = dataframe["company_id"].astype("string")

    result = validate_financial_schema(dataframe)

    assert not result.is_valid
    assert "company_id" in result.invalid_types


def test_expected_columns_are_defined():
    assert list(valid_dataframe().columns) == EXPECTED_COLUMNS