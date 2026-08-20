from datetime import datetime, timezone

from finsight.pipeline.run_error import PipelineRunError
from finsight.pipeline.run_tracking import (
    PipelineRun,
    PipelineRunStatus,
)


def test_pipeline_run_error_contains_run():
    run = PipelineRun(
        run_id="test-run",
        pipeline_name="local_financial_etl",
        status=PipelineRunStatus.FAILED,
        started_at=datetime.now(timezone.utc),
        completed_at=datetime.now(timezone.utc),
        error_message="test failure",
    )

    error = PipelineRunError(
        "test failure",
        run,
    )

    assert str(error) == "test failure"
    assert error.run is run
