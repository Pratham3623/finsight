from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class RowValidationResult:
    valid_mask: pd.Series
    rejection_reasons: pd.Series


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

    add_reason(
        dataframe["period_end_date"].isna()
        | pd.to_datetime(
            dataframe["period_end_date"],
            errors="coerce",
        ).isna(),
        "invalid_period_end_date",
    )

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

    duplicate_financial_id = dataframe["financial_id"].duplicated(
        keep=False
    )

    add_reason(
        duplicate_financial_id,
        "duplicate_financial_id",
    )

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