import time
from dataclasses import dataclass
from typing import Callable

from finsight.logging.config import get_logger


logger = get_logger(__name__)


@dataclass(frozen=True)
class SchedulerConfig:
    interval_seconds: float
    max_runs: int | None = None

    def __post_init__(self) -> None:
        if self.interval_seconds <= 0:
            raise ValueError(
                "interval_seconds must be greater than zero."
            )

        if (
            self.max_runs is not None
            and self.max_runs <= 0
        ):
            raise ValueError(
                "max_runs must be greater than zero."
            )


class PipelineScheduler:
    """Execute a pipeline on a configurable schedule."""

    def __init__(
        self,
        job: Callable[[], object],
        config: SchedulerConfig,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self.job = job
        self.config = config
        self.sleep = sleep

    def run(self) -> int:
        """Run the scheduled job.

        Returns the number of executions performed.
        """

        executions = 0

        while (
            self.config.max_runs is None
            or executions < self.config.max_runs
        ):
            executions += 1

            logger.info(
                "Scheduled pipeline execution started: "
                "execution=%d",
                executions,
            )

            try:
                self.job()

                logger.info(
                    "Scheduled pipeline execution completed: "
                    "execution=%d",
                    executions,
                )

            except Exception:
                logger.exception(
                    "Scheduled pipeline execution failed: "
                    "execution=%d",
                    executions,
                )

                if self.config.max_runs is None:
                    raise

            if (
                self.config.max_runs is None
                or executions < self.config.max_runs
            ):
                logger.info(
                    "Waiting before next scheduled execution: "
                    "interval_seconds=%.3f",
                    self.config.interval_seconds,
                )

                self.sleep(
                    self.config.interval_seconds
                )

        return executions
