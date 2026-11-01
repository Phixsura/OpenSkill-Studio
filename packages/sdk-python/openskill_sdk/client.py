"""OpenSkill Platform API client for Python."""

from __future__ import annotations

from typing import Any

import httpx

from openskill_sdk.errors import ApiError, AuthError, NotFoundError, RateLimitError


class OpenSkillClient:
    """Async API client for the OpenSkill Platform.

    Usage::

        client = OpenSkillClient(api_key="osk_app_...")
        account = await client.developer.get_me()
        apps = await client.apps.list()
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.openskill.dev",
        timeout: float = 30.0,
    ):
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._client = httpx.AsyncClient(
            base_url=f"{self._base_url}/api/v1",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            timeout=httpx.Timeout(timeout),
            trust_env=False,
        )

        self.developer = _DeveloperResource(self)
        self.apps = _AppResource(self)
        self.marketplace = _MarketplaceResource(self)

    async def request(
        self,
        method: str,
        path: str,
        *,
        json: Any = None,
        params: dict[str, Any] | None = None,
    ) -> dict:
        """Make an authenticated API request."""
        resp = await self._client.request(method, path, json=json, params=params)

        if resp.status_code == 401:
            raise AuthError()
        if resp.status_code == 404:
            body = resp.json()
            msg = body.get("error", {}).get("message", "Not found")
            raise NotFoundError(msg)
        if resp.status_code == 429:
            retry = int(resp.headers.get("retry-after", "60"))
            raise RateLimitError(retry)
        if resp.status_code >= 400:
            body = resp.json()
            err = body.get("error", {})
            raise ApiError(
                message=err.get("message", f"HTTP {resp.status_code}"),
                code=err.get("code", "API_ERROR"),
                status_code=resp.status_code,
                details=err.get("details"),
            )

        return resp.json()

    async def get(self, path: str, **params: Any) -> dict:
        return await self.request("GET", path, params=params or None)

    async def post(self, path: str, data: Any = None) -> dict:
        return await self.request("POST", path, json=data)

    async def patch(self, path: str, data: Any = None) -> dict:
        return await self.request("PATCH", path, json=data)

    async def delete(self, path: str) -> dict:
        return await self.request("DELETE", path)

    async def close(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> OpenSkillClient:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()


# ── Resource classes ─────────────────────────────────────


class _DeveloperResource:
    def __init__(self, client: OpenSkillClient):
        self._c = client

    async def get_me(self) -> dict:
        resp = await self._c.get("/developer/accounts/me")
        return resp["data"]

    async def create(
        self,
        *,
        display_name: str,
        slug: str,
        support_email: str,
        website_url: str | None = None,
        org_id: str | None = None,
    ) -> dict:
        resp = await self._c.post(
            "/developer/accounts",
            {
                "display_name": display_name,
                "slug": slug,
                "support_email": support_email,
                "website_url": website_url,
                "org_id": org_id,
            },
        )
        return resp["data"]


class _AppResource:
    def __init__(self, client: OpenSkillClient):
        self._c = client

    async def list(self, **params: Any) -> dict:
        return await self._c.get("/developer/apps", **params)

    async def get(self, app_id: str) -> dict:
        resp = await self._c.get(f"/developer/apps/{app_id}")
        return resp["data"]

    async def create(
        self,
        *,
        name: str,
        slug: str,
        category: str,
        description: str | None = None,
        visibility: str = "private",
        manifest: dict | None = None,
    ) -> dict:
        resp = await self._c.post(
            "/developer/apps",
            {
                "name": name,
                "slug": slug,
                "category": category,
                "description": description,
                "visibility": visibility,
                "manifest": manifest,
            },
        )
        return resp["data"]

    async def update(self, app_id: str, **data: Any) -> dict:
        resp = await self._c.patch(f"/developer/apps/{app_id}", data)
        return resp["data"]

    async def create_version(
        self,
        app_id: str,
        *,
        version: str,
        manifest: dict,
        content_hash: str,
        changelog: str | None = None,
        signature: str | None = None,
    ) -> dict:
        resp = await self._c.post(
            f"/developer/apps/{app_id}/versions",
            {
                "version": version,
                "manifest": manifest,
                "content_hash": content_hash,
                "changelog": changelog,
                "signature": signature,
            },
        )
        return resp["data"]

    async def list_versions(self, app_id: str, **params: Any) -> dict:
        return await self._c.get(f"/developer/apps/{app_id}/versions", **params)

    async def submit_for_review(self, app_id: str) -> dict:
        resp = await self._c.post(f"/developer/apps/{app_id}/submit")
        return resp["data"]

    async def publish(self, app_id: str) -> dict:
        resp = await self._c.post(f"/developer/apps/{app_id}/publish")
        return resp["data"]

    async def create_api_key(
        self, app_id: str, *, name: str, scopes: list[str] | None = None
    ) -> dict:
        resp = await self._c.post(
            f"/developer/apps/{app_id}/api-keys",
            {"name": name, "scopes": scopes or []},
        )
        return resp["data"]

    async def list_api_keys(self, app_id: str) -> list[dict]:
        resp = await self._c.get(f"/developer/apps/{app_id}/api-keys")
        return resp["data"]

    async def get_stats(self, app_id: str) -> dict:
        resp = await self._c.get(f"/developer/apps/{app_id}/stats")
        return resp["data"]

    async def run_conformance(self, app_id: str) -> dict:
        resp = await self._c.get(f"/developer/apps/{app_id}/conformance")
        return resp["data"]


class _MarketplaceResource:
    def __init__(self, client: OpenSkillClient):
        self._c = client

    async def browse(self, **params: Any) -> dict:
        return await self._c.get("/marketplace/apps", **params)

    async def get(self, app_id: str) -> dict:
        resp = await self._c.get(f"/marketplace/apps/{app_id}")
        return resp["data"]
