import pytest

from finsight.pipeline.retry_policy import RetryPolicy


def test_retry_policy_defaults_to_three_attempts():
    policy = RetryPolicy()

    assert policy.max_attempts == 3
    assert policy.retryable_exceptions == ()


def test_retry_policy_rejects_zero_attempts():
    with pytest.raises(ValueError):
        RetryPolicy(max_attempts=0)


def test_retry_policy_rejects_negative_attempts():
    with pytest.raises(ValueError):
        RetryPolicy(max_attempts=-1)


def test_retry_policy_requires_tuple():
    with pytest.raises(TypeError):
        RetryPolicy(
            retryable_exceptions=[TimeoutError],
        )


def test_retry_policy_retries_matching_exception():
    policy = RetryPolicy(
        max_attempts=3,
        retryable_exceptions=(TimeoutError,),
    )

    assert policy.should_retry(
        TimeoutError(),
        attempt=1,
    )

    assert policy.should_retry(
        TimeoutError(),
        attempt=2,
    )


def test_retry_policy_stops_at_max_attempts():
    policy = RetryPolicy(
        max_attempts=3,
        retryable_exceptions=(TimeoutError,),
    )

    assert not policy.should_retry(
        TimeoutError(),
        attempt=3,
    )


def test_retry_policy_does_not_retry_non_retryable_exception():
    policy = RetryPolicy(
        max_attempts=3,
        retryable_exceptions=(TimeoutError,),
    )

    assert not policy.should_retry(
        ValueError(),
        attempt=1,
    )


def test_retry_policy_supports_exception_subclasses():
    policy = RetryPolicy(
        max_attempts=3,
        retryable_exceptions=(OSError,),
    )

    assert policy.should_retry(
        FileNotFoundError(),
        attempt=1,
    )


def test_retry_policy_does_not_retry_after_max_attempts():
    policy = RetryPolicy(
        max_attempts=2,
        retryable_exceptions=(TimeoutError,),
    )

    assert policy.should_retry(
        TimeoutError(),
        attempt=1,
    )

    assert not policy.should_retry(
        TimeoutError(),
        attempt=2,
    )


def test_retry_policy_max_attempts_one_never_retries():
    policy = RetryPolicy(
        max_attempts=1,
        retryable_exceptions=(TimeoutError,),
    )

    assert not policy.should_retry(
        TimeoutError(),
        attempt=1,
    )


def test_retry_policy_empty_retryable_exceptions_never_retries():
    policy = RetryPolicy(
        max_attempts=5,
    )

    assert not policy.should_retry(
        TimeoutError(),
        attempt=1,
    )


def test_retry_policy_multiple_exception_types():
    policy = RetryPolicy(
        max_attempts=3,
        retryable_exceptions=(
            TimeoutError,
            ConnectionError,
        ),
    )

    assert policy.should_retry(
        TimeoutError(),
        attempt=1,
    )

    assert policy.should_retry(
        ConnectionError(),
        attempt=1,
    )

    assert not policy.should_retry(
        ValueError(),
        attempt=1,
    )
