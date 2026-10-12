"""Bounded live-HTTP fuzzer over the fabric surface (R353).

Schema-light, seeded, deterministic: for every fabric route it throws
hostile-but-cheap payload shapes (wrong JSON types, deep nesting, huge
strings, NULs, unicode, arrays-for-objects, empty bodies, junk ids in
paths) and asserts the ONE invariant the whole platform promises:
**never a 5xx** — every rejection is a clean enveloped 4xx.

Usage: api on :8443 (APP_ENV=test), then
  E2E_INTG_API=http://localhost:8443/api/v1 PYTHONPATH=. \
      uv run python tests/e2e_fuzz_fabric.py
"""

import asyncio
import json
import os
import random
import uuid

import httpx

API = os.environ.get("E2E_INTG_API", "http://localhost:8443/api/v1")
SEED = int(os.environ.get("FUZZ_SEED", "43"))
PASS = 0
FAIL = 0
rng = random.Random(SEED)


def check(label: str, ok: bool, detail: str = "") -> None:
    global PASS, FAIL
    if ok:
        PASS += 1
    else:
        FAIL += 1
        print(f" FAIL {label}: {detail[:220]}")


HOSTILE_BODIES = [
    None,
    {},
    [],
    "just a string",
    123,
    True,
    {"a": None},
    {"__proto__": {"x": 1}},
    {"name": "\x00nul"},
    {"name": "x" * 4000},
    {"name": {"nested": {"deep": ["wrong", {"type": 1}]}}},
    {"url": "not-a-url", "events": "not-a-list"},
    {"events": [{"obj": "not-a-string"}]},
    {"protocol": [], "oidc_issuer": {"a": 1}},
    {"domain": ["a", "b"]},
    {"user_id": 12345, "enabled": "yes"},
    {"kind": None, "mode": 3.14},
    {"schedule": {"cron": "* * * * *"}},
    {"field_allowlist": "id,type", "anonymize": ["hash"]},
    {"connection_id": True, "model": [], "direction": {}},
    {"group_map": {"G": "student"}},
    {"deployment_ids": "not-a-list", "issuer": 7},
    {"action": "", "user_id": ""},
    {"status": "💥", "name": "💥" * 500},
    {"attribute_map": [["email", "mail"]]},
]

JUNK_IDS = ["x", "0" * 26, "💥", "..%2f..", "null", str(uuid.uuid4()), "-1", "%00"]


def _mutate(obj):
    """One random structural mutation of a valid-ish body."""
    choice = rng.randrange(5)
    if choice == 0:
        return rng.choice(HOSTILE_BODIES)
    if not isinstance(obj, dict) or not obj:
        return rng.choice(HOSTILE_BODIES)
    out = dict(obj)
    k = rng.choice(list(out))
    if choice == 1:
        out[k] = rng.choice([None, [], {}, 1e308, "x" * 4000, ["a"] * 50])
    elif choice == 2:
        out.pop(k)
    elif choice == 3:
        out["extra_" + k] = out.get(k)
    else:
        out[k] = {"a": [out.get(k)] * 10}
    return out


async def main() -> None:
    async with httpx.AsyncClient(timeout=10.0, trust_env=False) as c:
        email = f"fuzz-{uuid.uuid4().hex[:10]}@test.com"
        r = await c.post(
            f"{API}/auth/register",
            json={"email": email, "password": "Test1234!", "display_name": "Fuzz"},
        )
        tok = r.json()["access_token"]
        h = {"Authorization": f"Bearer {tok}"}
        r = await c.post(f"{API}/orgs", json={"name": f"Fuzz {uuid.uuid4().hex[:6]}"}, headers=h)
        org = r.json()["data"]["id"]
        base = f"{API}/orgs/{org}/integrations"

        # mint a SCIM token for the scim surface
        r = await c.post(f"{base}/scim-tokens", json={"name": "f", "group_map": {}}, headers=h)
        scim_raw = r.json()["data"]["token"]
        sh = {"Authorization": f"Bearer {scim_raw}", "Content-Type": "application/scim+json"}

        targets = [
            ("POST", f"{base}/domains", {"domain": "fuzz.example.edu"}, h),
            ("POST", f"{base}/sso-connections",
             {"protocol": "oidc", "oidc_issuer": "https://idp.example.com",
              "oidc_client_id": "c"}, h),
            ("POST", f"{base}/scim-tokens", {"name": "t", "group_map": {}}, h),
            ("POST", f"{base}/break-glass", {"user_id": "0" * 26, "enabled": True}, h),
            ("POST", f"{base}/connections",
             {"provider_key": "generic_rest", "name": "n", "config": {},
              "base_url": "https://x.example.com"}, h),
            ("POST", f"{base}/mapping-profiles",
             {"name": "m", "direction": "inbound", "model": "roster.class",
              "document": {"fields": [{"target": "t", "path": "a"}]}}, h),
            ("POST", f"{base}/sync-profiles",
             {"connection_id": "0" * 26, "name": "p", "model": "roster.class",
              "direction": "pull", "mapping_profile_id": None}, h),
            ("POST", f"{base}/export-streams", {"name": "s", "dataset": "events"}, h),
            ("POST", f"{API}/orgs/{org}/webhooks",
             {"url": "https://sink.example.com/h",
              "events": ["com.openskill.project.approved.v1"]}, h),
            ("POST", f"{base}/lti/registrations",
             {"issuer": "https://lms.example.com", "client_id": "c",
              "auth_login_url": "https://lms.example.com/a",
              "auth_token_url": "https://lms.example.com/t",
              "jwks_url": "https://lms.example.com/j",
              "deployment_ids": ["d1"]}, h),
            ("POST", f"{API}/scim/v2/Users",
             {"userName": "u@fuzz.example.edu", "displayName": "U"}, sh),
            ("POST", f"{API}/scim/v2/Groups", {"displayName": "G"}, sh),
            ("POST", f"{API}/scim/v2/Bulk",
             {"schemas": ["urn:ietf:params:scim:api:messages:2.0:BulkRequest"],
              "Operations": [{"method": "POST", "path": "/Users",
                              "data": {"userName": "b@fuzz.example.edu"}}]}, sh),
        ]

        n_5xx = 0
        total = 0
        import time as _t
        _t0 = _t.monotonic()
        # 1) hostile bodies on every mutating route
        for method, url, good, headers in targets:
            for _ in range(10):
                body = _mutate(good)
                try:
                    rr = await c.request(method, url, json=body, headers=headers)
                except httpx.HTTPError as exc:
                    check(f"{method} {url.split('/integrations')[-1][:40]}", False,
                          f"transport {type(exc).__name__} body={json.dumps(body, default=str)[:120]}")
                    continue
                total += 1
                if rr.status_code >= 500:
                    n_5xx += 1
                    check(
                        f"5xx: {method} {url[-50:]}",
                        False,
                        f"{rr.status_code} body={json.dumps(body, default=str)[:160]} resp={rr.text[:120]}",
                    )

        # 2) junk ids on GET/DELETE/PATCH paths
        id_routes = [
            ("GET", f"{base}/domains"),
            ("DELETE", f"{base}/domains/{{id}}"),
            ("PATCH", f"{base}/sso-connections/{{id}}"),
            ("DELETE", f"{base}/sso-connections/{{id}}"),
            ("DELETE", f"{base}/scim-tokens/{{id}}"),
            ("PATCH", f"{base}/connections/{{id}}"),
            ("DELETE", f"{base}/connections/{{id}}"),
            ("PATCH", f"{base}/sync-profiles/{{id}}"),
            ("DELETE", f"{base}/sync-profiles/{{id}}"),
            ("PATCH", f"{base}/export-streams/{{id}}"),
            ("POST", f"{base}/export-streams/{{id}}/run"),
            ("POST", f"{base}/sync-runs/{{id}}/cancel"),
            ("GET", f"{API}/scim/v2/Users/{{id}}"),
            ("DELETE", f"{API}/scim/v2/Users/{{id}}"),
            ("PATCH", f"{API}/scim/v2/Groups/{{id}}"),
        ]
        for method, tmpl in id_routes:
            for junk in JUNK_IDS:
                url = tmpl.replace("{id}", junk)
                headers = sh if "/scim/v2/" in url else h
                body = {"Operations": []} if method == "PATCH" and "/scim/" in url else ({} if method in ("PATCH", "POST") else None)
                try:
                    rr = await c.request(method, url, json=body, headers=headers)
                except httpx.HTTPError as exc:
                    check(f"{method} {url[-40:]}", False, f"transport {type(exc).__name__}")
                    continue
                total += 1
                if rr.status_code >= 500:
                    n_5xx += 1
                    check(f"5xx: {method} {url[-50:]}", False,
                          f"{rr.status_code} resp={rr.text[:140]}")

        check(f"no 5xx across {total} hostile requests", n_5xx == 0, f"n_5xx={n_5xx}")
        print(f"elapsed={_t.monotonic()-_t0:.1f}s")
        print(f"\nseed={SEED} total={total} PASS={PASS} FAIL={FAIL}")
        raise SystemExit(0 if FAIL == 0 else 1)


asyncio.run(main())
