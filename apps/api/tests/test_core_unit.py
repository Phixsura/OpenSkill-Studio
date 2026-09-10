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


def test_comfyui_infinity_field_does_not_discard_whole_result():
    """R240: `"steps": Infinity` made int() raise OverflowError — not in the
    inner except tuple — so the outer fail-closed handler discarded ALL
    metadata. One hostile field must skip only itself."""
    import json

    from app.core.genmeta import parse_comfyui_prompt

    wf = {
        "3": {
            "class_type": "KSampler",
            "inputs": {"steps": 1e999, "cfg": 7.5, "seed": 42, "sampler_name": "euler"},
        },
    }
    out = parse_comfyui_prompt(json.dumps(wf))  # serializes as Infinity
    assert out is not None
    assert "steps" not in out                    # hostile field skipped
    assert out["cfg_scale"] == 7.5 and out["seed"] == 42 and out["sampler"] == "euler"


# ── R249: parser kill-tests (mutation-driven — 39/41 genmeta mutants lived) ──
# Post-wave status (green-baseline rerun after the R250 fix landed):
# genmeta 40/41, gamification 3/3, duplicate 8/9, sanitize 1/2. All three
# survivors are equivalent: genmeta's settings-walk range stop -1→-2 only
# adds an i=-1 revisit of the last line, reachable when nothing matched
# anyway; sanitize's pre-slice multiplier 8→9 only widens the DoS bound
# before the final [:max_len] clamp; _copy_name's <=→< sends an exact-fit
# name down the trim path, which reproduces name+suffix byte-for-byte.


def test_a1111_exact_extraction():
    """Pin the a1111 parser's structure: settings-line detection walks from
    the END, values clamp to the int8 window, strings truncate at 200."""
    from app.core.genmeta import parse_a1111_infotext

    txt = (
        "a castle at dawn\n"
        "Negative prompt: blurry, lowres\n"
        "Steps: 30, Sampler: Euler a, CFG scale: 4.5, Seed: 123, Size: 832x1216"
    )
    out = parse_a1111_infotext(txt)
    assert out is not None
    assert out["prompt"] == "a castle at dawn"
    assert out["negative_prompt"] == "blurry, lowres"
    assert out["steps"] == 30 and out["seed"] == 123 and out["cfg_scale"] == 4.5
    assert out["sampler"] == "Euler a"

    # int8-window clamp: 2**63-1 kept, 2**63 dropped, mirror for negatives
    hi = parse_a1111_infotext(f"p\nSteps: 20, Seed: {2**63 - 1}")
    assert hi is not None and hi["seed"] == 2**63 - 1
    over = parse_a1111_infotext(f"p\nSteps: 20, Seed: {2**63}")
    assert over is not None and "seed" not in over
    lo = parse_a1111_infotext(f"p\nSteps: 20, Seed: {-(2**63) + 1}")
    assert lo is not None and lo["seed"] == -(2**63) + 1
    under = parse_a1111_infotext(f"p\nSteps: 20, Seed: {-(2**63)}")
    assert under is not None and "seed" not in under

    # sampler string truncates at exactly 200
    long_sampler = "S" * 300
    t = parse_a1111_infotext(f"p\nSteps: 20, Sampler: {long_sampler}")
    assert t is not None and len(t["sampler"]) == 200

    # no settings line and no negative → not a1111 evidence
    assert parse_a1111_infotext("just some text\nmore text") is None
    # empty text rejected
    assert parse_a1111_infotext("") is None


def test_comfyui_exact_extraction():
    """Pin the ComfyUI parser: int8 window on node inputs, 200-char sampler
    truncation, first/second CLIPTextEncode → prompt/negative ordering."""
    import json

    from app.core.genmeta import MAX_COMFY_JSON, parse_comfyui_prompt

    wf = {
        "1": {"class_type": "KSampler",
              "inputs": {"seed": 2**63 - 1, "steps": 25, "cfg": 7.0,
                          "sampler_name": "x" * 300}},
        "2": {"class_type": "CLIPTextEncode", "inputs": {"text": "hero shot"}},
        "3": {"class_type": "CLIPTextEncode", "inputs": {"text": "ugly"}},
    }
    out = parse_comfyui_prompt(json.dumps(wf))
    assert out is not None
    assert out["seed"] == 2**63 - 1 and out["steps"] == 25
    assert len(out["sampler"]) == 200
    assert out["prompt"] == "hero shot" and out["negative_prompt"] == "ugly"

    # int8 overflow dropped field-locally (R240 companion)
    wf["1"]["inputs"]["seed"] = 2**63
    out2 = parse_comfyui_prompt(json.dumps(wf))
    assert out2 is not None and "seed" not in out2 and out2["steps"] == 25
    wf["1"]["inputs"]["seed"] = -(2**63)
    out3 = parse_comfyui_prompt(json.dumps(wf))
    assert out3 is not None and "seed" not in out3

    # size guard: exactly at the cap parses, one over is rejected
    pad_needed = MAX_COMFY_JSON - len(json.dumps(wf))
    wf["2"]["inputs"]["text"] = "hero shot" + " " * 0
    doc = json.dumps(wf)
    padded = doc + " " * (MAX_COMFY_JSON - len(doc))
    assert len(padded) == MAX_COMFY_JSON
    assert parse_comfyui_prompt(padded) is not None
    assert parse_comfyui_prompt(padded + " ") is None
    assert pad_needed > 0


def test_sanitize_default_and_dup_suffix_format():
    """R249: sanitize's default max_len is part of its contract (1000), and
    _dup_slug's suffix is exactly '-copy-' + 6 hex chars (3 random bytes)."""
    import re

    from app.core.sanitize import sanitize_untrusted_text
    from app.services.duplicate import _dup_slug

    assert len(sanitize_untrusted_text("y" * 5000)) == 1000
    assert re.search(r"-copy-[0-9a-f]{6}$", _dup_slug("my-skill"))


def test_parser_edge_kill_set():
    """R249 second wave: reverse-walk step, unknown settings key, minimal-
    evidence gates, bounded node scan, first-KSampler-wins, non-str text,
    single CLIPText, and the exact size caps."""
    import json

    from app.core.genmeta import MAX_TOTAL_TEXT, parse_a1111_infotext
    from app.core.genmeta import parse_comfyui_prompt as pc

    # settings line SECOND-TO-LAST: a step<-1 walk skips odd offsets
    out = parse_a1111_infotext("p\nSteps: 20, Seed: 5\ntrailing")
    assert out is not None and out["steps"] == 20

    # unknown key on the settings line must be skipped, not KeyError the parse
    out = parse_a1111_infotext("p\nSteps: 20, Wizardry: max")
    assert out is not None and out["steps"] == 20

    # single-field settings-only line is still evidence (2 keys > 1)
    out = parse_a1111_infotext("Steps: 20")
    assert out is not None and out["steps"] == 20
    # a settings-only line with nothing parseable is not evidence (R250:
    # it no longer leaks the whole text into `prompt` via the 0-falsy bug)
    assert parse_a1111_infotext("Steps: garbage") is None
    # negative-marker alone yields nothing extractable → no evidence → None
    assert parse_a1111_infotext("Negative prompt:") is None

    # R250: infotext STARTING with the negative marker (no positive prompt)
    # must not fall into the whole-text prompt fallback
    out = parse_a1111_infotext("Negative prompt: blurry\nSteps: 20, Seed: 5")
    assert out is not None
    assert "prompt" not in out
    assert out["negative_prompt"] == "blurry" and out["steps"] == 20

    # exactly at the text cap parses; one over is rejected
    base = "p\nSteps: 20, Seed: 5"
    doc = base + " " * (MAX_TOTAL_TEXT - len(base))
    assert parse_a1111_infotext(doc) is not None
    assert parse_a1111_infotext(doc + " ") is None

    # comfy: bounded scan reads exactly 200 nodes — a KSampler at #201 is out
    graph = {str(i): {"class_type": "Note", "inputs": {}} for i in range(199)}
    graph["clip"] = {"class_type": "CLIPTextEncode", "inputs": {"text": "p"}}
    graph["late"] = {"class_type": "KSampler", "inputs": {"steps": 9}}
    out = pc(json.dumps(graph))
    assert out is not None and out["prompt"] == "p" and "steps" not in out

    # first KSampler wins; a second must not overwrite
    two = {
        "1": {"class_type": "KSampler", "inputs": {"steps": 11}},
        "2": {"class_type": "KSampler", "inputs": {"steps": 22}},
    }
    assert pc(json.dumps(two))["steps"] == 11

    # non-str CLIPText text is skipped, not crashed into a None result
    mixed = {
        "1": {"class_type": "KSampler", "inputs": {"steps": 7}},
        "2": {"class_type": "CLIPTextEncode", "inputs": {"text": 123}},
    }
    assert pc(json.dumps(mixed))["steps"] == 7

    # single CLIPText → prompt only, no negative, no IndexError
    single = {"2": {"class_type": "CLIPTextEncode", "inputs": {"text": "solo"}}}
    out = pc(json.dumps(single))
    assert out is not None and out["prompt"] == "solo" and "negative_prompt" not in out

    # a graph with nothing extractable is not evidence
    assert pc(json.dumps({"1": {"class_type": "Note", "inputs": {}}})) is None
