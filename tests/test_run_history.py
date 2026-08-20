from datetime import datetime, timezone
from pathlib import Path

import pytest

from finsight.pipeline.run_history import (
    RunHistoryStore,
)
from finsight.pipeline.run_tracking import (
    PipelineRun,
    PipelineRunStatus,
)


def create_run(
    run_id: str = "test-run-id",
    status: PipelineRunStatus = PipelineRunStatus.SUCCESS,
) -> PipelineRun:
    started = datetime(
        2026,
        8,
        20,
        10,
        0,
        tzinfo=timezone.utc,
    )

    completed = datetime(
        2026,
        8,
        20,
        10,
        0,
        1,
        tzinfo=timezone.utc,
    )

    return PipelineRun(
        run_id=run_id,
        pipeline_name="local_financial_etl",
        status=status,
        started_at=started,
        completed_at=completed,
        records_extracted=100,
        records_processed=95,
        records_rejected=5,
        error_message=(
            "test failure"
            if status == PipelineRunStatus.FAILED
            else None
        ),
    )


def test_append_creates_history_file(
    tmp_path: Path,
):
    history_path = tmp_path / "run_history.jsonl"

    store = RunHistoryStore(history_path)

    store.append(create_run())

    assert history_path.exists()


def test_append_stores_run_as_json(
    tmp_path: Path,
):
    history_path = tmp_path / "run_history.jsonl"

    store = RunHistoryStore(history_path)

    store.append(create_run())

    records = store.read_all()

    assert len(records) == 1

    record = records[0]

    assert record["run_id"] == "test-run-id"
    assert (
        record["pipeline_name"]
        == "local_financial_etl"
    )
    assert record["status"] == "success"
    assert record["records_extracted"] == 100
    assert record["records_processed"] == 95
    assert record["records_rejected"] == 5


def test_append_preserves_multiple_runs(
    tmp_path: Path,
):
    history_path = tmp_path / "run_history.jsonl"

    store = RunHistoryStore(history_path)

    store.append(
        create_run("run-1")
    )

    store.append(
        create_run("run-2")
    )

    records = store.read_all()

    assert len(records) == 2
    assert records[0]["run_id"] == "run-1"
    assert records[1]["run_id"] == "run-2"


def test_read_all_returns_empty_when_file_missing(
    tmp_path: Path,
):
    history_path = tmp_path / "missing.jsonl"

    store = RunHistoryStore(history_path)

    assert store.read_all() == []


def test_latest_returns_most_recent_run(
    tmp_path: Path,
):
    history_path = tmp_path / "run_history.jsonl"

    store = RunHistoryStore(history_path)

    store.append(
        create_run("run-1")
    )

    store.append(
        create_run("run-2")
    )

    latest = store.latest()

    assert latest is not None
    assert latest["run_id"] == "run-2"


def test_latest_returns_none_when_history_empty(
    tmp_path: Path,
):
    history_path = tmp_path / "run_history.jsonl"

    store = RunHistoryStore(history_path)

    assert store.latest() is None


def test_get_by_run_id_returns_matching_run(
    tmp_path: Path,
):
    history_path = tmp_path / "run_history.jsonl"

    store = RunHistoryStore(history_path)

    store.append(
        create_run("run-1")
    )

    store.append(
        create_run("run-2")
    )

    result = store.get_by_run_id("run-2")

    assert result is not None
    assert result["run_id"] == "run-2"


def test_get_by_run_id_returns_none_when_missing(
    tmp_path: Path,
):
    history_path = tmp_path / "run_history.jsonl"

    store = RunHistoryStore(history_path)

    store.append(
        create_run("run-1")
    )

    assert (
        store.get_by_run_id("does-not-exist")
        is None
    )


def test_get_by_run_id_rejects_empty_id(
    tmp_path: Path,
):
    history_path = tmp_path / "run_history.jsonl"

    store = RunHistoryStore(history_path)

    with pytest.raises(ValueError):
        store.get_by_run_id("")


def test_get_failed_runs_returns_only_failures(
    tmp_path: Path,
):
    history_path = tmp_path / "run_history.jsonl"

    store = RunHistoryStore(history_path)

    store.append(
        create_run(
            "success-1",
            PipelineRunStatus.SUCCESS,
        )
    )

    store.append(
        create_run(
            "failed-1",
            PipelineRunStatus.FAILED,
        )
    )

    store.append(
        create_run(
            "success-2",
            PipelineRunStatus.SUCCESS,
        )
    )

    store.append(
        create_run(
            "failed-2",
            PipelineRunStatus.FAILED,
        )
    )

    failures = store.get_failed_runs()

    assert len(failures) == 2
    assert failures[0]["run_id"] == "failed-1"
    assert failures[1]["run_id"] == "failed-2"


def test_get_recent_runs_returns_latest_records(
    tmp_path: Path,
):
    history_path = tmp_path / "run_history.jsonl"

    store = RunHistoryStore(history_path)

    for index in range(5):
        store.append(
            create_run(f"run-{index}")
        )

    recent = store.get_recent_runs(3)

    assert len(recent) == 3
    assert recent[0]["run_id"] == "run-2"
    assert recent[1]["run_id"] == "run-3"
    assert recent[2]["run_id"] == "run-4"


def test_get_recent_runs_returns_all_when_limit_is_large(
    tmp_path: Path,
):
    history_path = tmp_path / "run_history.jsonl"

    store = RunHistoryStore(history_path)

    store.append(create_run("run-1"))
    store.append(create_run("run-2"))

    recent = store.get_recent_runs(100)

    assert len(recent) == 2


def test_get_recent_runs_rejects_invalid_limit(
    tmp_path: Path,
):
    history_path = tmp_path / "run_history.jsonl"

    store = RunHistoryStore(history_path)

    with pytest.raises(ValueError):
        store.get_recent_runs(0)

    with pytest.raises(ValueError):
        store.get_recent_runs(-1)


def test_get_recent_runs_rejects_non_integer_limit(
    tmp_path: Path,
):
    history_path = tmp_path / "run_history.jsonl"

    store = RunHistoryStore(history_path)

    with pytest.raises(TypeError):
        store.get_recent_runs("10")


# ============================================================
# Phase 13.7 — Run History Corruption Tests
# ============================================================


def test_read_all_skips_malformed_json_lines(
    tmp_path: Path,
):
    history_path = tmp_path / "run_history.jsonl"

    store = RunHistoryStore(history_path)

    store.append(create_run("run-1"))

    with history_path.open(
        "a",
        encoding="utf-8",
    ) as file:
        file.write(
            '{"this is": "not valid json"\n'
        )

    store.append(create_run("run-2"))

    records = store.read_all()

    assert len(records) == 2
    assert records[0]["run_id"] == "run-1"
    assert records[1]["run_id"] == "run-2"


def test_read_all_skips_blank_lines(
    tmp_path: Path,
):
    history_path = tmp_path / "run_history.jsonl"

    store = RunHistoryStore(history_path)

    store.append(create_run("run-1"))

    with history_path.open(
        "a",
        encoding="utf-8",
    ) as file:
        file.write("\n\n")

    store.append(create_run("run-2"))

    records = store.read_all()

    assert len(records) == 2


def test_read_all_skips_json_arrays(
    tmp_path: Path,
):
    history_path = tmp_path / "run_history.jsonl"

    store = RunHistoryStore(history_path)

    store.append(create_run("run-1"))

    with history_path.open(
        "a",
        encoding="utf-8",
    ) as file:
        file.write("[1, 2, 3]\n")

    store.append(create_run("run-2"))

    records = store.read_all()

    assert len(records) == 2
    assert records[0]["run_id"] == "run-1"
    assert records[1]["run_id"] == "run-2"


def test_latest_ignores_corrupted_final_line(
    tmp_path: Path,
):
    history_path = tmp_path / "run_history.jsonl"

    store = RunHistoryStore(history_path)

    store.append(create_run("run-1"))

    with history_path.open(
        "a",
        encoding="utf-8",
    ) as file:
        file.write(
            '{"broken": '
        )

    latest = store.latest()

    assert latest is not None
    assert latest["run_id"] == "run-1"


def test_get_by_run_id_works_after_corruption(
    tmp_path: Path,
):
    history_path = tmp_path / "run_history.jsonl"

    store = RunHistoryStore(history_path)

    store.append(create_run("run-1"))

    with history_path.open(
        "a",
        encoding="utf-8",
    ) as file:
        file.write(
            "CORRUPTED LINE\n"
        )

    store.append(create_run("run-2"))

    result = store.get_by_run_id("run-2")

    assert result is not None
    assert result["run_id"] == "run-2"


def test_get_failed_runs_ignores_corrupted_records(
    tmp_path: Path,
):
    history_path = tmp_path / "run_history.jsonl"

    store = RunHistoryStore(history_path)

    store.append(
        create_run(
            "success-1",
            PipelineRunStatus.SUCCESS,
        )
    )

    with history_path.open(
        "a",
        encoding="utf-8",
    ) as file:
        file.write(
            '{"status": "failed"\n'
        )

    store.append(
        create_run(
            "failed-1",
            PipelineRunStatus.FAILED,
        )
    )

    failures = store.get_failed_runs()

    assert len(failures) == 1
    assert failures[0]["run_id"] == "failed-1"


def test_append_recovers_after_corrupted_history(
    tmp_path: Path,
):
    history_path = tmp_path / "run_history.jsonl"

    store = RunHistoryStore(history_path)

    with history_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        file.write(
            "CORRUPTED HISTORY\n"
        )

    store.append(create_run("run-1"))

    records = store.read_all()

    assert len(records) == 1
    assert records[0]["run_id"] == "run-1"


def test_get_recent_runs_ignores_corrupted_lines(
    tmp_path: Path,
):
    history_path = tmp_path / "run_history.jsonl"

    store = RunHistoryStore(history_path)

    store.append(create_run("run-1"))

    with history_path.open(
        "a",
        encoding="utf-8",
    ) as file:
        file.write(
            "invalid json\n"
        )

    store.append(create_run("run-2"))
    store.append(create_run("run-3"))

    recent = store.get_recent_runs(2)

    assert len(recent) == 2
    assert recent[0]["run_id"] == "run-2"
    assert recent[1]["run_id"] == "run-3"
