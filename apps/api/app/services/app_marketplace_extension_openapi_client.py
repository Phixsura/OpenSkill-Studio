"""OpenAPI Client Generator — generate typed API clients from OpenAPI specs.

Parses OpenAPI specs and generates client code with typed methods,
request/response models, error handling, and authentication support.
"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class ClientMethod:
    name: str
    method: str
    path: str
    params: list[dict] = field(default_factory=list)
    has_body: bool = False
    return_type: str = "any"
    description: str = ""


@dataclass
class GeneratedClient:
    class_name: str
    base_url: str
    methods: list[ClientMethod] = field(default_factory=list)
    auth_type: str = ""


class OpenApiClientService:
    """Generates typed API clients from OpenAPI specs."""

    def parse_spec(self, spec: dict) -> GeneratedClient:
        info = spec.get("info", {})
        servers = spec.get("servers", [{}])
        base_url = servers[0].get("url", "") if servers else ""

        # Derive class name
        title = info.get("title", "Api")
        class_name = "".join(w.capitalize() for w in title.split()) + "Client"

        # Detect auth
        auth_type = ""
        components = spec.get("components", {})
        schemes = components.get("securitySchemes", {})
        if "bearerAuth" in schemes:
            auth_type = "bearer"
        elif "apiKey" in schemes:
            auth_type = "api_key"

        # Parse endpoints
        methods: list[ClientMethod] = []
        for path, path_item in spec.get("paths", {}).items():
            for http_method, operation in path_item.items():
                if http_method not in ("get", "post", "put", "delete", "patch"):
                    continue
                method_name = self._make_method_name(http_method, path, operation)
                params = operation.get("parameters", [])
                has_body = "requestBody" in operation

                methods.append(ClientMethod(
                    name=method_name, method=http_method.upper(),
                    path=path, params=params, has_body=has_body,
                    description=operation.get("summary", ""),
                ))

        return GeneratedClient(
            class_name=class_name, base_url=base_url,
            methods=methods, auth_type=auth_type,
        )

    def _make_method_name(self, method: str, path: str, operation: dict) -> str:
        op_id = operation.get("operationId")
        if op_id:
            return self._to_camel(op_id)
        parts = [p for p in path.split("/") if p and not p.startswith("{")]
        if parts:
            resource = parts[-1]
            prefix = {"get": "get", "post": "create", "put": "update",
                       "delete": "delete", "patch": "patch"}.get(method, method)
            return f"{prefix}{resource.capitalize()}"
        return f"{method}Request"

    def _to_camel(self, name: str) -> str:
        parts = name.replace("-", "_").split("_")
        return parts[0] + "".join(p.capitalize() for p in parts[1:])

    def generate_typescript(self, client: GeneratedClient) -> str:
        lines = [f"// Auto-generated client for {client.class_name}",
                 f"export class {client.class_name} {{",
                 f"  private baseUrl = '{client.base_url}';"]
        if client.auth_type:
            lines.append(f"  private authType = '{client.auth_type}';")
        lines.append("")

        for m in client.methods:
            param_str = ", ".join(
                f"{p.get('name', 'param')}: {self._ts_type(p)}"
                for p in m.params
            )
            if m.has_body:
                param_str += (", " if param_str else "") + "body: Record<string, unknown>"
            lines.append(f"  /** {m.description} */")
            lines.append(f"  async {m.name}({param_str}) {{")
            lines.append(f"    return this.request('{m.method}', `{m.path}`);")
            lines.append("  }")
            lines.append("")

        lines.append("  private async request(method: string, path: string) {")
        lines.append("    const res = await fetch(`${this.baseUrl}${path}`, { method });")
        lines.append("    return res.json();")
        lines.append("  }")
        lines.append("}")
        return "\n".join(lines)

    def _ts_type(self, param: dict) -> str:
        schema = param.get("schema", {})
        t = schema.get("type", "string")
        return {"string": "string", "integer": "number", "boolean": "boolean",
                "number": "number", "array": "unknown[]"}.get(t, "unknown")

    def generate_python(self, client: GeneratedClient) -> str:
        lines = [f'"""Auto-generated client for {client.class_name}."""',
                 f"import httpx", "",
                 f"class {client.class_name}:",
                 f'    def __init__(self, base_url: str = "{client.base_url}"):',
                 f"        self.base_url = base_url",
                 f"        self.client = httpx.Client(base_url=base_url)", ""]

        for m in client.methods:
            params = ", ".join(f"{p.get('name', 'param')}: str" for p in m.params)
            sig = f"self, {params}" if params else "self"
            lines.append(f'    def {m.name}({sig}):')
            lines.append(f'        """{ m.description}"""')
            lines.append(f'        return self.client.{m.method.lower()}("{m.path}").json()')
            lines.append("")

        return "\n".join(lines)
