from dataclasses import dataclass
from datetime import datetime

from finsight.pipeline.run_history import RunHistoryStore


@dataclass(frozen=True)
class PipelineMonitoringSummary:
    """Summary of historical pipeline execution."""

    total_runs: int
    successful_runs: int
    failed_runs: int
    success_rate_pct: float
    total_records_extracted: int
    total_records_processed: int
    total_records_rejected: int
    latest_run: dict | None
    latest_failure: dict | None
    last_attempted_at: datetime | None
    last_successful_at: datetime | None
    last_failed_at: datetime | None
    last_run_id: str | None
    last_status: str | None


def _parse_timestamp(
    value: str | None,
) -> datetime | None:
    if not value:
        return None

    return datetime.fromisoformat(value)


def build_monitoring_summary(
    store: RunHistoryStore,
) -> PipelineMonitoringSummary:
    """Build a monitoring summary from pipeline run history."""

    records = store.read_all()

    total_runs = len(records)

    successful_runs = sum(
        1
        for record in records
        if record.get("status") == "success"
    )

    failed_runs = sum(
        1
        for record in records
        if record.get("status") == "failed"
    )

    success_rate_pct = (
        (successful_runs / total_runs) * 100
        if total_runs > 0
        else 0.0
    )

    total_records_extracted = sum(
        record.get("records_extracted", 0)
        for record in records
    )

    total_records_processed = sum(
        record.get("records_processed", 0)
        for record in records
    )

    total_records_rejected = sum(
        record.get("records_rejected", 0)
        for record in records
    )

    latest_run = (
        records[-1]
        if records
        else None
    )

    failed_records = [
        record
        for record in records
        if record.get("status") == "failed"
    ]

    latest_failure = (
        failed_records[-1]
        if failed_records
        else None
    )

    last_successful_at = None

    successful_records = [
        record
        for record in records
        if record.get("status") == "success"
    ]

    if successful_records:
        last_successful_at = _parse_timestamp(
            successful_records[-1].get(
                "completed_at"
            )
        )

    last_failed_at = None

    if failed_records:
        last_failed_at = _parse_timestamp(
            failed_records[-1].get(
                "completed_at"
            )
        )

    last_attempted_at = None

    if latest_run:
        last_attempted_at = _parse_timestamp(
            latest_run.get("started_at")
        )

    return PipelineMonitoringSummary(
        total_runs=total_runs,
        successful_runs=successful_runs,
        failed_runs=failed_runs,
        success_rate_pct=success_rate_pct,
        total_records_extracted=(
            total_records_extracted
        ),
        total_records_processed=(
            total_records_processed
        ),
        total_records_rejected=(
            total_records_rejected
        ),
        latest_run=latest_run,
        latest_failure=latest_failure,
        last_attempted_at=last_attempted_at,
        last_successful_at=last_successful_at,
        last_failed_at=last_failed_at,
        last_run_id=(
            latest_run.get("run_id")
            if latest_run
            else None
        ),
        last_status=(
            latest_run.get("status")
            if latest_run
            else None
        ),
    )
