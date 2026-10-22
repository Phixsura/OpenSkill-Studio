"""SDK codegen — generate typed SDK clients from app API definitions."""


def generate_typescript_client(*, app: dict, endpoints: list[dict]) -> str:
    lines = [f"// Auto-generated SDK for {app['name']}", f"// Version: {app.get('version', '1.0.0')}", "",
             "export class AppClient {", "  constructor(private baseUrl: string, private token: string) {}", ""]
    for ep in endpoints:
        method = ep.get("method", "GET").upper()
        name = ep.get("operation_id", ep.get("path", "").replace("/", "_").strip("_"))
        path = ep.get("path", "/")
        lines.append(f"  async {name}(): Promise<any> {{")
        lines.append(f'    const res = await fetch(`${{this.baseUrl}}{path}`, {{')
        lines.append(f'      method: "{method}",')
        lines.append(f'      headers: {{ Authorization: `Bearer ${{this.token}}`, "Content-Type": "application/json" }},')
        lines.append(f"    }});")
        lines.append(f"    return res.json();")
        lines.append(f"  }}")
        lines.append("")
    lines.append("}")
    return "\n".join(lines)


def generate_python_client(*, app: dict, endpoints: list[dict]) -> str:
    lines = [f'"""Auto-generated SDK for {app["name"]}"""', "", "import httpx", "",
             "class AppClient:", '    def __init__(self, base_url: str, token: str) -> None:',
             "        self._base = base_url", "        self._token = token",
             '        self._headers = {"Authorization": f"Bearer {token}"}', ""]
    for ep in endpoints:
        method = ep.get("method", "GET").lower()
        name = ep.get("operation_id", ep.get("path", "").replace("/", "_").strip("_"))
        path = ep.get("path", "/")
        lines.append(f'    def {name}(self) -> dict:')
        lines.append(f'        r = httpx.{method}(f"{{self._base}}{path}", headers=self._headers)')
        lines.append(f'        return r.json()')
        lines.append("")
    return "\n".join(lines)


def list_supported_languages() -> list[str]:
    return ["typescript", "python", "go", "ruby", "java"]
