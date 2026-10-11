"""Integration fabric P1 unit tests — egress guard, config validator, API auth.

No DB required (egress + validator are pure; API tests only reach auth).
"""

import socket

import pytest
import pytest_asyncio

from app.integrations.security import (
    EgressBlockedError,
    EgressClient,
    validate_egress_url,
)


@pytest_asyncio.fixture(autouse=True)
async def _dispose_engine_pool():
    """The SCIM protocol tests below reach the DB through the HTTP client on
    THIS test's event loop; without a dispose the pooled connection outlives
    the loop and poisons the NEXT file's first DB test ("Event loop is
    closed" — same class as the known cross-file ordering flake)."""
    yield
    from app.core.database import engine

    await engine.dispose()


# ── validate_egress_url matrix (ADR-018 §14.1) ──

BLOCKED_URLS = [
    "",  # empty
    "ftp://example.com/x",  # scheme
    "gopher://example.com/",  # scheme
    "https://user:pw@example.com/",  # userinfo
    "https://example.com:6379/",  # port
    "https://",  # no host
    "https://localhost/hook",  # internal name
    "https://svc.internal/hook",  # blocked TLD
    "https://box.local/hook",  # blocked TLD
    "https://127.0.0.1/hook",  # loopback literal
    "https://10.1.2.3/hook",  # private literal
    "https://172.16.0.9/hook",  # private literal
    "https://192.168.1.1/hook",  # private literal
    "https://169.254.169.254/latest/meta-data",  # metadata
    "https://100.64.0.7/hook",  # CGNAT
    "https://[::1]/hook",  # v6 loopback
    "https://[fc00::1]/hook",  # v6 ULA
    "https://[::ffff:10.0.0.1]/hook",  # v4-mapped v6
    "https://0.0.0.0/hook",  # unspecified
    "http://example.com/hook",  # plain http outside test-private mode
    "https://example.com/" + "a" * 500,  # too long
]


@pytest.mark.parametrize("url", BLOCKED_URLS)
def test_validate_egress_url_blocks(url, monkeypatch):
    from app.config import settings

    monkeypatch.setattr(settings, "egress_allow_private", False)
    with pytest.raises(EgressBlockedError):
        validate_egress_url(url)


@pytest.mark.parametrize(
    "url",
    [
        "https://hooks.example.com/deliver",
        "https://api.example.com:8443/v1/ping",
        "https://example.com/path?x=1",
    ],
)
def test_validate_egress_url_allows_public(url, monkeypatch):
    from app.config import settings

    monkeypatch.setattr(settings, "egress_allow_private", False)
    assert validate_egress_url(url) == url


def test_test_mode_allows_localhost(monkeypatch):
    """E2E suites hit localhost — only via the explicit test flag (R79)."""
    from app.config import settings

    monkeypatch.setattr(settings, "egress_allow_private", True)
    assert validate_egress_url("http://localhost:8080/hook")


# ── request-time pinning (rebinding defense) ──


def _fake_getaddrinfo(ip):
    def fake(host, port, **kw):
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", (ip, port))]

    return fake


@pytest.mark.asyncio
async def test_request_blocks_private_resolution(monkeypatch):
    """A public-looking hostname resolving to a private IP is refused at
    dispatch time — registration-time validation alone can't stop a TTL flip."""
    from app.config import settings

    monkeypatch.setattr(settings, "egress_allow_private", False)
    monkeypatch.setattr(socket, "getaddrinfo", _fake_getaddrinfo("10.0.0.5"))
    with pytest.raises(EgressBlockedError):
        await EgressClient().request("POST", "https://rebind.example.com/hook")


@pytest.mark.asyncio
async def test_request_pins_resolved_ip(monkeypatch):
    """The client dials the validated literal IP with Host+SNI set to the
    hostname — no second resolution happens between check and connect."""
    import httpx

    from app.config import settings

    monkeypatch.setattr(settings, "egress_allow_private", False)
    monkeypatch.setattr(socket, "getaddrinfo", _fake_getaddrinfo("93.184.216.34"))

    captured = {}

    async def fake_request(self, method, url, headers=None, content=None, extensions=None):
        captured["url"] = str(url)
        captured["headers"] = dict(headers or {})
        captured["extensions"] = dict(extensions or {})
        return httpx.Response(200, request=httpx.Request(method, url))

    monkeypatch.setattr(httpx.AsyncClient, "request", fake_request)
    resp = await EgressClient().request("POST", "https://hooks.example.com/deliver?a=1")
    assert resp.status_code == 200
    assert captured["url"] == "https://93.184.216.34:443/deliver?a=1"
    assert captured["headers"]["Host"] == "hooks.example.com"
    assert captured["extensions"]["sni_hostname"] == "hooks.example.com"


@pytest.mark.asyncio
async def test_request_mixed_resolution_blocked(monkeypatch):
    """Mixed public+private DNS answers are an attack, not a CDN."""
    from app.config import settings

    monkeypatch.setattr(settings, "egress_allow_private", False)

    def fake(host, port, **kw):
        return [
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", port)),
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("192.168.0.10", port)),
        ]

    monkeypatch.setattr(socket, "getaddrinfo", fake)
    with pytest.raises(EgressBlockedError):
        await EgressClient().request("GET", "https://cdn.example.com/x")


# ── config boot guard ──


def test_egress_allow_private_refused_outside_test():
    from pydantic import ValidationError

    from app.config import Settings

    with pytest.raises(ValidationError):
        Settings(app_env="production", egress_allow_private=True)


# ── single-egress-path lint (ADR-018 §2.3) ──


def test_no_direct_httpx_outside_security_module():
    """Every outbound HTTP call in app/integrations must ride EgressClient."""
    from pathlib import Path

    pkg = Path(__file__).resolve().parents[1] / "app" / "integrations"
    offenders = []
    for py in pkg.rglob("*.py"):
        if py.name == "security.py":
            continue
        text = py.read_text()
        if "import httpx" in text or "from httpx" in text:
            offenders.append(str(py))
    assert offenders == [], f"direct httpx use outside security.py: {offenders}"


# ── provider/connector registry parity (§13) ──

def test_connector_registry_matches_catalog():
    from app.integrations.registry import CONNECTORS, PROVIDER_CATALOG

    assert set(CONNECTORS) == set(PROVIDER_CATALOG)
    for key, spec in PROVIDER_CATALOG.items():
        assert set(spec["capabilities"]) == set(CONNECTORS[key].capabilities), key


# ── API auth surface (no DB: 401 before any query) ──


@pytest.mark.asyncio
async def test_endpoints_require_auth(client):
    org = "01JARZZZZZZZZZZZZZZZZZZZZZ"
    for method, path in [
        ("GET", f"/api/v1/orgs/{org}/integrations/providers"),
        ("GET", f"/api/v1/orgs/{org}/integrations/connections"),
        ("POST", f"/api/v1/orgs/{org}/integrations/connections"),
        ("GET", f"/api/v1/orgs/{org}/integrations/connections/x"),
        ("PATCH", f"/api/v1/orgs/{org}/integrations/connections/x"),
        ("DELETE", f"/api/v1/orgs/{org}/integrations/connections/x"),
        ("POST", f"/api/v1/orgs/{org}/integrations/connections/x/credentials"),
        ("POST", f"/api/v1/orgs/{org}/integrations/connections/x/ping"),
    ]:
        resp = await client.request(method, path)
        assert resp.status_code == 401, (method, path, resp.status_code)


# ── credential response shape is the full allowlist (R82 pattern) ──


def test_credential_response_fields_are_exactly_the_allowlist():
    from app.integrations.schemas import CredentialResponse

    assert set(CredentialResponse.model_fields) == {"id", "kind", "expires_at", "rotated_at"}


def test_connection_response_has_no_secret_fields():
    from app.integrations.schemas import ConnectionResponse

    forbidden = {"ciphertext", "secret", "values", "token", "credential"}
    assert not (set(ConnectionResponse.model_fields) & forbidden)


# ── SCIM protocol surface (no DB for discovery; 401 shape) ──


@pytest.mark.asyncio
async def test_scim_discovery_endpoints(client):
    resp = await client.get("/api/v1/scim/v2/ServiceProviderConfig")
    assert resp.status_code == 200
    body = resp.json()
    assert body["bulk"] == {
        "supported": True,
        "maxOperations": 100,
        "maxPayloadSize": 1_048_576,
    }  # R52
    assert body["patch"]["supported"] is True
    rt = await client.get("/api/v1/scim/v2/ResourceTypes")
    assert {r["id"] for r in rt.json()["Resources"]} == {"User", "Group"}


@pytest.mark.asyncio
async def test_scim_requires_bearer_with_scim_error_shape(client):
    resp = await client.get("/api/v1/scim/v2/Users")
    assert resp.status_code == 401
    body = resp.json()
    assert body["schemas"] == ["urn:ietf:params:scim:api:messages:2.0:Error"]
    assert body["status"] == "401"
    # never the app envelope
    assert "error" not in body


def test_every_protocol_route_is_rate_limited():
    """R25 guard: unauthenticated protocol surfaces (SSO/SAML/OIDC, SCIM,
    LTI) must each carry a rate_limit dependency — a new route added without
    one is a state-mint flood / token brute-force vector (R21)."""
    from starlette.routing import Mount

    from app.main import app as fastapi_app

    def walk(routes, prefix=""):
        for r in routes:
            if isinstance(r, Mount):
                yield from walk(r.routes, prefix + r.path)
            elif hasattr(r, "original_router"):  # fastapi _IncludedRouter wrapper
                yield from walk(r.original_router.routes, prefix)
            else:
                yield prefix + getattr(r, "path", ""), r

    protocol = [
        (p, r)
        for p, r in walk(fastapi_app.routes)
        if p.startswith(("/sso", "/scim/v2", "/lti"))
    ]
    assert len(protocol) >= 20, "guard went vacuous — protocol prefixes moved?"
    missing = [
        p
        for p, r in protocol
        if not any(
            getattr(d.dependency, "__qualname__", "").startswith("rate_limit.")
            for d in (getattr(r, "dependencies", None) or [])
        )
    ]
    assert missing == [], f"protocol routes without rate_limit: {missing}"


def test_forbidden_ip_classification_matrix():
    """R27 mutation probe: every reserved-range clause must be load-bearing."""
    from app.integrations.security import _is_forbidden_ip

    forbidden = [
        "10.1.2.3",            # private
        "127.0.0.1",           # loopback
        "169.254.169.254",     # link-local (cloud metadata)
        "224.0.0.1",           # multicast
        "240.0.0.1",           # reserved
        "0.0.0.0",             # unspecified
        "100.64.0.1",          # carrier-grade NAT
        "::1",                 # v6 loopback
        "::",                  # v6 unspecified
        "fe80::1",             # v6 link-local
        "ff02::1",             # v6 multicast
        "fc00::1",             # v6 ULA (private)
        "::ffff:10.0.0.1",     # IPv4-mapped v6 smuggling a private v4
        "::ffff:127.0.0.1",    # IPv4-mapped loopback
        "not-an-ip",           # unparseable is forbidden, not ignored
    ]
    for ip in forbidden:
        assert _is_forbidden_ip(ip), ip
    for ip in ("8.8.8.8", "1.1.1.1", "2607:f8b0::1", "::ffff:8.8.8.8"):
        assert not _is_forbidden_ip(ip), ip


def test_mixed_resolution_set_is_refused_and_first_addr_returned(monkeypatch):
    """A hostname resolving to {public, private} is an attack (DNS pinning
    games) — refused outright, never 'skip to the public one'. An all-public
    set returns the FIRST address (the one that gets dialed)."""
    import socket as _socket

    from app.config import settings
    from app.integrations.security import EgressBlockedError, _resolve_and_validate

    monkeypatch.setattr(settings, "egress_allow_private", False)

    def fake(host, port, proto=0):
        return [
            (2, 1, 6, "", ("93.184.216.34", 443)),
            (2, 1, 6, "", ("10.0.0.5", 443)),
        ]

    monkeypatch.setattr(_socket, "getaddrinfo", fake)
    with pytest.raises(EgressBlockedError):
        _resolve_and_validate("evil.example.com", 443)

    def fake_pub(host, port, proto=0):
        return [
            (2, 1, 6, "", ("93.184.216.34", 443)),
            (2, 1, 6, "", ("93.184.216.35", 443)),
        ]

    monkeypatch.setattr(_socket, "getaddrinfo", fake_pub)
    assert _resolve_and_validate("ok.example.com", 443) == "93.184.216.34"


def test_egress_trailing_dot_and_mapped_literal(monkeypatch):
    """FQDN trailing dot must not dodge the TLD screen; a literal
    IPv4-mapped IPv6 URL is screened without a DNS step."""
    from app.config import settings
    from app.integrations.security import EgressBlockedError, validate_egress_url

    monkeypatch.setattr(settings, "egress_allow_private", False)
    for url in (
        "https://db.corp./x",
        "https://localhost./x",
        "https://[::ffff:10.0.0.1]/x",
        "https://[::1]/x",
    ):
        with pytest.raises(EgressBlockedError):
            validate_egress_url(url)


def test_every_fabric_sweep_has_a_registered_cron():
    """R43 guard (R11 class: schedule columns/sweeps nobody drives): every
    fabric sweep function must be wired into the worker cron registry, and
    the outbox handler module must be imported by load_handlers."""
    from app.controlplane.worker import _cron_jobs

    names = {j.name for j in _cron_jobs()}
    required = {
        "intg_domain_sweep",     # pending-domain DNS polling
        "intg_scheduled_syncs",  # SyncProfile.schedule driver
        "intg_stale_run_reaper", # crashed-run reaper
        "intg_exports",          # ExportStream.schedule driver
        "intg_cert_expiry",      # SAML cert expiry alerts
        "intg_conn_health",      # connection health decay + alerts
        "intg_retention",        # terminal-data age-out (R44)
        "intg_metadata_refresh", # SAML metadata cert rotation (R51)
    }
    missing = required - names
    assert missing == set(), f"fabric sweeps without a cron: {sorted(missing)}"

    from pathlib import Path

    import app.controlplane.worker as cp_worker

    src = Path(cp_worker.__file__).read_text()
    assert "app.integrations.worker" in src  # outbox handlers registered


# ── R61: generic connector contracts (previously untested) ──


def test_generic_connector_contracts():
    """GenericRest ping auth/5xx classification, api-key header placement;
    GenericAts write url join, auth header, per-record ack fidelity."""
    import asyncio
    import json as _json

    import httpx

    from app.exceptions import AppError
    from app.integrations.registry import (
        ConnCtx,
        GenericAtsConnector,
        GenericRestConnector,
    )

    class Scripted:
        def __init__(self, code):
            self.code = code
            self.calls = []

        async def request(self, method, url, *, headers=None, content=None, read_timeout=None):
            self.calls.append({"method": method, "url": url, "headers": headers,
                               "body": content})
            return httpx.Response(self.code, request=httpx.Request(method, url))

    async def loader():
        return {"api_key": "sk-123"}

    def ctx(egress, config=None, base="https://api.vendor.example.com"):
        c = ConnCtx(connection_id="x", config=config or {}, base_url=base,
                    _secret_loader=loader)
        c.egress = egress
        return c

    async def main():
        rest = GenericRestConnector()
        # 401/403 -> AUTH_REJECTED; 5xx -> PING_FAILED; 2xx/4xx-other pass.
        for code in (401, 403):
            try:
                await rest.ping(ctx(Scripted(code)))
                raise AssertionError("auth rejection not raised")
            except AppError as exc:
                assert exc.code == "CONNECTION_AUTH_REJECTED"
        try:
            await rest.ping(ctx(Scripted(503)))
            raise AssertionError("5xx not raised")
        except AppError as exc:
            assert exc.code == "CONNECTION_PING_FAILED"
        sc = Scripted(200)
        await rest.ping(ctx(sc, config={"auth_header": "X-Api-Key"}))
        assert sc.calls[0]["headers"] == {"X-Api-Key": "sk-123"}
        await rest.ping(ctx(Scripted(404)))  # non-auth 4xx is fine

        ats = GenericAtsConnector()
        sc2 = Scripted(202)
        out = await ats.write(
            ctx(sc2, base="https://ats.example.com/"),  # trailing slash
            "talent.application",
            [{"external_id": "a1"}, {"external_id": "a2"}],
        )
        assert sc2.calls[0]["url"] == "https://ats.example.com/applications"
        assert sc2.calls[0]["headers"]["Authorization"] == "sk-123"
        body = _json.loads(sc2.calls[0]["body"])
        assert [r["external_id"] for r in body["applications"]] == ["a1", "a2"]
        assert all(r["ok"] is True and r["error"] is None for r in out)
        # Non-2xx -> every record reports the failure, never ok.
        out2 = await ats.write(
            ctx(Scripted(422)), "talent.application", [{"external_id": "b1"}]
        )
        assert out2 == [{"external_id": "b1", "ok": False, "error": "http_422"}]

    asyncio.run(main())


def test_request_with_retry_honors_retry_after_and_caps():
    """R86 (Part G rate limits): 429 Retry-After honored (capped), transient
    5xx retried with backoff, retries bounded, final response surfaced."""
    import asyncio
    import time as _time

    import httpx

    from app.integrations.registry import request_with_retry

    class Scripted:
        def __init__(self, steps):
            self.steps = list(steps)  # (status, headers)
            self.calls = 0

        async def request(self, method, url, *, headers=None, content=None, read_timeout=None):
            self.calls += 1
            status, hdrs = self.steps.pop(0)
            return httpx.Response(status, headers=hdrs, request=httpx.Request(method, url))

    async def main():
        # 429 with Retry-After: waits then succeeds.
        s = Scripted([(429, {"retry-after": "0"}), (200, {})])
        resp = await request_with_retry(s, "GET", "https://x.example.com/")
        assert resp.status_code == 200 and s.calls == 2

        # Hostile Retry-After is CAPPED (3600 -> retry_cap_s), not slept raw.
        s = Scripted([(429, {"retry-after": "3600"}), (200, {})])
        t0 = _time.monotonic()
        resp = await request_with_retry(
            s, "GET", "https://x.example.com/", retry_cap_s=0.05
        )
        assert resp.status_code == 200
        assert _time.monotonic() - t0 < 2.0  # never slept the hour

        # Transient 503 retried; retries BOUNDED (3 attempts total), final
        # response returned for the caller to classify.
        s = Scripted([(503, {}), (200, {})])
        assert (await request_with_retry(s, "GET", "https://x/", retry_cap_s=0.01)).status_code == 200
        s = Scripted([(429, {"retry-after": "0"})] * 5)
        resp = await request_with_retry(s, "GET", "https://x/", retry_cap_s=0.01)
        assert resp.status_code == 429 and s.calls == 3

        # All-503 is BOUNDED too (3 attempts, final 503 surfaced).
        s = Scripted([(503, {})] * 5)
        resp = await request_with_retry(s, "GET", "https://x/", retry_cap_s=0.01)
        assert resp.status_code == 503 and s.calls == 3

        # Unparseable (HTTP-date) Retry-After falls back to a short beat.
        s = Scripted([(429, {"retry-after": "Sat, 11 Oct 2026 10:00:00 GMT"}), (200, {})])
        t0 = _time.monotonic()
        assert (await request_with_retry(s, "GET", "https://x/")).status_code == 200
        assert _time.monotonic() - t0 < 3.0

        # Hard 4xx never retried.
        s = Scripted([(401, {})])
        assert (await request_with_retry(s, "GET", "https://x/")).status_code == 401
        assert s.calls == 1

    asyncio.run(main())


def test_redirect_uris_derive_from_config_not_host_header():
    """R101 (Part O): a spoofed Host header must not steer the redirect_uri
    we hand to IdPs/platforms."""
    from starlette.requests import Request

    from app.integrations.api.lti import _launch_redirect_uri
    from app.integrations.api.sso import _callback_uri

    scope = {
        "type": "http", "method": "GET", "path": "/", "query_string": b"",
        "headers": [(b"host", b"evil.attacker.example")],
        "server": ("evil.attacker.example", 443), "scheme": "https",
    }
    req = Request(scope)
    assert "evil.attacker.example" not in _callback_uri(req)
    assert "evil.attacker.example" not in _launch_redirect_uri(req)
    assert _callback_uri(req).endswith("/api/v1/sso/oidc/callback")
    assert _launch_redirect_uri(req).endswith("/api/v1/lti/launch")


def test_oauth_scopes_stay_least_privilege():
    """R104 (Part O): every outbound token request pins its MINIMAL scope —
    widening any of these is privilege creep and must be a conscious edit."""
    from pathlib import Path

    import app.integrations.registry as reg_mod
    import app.integrations.services.lti as lti_mod
    import app.integrations.services.lti_ags as ags_mod
    import app.integrations.services.lti_nrps as nrps_mod
    import app.integrations.services.sso_oidc as oidc_mod

    assert ags_mod.AGS_SCORE_SCOPE == "https://purl.imsglobal.org/spec/lti-ags/scope/score"
    assert nrps_mod.NRPS_SCOPE == (
        "https://purl.imsglobal.org/spec/lti-nrps/scope/contextmembership.readonly"
    )
    assert '"scope": "https://purl.imsglobal.org/spec/or/v1p2/scope/roster.readonly"' in (
        Path(reg_mod.__file__).read_text()
    )
    assert '"scope": "openid email profile"' in Path(oidc_mod.__file__).read_text()
    assert '"scope": "openid",' in Path(lti_mod.__file__).read_text()
