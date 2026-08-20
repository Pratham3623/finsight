from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class PipelineRunStatus(str, Enum):
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


@dataclass(frozen=True)
class PipelineRun:
    run_id: str
    pipeline_name: str
    status: PipelineRunStatus
    started_at: datetime
    completed_at: datetime | None = None
    records_extracted: int = 0
    records_processed: int = 0
    records_rejected: int = 0
    error_message: str | None = None
