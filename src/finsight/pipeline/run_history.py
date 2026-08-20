import json
import logging
from dataclasses import asdict
from pathlib import Path

from finsight.pipeline.run_tracking import PipelineRun


logger = logging.getLogger(__name__)


class RunHistoryStore:
    """Persist and query pipeline run history as JSON Lines."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def append(self, run: PipelineRun) -> None:
        """Append a pipeline run to the history file."""

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        record = asdict(run)

        record["status"] = run.status.value
        record["started_at"] = (
            run.started_at.isoformat()
        )

        if run.completed_at is not None:
            record["completed_at"] = (
                run.completed_at.isoformat()
            )

        with self.path.open(
            "a",
            encoding="utf-8",
        ) as file:
            file.write(
                json.dumps(record)
                + "\n"
            )

    def read_all(self) -> list[dict]:
        """Return all valid stored pipeline runs.

        Malformed JSON lines are skipped so that a single
        corrupted record does not make the complete history
        unavailable.
        """

        if not self.path.exists():
            return []

        records: list[dict] = []

        with self.path.open(
            "r",
            encoding="utf-8",
        ) as file:
            for line_number, line in enumerate(
                file,
                start=1,
            ):
                line = line.strip()

                if not line:
                    continue

                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    logger.warning(
                        "Skipping malformed run history "
                        "record: path=%s line=%d",
                        self.path,
                        line_number,
                    )
                    continue

                if not isinstance(record, dict):
                    logger.warning(
                        "Skipping non-object run history "
                        "record: path=%s line=%d",
                        self.path,
                        line_number,
                    )
                    continue

                records.append(record)

        return records

    def latest(self) -> dict | None:
        """Return the most recent valid pipeline run."""

        records = self.read_all()

        if not records:
            return None

        return records[-1]

    def get_by_run_id(
        self,
        run_id: str,
    ) -> dict | None:
        """Return a pipeline run by its run ID."""

        if not run_id.strip():
            raise ValueError(
                "Run ID must not be empty."
            )

        for record in self.read_all():
            if record.get("run_id") == run_id:
                return record

        return None

    def get_failed_runs(self) -> list[dict]:
        """Return all failed pipeline runs."""

        return [
            record
            for record in self.read_all()
            if record.get("status") == "failed"
        ]

    def get_recent_runs(
        self,
        limit: int = 10,
    ) -> list[dict]:
        """Return the most recent valid pipeline runs."""

        if not isinstance(limit, int):
            raise TypeError(
                "Limit must be an integer."
            )

        if limit <= 0:
            raise ValueError(
                "Limit must be greater than zero."
            )

        records = self.read_all()

        return records[-limit:]
