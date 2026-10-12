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


_CALL_RE = re.compile(
    r"apiWithAuth(?:<[^>]*>)?\(\s*`([^`]+)`\s*,\s*\{[^}]*method:\s*\"([A-Z]+)\"",
    re.DOTALL,
)


def _page_calls_with_methods() -> set[tuple[str, str]]:
    """(path-pattern, METHOD) pairs for every non-GET page call."""
    calls: set[tuple[str, str]] = set()
    for page in sorted(WEB_INTG.rglob("*.tsx")):
        src = page.read_text()
        m = _BASE_RE.search(src)
        base = m.group(1) if m else "/orgs/${orgId}/integrations"
        for tmpl, method in _CALL_RE.findall(src):
            t = tmpl.replace("${base}", base).split("?", 1)[0]
            t = re.sub(r"\$\{[^}]*$", "", t)
            if not t.startswith("/orgs/"):
                continue
            t = _VAR_RE.sub("{param}", t).rstrip("/")
            calls.add((t, method))
    return calls


def _route_methods() -> list[tuple[list[str], set[str]]]:
    from app.main import app

    out = []
    for path, ops in app.openapi()["paths"].items():
        p = path.removeprefix("/api/v1")
        out.append(
            (
                [seg for seg in p.split("/") if seg],
                {m.upper() for m in ops},
            )
        )
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


def test_every_fabric_mutation_call_uses_a_served_method():
    """A path can exist while the page's METHOD is wrong (PATCH vs PUT) —
    match each explicit-method call against the operations the route
    actually serves."""
    calls = _page_calls_with_methods()
    assert calls, "method extraction found no calls — the regex rotted"
    table = _route_methods()
    bad = []
    for path, method in sorted(calls):
        segs = [s for s in path.split("/") if s]
        served: set[str] = set()
        for pat, methods in table:
            if len(pat) != len(segs):
                continue
            if all(
                ps.startswith("{") or cs == "{param}" or ps == cs
                for ps, cs in zip(pat, segs, strict=True)
            ):
                served |= methods
        if method not in served:
            bad.append(f"{method} {path} (served: {sorted(served) or 'nothing'})")
    assert bad == [], f"web pages use methods the API does not serve: {bad}"
