from dataclasses import dataclass
from pathlib import Path

from finsight.ingestion.csv_reader import read_csv
from finsight.quality.output import (
    write_processed_records,
    write_rejected_records,
)
from finsight.quality.report import (
    DataQualityReport,
    calculate_quality_report,
)
from finsight.validation.financial_rules import (
    validate_financial_rules,
)
from finsight.validation.schema_validator import (
    SchemaValidationResult,
    validate_financial_schema,
)


@dataclass(frozen=True)
class PipelineResult:
    schema_validation: SchemaValidationResult
    quality_report: DataQualityReport
    processed_path: Path
    rejected_path: Path


def run_local_etl(
    source_path: Path,
    processed_path: Path,
    rejected_path: Path,
) -> PipelineResult:
    """Run the complete local financial ETL pipeline."""

    ingestion = read_csv(source_path)

    schema_validation = validate_financial_schema(
        ingestion.dataframe
    )

    if not schema_validation.is_valid:
        raise ValueError(
            "Financial dataset failed schema validation: "
            f"missing={schema_validation.missing_columns}, "
            f"unexpected={schema_validation.unexpected_columns}, "
            f"invalid_types={schema_validation.invalid_types}"
        )

    validation = validate_financial_rules(
        ingestion.dataframe
    )

    quality_report = calculate_quality_report(
        ingestion.dataframe,
        validation,
    )

    write_processed_records(
        ingestion.dataframe,
        validation,
        processed_path,
    )

    write_rejected_records(
        ingestion.dataframe,
        validation,
        rejected_path,
    )

    return PipelineResult(
        schema_validation=schema_validation,
        quality_report=quality_report,
        processed_path=processed_path,
        rejected_path=rejected_path,
    )