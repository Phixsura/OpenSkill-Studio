"""Unit tests for core modules."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


class TestLogging:
    def test_setup_logging_console(self):
        from app.core.logging import setup_logging
        setup_logging(level="DEBUG", fmt="console")

    def test_setup_logging_json(self):
        from app.core.logging import setup_logging
        setup_logging(level="INFO", fmt="json")


class TestEmail:
    @pytest.mark.asyncio
    async def test_console_email_sender(self):
        from app.core.email import ConsoleEmailSender
        sender = ConsoleEmailSender()
        await sender.send("to@test.com", "Subject", "<p>Body</p>")

    def test_get_email_sender_returns_console(self):
        from app.core.email import get_email_sender
        sender = get_email_sender()
        assert sender.__class__.__name__ == "ConsoleEmailSender"


class TestStorage:
    @pytest.mark.asyncio
    async def test_ensure_bucket_exists(self):
        from app.core.storage import ensure_bucket
        client = AsyncMock()
        client.head_bucket = AsyncMock()
        await ensure_bucket(client)
        client.head_bucket.assert_called_once()

    @pytest.mark.asyncio
    async def test_ensure_bucket_creates(self):
        from app.core.storage import ensure_bucket
        client = AsyncMock()
        client.head_bucket = AsyncMock(side_effect=Exception("Not found"))
        client.create_bucket = AsyncMock()
        await ensure_bucket(client)
        client.create_bucket.assert_called_once()


class TestLLM:
    def test_calculate_cost_anthropic(self):
        from app.core.llm import LLMResponse, calculate_cost
        resp = LLMResponse(content="x", input_tokens=1000, output_tokens=500,
                           model="claude-sonnet-5", provider="anthropic")
        cost = calculate_cost(resp)
        assert cost == pytest.approx(0.0105, abs=0.001)

    def test_calculate_cost_unknown(self):
        from app.core.llm import LLMResponse, calculate_cost
        resp = LLMResponse(content="x", input_tokens=100, output_tokens=50,
                           model="unknown", provider="unknown")
        assert calculate_cost(resp) == 0

    def test_create_llm_client_anthropic(self):
        from app.core.llm import AnthropicClient, create_llm_client
        with patch("app.config.settings") as s:
            s.llm_provider = "anthropic"
            s.anthropic_api_key = "key"
            s.llm_model = "claude-sonnet-5"
            assert isinstance(create_llm_client(), AnthropicClient)

    def test_create_llm_client_openai(self):
        from app.core.llm import OpenAIClient, create_llm_client
        with patch("app.config.settings") as s:
            s.llm_provider = "openai"
            s.openai_api_key = "key"
            s.llm_model = "gpt-4o"
            assert isinstance(create_llm_client(), OpenAIClient)

    def test_create_llm_client_invalid(self):
        from app.core.llm import create_llm_client
        with patch("app.config.settings") as s:
            s.llm_provider = "invalid"
            with pytest.raises(ValueError):
                create_llm_client()

    @pytest.mark.asyncio
    async def test_anthropic_client_complete(self):
        from app.core.llm import AnthropicClient
        client = AnthropicClient.__new__(AnthropicClient)
        client.model = "claude-sonnet-5"
        client.client = AsyncMock()
        mock_resp = MagicMock()
        mock_resp.content = [MagicMock(text="Hello")]
        mock_resp.usage.input_tokens = 10
        mock_resp.usage.output_tokens = 5
        client.client.messages.create = AsyncMock(return_value=mock_resp)
        result = await client.complete("system", "user")
        assert result.content == "Hello"
        assert result.provider == "anthropic"

    @pytest.mark.asyncio
    async def test_openai_client_complete(self):
        from app.core.llm import OpenAIClient
        client = OpenAIClient.__new__(OpenAIClient)
        client.model = "gpt-4o"
        client.client = AsyncMock()
        mock_choice = MagicMock()
        mock_choice.message.content = "Hello"
        mock_resp = MagicMock()
        mock_resp.choices = [mock_choice]
        mock_resp.usage.prompt_tokens = 10
        mock_resp.usage.completion_tokens = 5
        client.client.chat.completions.create = AsyncMock(return_value=mock_resp)
        result = await client.complete("system", "user")
        assert result.content == "Hello"

    @pytest.mark.asyncio
    async def test_openai_client_no_usage(self):
        from app.core.llm import OpenAIClient
        client = OpenAIClient.__new__(OpenAIClient)
        client.model = "gpt-4o"
        client.client = AsyncMock()
        mock_choice = MagicMock()
        mock_choice.message.content = "Hi"
        mock_resp = MagicMock()
        mock_resp.choices = [mock_choice]
        mock_resp.usage = None
        client.client.chat.completions.create = AsyncMock(return_value=mock_resp)
        result = await client.complete("s", "u")
        assert result.input_tokens == 0


class TestRateLimit:
    @pytest.mark.asyncio
    async def test_check_rate_limit_allowed(self):
        from app.core.rate_limit import check_rate_limit
        with patch("app.core.rate_limit.redis_pool") as mock_pool:
            mock_redis = AsyncMock()
            mock_pipe = AsyncMock()
            mock_pipe.execute = AsyncMock(return_value=[None, 0, None, None])
            mock_redis.pipeline.return_value.__aenter__ = AsyncMock(return_value=mock_pipe)
            mock_redis.pipeline.return_value.__aexit__ = AsyncMock()
            mock_pool.return_value = mock_redis
            allowed, remaining = await check_rate_limit("test", 10, 60)
            assert allowed is True

    @pytest.mark.asyncio
    async def test_check_rate_limit_denied(self):
        from app.core.rate_limit import check_rate_limit
        with patch("app.core.rate_limit.redis_pool") as mock_pool:
            mock_redis = AsyncMock()
            mock_pipe = AsyncMock()
            mock_pipe.execute = AsyncMock(return_value=[None, 10, None, None])
            mock_redis.pipeline.return_value.__aenter__ = AsyncMock(return_value=mock_pipe)
            mock_redis.pipeline.return_value.__aexit__ = AsyncMock()
            mock_pool.return_value = mock_redis
            allowed, _ = await check_rate_limit("test", 10, 60)
            assert allowed is False

    @pytest.mark.asyncio
    async def test_check_rate_limit_redis_unavailable(self):
        from app.core.rate_limit import check_rate_limit
        with patch("app.core.rate_limit.redis_pool", side_effect=Exception("No Redis")):
            allowed, _ = await check_rate_limit("test", 10, 60)
            assert allowed is True


class TestPasswords:
    def test_common_passwords_case_insensitive(self):
        from app.core.passwords import is_common_password
        assert is_common_password("PASSWORD")
        assert is_common_password("Qwerty")

    def test_not_common(self):
        from app.core.passwords import is_common_password
        assert not is_common_password("xK9#mL2$pQ7!")


class TestExceptions:
    def test_app_error(self):
        from app.exceptions import AppError
        err = AppError("CODE", "message", 400, ["detail"])
        assert err.code == "CODE"
        assert err.status_code == 400


class TestConfig:
    def test_parse_cors_string(self):
        from app.config import Settings
        result = Settings.parse_cors('["http://localhost:3000"]')
        assert result == ["http://localhost:3000"]

    def test_parse_cors_list(self):
        from app.config import Settings
        result = Settings.parse_cors(["http://localhost:3000"])
        assert result == ["http://localhost:3000"]


class TestUserModelProperties:
    def test_user_is_active(self):
        from app.models.user import User, UserStatus
        user = User.__new__(User)
        user.status = UserStatus.ACTIVE
        assert user.is_active is True
        user.status = UserStatus.SUSPENDED
        assert user.is_active is False

    def test_user_has_password(self):
        from app.models.user import User
        user = User.__new__(User)
        user.password_hash = None
        assert user.has_password is False
        user.password_hash = "$2b$12$..."
        assert user.has_password is True

    def test_refresh_token_is_revoked(self):
        from datetime import datetime, timezone
        from app.models.user import RefreshToken
        token = RefreshToken.__new__(RefreshToken)
        token.revoked_at = None
        assert token.is_revoked is False
        token.revoked_at = datetime.now(timezone.utc)
        assert token.is_revoked is True
