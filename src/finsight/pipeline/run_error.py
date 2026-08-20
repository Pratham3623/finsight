from finsight.pipeline.run_tracking import PipelineRun


class PipelineRunError(Exception):
    """Exception raised when a pipeline execution fails."""

    def __init__(
        self,
        message: str,
        run: PipelineRun,
    ) -> None:
        super().__init__(message)
        self.run = run

