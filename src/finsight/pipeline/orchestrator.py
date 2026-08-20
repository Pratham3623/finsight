import time
from dataclasses import dataclass
from pathlib import Path

from finsight.logging.config import get_logger
from finsight.pipeline.local_etl import (
    PipelineResult,
    run_local_etl,
)
from finsight.pipeline.metrics import PipelineMetrics
from finsight.pipeline.retry_policy import RetryPolicy
from finsight.pipeline.run_error import PipelineRunError
from finsight.pipeline.run_history import RunHistoryStore
from finsight.pipeline.run_tracking import (
    PipelineRun,
    PipelineRunStatus,
)


logger = get_logger(__name__)


@dataclass(frozen=True)
class PipelineConfig:
    source_path: Path
    processed_path: Path
    rejected_path: Path
    run_history_path: Path = Path(
        "data/monitoring/run_history.jsonl"
    )


class PipelineOrchestrator:
    """Coordinate execution of the FinSight data pipeline."""

    def __init__(
        self,
        config: PipelineConfig,
        retry_policy: RetryPolicy | None = None,
    ) -> None:
        self.config = config
        self.retry_policy = retry_policy or RetryPolicy()

        self.history_store = RunHistoryStore(
            config.run_history_path
        )

    def run(self) -> PipelineResult:
        """Execute the configured FinSight pipeline with retries."""

        attempt = 1
        start_time = time.monotonic()

        logger.info(
            "Pipeline started: pipeline=local_financial_etl"
        )

        while True:
            logger.info(
                "Pipeline attempt started: "
                "pipeline=local_financial_etl "
                "attempt=%d",
                attempt,
            )

            try:
                result = run_local_etl(
                    source_path=self.config.source_path,
                    processed_path=self.config.processed_path,
                    rejected_path=self.config.rejected_path,
                )

                duration = time.monotonic() - start_time

                metrics = PipelineMetrics(
                    duration_seconds=duration,
                    attempts=attempt,
                    records_extracted=(
                        result.run.records_extracted
                    ),
                    records_processed=(
                        result.run.records_processed
                    ),
                    records_rejected=(
                        result.run.records_rejected
                    ),
                )

                result = PipelineResult(
                    schema_validation=result.schema_validation,
                    quality_report=result.quality_report,
                    processed_path=result.processed_path,
                    rejected_path=result.rejected_path,
                    run=result.run,
                    metrics=metrics,
                )

                self.history_store.append(
                    result.run
                )

                logger.info(
                    "Pipeline completed: "
                    "pipeline=local_financial_etl "
                    "attempt=%d "
                    "status=success "
                    "duration_seconds=%.3f "
                    "records_extracted=%d "
                    "records_processed=%d "
                    "records_rejected=%d",
                    attempt,
                    duration,
                    metrics.records_extracted,
                    metrics.records_processed,
                    metrics.records_rejected,
                )

                return result

            except PipelineRunError as exc:
                original_exception = (
                    exc.__cause__ or exc
                )

                if self.retry_policy.should_retry(
                    original_exception,
                    attempt,
                ):
                    logger.warning(
                        "Pipeline attempt failed; retrying: "
                        "pipeline=local_financial_etl "
                        "attempt=%d "
                        "error=%s",
                        attempt,
                        exc,
                    )

                    attempt += 1
                    continue

                self.history_store.append(
                    exc.run
                )

                duration = time.monotonic() - start_time

                logger.error(
                    "Pipeline failed: "
                    "pipeline=local_financial_etl "
                    "attempt=%d "
                    "status=failed "
                    "duration_seconds=%.3f "
                    "error=%s",
                    attempt,
                    duration,
                    exc,
                )

                raise original_exception

            except Exception as exc:
                if self.retry_policy.should_retry(
                    exc,
                    attempt,
                ):
                    logger.warning(
                        "Pipeline attempt failed; retrying: "
                        "pipeline=local_financial_etl "
                        "attempt=%d "
                        "error=%s",
                        attempt,
                        exc,
                    )

                    attempt += 1
                    continue

                duration = time.monotonic() - start_time

                logger.error(
                    "Pipeline failed: "
                    "pipeline=local_financial_etl "
                    "attempt=%d "
                    "status=failed "
                    "duration_seconds=%.3f "
                    "error=%s",
                    attempt,
                    duration,
                    exc,
                )

                raise
