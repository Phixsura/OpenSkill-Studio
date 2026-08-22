"""Core module unit tests for coverage."""

from datetime import UTC
from unittest.mock import AsyncMock, patch

import pytest

# ── Logging ──────────────────────────────────────────────


def test_setup_logging_console():
    from app.core.logging import setup_logging

    setup_logging(level="DEBUG", fmt="console")


def test_setup_logging_json():
    from app.core.logging import setup_logging

    setup_logging(level="INFO", fmt="json")


# ── Email ────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_console_email_sender():
    from app.core.email import ConsoleEmailSender

    sender = ConsoleEmailSender()
    await sender.send("test@example.com", "Subject", "<p>Body</p>")


def test_get_email_sender():
    from app.core.email import get_email_sender

    sender = get_email_sender()
    assert sender is not None


# ── Rate Limit ───────────────────────────────────────────


@pytest.mark.asyncio
async def test_check_rate_limit_allowed():
    from app.core.rate_limit import check_rate_limit

    with patch("app.core.rate_limit.redis_pool") as mock_pool:
        mock_redis = AsyncMock()
        mock_pipe = AsyncMock()
        mock_pipe.execute = AsyncMock(return_value=[0, 2, True, True])
        mock_redis.pipeline.return_value.__aenter__ = AsyncMock(return_value=mock_pipe)
        mock_redis.pipeline.return_value.__aexit__ = AsyncMock()
        mock_pool.return_value = mock_redis

        allowed, remaining = await check_rate_limit("test:key", 10, 60)
        assert allowed is True


@pytest.mark.asyncio
async def test_check_rate_limit_redis_unavailable():
    from app.core.rate_limit import check_rate_limit

    with patch("app.core.rate_limit.redis_pool", side_effect=Exception("no redis")):
        allowed, remaining = await check_rate_limit("test:key", 10, 60)
        assert allowed is True  # fail-open


# ── LLM ──────────────────────────────────────────────────


def test_calculate_cost_anthropic_sonnet():
    from app.core.llm import LLMResponse, calculate_cost

    resp = LLMResponse(
        content="x",
        input_tokens=1_000_000,
        output_tokens=0,
        model="claude-sonnet-5",
        provider="anthropic",
    )
    cost = calculate_cost(resp)
    assert cost == 3.0


def test_calculate_cost_openai_mini():
    from app.core.llm import LLMResponse, calculate_cost

    resp = LLMResponse(
        content="x",
        input_tokens=1_000_000,
        output_tokens=1_000_000,
        model="gpt-4o-mini",
        provider="openai",
    )
    cost = calculate_cost(resp)
    assert cost == pytest.approx(0.75, abs=0.01)


def test_create_llm_client_anthropic():
    with patch.dict("os.environ", {}, clear=False):
        with patch("app.core.llm.settings") as mock_settings:
            mock_settings.llm_provider = "anthropic"
            mock_settings.anthropic_api_key = "test-key"
            mock_settings.llm_model = "claude-sonnet-5"

            from app.core.llm import create_llm_client

            client = create_llm_client()
            assert client is not None


def test_create_llm_client_openai():
    with patch("app.core.llm.settings") as mock_settings:
        mock_settings.llm_provider = "openai"
        mock_settings.openai_api_key = "test-key"
        mock_settings.llm_model = "gpt-4o"

        from app.core.llm import create_llm_client

        client = create_llm_client()
        assert client is not None


def test_create_llm_client_unknown():
    with patch("app.core.llm.settings") as mock_settings:
        mock_settings.llm_provider = "unknown"

        from app.core.llm import create_llm_client

        with pytest.raises(ValueError, match="Unknown LLM provider"):
            create_llm_client()


# ── Storage ──────────────────────────────────────────────


@pytest.mark.asyncio
async def test_ensure_bucket_exists():
    from app.core.storage import ensure_bucket

    client = AsyncMock()
    client.head_bucket = AsyncMock()  # bucket exists
    await ensure_bucket(client)
    client.head_bucket.assert_called_once()


@pytest.mark.asyncio
async def test_ensure_bucket_creates():
    from botocore.exceptions import ClientError

    from app.core.storage import ensure_bucket

    client = AsyncMock()
    error_response = {"Error": {"Code": "404", "Message": "Not Found"}}
    client.head_bucket = AsyncMock(
        side_effect=ClientError(error_response, "HeadBucket")
    )
    client.create_bucket = AsyncMock()
    await ensure_bucket(client)
    client.create_bucket.assert_called_once()


# ── Config ───────────────────────────────────────────────


def test_cors_origins_string_parse():
    from app.config import Settings

    s = Settings(cors_origins='["http://localhost:3000"]')
    assert s.cors_origins == ["http://localhost:3000"]


# ── Exceptions ───────────────────────────────────────────


def test_app_error():
    from app.exceptions import AppError

    err = AppError("TEST_CODE", "Test message", 400, ["detail1"])
    assert err.code == "TEST_CODE"
    assert err.message == "Test message"
    assert err.status_code == 400
    assert err.details == ["detail1"]


# ── User model properties ────────────────────────────────


def test_user_is_active():
    from unittest.mock import MagicMock

    from app.models.user import User, UserStatus

    user = MagicMock(spec=User)
    user.status = UserStatus.ACTIVE
    user.is_active = User.is_active.fget(user)  # type: ignore
    assert user.is_active is True


def test_user_has_password_false():
    from unittest.mock import MagicMock

    from app.models.user import User

    user = MagicMock(spec=User)
    user.password_hash = None
    assert User.has_password.fget(user) is False  # type: ignore


def test_user_has_password_true():
    from unittest.mock import MagicMock

    from app.models.user import User

    user = MagicMock(spec=User)
    user.password_hash = "$2b$12$test"
    assert User.has_password.fget(user) is True  # type: ignore


def test_refresh_token_is_revoked_false():
    from unittest.mock import MagicMock

    from app.models.user import RefreshToken

    token = MagicMock(spec=RefreshToken)
    token.revoked_at = None
    assert RefreshToken.is_revoked.fget(token) is False  # type: ignore


def test_refresh_token_is_revoked_true():
    from datetime import datetime
    from unittest.mock import MagicMock

    from app.models.user import RefreshToken

    token = MagicMock(spec=RefreshToken)
    token.revoked_at = datetime.now(UTC)
    assert RefreshToken.is_revoked.fget(token) is True  # type: ignore
