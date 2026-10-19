"""R493: app-WIDE OpenAPI sweep (companion to e2e_fuzz_fabric phase 15).

The fabric phase 15 found 33 production-dead talent routes only because its
path markers happened to include them. This walks EVERY /api/v1 path in the
live spec with hostile path params, hostile query values and a skeletal
body, asserting the platform invariant: never a 5xx except the typed
UPSTREAM_UNREACHABLE 502 (dead upstream in a probe environment is a
legitimate outcome, not a crash).

Usage: api on :8443 (APP_ENV=test), then
  E2E_INTG_API=http://localhost:8443/api/v1 PYTHONPATH=. \
      uv run python tests/e2e_fuzz_appwide.py
"""

import asyncio
import os
import re
import uuid

import httpx

API = os.environ.get("E2E_INTG_API", "http://localhost:8443/api/v1")
HOST = API.rsplit("/api/v1", 1)[0]

PASS = 0
FAIL = 0


def check(label: str, ok: bool, detail: str = "") -> None:
    global PASS, FAIL
    if ok:
        PASS += 1
    else:
        FAIL += 1
        print(f" FAIL {label}: {detail[:220]}")


HOSTILE_PARAMS = ["0" * 26, "..%2f..%2fetc", "‮" * 12, "x" * 300, "%00"]
HOSTILE_QUERIES = [
    {"limit": "-1"},
    {"limit": "999999999999999999999"},
    {"cursor": "\x00junk"},
    {"status": ["a", "b"]},
]
# Paths that mutate global/auth state in ways that would break the probe
# account itself mid-run.
SKIP = re.compile(r"/auth/(logout|change-password)|/dev/|/admin/impersonate")


async def main() -> int:
    seen_5xx: dict[str, str] = {}
    async with httpx.AsyncClient(timeout=15.0, trust_env=False) as c:
        r = await c.post(
            f"{API}/auth/register",
            json={
                "email": f"aw-{uuid.uuid4().hex[:10]}@test.com",
                "password": "Test1234!",
                "display_name": "AW",
            },
        )
        tok = r.json()["access_token"]
        h = {"Authorization": f"Bearer {tok}"}
        r = await c.post(f"{API}/orgs", json={"name": f"AW {uuid.uuid4().hex[:10]}"}, headers=h)
        org = r.json()["data"]["id"]

        from app.main import app as _app

        spec_paths = _app.openapi()["paths"]
        total = 0
        for raw_path, methods in sorted(spec_paths.items()):
            if SKIP.search(raw_path):
                continue
            for method, _op in methods.items():
                if method not in ("get", "post", "patch", "put", "delete"):
                    continue
                for hostile in HOSTILE_PARAMS:
                    url = raw_path.replace("{org_id}", org)
                    if "{" in url:
                        url = re.sub(r"\{[^}]+\}", hostile, url)
                    elif hostile != HOSTILE_PARAMS[0]:
                        break
                    kwargs: dict = {"headers": h}
                    if method in ("post", "patch", "put"):
                        kwargs["json"] = {"a": None}
                    try:
                        rr = await getattr(c, method)(f"{HOST}{url}", **kwargs)
                    except httpx.HTTPError as exc:
                        check(f"transport: {method} {url[-60:]}", False, type(exc).__name__)
                        continue
                    total += 1
                    if rr.status_code >= 500:
                        body = rr.text[:160]
                        if '"UPSTREAM_UNREACHABLE"' in body and rr.status_code == 502:
                            continue  # typed dead-upstream outcome — legitimate here
                        seen_5xx.setdefault(f"{method.upper()} {raw_path}", body)
                if method == "get" and "{" not in raw_path:
                    for q in HOSTILE_QUERIES:
                        rr = await c.get(f"{HOST}{raw_path}", params=q, headers=h)
                        total += 1
                        if rr.status_code >= 500:
                            seen_5xx.setdefault(f"GET? {raw_path} {q}", rr.text[:160])

        for route, body in sorted(seen_5xx.items()):
            check(f"5xx: {route}", False, body)
        check(f"app-wide sweep covered {total} requests", total > 800, str(total))
        check("no unexplained 5xx app-wide", not seen_5xx, f"{len(seen_5xx)} routes")
    print(f"\ntotal={total} PASS={PASS} FAIL={FAIL}")
    return 0 if FAIL == 0 else 1


raise SystemExit(asyncio.run(main()))
