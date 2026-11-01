"""Extension API Playground V2 — interactive API explorer with snippets."""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class ApiEndpoint:
    path: str
    method: str
    description: str
    params: list[dict] = field(default_factory=list)
    example_request: dict = field(default_factory=dict)
    example_response: dict = field(default_factory=dict)


@dataclass
class CodeSnippet:
    language: str
    code: str


class ExtApiPlaygroundV2Service:
    def __init__(self):
        self._endpoints: dict[str, list[ApiEndpoint]] = {}  # ext_id -> endpoints

    def register_endpoint(self, extension_id: str, path: str, method: str,
                          description: str, params: list[dict] | None = None,
                          example_req: dict | None = None,
                          example_resp: dict | None = None) -> ApiEndpoint:
        ep = ApiEndpoint(path=path, method=method, description=description,
                         params=params or [],
                         example_request=example_req or {},
                         example_response=example_resp or {})
        if extension_id not in self._endpoints:
            self._endpoints[extension_id] = []
        self._endpoints[extension_id].append(ep)
        return ep

    def get_endpoints(self, extension_id: str) -> list[ApiEndpoint]:
        return self._endpoints.get(extension_id, [])

    def generate_snippet(self, endpoint: ApiEndpoint, language: str) -> CodeSnippet:
        if language == "curl":
            code = f'curl -X {endpoint.method} "https://api.openskill.dev{endpoint.path}"'
            if endpoint.example_request:
                code += f" \\\n  -H 'Content-Type: application/json' \\\n  -d '{{}}'  "
        elif language == "python":
            code = f'import requests\nresponse = requests.{endpoint.method.lower()}("https://api.openskill.dev{endpoint.path}")\nprint(response.json())'
        elif language == "javascript":
            code = f'const response = await fetch("https://api.openskill.dev{endpoint.path}", {{\n  method: "{endpoint.method}"\n}});\nconst data = await response.json();'
        else:
            code = f"// {endpoint.method} {endpoint.path}"
        return CodeSnippet(language=language, code=code)

    def search_endpoints(self, extension_id: str, query: str) -> list[ApiEndpoint]:
        q = query.lower()
        return [e for e in self.get_endpoints(extension_id)
                if q in e.path.lower() or q in e.description.lower()]
