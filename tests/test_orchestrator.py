from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest

from finsight.pipeline.local_etl import PipelineResult
from finsight.pipeline.metrics import PipelineMetrics
from finsight.pipeline.orchestrator import (
    PipelineConfig,
    PipelineOrchestrator,
)
from finsight.pipeline.retry_policy import RetryPolicy
from finsight.pipeline.run_error import PipelineRunError
from finsight.pipeline.run_tracking import (
    PipelineRun,
    PipelineRunStatus,
)


def create_source(path: Path) -> None:
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
            "revenue": [100.0, 200.0, 300.0],
            "operating_expenses": [70.0, 140.0, 210.0],
            "net_income": [20.0, 30.0, 40.0],
            "total_assets": [200.0, 300.0, 400.0],
            "total_liabilities": [100.0, 150.0, 200.0],
            "total_debt": [50.0, 75.0, 100.0],
            "operating_cash_flow": [20.0, 30.0, 40.0],
            "investing_cash_flow": [-10.0, -20.0, -30.0],
            "financing_cash_flow": [5.0, 10.0, 15.0],
        }
    )

    dataframe.to_csv(path, index=False)


def create_config(tmp_path: Path) -> PipelineConfig:
    source = tmp_path / "input.csv"
    processed = tmp_path / "processed.csv"
    rejected = tmp_path / "rejected.csv"
    history = tmp_path / "run_history.jsonl"

    create_source(source)

    return PipelineConfig(
        source_path=source,
        processed_path=processed,
        rejected_path=rejected,
        run_history_path=history,
    )


def create_successful_result(
    config: PipelineConfig,
) -> PipelineResult:
    started_at = datetime.now(timezone.utc)
    completed_at = datetime.now(timezone.utc)

    run = PipelineRun(
        run_id="test-run-id",
        pipeline_name="local_financial_etl",
        status=PipelineRunStatus.SUCCESS,
        started_at=started_at,
        completed_at=completed_at,
        records_extracted=3,
        records_processed=3,
        records_rejected=0,
    )

    metrics = PipelineMetrics(
        duration_seconds=0.1,
        attempts=1,
        records_extracted=3,
        records_processed=3,
        records_rejected=0,
    )

    return PipelineResult(
        schema_validation=None,
        quality_report=None,
        processed_path=config.processed_path,
        rejected_path=config.rejected_path,
        run=run,
        metrics=metrics,
    )


def test_orchestrator_runs_pipeline(
    tmp_path: Path,
):
    config = create_config(tmp_path)
    successful_result = create_successful_result(config)

    with patch(
        "finsight.pipeline.orchestrator.run_local_etl"
    ) as mock_etl:
        mock_etl.return_value = successful_result

        result = PipelineOrchestrator(config).run()

    assert result.run.status == PipelineRunStatus.SUCCESS
    assert result.run.records_extracted == 3
    assert result.run.records_processed == 3
    assert result.run.records_rejected == 0

    mock_etl.assert_called_once_with(
        source_path=config.source_path,
        processed_path=config.processed_path,
        rejected_path=config.rejected_path,
    )


def test_orchestrator_metrics_count_retries(
    tmp_path: Path,
):
    config = create_config(tmp_path)
    successful_result = create_successful_result(config)

    policy = RetryPolicy(
        max_attempts=3,
        retryable_exceptions=(TimeoutError,),
    )

    with patch(
        "finsight.pipeline.orchestrator.run_local_etl"
    ) as mock_etl:
        mock_etl.side_effect = [
            TimeoutError("temporary failure"),
            successful_result,
        ]

        result = PipelineOrchestrator(
            config,
            retry_policy=policy,
        ).run()

    assert result is not successful_result
    assert result.run is successful_result.run
    assert result.run.status == PipelineRunStatus.SUCCESS
    assert result.metrics.attempts == 2
    assert mock_etl.call_count == 2


def test_orchestrator_retries_retryable_failure(
    tmp_path: Path,
):
    config = create_config(tmp_path)
    successful_result = create_successful_result(config)

    policy = RetryPolicy(
        max_attempts=3,
        retryable_exceptions=(TimeoutError,),
    )

    with patch(
        "finsight.pipeline.orchestrator.run_local_etl"
    ) as mock_etl:
        mock_etl.side_effect = [
            TimeoutError("temporary failure"),
            successful_result,
        ]

        result = PipelineOrchestrator(
            config,
            retry_policy=policy,
        ).run()

    assert result is not successful_result
    assert result.run is successful_result.run
    assert result.run.status == PipelineRunStatus.SUCCESS
    assert result.metrics.attempts == 2
    assert mock_etl.call_count == 2


def test_orchestrator_does_not_retry_non_retryable_failure(
    tmp_path: Path,
):
    config = create_config(tmp_path)

    policy = RetryPolicy(
        max_attempts=3,
        retryable_exceptions=(TimeoutError,),
    )

    with patch(
        "finsight.pipeline.orchestrator.run_local_etl"
    ) as mock_etl:
        mock_etl.side_effect = ValueError(
            "permanent failure"
        )

        with pytest.raises(
            ValueError,
            match="permanent failure",
        ):
            PipelineOrchestrator(
                config,
                retry_policy=policy,
            ).run()

    assert mock_etl.call_count == 1


def test_orchestrator_retries_until_retry_limit(
    tmp_path: Path,
):
    config = create_config(tmp_path)

    policy = RetryPolicy(
        max_attempts=3,
        retryable_exceptions=(TimeoutError,),
    )

    with patch(
        "finsight.pipeline.orchestrator.run_local_etl"
    ) as mock_etl:
        mock_etl.side_effect = TimeoutError(
            "persistent failure"
        )

        with pytest.raises(
            TimeoutError,
            match="persistent failure",
        ):
            PipelineOrchestrator(
                config,
                retry_policy=policy,
            ).run()

    assert mock_etl.call_count == 3


def test_orchestrator_retries_until_final_success(
    tmp_path: Path,
):
    config = create_config(tmp_path)
    successful_result = create_successful_result(config)

    policy = RetryPolicy(
        max_attempts=3,
        retryable_exceptions=(TimeoutError,),
    )

    with patch(
        "finsight.pipeline.orchestrator.run_local_etl",
    ) as mock_etl:
        mock_etl.side_effect = [
            TimeoutError("temporary failure 1"),
            TimeoutError("temporary failure 2"),
            successful_result,
        ]

        result = PipelineOrchestrator(
            config,
            retry_policy=policy,
        ).run()

    assert result is not successful_result
    assert result.run is successful_result.run
    assert result.run.status == PipelineRunStatus.SUCCESS
    assert result.metrics.attempts == 3
    assert mock_etl.call_count == 3


def test_orchestrator_does_not_make_attempt_after_exhaustion(
    tmp_path: Path,
):
    config = create_config(tmp_path)

    policy = RetryPolicy(
        max_attempts=2,
        retryable_exceptions=(TimeoutError,),
    )

    with patch(
        "finsight.pipeline.orchestrator.run_local_etl",
    ) as mock_etl:
        mock_etl.side_effect = TimeoutError(
            "persistent timeout"
        )

        with pytest.raises(
            TimeoutError,
            match="persistent timeout",
        ):
            PipelineOrchestrator(
                config,
                retry_policy=policy,
            ).run()

    assert mock_etl.call_count == 2


def test_orchestrator_preserves_final_exception(
    tmp_path: Path,
):
    config = create_config(tmp_path)

    policy = RetryPolicy(
        max_attempts=3,
        retryable_exceptions=(TimeoutError,),
    )

    final_error = TimeoutError(
        "final timeout"
    )

    with patch(
        "finsight.pipeline.orchestrator.run_local_etl",
    ) as mock_etl:
        mock_etl.side_effect = [
            TimeoutError("first timeout"),
            TimeoutError("second timeout"),
            final_error,
        ]

        with pytest.raises(
            TimeoutError,
        ) as exc_info:
            PipelineOrchestrator(
                config,
                retry_policy=policy,
            ).run()

    assert exc_info.value is final_error
    assert str(exc_info.value) == "final timeout"
    assert mock_etl.call_count == 3


def test_orchestrator_retries_pipeline_run_error_using_cause(
    tmp_path: Path,
):
    config = create_config(tmp_path)
    successful_result = create_successful_result(config)

    policy = RetryPolicy(
        max_attempts=2,
        retryable_exceptions=(TimeoutError,),
    )

    failed_run = PipelineRun(
        run_id="failed-run",
        pipeline_name="local_financial_etl",
        status=PipelineRunStatus.FAILED,
        started_at=datetime.now(timezone.utc),
        completed_at=datetime.now(timezone.utc),
        error_message="temporary timeout",
    )

    pipeline_error = PipelineRunError(
        "temporary timeout",
        failed_run,
    )

    pipeline_error.__cause__ = TimeoutError(
        "temporary timeout"
    )

    with patch(
        "finsight.pipeline.orchestrator.run_local_etl",
    ) as mock_etl:
        mock_etl.side_effect = [
            pipeline_error,
            successful_result,
        ]

        result = PipelineOrchestrator(
            config,
            retry_policy=policy,
        ).run()

    assert result is not successful_result
    assert result.run is successful_result.run
    assert result.run.status == PipelineRunStatus.SUCCESS
    assert result.metrics.attempts == 2
    assert mock_etl.call_count == 2


def test_orchestrator_does_not_retry_pipeline_error_with_non_retryable_cause(
    tmp_path: Path,
):
    config = create_config(tmp_path)

    policy = RetryPolicy(
        max_attempts=3,
        retryable_exceptions=(TimeoutError,),
    )

    failed_run = PipelineRun(
        run_id="failed-run",
        pipeline_name="local_financial_etl",
        status=PipelineRunStatus.FAILED,
        started_at=datetime.now(timezone.utc),
        completed_at=datetime.now(timezone.utc),
        error_message="permanent error",
    )

    pipeline_error = PipelineRunError(
        "permanent error",
        failed_run,
    )

    pipeline_error.__cause__ = ValueError(
        "permanent error"
    )

    with patch(
        "finsight.pipeline.orchestrator.run_local_etl",
    ) as mock_etl:
        mock_etl.side_effect = pipeline_error

        with pytest.raises(
            ValueError,
            match="permanent error",
        ):
            PipelineOrchestrator(
                config,
                retry_policy=policy,
            ).run()

    assert mock_etl.call_count == 1


def test_orchestrator_records_final_pipeline_run_error(
    tmp_path: Path,
):
    config = create_config(tmp_path)

    policy = RetryPolicy(
        max_attempts=2,
        retryable_exceptions=(TimeoutError,),
    )

    failed_run = PipelineRun(
        run_id="failed-run",
        pipeline_name="local_financial_etl",
        status=PipelineRunStatus.FAILED,
        started_at=datetime.now(timezone.utc),
        completed_at=datetime.now(timezone.utc),
        error_message="persistent timeout",
    )

    pipeline_error = PipelineRunError(
        "persistent timeout",
        failed_run,
    )

    pipeline_error.__cause__ = TimeoutError(
        "persistent timeout"
    )

    with patch(
        "finsight.pipeline.orchestrator.run_local_etl",
    ) as mock_etl:
        mock_etl.side_effect = pipeline_error

        with pytest.raises(
            TimeoutError,
            match="persistent timeout",
        ):
            PipelineOrchestrator(
                config,
                retry_policy=policy,
            ).run()

    history = config.run_history_path.read_text(
        encoding="utf-8"
    )

    assert "failed-run" in history
    assert "persistent timeout" in history


def test_orchestrator_history_is_written_only_for_final_pipeline_run(
    tmp_path: Path,
):
    config = create_config(tmp_path)
    successful_result = create_successful_result(config)

    policy = RetryPolicy(
        max_attempts=3,
        retryable_exceptions=(TimeoutError,),
    )

    with patch(
        "finsight.pipeline.orchestrator.run_local_etl",
    ) as mock_etl:
        mock_etl.side_effect = [
            TimeoutError("temporary failure"),
            successful_result,
        ]

        PipelineOrchestrator(
            config,
            retry_policy=policy,
        ).run()

    lines = (
        config.run_history_path
        .read_text(encoding="utf-8")
        .splitlines()
    )

    assert len(lines) == 1
    assert "test-run-id" in lines[0]
