"""Test configuration.

Creates a test FastAPI app that skips the lifespan (no Postgres/Redis needed).
The app still has all routes and middleware, so schema validation, auth checks,
and error handling all work correctly.
"""

import os
from contextlib import asynccontextmanager

import pytest
from httpx import ASGITransport, AsyncClient

# Disable rate limiting in test environment
os.environ["APP_ENV"] = "test"


@asynccontextmanager
async def _noop_lifespan(app):
    """Skip infrastructure checks for unit tests."""
    yield


@pytest.fixture
async def client():
    # Import app lazily so we can patch the lifespan
    from app.main import app

    # Replace lifespan with a no-op for tests
    original_lifespan = app.router.lifespan_context
    app.router.lifespan_context = _noop_lifespan

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    # Restore original lifespan
    app.router.lifespan_context = original_lifespan

@pytest.fixture(autouse=True)
def _pin_example_dns(monkeypatch):
    """R243 anti-flake: eco test sources use example.com, and the SSRF guard
    re-resolves it on every sync — under machine load a real DNS timeout
    fail-closes into ECO_SSRF_BLOCKED and flakes unrelated tests. Pin the
    fixture domain to a fixed public IP without touching the network;
    every other hostname (SSRF matrix, rebinding stubs) resolves as before.
    """
    import socket as _socket

    real = _socket.getaddrinfo

    def pinned(host, *args, **kwargs):
        if isinstance(host, str) and host.rstrip(".").endswith("example.com"):
            return [(_socket.AF_INET, _socket.SOCK_STREAM, 6, "", ("93.184.215.14", 443))]
        return real(host, *args, **kwargs)

    monkeypatch.setattr(_socket, "getaddrinfo", pinned)

