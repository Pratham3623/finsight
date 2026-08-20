from pathlib import Path

import pandas as pd
import pytest

from finsight.pipeline.monitoring import (
    build_monitoring_summary,
)
from finsight.pipeline.orchestrator import (
    PipelineConfig,
    PipelineOrchestrator,
)
from finsight.pipeline.run_history import (
    RunHistoryStore,
)


def create_source(path: Path) -> None:
    dataframe = pd.DataFrame(
        {
            "financial_id": [1, 2, 3, 4],
            "company_id": [1, 2, 3, 4],
            "fiscal_year": [2021, 2021, 2021, 2021],
            "fiscal_quarter": [1, 2, 3, 4],
            "period_end_date": [
                "2021-03-31",
                "2021-06-30",
                "2021-09-30",
                "2021-12-31",
            ],
            "revenue": [
                100.0,
                200.0,
                300.0,
                400.0,
            ],
            "operating_expenses": [
                70.0,
                140.0,
                210.0,
                280.0,
            ],
            "net_income": [
                20.0,
                30.0,
                40.0,
                50.0,
            ],
            "total_assets": [
                200.0,
                300.0,
                400.0,
                500.0,
            ],
            "total_liabilities": [
                100.0,
                150.0,
                200.0,
                250.0,
            ],
            "total_debt": [
                50.0,
                75.0,
                100.0,
                125.0,
            ],
            "operating_cash_flow": [
                20.0,
                30.0,
                40.0,
                50.0,
            ],
            "investing_cash_flow": [
                -10.0,
                -20.0,
                -30.0,
                -40.0,
            ],
            "financing_cash_flow": [
                5.0,
                10.0,
                15.0,
                20.0,
            ],
        }
    )

    dataframe.to_csv(
        path,
        index=False,
    )


def create_invalid_source(path: Path) -> None:
    dataframe = pd.DataFrame(
        {
            "financial_id": [1, 2, 3],
            "company_id": [1, 2, 3],
            "fiscal_year": [2021, 2021, 2021],
            "fiscal_quarter": [1, 2, 3],
            "period_end_date": [
                "2021-03-31",
                "2021-06-30",
                "2021-09-30",
            ],
            "revenue": [
                100.0,
                -200.0,
                300.0,
            ],
            "operating_expenses": [
                70.0,
                140.0,
                210.0,
            ],
            "net_income": [
                20.0,
                30.0,
                40.0,
            ],
            "total_assets": [
                200.0,
                300.0,
                400.0,
            ],
            "total_liabilities": [
                100.0,
                150.0,
                200.0,
            ],
            "total_debt": [
                50.0,
                75.0,
                100.0,
            ],
            "operating_cash_flow": [
                20.0,
                30.0,
                40.0,
            ],
            "investing_cash_flow": [
                -10.0,
                -20.0,
                -30.0,
            ],
            "financing_cash_flow": [
                5.0,
                10.0,
                15.0,
            ],
        }
    )

    dataframe.to_csv(
        path,
        index=False,
    )


def create_config(
    tmp_path: Path,
    source: Path,
) -> PipelineConfig:
    return PipelineConfig(
        source_path=source,
        processed_path=(
            tmp_path / "processed.csv"
        ),
        rejected_path=(
            tmp_path / "rejected.csv"
        ),
        run_history_path=(
            tmp_path / "run_history.jsonl"
        ),
    )


def test_full_pipeline_success_creates_outputs_and_history(
    tmp_path: Path,
):
    source = tmp_path / "input.csv"

    create_source(source)

    config = create_config(
        tmp_path,
        source,
    )

    result = PipelineOrchestrator(
        config
    ).run()

    assert result.run.status.value == "success"

    assert (
        result.metrics.records_extracted
        == 4
    )

    assert (
        result.metrics.records_processed
        == 4
    )

    assert (
        result.metrics.records_rejected
        == 0
    )

    assert (
        result.metrics.attempts
        == 1
    )

    assert (
        result.processed_path.exists()
    )

    assert (
        result.rejected_path.exists()
    )

    history = RunHistoryStore(
        config.run_history_path
    )

    records = history.read_all()

    assert len(records) == 1

    assert (
        records[0]["run_id"]
        == result.run.run_id
    )

    assert (
        records[0]["status"]
        == "success"
    )


def test_full_pipeline_outputs_have_expected_row_counts(
    tmp_path: Path,
):
    source = tmp_path / "input.csv"

    create_source(source)

    config = create_config(
        tmp_path,
        source,
    )

    PipelineOrchestrator(
        config
    ).run()

    processed = pd.read_csv(
        config.processed_path
    )

    rejected = pd.read_csv(
        config.rejected_path
    )

    assert len(processed) == 4
    assert len(rejected) == 0


def test_full_pipeline_monitoring_reflects_success(
    tmp_path: Path,
):
    source = tmp_path / "input.csv"

    create_source(source)

    config = create_config(
        tmp_path,
        source,
    )

    PipelineOrchestrator(
        config
    ).run()

    store = RunHistoryStore(
        config.run_history_path
    )

    summary = build_monitoring_summary(
        store
    )

    assert summary.total_runs == 1
    assert summary.successful_runs == 1
    assert summary.failed_runs == 0
    assert summary.success_rate_pct == 100.0

    assert (
        summary.total_records_extracted
        == 4
    )

    assert (
        summary.total_records_processed
        == 4
    )

    assert (
        summary.total_records_rejected
        == 0
    )

    assert summary.last_status == "success"

    assert (
        summary.last_run_id
        is not None
    )

    assert (
        summary.last_successful_at
        is not None
    )


def test_full_pipeline_rejection_flows_to_output_and_monitoring(
    tmp_path: Path,
):
    source = tmp_path / "input.csv"

    create_invalid_source(source)

    config = create_config(
        tmp_path,
        source,
    )

    result = PipelineOrchestrator(
        config
    ).run()

    assert (
        result.run.status.value
        == "success"
    )

    assert (
        result.metrics.records_extracted
        == 3
    )

    assert (
        result.metrics.records_processed
        == 2
    )

    assert (
        result.metrics.records_rejected
        == 1
    )

    processed = pd.read_csv(
        config.processed_path
    )

    rejected = pd.read_csv(
        config.rejected_path
    )

    assert len(processed) == 2
    assert len(rejected) == 1

    assert (
        rejected.loc[
            0,
            "rejection_reason",
        ]
        == "invalid_revenue"
    )

    store = RunHistoryStore(
        config.run_history_path
    )

    summary = build_monitoring_summary(
        store
    )

    assert summary.total_runs == 1
    assert summary.successful_runs == 1
    assert summary.failed_runs == 0
    assert (
        summary.total_records_rejected
        == 1
    )


def test_multiple_orchestrator_runs_accumulate_history(
    tmp_path: Path,
):
    source = tmp_path / "input.csv"

    create_source(source)

    config = create_config(
        tmp_path,
        source,
    )

    orchestrator = PipelineOrchestrator(
        config
    )

    first = orchestrator.run()
    second = orchestrator.run()

    assert (
        first.run.run_id
        != second.run.run_id
    )

    store = RunHistoryStore(
        config.run_history_path
    )

    records = store.read_all()

    assert len(records) == 2

    assert (
        records[0]["run_id"]
        == first.run.run_id
    )

    assert (
        records[1]["run_id"]
        == second.run.run_id
    )


def test_multiple_runs_monitoring_totals_accumulate(
    tmp_path: Path,
):
    source = tmp_path / "input.csv"

    create_source(source)

    config = create_config(
        tmp_path,
        source,
    )

    orchestrator = PipelineOrchestrator(
        config
    )

    orchestrator.run()
    orchestrator.run()

    store = RunHistoryStore(
        config.run_history_path
    )

    summary = build_monitoring_summary(
        store
    )

    assert summary.total_runs == 2
    assert summary.successful_runs == 2
    assert summary.failed_runs == 0
    assert summary.success_rate_pct == 100.0

    assert (
        summary.total_records_extracted
        == 8
    )

    assert (
        summary.total_records_processed
        == 8
    )

    assert (
        summary.total_records_rejected
        == 0
    )


def test_missing_source_fails_without_creating_successful_run(
    tmp_path: Path,
):
    source = (
        tmp_path / "does_not_exist.csv"
    )

    config = create_config(
        tmp_path,
        source,
    )

    with pytest.raises(
        FileNotFoundError
    ):
        PipelineOrchestrator(
            config
        ).run()

    store = RunHistoryStore(
        config.run_history_path
    )

    records = store.read_all()

    assert len(records) == 1
    assert records[0]["status"] == "failed"

    summary = build_monitoring_summary(
        store
    )

    assert summary.total_runs == 1
    assert summary.successful_runs == 0
    assert summary.failed_runs == 1
    assert summary.success_rate_pct == 0.0

    assert (
        summary.latest_failure
        is not None
    )

    assert (
        summary.last_status
        == "failed"
    )


def test_failed_run_does_not_create_processed_output(
    tmp_path: Path,
):
    source = (
        tmp_path / "missing.csv"
    )

    config = create_config(
        tmp_path,
        source,
    )

    with pytest.raises(
        FileNotFoundError
    ):
        PipelineOrchestrator(
            config
        ).run()

    assert not config.processed_path.exists()
    assert not config.rejected_path.exists()


def test_corrupted_history_does_not_break_new_pipeline_run(
    tmp_path: Path,
):
    source = tmp_path / "input.csv"

    create_source(source)

    config = create_config(
        tmp_path,
        source,
    )

    config.run_history_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    config.run_history_path.write_text(
        "CORRUPTED HISTORY\n",
        encoding="utf-8",
    )

    result = PipelineOrchestrator(
        config
    ).run()

    assert (
        result.run.status.value
        == "success"
    )

    store = RunHistoryStore(
        config.run_history_path
    )

    records = store.read_all()

    assert len(records) == 1

    assert (
        records[0]["run_id"]
        == result.run.run_id
    )

    assert (
        records[0]["status"]
        == "success"
    )


def test_monitoring_handles_empty_history(
    tmp_path: Path,
):
    history = (
        tmp_path / "run_history.jsonl"
    )

    store = RunHistoryStore(
        history
    )

    summary = build_monitoring_summary(
        store
    )

    assert summary.total_runs == 0
    assert summary.successful_runs == 0
    assert summary.failed_runs == 0
    assert summary.success_rate_pct == 0.0

    assert (
        summary.total_records_extracted
        == 0
    )

    assert (
        summary.total_records_processed
        == 0
    )

    assert (
        summary.total_records_rejected
        == 0
    )

    assert summary.latest_run is None
    assert summary.latest_failure is None
    assert summary.last_attempted_at is None
    assert summary.last_successful_at is None
    assert summary.last_failed_at is None
    assert summary.last_run_id is None
    assert summary.last_status is None
