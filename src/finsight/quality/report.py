from dataclasses import dataclass

import pandas as pd

from finsight.validation.financial_rules import RowValidationResult


@dataclass(frozen=True)
class DataQualityReport:
    records_extracted: int
    records_valid: int
    records_rejected: int
    completeness_score: float
    validity_score: float
    uniqueness_score: float
    consistency_score: float
    overall_quality_score: float
    rejection_counts: dict[str, int]


def calculate_quality_report(
    dataframe: pd.DataFrame,
    validation: RowValidationResult,
) -> DataQualityReport:
    """Calculate data-quality metrics for a financial dataset."""

    records_extracted = len(dataframe)

    if records_extracted == 0:
        return DataQualityReport(
            records_extracted=0,
            records_valid=0,
            records_rejected=0,
            completeness_score=100.0,
            validity_score=100.0,
            uniqueness_score=100.0,
            consistency_score=100.0,
            overall_quality_score=100.0,
            rejection_counts={},
        )

    records_valid = int(validation.valid_mask.sum())
    records_rejected = records_extracted - records_valid

    # Completeness:
    # Percentage of expected financial fields that are populated.
    total_cells = dataframe.size
    populated_cells = int(dataframe.notna().sum().sum())

    completeness_score = (
        populated_cells / total_cells * 100
        if total_cells
        else 100.0
    )

    # Validity:
    # Percentage of records that passed business-rule validation.
    validity_score = (
        records_valid / records_extracted * 100
    )

    # Uniqueness:
    # Percentage of unique financial IDs.
    unique_ids = dataframe["financial_id"].nunique()

    uniqueness_score = (
        unique_ids / records_extracted * 100
    )

    # Consistency:
    # Percentage of records satisfying core financial relationships.
    consistency_mask = (
        (dataframe["total_debt"] <= dataframe["total_liabilities"])
        & (
            dataframe["total_liabilities"]
            <= dataframe["total_assets"]
        )
    )

    consistency_score = (
        consistency_mask.sum() / records_extracted * 100
    )

    overall_quality_score = (
        completeness_score
        + validity_score
        + uniqueness_score
        + consistency_score
    ) / 4

    rejection_counts = (
        validation.rejection_reasons[
            validation.rejection_reasons != ""
        ]
        .value_counts()
        .astype(int)
        .to_dict()
    )

    return DataQualityReport(
        records_extracted=records_extracted,
        records_valid=records_valid,
        records_rejected=records_rejected,
        completeness_score=round(completeness_score, 2),
        validity_score=round(validity_score, 2),
        uniqueness_score=round(uniqueness_score, 2),
        consistency_score=round(consistency_score, 2),
        overall_quality_score=round(
            overall_quality_score,
            2,
        ),
        rejection_counts=rejection_counts,
    )