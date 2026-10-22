"""SDK codegen — generate typed SDK clients from app API definitions."""

import re

_IDENTIFIER_RE = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')
_PATH_RE = re.compile(r'^/[A-Za-z0-9_\-./{}]*$')
_VALID_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE"}


def _safe_identifier(name: str) -> str:
    clean = re.sub(r'[^A-Za-z0-9_]', '_', name)
    if not clean or clean[0].isdigit():
        clean = f"fn_{clean}"
    return clean


def _safe_path(path: str) -> str:
    if not _PATH_RE.match(path):
        return "/invalid"
    return path


def _safe_method(method: str) -> str:
    m = method.upper()
    return m if m in _VALID_METHODS else "GET"


def _safe_version(v: str) -> str:
    s = str(v)
    return s if re.fullmatch(r"[0-9A-Za-z.+\-]{1,32}", s) else "1.0.0"

def generate_typescript_client(*, app: dict, endpoints: list[dict]) -> str:
    app_name = re.sub(r'[^w -]', '', str(app.get('name', 'App')))[:50]
    lines = [f"// Auto-generated SDK for {app_name}", f"// Version: {_safe_version(app.get('version', '1.0.0'))}", "",
             "export class AppClient {", "  constructor(private baseUrl: string, private token: string) {}", ""]
    for ep in endpoints:
        method = _safe_method(ep.get("method", "GET"))
        name = _safe_identifier(ep.get("operation_id", ep.get("path", "").replace("/", "_").strip("_")))
        path = repr(_safe_path(ep.get("path", "/")))
        lines.append(f"  async {name}(): Promise<any> {{")
        lines.append(f'    const res = await fetch(this.baseUrl + {path}, {{')
        lines.append(f'      method: "{method}",')
        lines.append(f'      headers: {{ Authorization: `Bearer ${{this.token}}`, "Content-Type": "application/json" }},')
        lines.append(f"    }});")
        lines.append(f"    return res.json();")
        lines.append(f"  }}")
        lines.append("")
    lines.append("}")
    return "\n".join(lines)


def generate_python_client(*, app: dict, endpoints: list[dict]) -> str:
    app_name = re.sub(r'[^w -]', '', str(app.get('name', 'App')))[:50]
    lines = [f'"""Auto-generated SDK for {app_name}"""', "", "import httpx", "",
             "class AppClient:", '    def __init__(self, base_url: str, token: str) -> None:',
             "        self._base = base_url", "        self._token = token",
             '        self._headers = {"Authorization": f"Bearer {token}"}', ""]
    for ep in endpoints:
        method = _safe_method(ep.get("method", "GET")).lower()
        name = _safe_identifier(ep.get("operation_id", ep.get("path", "").replace("/", "_").strip("_")))
        path = repr(_safe_path(ep.get("path", "/")))
        lines.append(f'    def {name}(self) -> dict:')
        lines.append(f'        r = httpx.{method}(self._base + {path}, headers=self._headers)')
        lines.append(f'        return r.json()')
        lines.append("")
    return "\n".join(lines)


def list_supported_languages() -> list[str]:
    return ["typescript", "python", "go", "ruby", "java"]
