"""Python SDK error class tests."""

import pytest
from openskill_sdk.errors import (
    OpenSkillError, ApiError, AuthError, NotFoundError,
    RateLimitError, ValidationError,
)

ERRORS = [
    (OpenSkillError, {"message": "test"}, 500),
    (ApiError, {"message": "bad", "code": "BAD", "status_code": 400}, 400),
    (AuthError, {}, 401),
    (NotFoundError, {}, 404),
    (RateLimitError, {}, 429),
    (ValidationError, {"message": "invalid"}, 422),
]

@pytest.mark.parametrize("cls,kwargs,expected_status", ERRORS, ids=lambda x: x.__name__ if hasattr(x, '__name__') else str(x))
def test_instantiation(cls, kwargs, expected_status):
    err = cls(**kwargs)
    assert err.status_code == expected_status

@pytest.mark.parametrize("cls,kwargs,expected_status", ERRORS, ids=lambda x: x.__name__ if hasattr(x, '__name__') else str(x))
def test_is_exception(cls, kwargs, expected_status):
    assert issubclass(cls, Exception)

@pytest.mark.parametrize("cls,kwargs,expected_status", ERRORS, ids=lambda x: x.__name__ if hasattr(x, '__name__') else str(x))
def test_has_message(cls, kwargs, expected_status):
    err = cls(**kwargs)
    assert str(err) != ""

def test_all_inherit_base():
    for cls in [ApiError, AuthError, NotFoundError, RateLimitError, ValidationError]:
        assert issubclass(cls, OpenSkillError)

def test_rate_limit_retry_after():
    err = RateLimitError(retry_after=120)
    assert err.retry_after == 120

def test_validation_details():
    err = ValidationError(message="bad", details=[{"field": "name"}])
    assert err.details == [{"field": "name"}]

def test_api_error_code():
    err = ApiError(message="x", code="INVALID", status_code=422)
    assert err.code == "INVALID"
