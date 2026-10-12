"""R287 (R231 drift-guard class, cross-layer): every API path the fabric
web pages call must resolve to a real FastAPI route.

The R63-R71 login-journey defects (a redirect to a URL that never existed)
were exactly this class: the frontend references a path nobody serves, all
backend tests stay green, and the 404 only fires in production. This test
extracts every template-literal API call from the five fabric pages,
expands the shared ``base`` prefix, and matches each against the mounted
route table — so a renamed/removed endpoint breaks CI, not an admin.
"""

from __future__ import annotations

import pathlib
import re

WEB_INTG = (
    pathlib.Path(__file__).resolve().parents[3]
    / "apps/web/src/app/(dashboard)/dashboard/orgs/[orgId]/integrations"
)

_TEMPLATE_RE = re.compile(r"`(/orgs/\$\{orgId\}[^`]*|\$\{base\}[^`]*)`")
_BASE_RE = re.compile(r"const base = `(/orgs/\$\{orgId\}[^`]*)`")
_VAR_RE = re.compile(r"\$\{[^}]+\}")


def _page_paths() -> set[str]:
    paths: set[str] = set()
    for page in sorted(WEB_INTG.rglob("*.tsx")):
        src = page.read_text()
        m = _BASE_RE.search(src)
        base = m.group(1) if m else "/orgs/${orgId}/integrations"
        for tmpl in _TEMPLATE_RE.findall(src):
            t = tmpl.replace("${base}", base)
            t = t.split("?", 1)[0]  # query strings are not routing
            # a nested-ternary template (`...${flag ? `?q=1` : ""}`) stops
            # the outer capture mid-interpolation — drop the unclosed tail.
            t = re.sub(r"\$\{[^}]*$", "", t)
            if not t.startswith("/orgs/"):
                continue
            # every interpolation is a path parameter
            t = _VAR_RE.sub("{param}", t)
            t = t.rstrip("/")
            if t == _VAR_RE.sub("{param}", base):
                continue  # the shared prefix itself, not a call
            paths.add(t)
    return paths


def _route_patterns() -> list[list[str]]:
    # app.routes holds lazy _IncludedRouter entries on current FastAPI —
    # the OpenAPI schema is the resolved, authoritative route table.
    from app.main import app

    out = []
    for path in app.openapi()["paths"]:
        p = path.removeprefix("/api/v1")
        out.append([seg for seg in p.split("/") if seg])
    return out


def _matches(call: str, patterns: list[list[str]]) -> bool:
    segs = [s for s in call.split("/") if s]
    for pat in patterns:
        if len(pat) != len(segs):
            continue
        ok = True
        for ps, cs in zip(pat, segs, strict=True):
            if ps.startswith("{") or cs == "{param}":
                continue
            if ps != cs:
                ok = False
                break
        if ok:
            return True
    return False


def test_every_fabric_page_api_call_has_a_route():
    calls = _page_paths()
    assert calls, "extraction found no API calls — the regexes rotted"
    patterns = _route_patterns()
    missing = sorted(c for c in calls if not _matches(c, patterns))
    assert missing == [], f"web pages call routes nobody serves: {missing}"
