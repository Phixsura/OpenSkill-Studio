"""Test configuration.

Creates a test FastAPI app that skips the lifespan (no Postgres/Redis needed).
The app still has all routes and middleware, so schema validation, auth checks,
and error handling all work correctly.
"""

from contextlib import asynccontextmanager

import pytest
from httpx import ASGITransport, AsyncClient


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
