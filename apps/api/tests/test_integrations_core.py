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

    async def fake_send(self, request, *, stream=False, **kw):
        captured["url"] = str(request.url)
        captured["headers"] = dict(request.headers)
        captured["extensions"] = dict(request.extensions or {})
        return httpx.Response(200, request=request)

    # R217 made EgressClient stream via build_request+send, so patch send.
    monkeypatch.setattr(httpx.AsyncClient, "send", fake_send)
    resp = await EgressClient().request("POST", "https://hooks.example.com/deliver?a=1")
    assert resp.status_code == 200
    # httpx normalizes the default :443 away on the Request object.
    assert captured["url"] == "https://93.184.216.34/deliver?a=1"
    assert captured["headers"]["host"] == "hooks.example.com"
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


def _fresh_connectors():
    """FRESH connector instances from the real classes: many tests swap
    fakes into the module-level CONNECTORS singleton (order pollution) —
    registry contracts are about the REAL classes, not whatever a prior
    test left behind."""
    from app.integrations import registry as _registry
    from app.integrations.registry import PROVIDER_CATALOG

    return {
        obj.key: obj()
        for obj in vars(_registry).values()
        if isinstance(obj, type)
        and hasattr(obj, "key")
        and hasattr(obj, "capabilities")
        and getattr(obj, "key", None) in PROVIDER_CATALOG
    }


def test_connector_registry_matches_catalog():
    from app.integrations.registry import PROVIDER_CATALOG

    connectors = _fresh_connectors()
    assert set(connectors) == set(PROVIDER_CATALOG)
    for key, spec in PROVIDER_CATALOG.items():
        assert set(spec["capabilities"]) == set(connectors[key].capabilities), key


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
        (p, r) for p, r in walk(fastapi_app.routes) if p.startswith(("/sso", "/scim/v2", "/lti"))
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
        "10.1.2.3",  # private
        "127.0.0.1",  # loopback
        "169.254.169.254",  # link-local (cloud metadata)
        "224.0.0.1",  # multicast
        "240.0.0.1",  # reserved
        "0.0.0.0",  # unspecified
        "100.64.0.1",  # carrier-grade NAT
        "::1",  # v6 loopback
        "::",  # v6 unspecified
        "fe80::1",  # v6 link-local
        "ff02::1",  # v6 multicast
        "fc00::1",  # v6 ULA (private)
        "::ffff:10.0.0.1",  # IPv4-mapped v6 smuggling a private v4
        "::ffff:127.0.0.1",  # IPv4-mapped loopback
        "not-an-ip",  # unparseable is forbidden, not ignored
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
        "intg_domain_sweep",  # pending-domain DNS polling
        "intg_scheduled_syncs",  # SyncProfile.schedule driver
        "intg_stale_run_reaper",  # crashed-run reaper
        "intg_exports",  # ExportStream.schedule driver
        "intg_cert_expiry",  # SAML cert expiry alerts
        "intg_conn_health",  # connection health decay + alerts
        "intg_retention",  # terminal-data age-out (R44)
        "intg_metadata_refresh",  # SAML metadata cert rotation (R51)
    }
    missing = required - names
    assert missing == set(), f"fabric sweeps without a cron: {sorted(missing)}"

    # R185: the export sweep must run at least hourly (not hour-pinned), else
    # an `hourly` ExportStream silently degrades to daily.
    exports = next(j for j in _cron_jobs() if j.name == "intg_exports")
    hour_spec = getattr(exports, "hour", None)
    assert hour_spec in (None, set(), "*"), (
        f"intg_exports is hour-pinned ({hour_spec!r}) — hourly streams would run daily"
    )

    from pathlib import Path

    import app.controlplane.worker as cp_worker

    src = Path(cp_worker.__file__).read_text()
    assert "app.integrations.worker" in src  # outbox handlers registered

    # R289: the name list above is hand-maintained — back it with a source
    # scan so a brand-new sweep function cannot ship undriven. Every
    # `async def sweep_*` under app/integrations must be referenced by the
    # worker module (directly or inside another cron's body).
    import re as _re

    import app.integrations as _intg

    intg_root = Path(_intg.__file__).parent
    sweep_names = set()
    for f in intg_root.rglob("*.py"):
        sweep_names |= set(_re.findall(r"async def (sweep_\w+)", f.read_text()))
    assert sweep_names, "sweep source-scan found nothing — the regex rotted"
    undriven = sorted(n for n in sweep_names if n not in src)
    assert undriven == [], f"fabric sweeps nobody drives: {undriven}"


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
            self.calls.append({"method": method, "url": url, "headers": headers, "body": content})
            return httpx.Response(self.code, request=httpx.Request(method, url))

    async def loader():
        return {"api_key": "sk-123"}

    def ctx(egress, config=None, base="https://api.vendor.example.com"):
        c = ConnCtx(connection_id="x", config=config or {}, base_url=base, _secret_loader=loader)
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
        out2 = await ats.write(ctx(Scripted(422)), "talent.application", [{"external_id": "b1"}])
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
        resp = await request_with_retry(s, "GET", "https://x.example.com/", retry_cap_s=0.05)
        assert resp.status_code == 200
        assert _time.monotonic() - t0 < 2.0  # never slept the hour

        # Transient 503 retried; retries BOUNDED (3 attempts total), final
        # response returned for the caller to classify.
        s = Scripted([(503, {}), (200, {})])
        assert (
            await request_with_retry(s, "GET", "https://x/", retry_cap_s=0.01)
        ).status_code == 200
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
        "type": "http",
        "method": "GET",
        "path": "/",
        "query_string": b"",
        "headers": [(b"host", b"evil.attacker.example")],
        "server": ("evil.attacker.example", 443),
        "scheme": "https",
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


def test_generic_crm_connector_contract():
    """R120 (Part E): CRM reader maps accounts/contacts/deals, paginates by
    real item count, classifies 401/5xx, refuses unknown models, read-only."""
    import asyncio

    import httpx

    from app.exceptions import AppError
    from app.integrations.registry import ConnCtx, GenericCrmConnector

    class CrmApi:
        def __init__(self, pages_by_key, status=200):
            self.pages = pages_by_key
            self.status = status
            self.calls = []

        async def request(self, method, url, *, headers=None, content=None, read_timeout=None):
            self.calls.append(url)
            if self.status != 200:
                return httpx.Response(self.status, request=httpx.Request(method, url))
            from urllib.parse import parse_qs, urlsplit

            parsed = urlsplit(url)
            key = parsed.path.rstrip("/").split("/")[-1]
            qs = parse_qs(parsed.query)
            offset = int(qs.get("offset", ["0"])[0])
            limit = int(qs.get("limit", ["100"])[0])
            items = self.pages.get(key, [])[offset : offset + limit]
            return httpx.Response(200, json={key: items}, request=httpx.Request(method, url))

    async def loader():
        return {"api_key": "crm-key"}

    def ctx(egress, page_size=2):
        c = ConnCtx(
            connection_id="x",
            config={"page_size": page_size, "auth_header": "X-Api-Key"},
            base_url="https://crm.example.com/api/",
            _secret_loader=loader,
        )
        c.egress = egress
        return c

    async def main():
        conn = GenericCrmConnector()
        api = CrmApi(
            {
                "accounts": [
                    {"id": "a1", "name": "Acme", "domain": "acme.io"},
                    {"id": "a2", "name": "Globex"},
                    {"id": "a3", "name": "Initech"},
                ],
            }
        )
        batches = [b async for b in conn.read(ctx(api), "crm.account", {})]
        recs = [r for b in batches for r in b["records"]]
        assert [r["external_id"] for r in recs] == ["a1", "a2", "a3"]
        assert recs[0] == {"external_id": "a1", "name": "Acme", "domain": "acme.io"}
        assert batches[-1]["state"] == {"endpoint_offset": 0}
        # api-key header placed under the configured name.
        assert all("X-Api-Key" not in u for u in api.calls)  # header, not query

        # contacts map account_external_id; deals map stage.
        api2 = CrmApi({"contacts": [{"id": "c1", "email": "p@acme.io", "account_id": "a1"}]})
        [c1] = [r async for b in conn.read(ctx(api2), "crm.contact", {}) for r in b["records"]]
        assert c1 == {
            "external_id": "c1",
            "email": "p@acme.io",
            "name": None,
            "account_external_id": "a1",
        }

        # error classification + unknown model.
        try:
            async for _ in conn.read(ctx(CrmApi({}, status=401)), "crm.deal", {}):
                pass
            raise AssertionError("no 401")
        except AppError as e:
            assert e.code == "CONNECTION_AUTH_REJECTED"
        try:
            async for _ in conn.read(ctx(api), "talent.candidate", {}):
                pass
            raise AssertionError("no model guard")
        except AppError as e:
            assert e.code == "SYNC_PROFILE_INVALID"
        # read-only: no write method.
        assert not hasattr(conn, "write")

    asyncio.run(main())


def test_generic_crm_in_catalog():
    """R120: generic_crm registered with crm.read capability."""
    from app.integrations.registry import CONNECTORS, PROVIDER_CATALOG

    assert "generic_crm" in CONNECTORS
    assert PROVIDER_CATALOG["generic_crm"]["capabilities"] == ["crm.read"]


def test_connector_sdk_boundary_contract():
    """R125 (Part M): every registered connector declares key + capabilities
    + ping; its declared capabilities MATCH the methods it implements; and
    the CONNECTORS registry is consistent with PROVIDER_CATALOG."""
    import inspect

    from app.integrations.registry import PROVIDER_CATALOG

    connectors = _fresh_connectors()

    cap_method = {
        "roster.read": "read",
        "crm.read": "read",
        "talent.write": "write",
        "events.deliver": None,
    }
    for key, conn in connectors.items():
        assert conn.key == key, f"{key}: key mismatch"
        assert isinstance(conn.capabilities, frozenset), key
        assert inspect.iscoroutinefunction(conn.ping), f"{key}: ping must be async"
        for cap in conn.capabilities:
            method = cap_method.get(cap)
            if method:
                assert hasattr(conn, method), f"{key} claims {cap} but has no {method}()"
                fn = getattr(conn, method)
                assert inspect.iscoroutinefunction(fn) or inspect.isasyncgenfunction(fn), (
                    f"{key}.{method} must be async"
                )
        if hasattr(conn, "write"):
            assert any(c.endswith(".write") for c in conn.capabilities), f"{key}: undeclared write"

    assert set(connectors) == set(PROVIDER_CATALOG)
    for key, conn in connectors.items():
        assert set(conn.capabilities) == set(PROVIDER_CATALOG[key]["capabilities"]), key
        assert PROVIDER_CATALOG[key]["version"] >= 1


def test_every_fabric_audit_action_is_registered():
    """R147 (inverse of the R100 lesson): record_audit SWALLOWS unregistered
    actions silently — scan every record_fabric_audit call site and assert
    its action literal is in AUDIT_ACTIONS, so a typo'd or unregistered
    action can never ship as a silent no-op."""
    import pathlib
    import re

    from app.controlplane.services.audit import AUDIT_ACTIONS

    call_re = re.compile(
        r"""record_fabric_audit\(\s*[^,]+,\s*[^,]+,\s*[^,]+,\s*["']([a-z0-9_.]+)["']"""
    )
    found: set[str] = set()
    for f in pathlib.Path("app").rglob("*.py"):
        found |= set(call_re.findall(f.read_text()))
    assert found, "record_fabric_audit scan found nothing - regex drifted"
    unregistered = sorted(found - set(AUDIT_ACTIONS))
    assert not unregistered, f"audited actions never land: {unregistered}"


def test_write_amplifying_routes_are_rate_limited():
    """R159-R160: the write-amplifying / provisioning fabric routes carry a
    rate_limit dependency (bulk replay, import upload+commit, sync run) —
    a regression that drops the limit is caught here."""
    from app.integrations.api import events as ev_api
    from app.integrations.api import imports as im_api
    from app.integrations.api import sync as sync_api

    def _paths_with_ratelimit(router):
        out = {}
        for r in router.routes:
            deps = getattr(r, "dependencies", []) or []
            has = any(
                "rate_limit" in getattr(getattr(d, "dependency", None), "__qualname__", "")
                for d in deps
            )
            out[(tuple(sorted(r.methods or [])), r.path)] = has
        return out

    ev = _paths_with_ratelimit(ev_api.router)
    assert ev[
        (("POST",), "/orgs/{org_id}/integrations/webhooks/{subscription_id}/replay-exhausted")
    ]
    im = _paths_with_ratelimit(im_api.router)
    assert im[(("POST",), "/orgs/{org_id}/integrations/imports")]
    assert im[(("POST",), "/orgs/{org_id}/integrations/imports/{job_id}/commit")]
    sy = _paths_with_ratelimit(sync_api.router)
    assert sy[(("POST",), "/orgs/{org_id}/integrations/sync-profiles/{profile_id}/run")]
    from app.integrations.api import connections as conn_api

    cn = _paths_with_ratelimit(conn_api.router)
    assert cn[(("POST",), "/orgs/{org_id}/integrations/connections/{connection_id}/ping")]


def test_sync_connctx_always_builds_with_secret_loader():
    """R194 guard: every ConnCtx built in the sync engine must pass a
    _secret_loader — a bare ConnCtx silently authenticates connectors with an
    empty secret (ping-healthy-but-sync-401). Source-level check so a new
    construction site that forgets the loader is caught."""
    import pathlib
    import re

    src = pathlib.Path("app/integrations/services/sync_engine.py").read_text()
    # Find each ConnCtx(...) call body and require _secret_loader in it.
    for m in re.finditer(r"ConnCtx\((.*?)\)", src, re.DOTALL):
        body = m.group(1)
        assert "_secret_loader" in body, (
            "a sync-engine ConnCtx is built without _secret_loader "
            f"(connectors would get empty secrets): {body[:120]!r}"
        )


@pytest.mark.asyncio
async def test_response_size_cap_aborts_before_buffering(monkeypatch):
    """R217: the egress response cap must reject OVERSIZED bodies without
    buffering them whole — the old `len(resp.content) > cap` ran only AFTER
    httpx had already read the entire body into memory (a hostile server
    returning gigabytes OOM'd the worker before the cap ever fired).
    Three cases: declared Content-Length too big (rejected before any body
    read), undeclared/chunked body that exceeds the cap mid-stream (aborted
    at the cap, not at the end), and a normal small response (unchanged)."""
    import httpx as _httpx

    from app.config import settings
    from app.integrations import security as sec

    monkeypatch.setattr(settings, "egress_allow_private", False)
    monkeypatch.setattr(socket, "getaddrinfo", _fake_getaddrinfo("93.184.216.34"))
    monkeypatch.setattr(sec, "MAX_RESPONSE_BYTES", 1024)

    state = {"mode": "declared", "body_reads": 0}

    class CountingStream(_httpx.AsyncByteStream):
        """64 chunks of 64B = 4KB total (> 1KB cap); counts chunks served."""

        async def __aiter__(self):
            for _ in range(64):
                state["body_reads"] += 1
                yield b"x" * 64

        async def aclose(self):
            return None

    async def fake_send(self, request, *, stream=False, **kw):
        if state["mode"] == "declared":
            # Content-Length says 4096 — must be rejected with ZERO chunk reads.
            return _httpx.Response(
                200,
                headers={"content-length": "4096"},
                stream=CountingStream(),
                request=request,
            )
        if state["mode"] == "chunked":
            # No usable length — must abort mid-stream at the cap.
            return _httpx.Response(200, stream=CountingStream(), request=request)
        return _httpx.Response(200, json={"ok": True}, request=request)

    monkeypatch.setattr(_httpx.AsyncClient, "send", fake_send)

    with pytest.raises(sec.EgressBlockedError):
        await EgressClient().request("GET", "https://api.example.com/huge")
    assert state["body_reads"] == 0  # declared-length reject: nothing buffered

    state["mode"] = "chunked"
    with pytest.raises(sec.EgressBlockedError):
        await EgressClient().request("GET", "https://api.example.com/huge2")
    # Aborted at the cap (1KB = 16 chunks + 1 overflow), far short of all 64.
    assert state["body_reads"] <= 20

    state["mode"] = "ok"
    resp = await EgressClient().request("GET", "https://api.example.com/small")
    assert resp.status_code == 200 and resp.json() == {"ok": True}


def test_event_catalog_covers_every_emitted_name():
    """R231 catalog-drift guard: every bare mesh-event name emitted anywhere
    in the backend (emit_event literals, SCIM _audit literals, and
    INTERNAL_EVENT_PREFIX f-strings) must appear in the subscription
    catalog — legacy set, DIRECT_EMISSIONS, or the internal-alertable map.
    And DIRECT_EMISSIONS must contain no phantom entries nothing emits."""
    import pathlib
    import re

    from app.integrations.api.events import _INTERNAL_ALERTABLE, DIRECT_EMISSIONS
    from app.services.webhook import _MESH_NAME_MAP, VALID_EVENT_TYPES

    root = pathlib.Path(__file__).resolve().parents[1] / "app"
    emitted: set[str] = set()
    name_re = re.compile(r'"([a-z][a-z_]*(?:\.[a-z_]+)+)"')
    for py in root.rglob("*.py"):
        text = py.read_text()
        for m in re.finditer(r"emit_event\(", text):
            window = text[m.end() : m.end() + 300]
            found = name_re.search(window)
            if found:
                emitted.add(found.group(1))
        for m in re.finditer(r'_audit\(\s*"([a-z][a-z_.]+)"', text):
            emitted.add(m.group(1))
        for m in re.finditer(r'f"\{INTERNAL_EVENT_PREFIX\}([a-z][a-z_.]+)"', text):
            emitted.add("integration." + m.group(1))

    assert emitted, "source scan found nothing — the regex broke, fix the test"
    catalog_bare = (
        set(VALID_EVENT_TYPES)
        | {_MESH_NAME_MAP.get(n, n) for n in VALID_EVENT_TYPES}
        | set(DIRECT_EMISSIONS)
        | {t.removeprefix("com.openskill.").removesuffix(".v1") for t in _INTERNAL_ALERTABLE}
    )
    uncatalogued = {
        n for n in emitted if n not in catalog_bare and _MESH_NAME_MAP.get(n, n) not in catalog_bare
    }
    assert not uncatalogued, f"emitted but not in the catalog: {sorted(uncatalogued)}"
    phantom = set(DIRECT_EMISSIONS) - emitted
    assert not phantom, f"catalogued but nothing emits them: {sorted(phantom)}"


@pytest.mark.asyncio
async def test_egress_never_follows_redirects(monkeypatch):
    """R301 (survivor pin): a 3xx from the receiver is a TERMINAL answer —
    following it would fetch an attacker-chosen Location (e.g. the cloud
    metadata IP) from inside our network, bypassing the URL screen. The
    transport must be hit exactly once and the 302 returned as-is.
    (Patched at the TRANSPORT layer: httpx's redirect loop lives inside
    AsyncClient.send, so a send-level fake would mask the flag.)"""
    import httpx

    from app.config import settings

    monkeypatch.setattr(settings, "egress_allow_private", False)
    monkeypatch.setattr(socket, "getaddrinfo", _fake_getaddrinfo("93.184.216.34"))

    hops = []

    async def fake_handle(self, request):
        hops.append(str(request.url))
        return httpx.Response(
            302,
            headers={"location": "http://169.254.169.254/latest/meta-data/"},
            request=request,
        )

    monkeypatch.setattr(httpx.AsyncHTTPTransport, "handle_async_request", fake_handle)
    resp = await EgressClient().request("POST", "https://hooks.example.com/deliver")
    assert resp.status_code == 302
    assert len(hops) == 1  # one hop, Location never fetched


@pytest.mark.asyncio
async def test_egress_client_hardening_flags(monkeypatch):
    """R302 (survivor pin): the EgressClient must be constructed with
    trust_env=False (HTTP(S)_PROXY env vars must never reroute pinned
    egress through an attacker-influenced proxy) and
    follow_redirects=False (R301). Pinned at construction — behavioral
    proxy routing is invisible under a patched transport, so the honest
    assertion is the client config itself."""
    import httpx

    from app.config import settings

    monkeypatch.setattr(settings, "egress_allow_private", False)
    monkeypatch.setattr(socket, "getaddrinfo", _fake_getaddrinfo("93.184.216.34"))

    seen = {}
    real_init = httpx.AsyncClient.__init__

    def spy_init(self, *args, **kwargs):
        seen.update(kwargs)
        return real_init(self, *args, **kwargs)

    monkeypatch.setattr(httpx.AsyncClient, "__init__", spy_init)

    async def fake_handle(self, request):
        return httpx.Response(200, request=request)

    monkeypatch.setattr(httpx.AsyncHTTPTransport, "handle_async_request", fake_handle)
    resp = await EgressClient().request("GET", "https://hooks.example.com/x")
    assert resp.status_code == 200
    assert seen.get("trust_env") is False
    assert seen.get("follow_redirects") is False


def test_csv_oversized_cell_is_file_error_not_crash():
    """R370 (fuzz phase 7): a single CSV cell beyond Python's 128KB field
    limit raised _csv.Error out of parse_users_csv — a 500 on upload. It
    must land as a clean per-file `malformed_csv` error instead, both when
    the explosion happens in the header row and mid-file."""
    from app.integrations.services.bulk_import import parse_users_csv

    big = b"email,display_name\na@x.com," + b"A" * 300_000 + b"\n"
    rows, errors = parse_users_csv(big)
    assert rows == []
    assert errors and errors[0]["code"] == "malformed_csv"

    big_header = b"email,display_name" + b"X" * 300_000 + b"\nb@x.com,B\n"
    rows, errors = parse_users_csv(big_header)
    assert rows == []
    assert errors and errors[0]["code"] == "malformed_csv"


def test_fabric_route_contract():
    """R374: structural contract over every MOUNTED fabric route — a new
    endpoint added without auth, or an org-scoped JSON route without a
    response envelope, fails here before any live test runs.

    - Every /orgs/{org_id}/integrations route must carry get_current_user
      in its dependant tree (protocol surfaces — /sso, /scim, /lti — auth
      inside the handler via connection/token/JWKS and are allowlisted).
    - Every such route must declare a response_model unless it is a 204
      DELETE or a deliberate raw-Response route (csv, template, payload).
    - The org-scoped integrations router itself must carry the
      router-level rate limiter (R366: route.dependant does NOT show
      router-level deps in this FastAPI version, so check the router).
    """
    from fastapi.routing import APIRoute

    from app.integrations.api import integrations_router
    from app.main import app

    def collect(routes, acc):
        for r in routes:
            if isinstance(r, APIRoute):
                acc.append(r)
            inner = getattr(r, "original_router", None)
            if inner is not None:
                collect(inner.routes, acc)
            sub = getattr(r, "routes", None)
            if sub and not isinstance(r, APIRoute):
                collect(sub, acc)
        return acc

    def dep_names(dependant, acc):
        for d in dependant.dependencies:
            if d.call is not None:
                acc.add(getattr(d.call, "__qualname__", str(d.call)))
            dep_names(d, acc)
        return acc

    fabric = [r for r in collect(app.routes, []) if "/integrations" in r.path]
    assert len(fabric) >= 60, f"route collection broke: only {len(fabric)} fabric routes found"

    raw_response_ok = ("/errors.csv", "/imports/template", "/payload")
    unauthed, unmodeled = [], []
    for r in fabric:
        names = dep_names(r.dependant, set())
        if not any("get_current_user" in x for x in names):
            unauthed.append(f"{sorted(r.methods)} {r.path}")
        if r.response_model is None:
            if "DELETE" in r.methods or r.path.endswith(raw_response_ok):
                continue
            if r.path.endswith("/break-glass"):  # 204 by design
                continue
            unmodeled.append(f"{sorted(r.methods)} {r.path}")
    assert not unauthed, f"fabric routes without user auth: {unauthed}"
    assert not unmodeled, f"fabric JSON routes without response_model: {unmodeled}"

    router_dep_names = {
        getattr(d.dependency, "__qualname__", str(d.dependency))
        for d in integrations_router.dependencies
    }
    assert any("rate_limit" in x or "checker" in x for x in router_dep_names), (
        "org-scoped integrations router lost its router-level rate limiter"
    )


def test_every_mutating_fabric_route_audits_or_is_exempt():
    """R377: admin mutations on fabric config must write the audit trail
    (Part O). Found live: break-glass — the single most audit-worthy switch
    in the fabric — plus connection/domains/export/LTI/sync mutations wrote
    NO audit row. Every mutating /integrations route must now either call
    record_fabric_audit in its handler or sit on the EXPLICIT exempt list
    (with the reason); a new mutating route fails here until it declares
    its audit posture."""
    import inspect

    from fastapi.routing import APIRoute

    from app.main import app

    def collect(routes, acc):
        for r in routes:
            if isinstance(r, APIRoute):
                acc.append(r)
            inner = getattr(r, "original_router", None)
            if inner is not None:
                collect(inner.routes, acc)
            sub = getattr(r, "routes", None)
            if sub and not isinstance(r, APIRoute):
                collect(sub, acc)
        return acc

    exempt = {
        # read-like probes / previews: no config change to audit
        "POST /orgs/{org_id}/integrations/connections/{connection_id}/ping",
        "POST /orgs/{org_id}/integrations/mapping-profiles/{profile_id}/preview",
        "POST /orgs/{org_id}/integrations/sync-profiles/{profile_id}/preview",
        # LTI protocol-driven surfaces (platform-initiated, signed launches)
        "POST /orgs/{org_id}/integrations/lti/registrations/{reg_id}/resource-links",
        "POST /orgs/{org_id}/integrations/lti/resource-links/{link_id}/nrps-sync",
        "POST /orgs/{org_id}/integrations/lti/deep-link/select",
    }
    uncovered = []
    for r in collect(app.routes, []):
        if "/integrations" not in r.path:
            continue
        if r.path.startswith("/talent/"):  # talent epic, not fabric (#43)
            continue
        methods = r.methods & {"POST", "PATCH", "PUT", "DELETE"}
        if not methods:
            continue
        key = f"{sorted(methods)[0]} {r.path}"
        if key in exempt:
            continue
        try:
            src = inspect.getsource(r.endpoint)
        except OSError:
            src = ""
        if "record_fabric_audit" not in src:
            uncovered.append(key)
    assert not uncovered, f"mutating fabric routes with no audit posture: {uncovered}"
