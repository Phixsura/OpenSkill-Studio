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
    client.head_bucket = AsyncMock(side_effect=ClientError(error_response, "HeadBucket"))
    client.create_bucket = AsyncMock()
    await ensure_bucket(client)
    client.create_bucket.assert_called_once()


# ── Config ───────────────────────────────────────────────


def test_cors_origins_string_parse():
    from app.config import Settings

    s = Settings(cors_origins='["http://localhost:3000"]')
    assert s.cors_origins == ["http://localhost:3000"]


def test_cors_wildcard_refused_in_production():
    """R189: the app runs CORS with allow_credentials=True — starlette then
    ECHOES the request Origin for a wildcard entry, so CORS_ORIGINS='["*"]'
    silently granted every website credentialed API access (any page could
    hit /auth/refresh with the visitor's httpOnly cookie). Production boot
    must refuse the wildcard, same guard family as jwt_secret."""
    import pytest as _pytest
    from pydantic import ValidationError

    from app.config import Settings

    with _pytest.raises(ValidationError, match="wildcard"):
        Settings(
            app_env="production",
            cors_origins='["*"]',
            jwt_secret="x" * 64,
            s3_secret_key="real-secret",
            database_url="postgresql+asyncpg://app:secret@db/prod",
            credential_encryption_key="",
            domain_verifier="dns",
        )
    # Dev keeps the convenience
    assert Settings(app_env="development", cors_origins='["*"]').cors_origins == ["*"]


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


@pytest.mark.asyncio
async def test_rate_limit_keys_on_route_template_not_concrete_path():
    """R75b: the bucket key must use the ROUTE TEMPLATE, not the concrete URL —
    keying on request.url.path let each distinct high-cardinality path-param
    value (e.g. {project_id}, {pack_id}) mint its own bucket, bypassing the
    limit (an endpoint could be hit limit×N for N accessible resources). Two
    requests to the SAME route template with DIFFERENT path-param values must
    resolve to the SAME rate-limit key."""
    from unittest.mock import AsyncMock, MagicMock, patch

    from app.core.rate_limit import rate_limit

    captured_keys = []

    async def _fake_check(key, limit, window):
        captured_keys.append(key)
        return True, limit

    def _req(concrete_path, template):
        r = MagicMock()
        r.client = MagicMock()
        r.client.host = "10.0.0.1"
        r.method = "GET"
        r.url = MagicMock()
        r.url.path = concrete_path
        route = MagicMock()
        route.path = template
        r.scope = {"route": route}
        r.state = MagicMock()
        return r

    checker = rate_limit(10, 60)
    template = "/orgs/{org_id}/projects/{project_id}/creator-shortlist"
    with (
        patch("app.core.rate_limit.settings") as mock_settings,
        patch("app.core.rate_limit.check_rate_limit", new=AsyncMock(side_effect=_fake_check)),
    ):
        mock_settings.app_env = "production"
        mock_settings.trusted_proxy_hops = 0  # R78b: identity resolution reads it
        await checker(_req("/orgs/O1/projects/P1/creator-shortlist", template))
        await checker(_req("/orgs/O1/projects/P2/creator-shortlist", template))

    assert len(captured_keys) == 2
    assert captured_keys[0] == captured_keys[1], (
        f"different path-param values got different buckets: {captured_keys}"
    )
    # And the key uses the template, not either concrete path
    assert "{project_id}" in captured_keys[0]
    assert "/P1/" not in captured_keys[0] and "/P2/" not in captured_keys[0]


@pytest.mark.asyncio
async def test_email_log_redacts_tokens_outside_dev(monkeypatch):
    """R191 (CWE-532): ConsoleEmailSender logged body_preview — reset/verify
    emails embed SINGLE-USE auth tokens, so a production log line was an
    account-takeover primitive for anyone with log access; the raw recipient
    also violated the codebase's email_hash convention. Outside dev/test the
    log must carry neither the body nor the plaintext address."""
    import structlog

    from app.config import settings as app_settings
    from app.core.email import ConsoleEmailSender

    captured: list[dict] = []

    def capture(logger, method, event_dict):
        captured.append(dict(event_dict))
        raise structlog.DropEvent

    structlog.configure(processors=[capture])
    try:
        sender = ConsoleEmailSender()
        secret_html = '<a href="https://x/reset-password?token=SECRET_TOKEN_ABC">reset</a>'

        monkeypatch.setattr(app_settings, "app_env", "production")
        await sender.send(to="victim@example.com", subject="Reset", html=secret_html)
        prod = captured[-1]
        flat = str(prod)
        assert "SECRET_TOKEN_ABC" not in flat, "token leaked into production log"
        assert "victim@example.com" not in flat, "plaintext email in production log"
        assert prod.get("to_hash"), "hashed recipient expected"

        monkeypatch.setattr(app_settings, "app_env", "development")
        await sender.send(to="dev@example.com", subject="Reset", html=secret_html)
        dev = captured[-1]
        assert "SECRET_TOKEN_ABC" in str(dev), "dev console IS the delivery mechanism"
    finally:
        structlog.reset_defaults()


# ── R239: gamification level + duplicate slug/name + sanitize (pure) ──


def test_compute_level_thresholds():
    from app.services.gamification import _compute_level

    assert _compute_level(0) == 1
    assert _compute_level(99) == 1
    assert _compute_level(100) == 2
    assert _compute_level(250) == 3
    assert _compute_level(-50) == 1          # never below level 1
    # monotonic non-decreasing
    prev = 0
    for pts in range(0, 2000, 37):
        lvl = _compute_level(pts)
        assert lvl >= prev
        prev = lvl


def test_duplicate_slug_and_name_survive_max_length():
    """R89: a base already at VARCHAR(200)/name max must keep its uniqueness
    suffix (slug) / fit the column (name) — else duplicate 500s on the
    unique index / string-truncation."""
    from app.services.duplicate import _copy_name, _dup_slug

    long_slug = "s" * 250
    dup = _dup_slug(long_slug)
    assert len(dup) <= 200
    assert "-copy-" in dup                       # suffix survived the trim
    # re-duplicating strips the prior -copy- marker (no unbounded growth)
    again = _dup_slug(dup)
    assert len(again) <= 200 and again.count("-copy-") == 1

    long_name = "n" * 200
    cp = _copy_name(long_name, 200)
    assert len(cp) <= 200 and cp.endswith(" (Copy)")
    # short name just gets the suffix appended
    assert _copy_name("Skill", 200) == "Skill (Copy)"


def test_sanitize_length_bound_and_prefslice():
    from app.core.sanitize import sanitize_untrusted_text

    assert sanitize_untrusted_text("", 100) == ""
    assert len(sanitize_untrusted_text("x" * 5000, 100)) == 100
    # a hostile multi-MB string is pre-sliced before NFKC (no seconds of CPU)
    huge = "a" * 10_000_000
    out = sanitize_untrusted_text(huge, 50)
    assert len(out) == 50
