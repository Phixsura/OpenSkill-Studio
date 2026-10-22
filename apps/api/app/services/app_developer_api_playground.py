"""Developer API playground — interactive API testing data."""

PLAYGROUND_ENDPOINTS = [
    {"method": "GET", "path": "/api/v1/developer/accounts/me", "description": "Get your developer account", "auth": True},
    {"method": "GET", "path": "/api/v1/developer/apps", "description": "List your apps", "auth": True},
    {"method": "POST", "path": "/api/v1/developer/apps", "description": "Create a new app", "auth": True, "body": {"name": "My App", "slug": "my-app", "category": "connector"}},
    {"method": "GET", "path": "/api/v1/marketplace/apps", "description": "Search marketplace", "auth": False},
    {"method": "GET", "path": "/api/v1/marketplace/featured", "description": "Featured apps", "auth": False},
]


def get_playground_endpoints() -> list[dict]:
    return PLAYGROUND_ENDPOINTS


def build_curl_command(endpoint: dict, *, api_key: str = "$API_KEY", base_url: str = "https://api.openskill.studio") -> str:
    method = endpoint.get("method", "GET")
    path = endpoint.get("path", "/")
    curl = f'curl -X {method} "{base_url}{path}"'
    if endpoint.get("auth"):
        curl += f' \\\n  -H "Authorization: Bearer {api_key}"'
    if endpoint.get("body"):
        import json
        curl += ' \\\n  -H "Content-Type: application/json"'
        curl += f" \\\n  -d '{json.dumps(endpoint['body'])}'"
    return curl
