from datetime import datetime, timezone
from pathlib import Path

from finsight.pipeline.monitoring import (
    build_monitoring_summary,
)
from finsight.pipeline.run_history import (
    RunHistoryStore,
)
from finsight.pipeline.run_tracking import (
    PipelineRun,
    PipelineRunStatus,
)


def create_run(
    run_id: str,
    status: PipelineRunStatus,
    extracted: int,
    processed: int,
    rejected: int,
) -> PipelineRun:
    now = datetime.now(timezone.utc)

    return PipelineRun(
        run_id=run_id,
        pipeline_name="local_financial_etl",
        status=status,
        started_at=now,
        completed_at=now,
        records_extracted=extracted,
        records_processed=processed,
        records_rejected=rejected,
        error_message=(
            "test failure"
            if status == PipelineRunStatus.FAILED
            else None
        ),
    )


def test_empty_history_returns_zero_summary(
    tmp_path: Path,
):
    store = RunHistoryStore(
        tmp_path / "history.jsonl"
    )

    summary = build_monitoring_summary(store)

    assert summary.total_runs == 0
    assert summary.successful_runs == 0
    assert summary.failed_runs == 0
    assert summary.success_rate_pct == 0.0
    assert summary.total_records_extracted == 0
    assert summary.total_records_processed == 0
    assert summary.total_records_rejected == 0
    assert summary.latest_run is None
    assert summary.latest_failure is None
    assert summary.last_attempted_at is None
    assert summary.last_successful_at is None
    assert summary.last_failed_at is None
    assert summary.last_run_id is None
    assert summary.last_status is None


def test_summary_counts_successful_runs(
    tmp_path: Path,
):
    store = RunHistoryStore(
        tmp_path / "history.jsonl"
    )

    store.append(
        create_run(
            "run-1",
            PipelineRunStatus.SUCCESS,
            100,
            95,
            5,
        )
    )

    store.append(
        create_run(
            "run-2",
            PipelineRunStatus.SUCCESS,
            200,
            190,
            10,
        )
    )

    summary = build_monitoring_summary(store)

    assert summary.total_runs == 2
    assert summary.successful_runs == 2
    assert summary.failed_runs == 0
    assert summary.success_rate_pct == 100.0


def test_summary_counts_failed_runs(
    tmp_path: Path,
):
    store = RunHistoryStore(
        tmp_path / "history.jsonl"
    )

    store.append(
        create_run(
            "run-1",
            PipelineRunStatus.SUCCESS,
            100,
            95,
            5,
        )
    )

    store.append(
        create_run(
            "run-2",
            PipelineRunStatus.FAILED,
            0,
            0,
            0,
        )
    )

    summary = build_monitoring_summary(store)

    assert summary.total_runs == 2
    assert summary.successful_runs == 1
    assert summary.failed_runs == 1
    assert summary.success_rate_pct == 50.0


def test_summary_calculates_record_totals(
    tmp_path: Path,
):
    store = RunHistoryStore(
        tmp_path / "history.jsonl"
    )

    store.append(
        create_run(
            "run-1",
            PipelineRunStatus.SUCCESS,
            100,
            90,
            10,
        )
    )

    store.append(
        create_run(
            "run-2",
            PipelineRunStatus.SUCCESS,
            200,
            180,
            20,
        )
    )

    summary = build_monitoring_summary(store)

    assert summary.total_records_extracted == 300
    assert summary.total_records_processed == 270
    assert summary.total_records_rejected == 30


def test_summary_returns_latest_run(
    tmp_path: Path,
):
    store = RunHistoryStore(
        tmp_path / "history.jsonl"
    )

    store.append(
        create_run(
            "run-1",
            PipelineRunStatus.SUCCESS,
            100,
            95,
            5,
        )
    )

    store.append(
        create_run(
            "run-2",
            PipelineRunStatus.SUCCESS,
            200,
            190,
            10,
        )
    )

    summary = build_monitoring_summary(store)

    assert summary.latest_run is not None
    assert summary.latest_run["run_id"] == "run-2"


def test_summary_returns_latest_failure(
    tmp_path: Path,
):
    store = RunHistoryStore(
        tmp_path / "history.jsonl"
    )

    store.append(
        create_run(
            "success-1",
            PipelineRunStatus.SUCCESS,
            100,
            95,
            5,
        )
    )

    store.append(
        create_run(
            "failed-1",
            PipelineRunStatus.FAILED,
            0,
            0,
            0,
        )
    )

    store.append(
        create_run(
            "failed-2",
            PipelineRunStatus.FAILED,
            0,
            0,
            0,
        )
    )

    summary = build_monitoring_summary(store)

    assert summary.latest_failure is not None
    assert (
        summary.latest_failure["run_id"]
        == "failed-2"
    )


def test_refresh_tracking_after_success(
    tmp_path: Path,
):
    store = RunHistoryStore(
        tmp_path / "history.jsonl"
    )

    run = create_run(
        "success-1",
        PipelineRunStatus.SUCCESS,
        100,
        95,
        5,
    )

    store.append(run)

    summary = build_monitoring_summary(store)

    assert summary.last_run_id == "success-1"
    assert summary.last_status == "success"
    assert summary.last_attempted_at is not None
    assert summary.last_successful_at is not None
    assert summary.last_failed_at is None


def test_refresh_tracking_after_failure(
    tmp_path: Path,
):
    store = RunHistoryStore(
        tmp_path / "history.jsonl"
    )

    success = create_run(
        "success-1",
        PipelineRunStatus.SUCCESS,
        100,
        95,
        5,
    )

    failure = create_run(
        "failed-1",
        PipelineRunStatus.FAILED,
        0,
        0,
        0,
    )

    store.append(success)
    store.append(failure)

    summary = build_monitoring_summary(store)

    assert summary.last_run_id == "failed-1"
    assert summary.last_status == "failed"
    assert summary.last_attempted_at is not None
    assert summary.last_successful_at is not None
    assert summary.last_failed_at is not None
