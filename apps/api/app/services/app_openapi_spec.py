"""OpenAPI spec generator for developer platform apps."""


def generate_app_openapi(*, app_name: str, app_slug: str, version: str, permissions: list[str], endpoints: list[dict] | None = None) -> dict:
    """Generate a minimal OpenAPI 3.0 spec for an app's API surface."""
    paths = {}
    for ep in (endpoints or []):
        paths[ep.get("path", "/")] = {
            ep.get("method", "get").lower(): {
                "summary": ep.get("summary", ""),
                "security": [{"apiKey": []}],
                "responses": {"200": {"description": "Success"}},
            }
        }
    return {
        "openapi": "3.0.3",
        "info": {"title": f"{app_name} API", "version": version},
        "servers": [{"url": f"/api/v1/apps/{app_slug}"}],
        "paths": paths,
        "components": {
            "securitySchemes": {
                "apiKey": {"type": "apiKey", "in": "header", "name": "X-API-Key"},
            }
        },
        "x-permissions": permissions,
    }
