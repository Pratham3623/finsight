from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class RowValidationResult:
    """Result of financial business-rule validation."""

    valid_mask: pd.Series
    rejection_reasons: pd.Series


# Backwards-compatible descriptive alias.
FinancialValidationResult = RowValidationResult


def validate_financial_rules(
    dataframe: pd.DataFrame,
) -> RowValidationResult:
    """Validate financial records against business rules."""

    valid_mask = pd.Series(
        True,
        index=dataframe.index,
    )

    rejection_reasons = pd.Series(
        "",
        index=dataframe.index,
        dtype="object",
    )

    def reject(
        mask: pd.Series,
        reason: str,
    ) -> None:
        nonlocal valid_mask

        new_rejections = (
            mask
            & valid_mask
        )

        rejection_reasons.loc[
            new_rejections
        ] = reason

        valid_mask = (
            valid_mask
            & ~mask
        )

    reject(
        dataframe["financial_id"].isna()
        | (dataframe["financial_id"] <= 0),
        "invalid_financial_id",
    )

    reject(
        dataframe["company_id"].isna()
        | (dataframe["company_id"] <= 0),
        "invalid_company_id",
    )

    reject(
        dataframe["fiscal_year"].isna()
        | (dataframe["fiscal_year"] < 2000),
        "invalid_fiscal_year",
    )

    reject(
        dataframe["fiscal_quarter"].isna()
        | ~dataframe["fiscal_quarter"].isin(
            [1, 2, 3, 4]
        ),
        "invalid_fiscal_quarter",
    )

    parsed_dates = pd.to_datetime(
        dataframe["period_end_date"],
        errors="coerce",
        format="mixed",
    )

    reject(
        parsed_dates.isna(),
        "invalid_period_end_date",
    )

    required_columns = [
        "revenue",
        "operating_expenses",
        "net_income",
        "total_assets",
        "total_liabilities",
        "total_debt",
    ]

    missing_required_values = dataframe[
        required_columns
    ].isna().any(axis=1)

    reject(
        missing_required_values,
        "missing_required_value",
    )

    reject(
        dataframe["revenue"].notna()
        & (dataframe["revenue"] < 0),
        "invalid_revenue",
    )

    reject(
        dataframe["operating_expenses"].notna()
        & (
            dataframe["operating_expenses"] < 0
        ),
        "invalid_operating_expenses",
    )

    reject(
        dataframe["total_assets"].notna()
        & (dataframe["total_assets"] < 0),
        "invalid_total_assets",
    )

    reject(
        dataframe["total_liabilities"].notna()
        & (
            dataframe["total_liabilities"] < 0
        ),
        "invalid_total_liabilities",
    )

    reject(
        dataframe["total_debt"].notna()
        & (dataframe["total_debt"] < 0),
        "invalid_total_debt",
    )

    reject(
        dataframe["total_debt"].notna()
        & dataframe["total_liabilities"].notna()
        & (
            dataframe["total_debt"]
            > dataframe["total_liabilities"]
        ),
        "debt_exceeds_liabilities",
    )

    reject(
        dataframe["total_liabilities"].notna()
        & dataframe["total_assets"].notna()
        & (
            dataframe["total_liabilities"]
            > dataframe["total_assets"]
        ),
        "liabilities_exceed_assets",
    )

    reject(
        dataframe["net_income"].notna()
        & dataframe["revenue"].notna()
        & (
            dataframe["net_income"]
            > dataframe["revenue"]
        ),
        "net_income_exceeds_revenue",
    )

    duplicate_financial_id = (
        dataframe["financial_id"]
        .notna()
        & dataframe["financial_id"].duplicated(
            keep=False
        )
    )

    reject(
        duplicate_financial_id,
        "duplicate_financial_id",
    )

    duplicate_financial_grain = (
        dataframe[
            [
                "company_id",
                "fiscal_year",
                "fiscal_quarter",
            ]
        ]
        .duplicated(keep=False)
    )

    reject(
        duplicate_financial_grain,
        "duplicate_financial_grain",
    )

    return RowValidationResult(
        valid_mask=valid_mask,
        rejection_reasons=rejection_reasons,
    )
