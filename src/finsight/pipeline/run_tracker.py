from datetime import datetime, timezone
from uuid import uuid4

from finsight.pipeline.run_tracking import (
    PipelineRun,
    PipelineRunStatus,
)


class PipelineRunTracker:
    """Track the lifecycle of a single pipeline execution."""

    def __init__(
        self,
        pipeline_name: str,
    ) -> None:
        if not pipeline_name.strip():
            raise ValueError(
                "Pipeline name must not be empty."
            )

        self._pipeline_name = pipeline_name
        self._run: PipelineRun | None = None

    @property
    def run(self) -> PipelineRun:
        """Return the current pipeline run."""

        if self._run is None:
            raise RuntimeError(
                "Pipeline run has not been started."
            )

        return self._run

    def start(self) -> PipelineRun:
        """Start a new pipeline run."""

        if self._run is not None:
            raise RuntimeError(
                "Pipeline run has already been started."
            )

        self._run = PipelineRun(
            run_id=str(uuid4()),
            pipeline_name=self._pipeline_name,
            status=PipelineRunStatus.RUNNING,
            started_at=datetime.now(timezone.utc),
        )

        return self._run

    def succeed(
        self,
        records_extracted: int = 0,
        records_processed: int = 0,
        records_rejected: int = 0,
    ) -> PipelineRun:
        """Mark the current pipeline run as successful."""

        self._ensure_started()

        self._validate_counts(
            records_extracted,
            records_processed,
            records_rejected,
        )

        self._run = PipelineRun(
            run_id=self._run.run_id,
            pipeline_name=self._run.pipeline_name,
            status=PipelineRunStatus.SUCCESS,
            started_at=self._run.started_at,
            completed_at=datetime.now(timezone.utc),
            records_extracted=records_extracted,
            records_processed=records_processed,
            records_rejected=records_rejected,
        )

        return self._run

    def fail(
        self,
        error_message: str,
        records_extracted: int = 0,
        records_processed: int = 0,
        records_rejected: int = 0,
    ) -> PipelineRun:
        """Mark the current pipeline run as failed."""

        self._ensure_started()

        if not error_message.strip():
            raise ValueError(
                "Error message must not be empty."
            )

        self._validate_counts(
            records_extracted,
            records_processed,
            records_rejected,
        )

        self._run = PipelineRun(
            run_id=self._run.run_id,
            pipeline_name=self._run.pipeline_name,
            status=PipelineRunStatus.FAILED,
            started_at=self._run.started_at,
            completed_at=datetime.now(timezone.utc),
            records_extracted=records_extracted,
            records_processed=records_processed,
            records_rejected=records_rejected,
            error_message=error_message,
        )

        return self._run

    def _ensure_started(self) -> None:
        if self._run is None:
            raise RuntimeError(
                "Pipeline run has not been started."
            )

    @staticmethod
    def _validate_counts(
        records_extracted: int,
        records_processed: int,
        records_rejected: int,
    ) -> None:
        counts = {
            "records_extracted": records_extracted,
            "records_processed": records_processed,
            "records_rejected": records_rejected,
        }

        for name, value in counts.items():
            if not isinstance(value, int):
                raise TypeError(
                    f"{name} must be an integer."
                )

            if value < 0:
                raise ValueError(
                    f"{name} must not be negative."
                )
