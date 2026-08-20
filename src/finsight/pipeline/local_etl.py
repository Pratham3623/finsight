from dataclasses import dataclass
from pathlib import Path

from finsight.ingestion.csv_reader import read_csv
from finsight.pipeline.metrics import PipelineMetrics
from finsight.pipeline.run_error import PipelineRunError
from finsight.pipeline.run_tracker import PipelineRunTracker
from finsight.pipeline.run_tracking import PipelineRun
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
    run: PipelineRun
    metrics: PipelineMetrics


def run_local_etl(
    source_path: Path,
    processed_path: Path,
    rejected_path: Path,
) -> PipelineResult:
    """Run the complete local financial ETL pipeline."""

    tracker = PipelineRunTracker(
        "local_financial_etl"
    )
    tracker.start()

    try:
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

        run = tracker.succeed(
            records_extracted=quality_report.records_extracted,
            records_processed=quality_report.records_valid,
            records_rejected=quality_report.records_rejected,
        )

        metrics = PipelineMetrics(
            duration_seconds=(
                run.completed_at - run.started_at
            ).total_seconds()
            if run.completed_at is not None
            else 0.0,
            attempts=1,
            records_extracted=quality_report.records_extracted,
            records_processed=quality_report.records_valid,
            records_rejected=quality_report.records_rejected,
        )

        return PipelineResult(
            schema_validation=schema_validation,
            quality_report=quality_report,
            processed_path=processed_path,
            rejected_path=rejected_path,
            run=run,
            metrics=metrics,
        )

    except Exception as exc:
        failed_run = tracker.fail(
            str(exc),
        )

        raise PipelineRunError(
            str(exc),
            failed_run,
        ) from exc
