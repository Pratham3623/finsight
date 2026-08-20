from datetime import datetime, timezone

import pytest

from finsight.pipeline.run_tracker import PipelineRunTracker
from finsight.pipeline.run_tracking import PipelineRunStatus


def test_tracker_starts_run():
    tracker = PipelineRunTracker(
        "local_financial_etl"
    )

    run = tracker.start()

    assert run.run_id
    assert run.pipeline_name == "local_financial_etl"
    assert run.status == PipelineRunStatus.RUNNING
    assert run.started_at.tzinfo == timezone.utc
    assert run.completed_at is None


def test_tracker_marks_success():
    tracker = PipelineRunTracker(
        "local_financial_etl"
    )

    started = tracker.start()

    completed = tracker.succeed(
        records_extracted=100,
        records_processed=95,
        records_rejected=5,
    )

    assert completed.run_id == started.run_id
    assert completed.status == PipelineRunStatus.SUCCESS
    assert completed.records_extracted == 100
    assert completed.records_processed == 95
    assert completed.records_rejected == 5
    assert completed.completed_at is not None
    assert completed.completed_at >= completed.started_at
    assert completed.error_message is None


def test_tracker_marks_failure():
    tracker = PipelineRunTracker(
        "local_financial_etl"
    )

    started = tracker.start()

    failed = tracker.fail(
        "Database connection failed.",
        records_extracted=100,
        records_processed=50,
        records_rejected=10,
    )

    assert failed.run_id == started.run_id
    assert failed.status == PipelineRunStatus.FAILED
    assert failed.records_extracted == 100
    assert failed.records_processed == 50
    assert failed.records_rejected == 10
    assert failed.completed_at is not None
    assert failed.error_message == (
        "Database connection failed."
    )


def test_tracker_requires_start_before_success():
    tracker = PipelineRunTracker(
        "local_financial_etl"
    )

    with pytest.raises(
        RuntimeError,
        match="has not been started",
    ):
        tracker.succeed()


def test_tracker_requires_start_before_failure():
    tracker = PipelineRunTracker(
        "local_financial_etl"
    )

    with pytest.raises(
        RuntimeError,
        match="has not been started",
    ):
        tracker.fail("Something failed.")


def test_tracker_rejects_empty_pipeline_name():
    with pytest.raises(
        ValueError,
        match="Pipeline name must not be empty",
    ):
        PipelineRunTracker("   ")


def test_tracker_cannot_start_twice():
    tracker = PipelineRunTracker(
        "local_financial_etl"
    )

    tracker.start()

    with pytest.raises(
        RuntimeError,
        match="already been started",
    ):
        tracker.start()


@pytest.mark.parametrize(
    "method_name",
    ["succeed", "fail"],
)
def test_tracker_rejects_negative_counts(
    method_name: str,
):
    tracker = PipelineRunTracker(
        "local_financial_etl"
    )

    tracker.start()

    method = getattr(tracker, method_name)

    kwargs = (
        {"error_message": "failure"}
        if method_name == "fail"
        else {}
    )

    with pytest.raises(
        ValueError,
        match="must not be negative",
    ):
        method(
            **kwargs,
            records_extracted=-1,
        )


def test_tracker_rejects_non_integer_counts():
    tracker = PipelineRunTracker(
        "local_financial_etl"
    )

    tracker.start()

    with pytest.raises(
        TypeError,
        match="must be an integer",
    ):
        tracker.succeed(
            records_extracted=1.5,
        )


def test_tracker_run_property_requires_start():
    tracker = PipelineRunTracker(
        "local_financial_etl"
    )

    with pytest.raises(
        RuntimeError,
        match="has not been started",
    ):
        _ = tracker.run
