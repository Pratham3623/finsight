import pytest

from finsight.pipeline.scheduler import (
    PipelineScheduler,
    SchedulerConfig,
)


def test_scheduler_runs_job_requested_number_of_times():
    executions = []

    def job():
        executions.append("run")

    scheduler = PipelineScheduler(
        job=job,
        config=SchedulerConfig(
            interval_seconds=10,
            max_runs=3,
        ),
        sleep=lambda _: None,
    )

    count = scheduler.run()

    assert count == 3
    assert executions == [
        "run",
        "run",
        "run",
    ]


def test_scheduler_waits_between_runs():
    executions = []
    sleep_calls = []

    def job():
        executions.append("run")

    def fake_sleep(seconds):
        sleep_calls.append(seconds)

    scheduler = PipelineScheduler(
        job=job,
        config=SchedulerConfig(
            interval_seconds=30,
            max_runs=3,
        ),
        sleep=fake_sleep,
    )

    count = scheduler.run()

    assert count == 3
    assert len(executions) == 3
    assert sleep_calls == [30, 30]


def test_scheduler_supports_single_execution():
    executions = []

    scheduler = PipelineScheduler(
        job=lambda: executions.append("run"),
        config=SchedulerConfig(
            interval_seconds=60,
            max_runs=1,
        ),
        sleep=lambda _: None,
    )

    count = scheduler.run()

    assert count == 1
    assert executions == ["run"]


def test_scheduler_config_rejects_zero_interval():
    with pytest.raises(
        ValueError,
        match="interval_seconds",
    ):
        SchedulerConfig(
            interval_seconds=0,
        )


def test_scheduler_config_rejects_negative_interval():
    with pytest.raises(
        ValueError,
        match="interval_seconds",
    ):
        SchedulerConfig(
            interval_seconds=-1,
        )


def test_scheduler_config_rejects_invalid_max_runs():
    with pytest.raises(
        ValueError,
        match="max_runs",
    ):
        SchedulerConfig(
            interval_seconds=10,
            max_runs=0,
        )

    with pytest.raises(
        ValueError,
        match="max_runs",
    ):
        SchedulerConfig(
            interval_seconds=10,
            max_runs=-1,
        )


def test_scheduler_continues_after_failure_when_bounded():
    executions = []

    def job():
        executions.append("run")

        if len(executions) == 1:
            raise RuntimeError(
                "temporary scheduler failure"
            )

    scheduler = PipelineScheduler(
        job=job,
        config=SchedulerConfig(
            interval_seconds=10,
            max_runs=2,
        ),
        sleep=lambda _: None,
    )

    count = scheduler.run()

    assert count == 2
    assert executions == [
        "run",
        "run",
    ]


def test_scheduler_continues_after_multiple_failures_when_bounded():
    executions = []

    def job():
        executions.append("run")

        if len(executions) < 3:
            raise RuntimeError(
                "temporary scheduler failure"
            )

    scheduler = PipelineScheduler(
        job=job,
        config=SchedulerConfig(
            interval_seconds=10,
            max_runs=3,
        ),
        sleep=lambda _: None,
    )

    count = scheduler.run()

    assert count == 3
    assert executions == [
        "run",
        "run",
        "run",
    ]


def test_scheduler_does_not_sleep_after_final_execution():
    sleep_calls = []

    scheduler = PipelineScheduler(
        job=lambda: None,
        config=SchedulerConfig(
            interval_seconds=25,
            max_runs=3,
        ),
        sleep=lambda seconds: sleep_calls.append(
            seconds
        ),
    )

    count = scheduler.run()

    assert count == 3
    assert sleep_calls == [
        25,
        25,
    ]


def test_scheduler_does_not_sleep_after_single_execution():
    sleep_calls = []

    scheduler = PipelineScheduler(
        job=lambda: None,
        config=SchedulerConfig(
            interval_seconds=25,
            max_runs=1,
        ),
        sleep=lambda seconds: sleep_calls.append(
            seconds
        ),
    )

    count = scheduler.run()

    assert count == 1
    assert sleep_calls == []


def test_scheduler_unbounded_re_raises_job_failure():
    executions = []

    def job():
        executions.append("run")
        raise RuntimeError(
            "scheduler failure"
        )

    scheduler = PipelineScheduler(
        job=job,
        config=SchedulerConfig(
            interval_seconds=10,
            max_runs=None,
        ),
        sleep=lambda _: None,
    )

    with pytest.raises(
        RuntimeError,
        match="scheduler failure",
    ):
        scheduler.run()

    assert executions == ["run"]


def test_scheduler_unbounded_does_not_sleep_after_failure():
    sleep_calls = []

    def job():
        raise RuntimeError(
            "scheduler failure"
        )

    scheduler = PipelineScheduler(
        job=job,
        config=SchedulerConfig(
            interval_seconds=10,
            max_runs=None,
        ),
        sleep=lambda seconds: sleep_calls.append(
            seconds
        ),
    )

    with pytest.raises(RuntimeError):
        scheduler.run()

    assert sleep_calls == []


def test_scheduler_counts_failed_executions():
    executions = []

    def job():
        executions.append(len(executions) + 1)

        raise RuntimeError(
            "failure"
        )

    scheduler = PipelineScheduler(
        job=job,
        config=SchedulerConfig(
            interval_seconds=1,
            max_runs=4,
        ),
        sleep=lambda _: None,
    )

    count = scheduler.run()

    assert count == 4
    assert executions == [
        1,
        2,
        3,
        4,
    ]


def test_scheduler_preserves_job_return_value_independently():
    results = []

    def job():
        results.append("completed")
        return "ignored"

    scheduler = PipelineScheduler(
        job=job,
        config=SchedulerConfig(
            interval_seconds=1,
            max_runs=2,
        ),
        sleep=lambda _: None,
    )

    count = scheduler.run()

    assert count == 2
    assert results == [
        "completed",
        "completed",
    ]


def test_scheduler_rejects_non_positive_interval():
    with pytest.raises(ValueError):
        SchedulerConfig(
            interval_seconds=-0.1,
            max_runs=1,
        )


def test_scheduler_allows_unbounded_runs():
    executions = []

    def job():
        executions.append("run")

        if len(executions) >= 3:
            raise RuntimeError(
                "stop scheduler"
            )

    scheduler = PipelineScheduler(
        job=job,
        config=SchedulerConfig(
            interval_seconds=1,
            max_runs=None,
        ),
        sleep=lambda _: None,
    )

    with pytest.raises(
        RuntimeError,
        match="stop scheduler",
    ):
        scheduler.run()

    assert executions == [
        "run",
        "run",
        "run",
    ]
