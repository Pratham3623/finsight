from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class RowValidationResult:
    valid_mask: pd.Series
    rejection_reasons: pd.Series


REQUIRED_COLUMNS = [
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


def validate_financial_rules(
    dataframe: pd.DataFrame,
) -> RowValidationResult:
    """Validate financial records against business rules."""

    reasons = pd.Series(
        "",
        index=dataframe.index,
        dtype="object",
    )

    def add_reason(mask: pd.Series, reason: str) -> None:
        nonlocal reasons

        applicable = mask & reasons.eq("")
        reasons.loc[applicable] = reason

    # Required fields
    missing_required = dataframe[REQUIRED_COLUMNS].isna().any(axis=1)

    add_reason(
        missing_required,
        "missing_required_value",
    )

    # IDs
    add_reason(
        dataframe["financial_id"].isna()
        | (dataframe["financial_id"] <= 0),
        "invalid_financial_id",
    )

    add_reason(
        dataframe["company_id"].isna()
        | (dataframe["company_id"] <= 0),
        "invalid_company_id",
    )

    # Time dimensions
    add_reason(
        dataframe["fiscal_year"].isna()
        | (dataframe["fiscal_year"] < 2000),
        "invalid_fiscal_year",
    )

    add_reason(
        dataframe["fiscal_quarter"].isna()
        | ~dataframe["fiscal_quarter"].isin([1, 2, 3, 4]),
        "invalid_fiscal_quarter",
    )

    parsed_dates = pd.to_datetime(
        dataframe["period_end_date"],
        errors="coerce",
    )

    add_reason(
        parsed_dates.isna(),
        "invalid_period_end_date",
    )

    # Financial values
    non_negative_columns = [
        "revenue",
        "operating_expenses",
        "total_assets",
        "total_liabilities",
        "total_debt",
    ]

    for column in non_negative_columns:
        add_reason(
            dataframe[column].isna()
            | (dataframe[column] < 0),
            f"invalid_{column}",
        )

    # Financial relationships
    add_reason(
        dataframe["total_debt"] > dataframe["total_liabilities"],
        "debt_exceeds_liabilities",
    )

    add_reason(
        dataframe["total_liabilities"] > dataframe["total_assets"],
        "liabilities_exceed_assets",
    )

    add_reason(
        dataframe["net_income"] > dataframe["revenue"],
        "net_income_exceeds_revenue",
    )

    # Duplicate financial IDs
    duplicate_financial_id = dataframe["financial_id"].duplicated(
        keep=False
    )

    add_reason(
        duplicate_financial_id,
        "duplicate_financial_id",
    )

    # Duplicate business grain
    duplicate_grain = dataframe.duplicated(
        subset=[
            "company_id",
            "fiscal_year",
            "fiscal_quarter",
        ],
        keep=False,
    )

    add_reason(
        duplicate_grain,
        "duplicate_financial_grain",
    )

    valid_mask = reasons.eq("")

    return RowValidationResult(
        valid_mask=valid_mask,
        rejection_reasons=reasons,
    )