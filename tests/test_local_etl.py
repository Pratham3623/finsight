from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest

from finsight.pipeline.local_etl import run_local_etl
from finsight.pipeline.run_error import PipelineRunError
from finsight.pipeline.run_tracking import PipelineRunStatus


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


def test_local_etl_processes_valid_records(
    tmp_path: Path,
):
    source = tmp_path / "input.csv"
    processed = tmp_path / "processed.csv"
    rejected = tmp_path / "rejected.csv"

    create_source(source)

    result = run_local_etl(
        source,
        processed,
        rejected,
    )

    assert result.quality_report.records_extracted == 3
    assert result.quality_report.records_valid == 3
    assert result.quality_report.records_rejected == 0

    assert result.run.status == PipelineRunStatus.SUCCESS
    assert result.run.records_extracted == 3
    assert result.run.records_processed == 3
    assert result.run.records_rejected == 0
    assert result.run.completed_at is not None

    assert processed.exists()
    assert rejected.exists()

    processed_df = pd.read_csv(processed)

    assert len(processed_df) == 3


def test_local_etl_rejects_invalid_records(
    tmp_path: Path,
):
    source = tmp_path / "input.csv"
    processed = tmp_path / "processed.csv"
    rejected = tmp_path / "rejected.csv"

    create_source(source)

    dataframe = pd.read_csv(source)
    dataframe.loc[1, "revenue"] = -100
    dataframe.to_csv(source, index=False)

    result = run_local_etl(
        source,
        processed,
        rejected,
    )

    assert result.quality_report.records_extracted == 3
    assert result.quality_report.records_valid == 2
    assert result.quality_report.records_rejected == 1

    rejected_df = pd.read_csv(rejected)

    assert len(rejected_df) == 1
    assert (
        rejected_df.loc[0, "rejection_reason"]
        == "invalid_revenue"
    )


def test_local_etl_missing_source_raises_pipeline_error(
    tmp_path: Path,
):
    source = tmp_path / "missing.csv"
    processed = tmp_path / "processed.csv"
    rejected = tmp_path / "rejected.csv"

    with pytest.raises(
        PipelineRunError,
        match="Input file does not exist",
    ) as exc_info:
        run_local_etl(
            source,
            processed,
            rejected,
        )

    error = exc_info.value

    assert isinstance(
        error.__cause__,
        FileNotFoundError,
    )

    assert error.run.status == PipelineRunStatus.FAILED
    assert error.run.error_message is not None
    assert (
        "Input file does not exist"
        in error.run.error_message
    )
    assert error.run.completed_at is not None
    assert error.run.records_extracted == 0
    assert error.run.records_processed == 0
    assert error.run.records_rejected == 0


def test_local_etl_directory_source_raises_pipeline_error(
    tmp_path: Path,
):
    source = tmp_path / "input_directory"
    source.mkdir()

    processed = tmp_path / "processed.csv"
    rejected = tmp_path / "rejected.csv"

    with pytest.raises(
        PipelineRunError,
        match="Input path is not a file",
    ) as exc_info:
        run_local_etl(
            source,
            processed,
            rejected,
        )

    error = exc_info.value

    assert isinstance(
        error.__cause__,
        ValueError,
    )
    assert error.run.status == PipelineRunStatus.FAILED


def test_local_etl_schema_failure_is_tracked(
    tmp_path: Path,
):
    source = tmp_path / "invalid_schema.csv"
    processed = tmp_path / "processed.csv"
    rejected = tmp_path / "rejected.csv"

    create_source(source)

    dataframe = pd.read_csv(source)

    dataframe = dataframe.drop(
        columns=["revenue"]
    )

    dataframe.to_csv(source, index=False)

    with pytest.raises(
        PipelineRunError,
        match="Financial dataset failed schema validation",
    ) as exc_info:
        run_local_etl(
            source,
            processed,
            rejected,
        )

    error = exc_info.value

    assert isinstance(
        error.__cause__,
        ValueError,
    )

    assert error.run.status == PipelineRunStatus.FAILED
    assert error.run.completed_at is not None

    assert not processed.exists()
    assert not rejected.exists()


def test_local_etl_writer_failure_is_tracked(
    tmp_path: Path,
):
    source = tmp_path / "input.csv"
    processed = tmp_path / "processed.csv"
    rejected = tmp_path / "rejected.csv"

    create_source(source)

    with patch(
        "finsight.pipeline.local_etl.write_processed_records",
        side_effect=OSError(
            "Unable to write processed output"
        ),
    ):
        with pytest.raises(
            PipelineRunError,
            match="Unable to write processed output",
        ) as exc_info:
            run_local_etl(
                source,
                processed,
                rejected,
            )

    error = exc_info.value

    assert isinstance(
        error.__cause__,
        OSError,
    )

    assert error.run.status == PipelineRunStatus.FAILED
    assert (
        error.run.error_message
        == "Unable to write processed output"
    )


def test_local_etl_failure_preserves_run_identity(
    tmp_path: Path,
):
    source = tmp_path / "missing.csv"
    processed = tmp_path / "processed.csv"
    rejected = tmp_path / "rejected.csv"

    with pytest.raises(
        PipelineRunError
    ) as exc_info:
        run_local_etl(
            source,
            processed,
            rejected,
        )

    error = exc_info.value

    assert error.run.run_id
    assert (
        error.run.pipeline_name
        == "local_financial_etl"
    )
    assert (
        error.run.started_at is not None
    )
    assert (
        error.run.completed_at is not None
    )


def test_local_etl_success_after_previous_failure(
    tmp_path: Path,
):
    source = tmp_path / "input.csv"
    processed = tmp_path / "processed.csv"
    rejected = tmp_path / "rejected.csv"

    missing_source = tmp_path / "missing.csv"

    create_source(source)

    with pytest.raises(PipelineRunError):
        run_local_etl(
            missing_source,
            processed,
            rejected,
        )

    result = run_local_etl(
        source,
        processed,
        rejected,
    )

    assert result.run.status == PipelineRunStatus.SUCCESS
    assert result.run.records_extracted == 3
    assert result.run.records_processed == 3
    assert result.run.records_rejected == 0

    assert processed.exists()
    assert rejected.exists()
