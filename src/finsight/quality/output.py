from pathlib import Path

import pandas as pd

from finsight.validation.financial_rules import RowValidationResult


def write_processed_records(
    dataframe: pd.DataFrame,
    validation: RowValidationResult,
    output_path: Path,
) -> None:
    """Write records that passed validation."""

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    processed = dataframe.loc[
        validation.valid_mask
    ].copy()

    processed.to_csv(
        output_path,
        index=False,
    )


def write_rejected_records(
    dataframe: pd.DataFrame,
    validation: RowValidationResult,
    output_path: Path,
) -> None:
    """Write rejected records with their rejection reason."""

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    rejected = dataframe.loc[
        ~validation.valid_mask
    ].copy()

    rejected["rejection_reason"] = (
        validation.rejection_reasons.loc[
            ~validation.valid_mask
        ]
    )

    rejected.to_csv(
        output_path,
        index=False,
    )