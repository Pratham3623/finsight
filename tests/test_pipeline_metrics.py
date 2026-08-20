import pytest

from finsight.pipeline.metrics import PipelineMetrics


def test_pipeline_metrics_stores_values():
    metrics = PipelineMetrics(
        duration_seconds=2.5,
        attempts=2,
        records_extracted=100,
        records_processed=95,
        records_rejected=5,
    )

    assert metrics.duration_seconds == 2.5
    assert metrics.attempts == 2
    assert metrics.records_extracted == 100
    assert metrics.records_processed == 95
    assert metrics.records_rejected == 5


def test_pipeline_metrics_rejects_negative_duration():
    with pytest.raises(ValueError):
        PipelineMetrics(
            duration_seconds=-1,
            attempts=1,
            records_extracted=0,
            records_processed=0,
            records_rejected=0,
        )


def test_pipeline_metrics_requires_at_least_one_attempt():
    with pytest.raises(ValueError):
        PipelineMetrics(
            duration_seconds=1,
            attempts=0,
            records_extracted=0,
            records_processed=0,
            records_rejected=0,
        )


@pytest.mark.parametrize(
    "field",
    [
        "records_extracted",
        "records_processed",
        "records_rejected",
    ],
)
def test_pipeline_metrics_rejects_negative_counts(field):
    values = {
        "duration_seconds": 1,
        "attempts": 1,
        "records_extracted": 0,
        "records_processed": 0,
        "records_rejected": 0,
    }

    values[field] = -1

    with pytest.raises(ValueError):
        PipelineMetrics(**values)
