from dataclasses import dataclass

import pandas as pd

from finsight.ingestion.schemas import FINANCIAL_SCHEMA


@dataclass(frozen=True)
class SchemaValidationResult:
    is_valid: bool
    missing_columns: list[str]
    unexpected_columns: list[str]
    invalid_types: dict[str, str]


def validate_financial_schema(
    dataframe: pd.DataFrame,
) -> SchemaValidationResult:
    expected_columns = [column.name for column in FINANCIAL_SCHEMA]
    actual_columns = list(dataframe.columns)

    missing_columns = [
        column
        for column in expected_columns
        if column not in actual_columns
    ]

    unexpected_columns = [
        column
        for column in actual_columns
        if column not in expected_columns
    ]

    invalid_types: dict[str, str] = {}

    for column in FINANCIAL_SCHEMA:
        if column.name not in dataframe.columns:
            continue

        actual_dtype = str(dataframe[column.name].dtype)

        if actual_dtype != column.pandas_dtype:
            invalid_types[column.name] = (
                f"expected {column.pandas_dtype}, "
                f"got {actual_dtype}"
            )

    is_valid = not (
        missing_columns
        or unexpected_columns
        or invalid_types
    )

    return SchemaValidationResult(
        is_valid=is_valid,
        missing_columns=missing_columns,
        unexpected_columns=unexpected_columns,
        invalid_types=invalid_types,
    )