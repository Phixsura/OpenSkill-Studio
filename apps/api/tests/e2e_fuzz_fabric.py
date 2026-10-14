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
import base64
import json
import os
import random
import uuid
from datetime import UTC as _UTC
from datetime import datetime as _dt
from datetime import timedelta as _td

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
    # R389: envelope invariant — every 4xx a JSON admin surface returns
    # must carry the documented {error: {code, message}} envelope (SCIM
    # surfaces speak the SCIM error schema and protocol surfaces return
    # redirects/XML, so only /orgs/ URLs are held to it). One response
    # hook covers every phase.
    malformed_env: list[str] = []

    async def _env_hook(response: httpx.Response) -> None:
        url = str(response.request.url)
        if "/orgs/" not in url or not 400 <= response.status_code < 500:
            return
        await response.aread()
        try:
            body = response.json()
        except Exception:
            malformed_env.append(f"{response.status_code} non-json {url[-60:]}")
            return
        err = body.get("error") if isinstance(body, dict) else None
        if not isinstance(err, dict) or "code" not in err or "message" not in err:
            malformed_env.append(
                f"{response.status_code} bad-envelope {url[-60:]} {str(body)[:80]}"
            )

    async with httpx.AsyncClient(
        timeout=10.0, trust_env=False, event_hooks={"response": [_env_hook]}
    ) as c:
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
            (
                "POST",
                f"{base}/sso-connections",
                {
                    "protocol": "oidc",
                    "oidc_issuer": "https://idp.example.com",
                    "oidc_client_id": "c",
                },
                h,
            ),
            ("POST", f"{base}/scim-tokens", {"name": "t", "group_map": {}}, h),
            ("POST", f"{base}/break-glass", {"user_id": "0" * 26, "enabled": True}, h),
            (
                "POST",
                f"{base}/connections",
                {
                    "provider_key": "generic_rest",
                    "name": "n",
                    "config": {},
                    "base_url": "https://x.example.com",
                },
                h,
            ),
            (
                "POST",
                f"{base}/mapping-profiles",
                {
                    "name": "m",
                    "direction": "inbound",
                    "model": "roster.class",
                    "document": {"fields": [{"target": "t", "path": "a"}]},
                },
                h,
            ),
            (
                "POST",
                f"{base}/sync-profiles",
                {
                    "connection_id": "0" * 26,
                    "name": "p",
                    "model": "roster.class",
                    "direction": "pull",
                    "mapping_profile_id": None,
                },
                h,
            ),
            ("POST", f"{base}/export-streams", {"name": "s", "dataset": "events"}, h),
            (
                "POST",
                f"{API}/orgs/{org}/webhooks",
                {
                    "url": "https://sink.example.com/h",
                    "events": ["com.openskill.project.approved.v1"],
                },
                h,
            ),
            (
                "POST",
                f"{base}/lti/registrations",
                {
                    "issuer": "https://lms.example.com",
                    "client_id": "c",
                    "auth_login_url": "https://lms.example.com/a",
                    "auth_token_url": "https://lms.example.com/t",
                    "jwks_url": "https://lms.example.com/j",
                    "deployment_ids": ["d1"],
                },
                h,
            ),
            (
                "POST",
                f"{API}/scim/v2/Users",
                {"userName": "u@fuzz.example.edu", "displayName": "U"},
                sh,
            ),
            ("POST", f"{API}/scim/v2/Groups", {"displayName": "G"}, sh),
            (
                "POST",
                f"{API}/scim/v2/Bulk",
                {
                    "schemas": ["urn:ietf:params:scim:api:messages:2.0:BulkRequest"],
                    "Operations": [
                        {
                            "method": "POST",
                            "path": "/Users",
                            "data": {"userName": "b@fuzz.example.edu"},
                        }
                    ],
                },
                sh,
            ),
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
                    check(
                        f"{method} {url.split('/integrations')[-1][:40]}",
                        False,
                        f"transport {type(exc).__name__} body={json.dumps(body, default=str)[:120]}",
                    )
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
                body = (
                    {"Operations": []}
                    if method == "PATCH" and "/scim/" in url
                    else ({} if method in ("PATCH", "POST") else None)
                )
                try:
                    rr = await c.request(method, url, json=body, headers=headers)
                except httpx.HTTPError as exc:
                    check(f"{method} {url[-40:]}", False, f"transport {type(exc).__name__}")
                    continue
                total += 1
                if rr.status_code >= 500:
                    n_5xx += 1
                    check(
                        f"5xx: {method} {url[-50:]}",
                        False,
                        f"{rr.status_code} resp={rr.text[:140]}",
                    )

        # 3) hostile HEADERS on a representative authed route
        hostile_headers = [
            {"Authorization": "Bearer " + "A" * 8000},
            {"Authorization": "Basic!!!"},
            {"Content-Type": "application/json; charset=utf-7"},
            {"X-Forwarded-For": "1.2.3.4" * 500},
            {"Authorization": "Bearer " + ".".join(["e30"] * 3)},  # junk JWT
        ]
        for extra in hostile_headers:
            merged = {**h, **{k: v for k, v in extra.items()}}
            try:
                rr = await c.get(f"{base}/domains", headers=merged)
            except httpx.HTTPError as exc:
                # httpx may refuse to SEND illegal header values — that's a
                # client-side wall, not a server defect; skip those.
                if isinstance(exc, (httpx.LocalProtocolError, httpx.InvalidURL)):
                    continue
                check("hostile header transport", False, f"{type(exc).__name__} {extra}")
                continue
            total += 1
            if rr.status_code >= 500:
                n_5xx += 1
                check("5xx: hostile header", False, f"{rr.status_code} {extra} {rr.text[:100]}")

        # 4) unauthenticated PROTOCOL endpoints — the most exposed surface
        proto_cases = [
            ("GET", f"{API}/sso/login", {"params": {"email": "💥@💥"}}),
            ("GET", f"{API}/sso/login", {"params": {"email": "a" * 400 + "@x.com"}}),
            ("GET", f"{API}/sso/login", {"params": {"email": "no-at-sign"}}),
            (
                "GET",
                f"{API}/sso/oidc/authorize",
                {"params": {"connection": "x" * 26, "return_to": "//evil"}},
            ),
            ("GET", f"{API}/sso/oidc/callback", {"params": {"state": "junk", "code": "junk"}}),
            (
                "GET",
                f"{API}/sso/oidc/callback",
                {"params": {"error": "access_denied", "state": "x"}},
            ),
            (
                "POST",
                f"{API}/sso/saml/acs/{'0' * 26}",
                {"data": {"SAMLResponse": "not-base64!!!", "RelayState": "x"}},
            ),
            (
                "POST",
                f"{API}/sso/saml/acs/{'0' * 26}",
                {"data": {"SAMLResponse": "aGVsbG8=", "RelayState": "y" * 600}},
            ),
            (
                "GET",
                f"{API}/sso/saml/slo/{'0' * 26}",
                {"params": {"SAMLRequest": "zzz", "SigAlg": "x", "Signature": "y"}},
            ),
            (
                "POST",
                f"{API}/sso/oidc/backchannel-logout/{'0' * 26}",
                {"data": {"logout_token": "nope.nope.nope"}},
            ),
            (
                "POST",
                f"{API}/sso/oidc/backchannel-logout/{'0' * 26}",
                {"data": {"logout_token": "x" * 5000}},
            ),
            ("GET", f"{API}/lti/jwks", {}),
            (
                "POST",
                f"{API}/lti/login",
                {
                    "data": {
                        "iss": "https://nope.example.com",
                        "login_hint": "x" * 2000,
                        "target_link_uri": "https://x/launch",
                    }
                },
            ),
            ("POST", f"{API}/lti/launch", {"data": {"state": "junk", "id_token": "a.b.c"}}),
        ]
        for method, url, kw in proto_cases:
            try:
                rr = await c.request(method, url, **kw)
            except httpx.HTTPError as exc:
                check(f"proto transport {url[-30:]}", False, type(exc).__name__)
                continue
            total += 1
            if rr.status_code >= 500:
                n_5xx += 1
                check(f"5xx: {method} {url[-45:]}", False, f"{rr.status_code} {rr.text[:140]}")

        # 5) SCIM PATCH path-filter bombs (the op-path mini-grammar)
        rr = await c.post(
            f"{API}/scim/v2/Groups", json={"displayName": f"FZ-{uuid.uuid4().hex[:6]}"}, headers=sh
        )
        gid = rr.json().get("id", "x")
        rr = await c.post(
            f"{API}/scim/v2/Users",
            json={"userName": f"fz-{uuid.uuid4().hex[:6]}@fz.example.edu"},
            headers=sh,
        )
        uid2 = rr.json().get("id", "x")
        path_bombs = [
            'members[value eq "unclosed',
            "members[💥]",
            'members[value eq "a"][value eq "b"]',
            "members[[[[",
            'members[value eq "' + "x" * 3000 + '"]',
            "members[value ne null]",
            "",
            None,
            123,
            "displayName[sub]",
        ]
        for pb in path_bombs:
            ops = [{"op": "remove", "path": pb}]
            rr = await c.patch(f"{API}/scim/v2/Groups/{gid}", json={"Operations": ops}, headers=sh)
            total += 1
            if rr.status_code >= 500:
                n_5xx += 1
                check(
                    "5xx: scim path bomb",
                    False,
                    f"{rr.status_code} path={str(pb)[:60]} {rr.text[:100]}",
                )
            rr = await c.patch(
                f"{API}/scim/v2/Users/{uid2}",
                json={"Operations": [{"op": "replace", "path": pb, "value": False}]},
                headers=sh,
            )
            total += 1
            if rr.status_code >= 500:
                n_5xx += 1
                check(
                    "5xx: user path bomb",
                    False,
                    f"{rr.status_code} path={str(pb)[:60]} {rr.text[:100]}",
                )
        # giant Operations array (over the 100-op bulk cap analogue in PATCH)
        rr = await c.patch(
            f"{API}/scim/v2/Groups/{gid}",
            json={"Operations": [{"op": "remove", "path": 'members[value eq "x"]'}] * 2000},
            headers=sh,
        )
        total += 1
        if rr.status_code >= 500:
            n_5xx += 1
            check("5xx: 2000-op PATCH", False, f"{rr.status_code} {rr.text[:100]}")

        # 6) hostile QUERY params on list endpoints
        q_bombs = [
            "💥",
            "x" * 299,
            "' OR 1=1 --",
            "%00",
            "null",
            "-1",
            "1e308",
            '"; DROP TABLE users; --',
        ]
        list_routes = [
            (f"{base}/deliveries", "status"),
            (f"{base}/events", "type_prefix"),
            (f"{base}/sync-runs", "profile_id"),
            (f"{base}/events", "before"),  # R375 keyset cursor
            (f"{base}/deliveries", "before"),
            (f"{base}/imports", "kind"),
            (f"{API}/scim/v2/Users", "filter"),
            (f"{API}/scim/v2/Groups", "filter"),  # R391
        ]
        for url, param in list_routes:
            for qb in q_bombs:
                headers = sh if "/scim/" in url else h
                rr = await c.get(url, params={param: qb, "count": 5, "limit": 5}, headers=headers)
                total += 1
                if rr.status_code >= 500:
                    n_5xx += 1
                    check(
                        f"5xx: GET {url[-35:]}?{param}",
                        False,
                        f"{rr.status_code} q={qb[:30]} {rr.text[:100]}",
                    )

        # ── phase 7: hostile multipart / CSV-XLSX import surface ──
        # Upload runs the sniffer + parser inline (dry-run preview inside
        # create_job), so binary garbage reaches csv/openpyxl immediately —
        # the one surface phases 1-6 never touched.
        hostile_files = [
            ("empty", b""),
            ("whitespace", b"   \n\t\r\n  "),
            ("nul-cells", b"email,display_name\nnul\x00@x.com,A\x00B\n"),
            ("bad-utf8", b"email,display_name\n\xff\xfe\xfa@x.com,caf\xe9\n"),
            ("bom-only", b"\xef\xbb\xbf"),
            ("bom-csv", b"\xef\xbb\xbfemail,display_name\nb@x.com,B\n"),
            ("huge-cell", b"email,display_name\na@x.com," + b"A" * 300_000 + b"\n"),
            (
                "5000-cols",
                b",".join(b"c%d" % i for i in range(5000)) + b"\n" + b"x," * 4999 + b"x\n",
            ),
            ("unclosed-quote", b'email,display_name\n"unterminated,oops\n'),
            ("cr-only", b"email,display_name\ra@x.com,A\rb@x.com,B"),
            ("formula-inj", b"email,display_name\n=cmd|calc!A1@x.com,=1+1\n"),
            ("png-magic", b"\x89PNG\r\n\x1a\n" + bytes(rng.randrange(256) for _ in range(512))),
            ("fake-xlsx", b"PK\x03\x04" + bytes(rng.randrange(256) for _ in range(2048))),
            ("fake-zip-bomb", b"PK\x03\x04\x14\x00\x00\x00\x08\x00" + b"\x00" * 500),
            ("json-garbage", b'{"rows": [{"email": NaN,}]'),
            ("json-deep", b"[" * 3000 + b"]" * 3000),
            ("binary-random", bytes(rng.randrange(256) for _ in range(4096))),
            ("emoji-headers", "💥,🙂\na@x.com,B\n".encode()),
        ]
        hostile_forms = [
            {"kind": "users", "mode": "partial"},
            {"kind": "💥", "mode": "partial"},
            {"kind": "users", "mode": "\x00"},
            {"kind": "users", "mode": "partial", "header_map": "{not json"},
            {"kind": "users", "mode": "partial", "header_map": '{"a": ' * 100 + "1" + "}" * 100},
            {"kind": "users", "mode": "partial", "header_map": '{"email": ["list","not","str"]}'},
            {"kind": "roster", "mode": "partial"},
        ]
        for fname, fbytes in hostile_files:
            # valid kind so the file always REACHES the parser; hostile
            # form fields get their own pass below
            form = {"kind": rng.choice(["users", "roster"]), "mode": "partial"}
            filename = rng.choice(
                [fname + ".csv", fname + ".xlsx", fname + ".json", fname, "💥.csv"]
            )
            ctype = rng.choice(["text/csv", "application/octet-stream", "application/json", ""])
            try:
                rr = await c.post(
                    f"{base}/imports",
                    data=form,
                    files={"file": (filename, fbytes, ctype or None)},
                    headers=h,
                )
                total += 1
                if rr.status_code >= 500:
                    n_5xx += 1
                    check(
                        f"5xx: import {fname}",
                        False,
                        f"{rr.status_code} form={form} {rr.text[:120]}",
                    )
            except httpx.HTTPError as e:
                total += 1
                check(f"transport error: import {fname}", False, repr(e)[:120])
        benign = b"email,display_name\\na@x.com,A\\n"
        for form in hostile_forms:
            rr = await c.post(
                f"{base}/imports",
                data=form,
                files={"file": ("a.csv", benign, "text/csv")},
                headers=h,
            )
            total += 1
            if rr.status_code >= 500:
                n_5xx += 1
                check(f"5xx: import form {form}", False, f"{rr.status_code} {rr.text[:120]}")

        # malformed multipart envelopes (hand-rolled bodies)
        raw_bodies = [
            ("no-boundary", {"Content-Type": "multipart/form-data"}, b"junk"),
            (
                "bad-boundary",
                {"Content-Type": "multipart/form-data; boundary=XYZ"},
                b"--ABC\r\nContent-Disposition: form-data; name=file\r\n\r\nx\r\n--ABC--",
            ),
            (
                "no-file-part",
                {"Content-Type": "multipart/form-data; boundary=B"},
                b'--B\r\nContent-Disposition: form-data; name="kind"\r\n\r\nusers\r\n--B--\r\n',
            ),
            (
                "truncated",
                {"Content-Type": "multipart/form-data; boundary=B"},
                b'--B\r\nContent-Disposition: form-data; name="file"; filename="a.csv"\r\n',
            ),
        ]
        for label, ct_headers, body in raw_bodies:
            rr = await c.post(f"{base}/imports", content=body, headers={**h, **ct_headers})
            total += 1
            if rr.status_code >= 500:
                n_5xx += 1
                check(f"5xx: multipart {label}", False, f"{rr.status_code} {rr.text[:120]}")

        # ── phase 8: hostile STRUCTURED XML at a real SAML connection ──
        # The proto cases above 404 at connection lookup before any XML is
        # parsed. Mint an ACTIVE SAML connection (throwaway self-signed
        # cert) so XXE / billion-laughs / external-DTD / deep-nesting /
        # unsigned-assertion payloads actually reach the hardened parser
        # and the signature wall (R394).
        from cryptography import x509 as _x509
        from cryptography.hazmat.primitives import hashes as _hashes
        from cryptography.hazmat.primitives import serialization as _ser
        from cryptography.hazmat.primitives.asymmetric import rsa as _rsa
        from cryptography.x509.oid import NameOID as _NameOID

        _key = _rsa.generate_private_key(public_exponent=65537, key_size=2048)
        _name = _x509.Name([_x509.NameAttribute(_NameOID.COMMON_NAME, "fuzz-idp")])
        _cert = (
            _x509.CertificateBuilder()
            .subject_name(_name)
            .issuer_name(_name)
            .public_key(_key.public_key())
            .serial_number(_x509.random_serial_number())
            .not_valid_before(_dt.now(_UTC) - _td(days=1))
            .not_valid_after(_dt.now(_UTC) + _td(days=365))
            .sign(_key, _hashes.SHA256())
        )
        _pem = _cert.public_bytes(_ser.Encoding.PEM).decode()
        rr = await c.post(
            f"{base}/sso-connections",
            json={
                "protocol": "saml",
                "idp_entity_id": "https://fuzz-idp.example.com/meta",
                "idp_sso_url": "https://fuzz-idp.example.com/sso",
                "idp_certificates": [{"pem": _pem}],
            },
            headers=h,
        )
        if rr.status_code == 201:
            saml_conn = rr.json()["data"]["id"]
            await c.patch(
                f"{base}/sso-connections/{saml_conn}", json={"status": "active"}, headers=h
            )
            _laughs = (
                b"""<?xml version="1.0"?>\n<!DOCTYPE lolz [<!ENTITY lol "lol">"""
                + b"".join(
                    b'<!ENTITY lol%d "%s">' % (i, b"&lol%d;" % (i - 1) * 10) for i in range(1, 9)
                )
                + b']><samlp:Response xmlns:samlp="urn:x">&lol8;</samlp:Response>'
            )
            xml_bombs = [
                b"""<?xml version="1.0"?>\n<!DOCTYPE foo [<!ENTITY x SYSTEM "file:///etc/passwd">]>\n<samlp:Response xmlns:samlp="urn:x">&x;</samlp:Response>""",
                _laughs,
                b'<?xml version="1.0"?>' + b"<a>" * 4000 + b"</a>" * 4000,
                b"""<?xml version="1.0"?>\n<!DOCTYPE foo SYSTEM "http://169.254.169.254/meta">\n<samlp:Response xmlns:samlp="urn:x">x</samlp:Response>""",
                b'<?xml version="1.0"?><samlp:Response xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol" ID="_x" Version="2.0"><saml:Assertion xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion" ID="_a"><saml:Subject><saml:NameID>evil@x.com</saml:NameID></saml:Subject></saml:Assertion></samlp:Response>',
                b'<?xml version="1.0"?><r>\x00</r>',
            ]
            for xml in xml_bombs:
                _t1 = _t.monotonic()
                rr = await c.post(
                    f"{API}/sso/saml/acs/{saml_conn}",
                    data={"SAMLResponse": base64.b64encode(xml).decode()},
                )
                _el = _t.monotonic() - _t1
                total += 1
                if rr.status_code >= 500:
                    n_5xx += 1
                    check("5xx: hostile XML at real SAML conn", False, f"{rr.status_code}")
                if _el > 5:
                    check("hostile XML parse stayed fast", False, f"{_el:.1f}s")
        else:
            check("fuzz SAML connection minted", False, f"{rr.status_code} {rr.text[:100]}")

        # ── phase 9: hostile JWTs at /lti/launch with a REAL state ──
        # Same R394 lesson for LTI: a hostile id_token only reaches the JWT
        # validator when the state is real — mint a registration, then a
        # state via /lti/login per attempt (states are single-use).
        import json as _json
        from urllib.parse import parse_qs as _pq
        from urllib.parse import urlparse as _up

        def _b64u(b: bytes) -> str:
            return base64.urlsafe_b64encode(b).rstrip(b"=").decode()

        _issuer = f"https://lms-{uuid.uuid4().hex[:6]}.example.com"
        rr = await c.post(
            f"{base}/lti/registrations",
            json={
                "issuer": _issuer,
                "client_id": "fz-client",
                "auth_login_url": f"{_issuer}/auth",
                "auth_token_url": f"{_issuer}/token",
                "jwks_url": f"{_issuer}/jwks",
                "deployment_ids": ["dep-1"],
            },
            headers=h,
        )
        if rr.status_code == 201:

            def _claims(nonce):
                return {
                    "iss": _issuer,
                    "aud": "fz-client",
                    "sub": "u1",
                    "nonce": nonce,
                    "exp": int(_t.time()) + 300,
                }

            def _jwt(header: dict, payload: dict, sig: bytes = b"") -> str:
                return (
                    _b64u(_json.dumps(header).encode())
                    + "."
                    + _b64u(_json.dumps(payload).encode())
                    + "."
                    + (_b64u(sig) if sig else "")
                )

            jwt_makers = [
                lambda n: _jwt({"alg": "none"}, _claims(n)),
                lambda n: _jwt({"alg": "HS256", "kid": "k"}, _claims(n), b"x" * 64),
                lambda n: _jwt({"alg": "RS256", "kid": "../../etc"}, _claims(n), b"x" * 256),
                lambda n: "💥💥💥",
                lambda n: "..",
            ]
            for make in jwt_makers:
                lr = await c.get(
                    f"{API}/lti/login",
                    params={
                        "iss": _issuer,
                        "client_id": "fz-client",
                        "login_hint": "u1",
                        "target_link_uri": "https://app/launch",
                    },
                )
                if lr.status_code not in (302, 307):
                    check("fuzz LTI state minted", False, f"{lr.status_code}")
                    continue
                q = _pq(_up(lr.headers["location"]).query)
                state = q.get("state", [""])[0]
                nonce = q.get("nonce", [""])[0]
                rr = await c.post(
                    f"{API}/lti/launch", data={"state": state, "id_token": make(nonce)}
                )
                total += 1
                if rr.status_code >= 500:
                    n_5xx += 1
                    check("5xx: hostile LTI JWT", False, f"{rr.status_code} {rr.text[:100]}")
        else:
            check("fuzz LTI registration minted", False, f"{rr.status_code} {rr.text[:100]}")

        # ── phase 9b: hostile logout_tokens at a REAL OIDC connection ──
        rr = await c.post(
            f"{base}/sso-connections",
            json={
                "protocol": "oidc",
                "oidc_issuer": f"https://oidc-{uuid.uuid4().hex[:6]}.example.com",
                "oidc_client_id": "fz-oidc",
                "oidc_client_secret": "s3cret",
            },
            headers=h,
        )
        if rr.status_code == 201:
            oidc_conn = rr.json()["data"]["id"]
            await c.patch(
                f"{base}/sso-connections/{oidc_conn}", json={"status": "active"}, headers=h
            )
            logout_tokens = [
                _jwt({"alg": "none"}, {"iss": "x", "sub": "u", "events": {}}),
                _jwt({"alg": "HS256"}, {"iss": "x"}, b"y" * 64),
                "💥",
                "..",
                "a" * 10_000,
            ]
            for lt in logout_tokens:
                rr = await c.post(
                    f"{API}/sso/oidc/backchannel-logout/{oidc_conn}",
                    data={"logout_token": lt},
                )
                total += 1
                if rr.status_code >= 500:
                    n_5xx += 1
                    check("5xx: hostile logout_token", False, f"{rr.status_code} {rr.text[:100]}")
        else:
            check("fuzz OIDC connection minted", False, f"{rr.status_code} {rr.text[:100]}")

        # ── phase 10: hostile warehouse EXPORT stream configs ──
        # The projection is BUILT from field_allowlist + data.<key> paths and
        # anonymize modes (R130) — hostile allowlists/modes must 4xx, never 5xx.
        export_bodies = [
            {"name": "e1", "dataset": "events", "field_allowlist": ["data." + "x" * 5000]},
            {"name": "e2", "dataset": "events", "field_allowlist": [1, 2, 3]},
            {"name": "e3", "dataset": "events", "field_allowlist": ["../../etc/passwd"]},
            {"name": "e4", "dataset": "events", "anonymize": {"id": "no-such-mode"}},
            {"name": "e5", "dataset": "events", "anonymize": {"\x00": "rot13"}},
            {"name": "e6", "dataset": "events", "anonymize": "not-a-dict"},
            {"name": "e7", "dataset": "\x00bad", "field_allowlist": ["id"]},
            {"name": "e8", "dataset": "events", "schedule": "\x00"},
            {"name": "e9", "dataset": "events", "field_allowlist": ["data." + "a.b.c." * 200]},
            {"name": "\x00", "dataset": "events"},
            {"name": "💥", "dataset": "events", "field_allowlist": ["💥"]},
            {"name": "e12", "dataset": "events", "field_allowlist": ["data.a[" * 50]},
        ]
        for body in export_bodies:
            body = dict(body, name=f"{body['name']}-{uuid.uuid4().hex[:6]}")
            rr = await c.post(f"{base}/export-streams", json=body, headers=h)
            total += 1
            if rr.status_code >= 500:
                n_5xx += 1
                check("5xx: hostile export stream", False, f"{rr.status_code} {rr.text[:120]}")

        # ── phase 11: hostile sync MAPPING documents + preview ──
        # The mapping document carries attacker-shaped jmespath paths and
        # transform chains; create validates, preview applies them to samples.
        mapping_docs = [
            {"fields": [{"target": "x", "path": "a" * 10000}]},
            {"fields": [{"target": "x", "path": "a[[[[[[", }]},
            {"fields": [{"target": "x", "path": "a", "transform": ["eval", "exec", "__import__"]}]},
            {"fields": [{"target": "x", "path": "a", "transform": ["to_int"] * 500}]},
            {"fields": [{"target": "x", "path": "a", "enum_map": {str(i): i for i in range(5000)}}]},
            {"fields": "not-a-list"},
            {"fields": [{"no_target": "x"}]},
            {"fields": [{"target": "\x00", "path": "a"}]},
            {"fields": [{"target": "x", "path": None}]},
            {"not_fields": 1},
            {"fields": [{"target": "x", "path": "a || b && c | [*].@"}]},
        ]
        for doc in mapping_docs:
            rr = await c.post(
                f"{base}/mapping-profiles",
                json={
                    "name": f"m-{uuid.uuid4().hex[:6]}",
                    "direction": "inbound",
                    "model": "roster.class",
                    "document": doc,
                },
                headers=h,
            )
            total += 1
            if rr.status_code >= 500:
                n_5xx += 1
                check("5xx: hostile mapping document", False, f"{rr.status_code} {rr.text[:120]}")
            # If a doc was accepted, hammer its preview with hostile samples.
            if rr.status_code < 300:
                mid = rr.json()["data"]["id"]
                hostile_samples = [
                    {"a": "x" * 100_000},
                    {"a": {"nested": {"deep": [1, 2, 3]}}},
                    {"a": None},
                    {"\x00": "v"},
                    {"a": float("nan")} if False else {"a": 1e308},
                ]
                pr = await c.post(
                    f"{base}/mapping-profiles/{mid}/preview",
                    json={"samples": hostile_samples},
                    headers=h,
                )
                total += 1
                if pr.status_code >= 500:
                    n_5xx += 1
                    check("5xx: hostile mapping preview", False, f"{pr.status_code} {pr.text[:120]}")

        check(f"no 5xx across {total} hostile requests", n_5xx == 0, f"n_5xx={n_5xx}")
        check(
            "every 4xx on JSON admin surfaces carries the error envelope",
            not malformed_env,
            " | ".join(malformed_env[:4]),
        )
        print(f"elapsed={_t.monotonic() - _t0:.1f}s")
        print(f"\nseed={SEED} total={total} PASS={PASS} FAIL={FAIL}")
        raise SystemExit(0 if FAIL == 0 else 1)


asyncio.run(main())
