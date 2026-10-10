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
    assert body["bulk"]["supported"] is False  # advertised unsupported (ADR §19)
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
