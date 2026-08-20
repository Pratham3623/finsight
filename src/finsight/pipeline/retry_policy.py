from dataclasses import dataclass
from typing import Type


@dataclass(frozen=True)
class RetryPolicy:
    """Define how pipeline failures should be retried."""

    max_attempts: int = 3
    retryable_exceptions: tuple[
        Type[Exception],
        ...
    ] = ()

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError(
                "max_attempts must be at least 1."
            )

        if not isinstance(
            self.retryable_exceptions,
            tuple,
        ):
            raise TypeError(
                "retryable_exceptions must be a tuple."
            )

    def should_retry(
        self,
        exception: Exception,
        attempt: int,
    ) -> bool:
        """Return whether another attempt should be made."""

        if attempt >= self.max_attempts:
            return False

        return isinstance(
            exception,
            self.retryable_exceptions,
        )
