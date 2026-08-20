from dataclasses import dataclass


@dataclass(frozen=True)
class PipelineMetrics:
    """Execution metrics for a pipeline run."""

    duration_seconds: float
    attempts: int
    records_extracted: int
    records_processed: int
    records_rejected: int

    def __post_init__(self) -> None:
        if self.duration_seconds < 0:
            raise ValueError(
                "duration_seconds must not be negative."
            )

        if self.attempts < 1:
            raise ValueError(
                "attempts must be at least 1."
            )

        counts = {
            "records_extracted": self.records_extracted,
            "records_processed": self.records_processed,
            "records_rejected": self.records_rejected,
        }

        for name, value in counts.items():
            if value < 0:
                raise ValueError(
                    f"{name} must not be negative."
                )
