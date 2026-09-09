"""Full adversarial battery against a LIVE API at localhost:8000.

Hostile-actor simulation: a registered attacker probes every isolation
boundary, escalation path, token weakness, and parser edge. PASS criteria are
strict: any 5xx anywhere, or any 2xx on a forbidden action, fails the check.
Monitor the API log for tracebacks alongside (issue §12.4 rule).

Usage: APP_ENV=test API on :8000, then
  cd apps/api && PYTHONPATH=. uv run python tests/e2e_adversarial.py
"""

import asyncio
import uuid

import httpx
import jwt as pyjwt


def _exp():
    from datetime import UTC, datetime, timedelta

    return (datetime.now(UTC) + timedelta(days=7)).isoformat()

API = "http://localhost:8000/api/v1"
PASS = 0
FAIL = 0
RESULTS: list[str] = []


def check(label: str, ok: bool, detail: str = ""):
    global PASS, FAIL
    if ok:
        PASS += 1
        RESULTS.append(f"  ✅ {label}")
    else:
        FAIL += 1
        RESULTS.append(f"  ❌ {label}{f' — {detail}' if detail else ''}")


def denied(r, label, allow=(401, 403, 404, 409, 422)):
    """Forbidden action: must be a clean 4xx — never 2xx, never 5xx."""
    check(label, r.status_code in allow, f"got {r.status_code}: {r.text[:120]}")


def section(name):
    RESULTS.append(f"\n── {name} " + "─" * max(0, 50 - len(name)))


async def register(c, name):
    email = f"adv-{name}-{uuid.uuid4().hex[:10]}@test.com"
    r = await c.post(
        "/auth/register",
        json={"email": email, "password": "Adv3rs4ry!x", "display_name": f"Adv {name}"},
    )
    r.raise_for_status()
    data = r.json()
    return {"Authorization": f"Bearer {data['access_token']}"}, data["user"]["id"], data[
        "access_token"
    ]


async def mk_org(c, h, name):
    r = await c.post(
        "/orgs",
        json={
            "name": f"{name} {uuid.uuid4().hex[:6]}",
            "slug": f"adv-{name}-{uuid.uuid4().hex[:10]}",
            "description": "adv",
        },
        headers=h,
    )
    r.raise_for_status()
    return r.json()["data"]["id"]


async def main():
    async with httpx.AsyncClient(base_url=API, timeout=30, trust_env=False) as c:
        # ── setup: victim builds a full estate; attacker registers ──
        vh, v_uid, v_tok = await register(c, "victim")
        ah, a_uid, a_tok = await register(c, "attacker")
        v_org = await mk_org(c, vh, "victim")
        a_org = await mk_org(c, ah, "attacker")
        v_tenant = (await c.get(f"/orgs/{v_org}", headers=vh)).json()["data"].get("tenant_id")
        if not v_tenant:
            r = await c.get("/tenants/mine", headers=vh)
            v_tenant = r.json()["data"][0]["id"] if r.status_code == 200 else None
        cat = (
            await c.post(f"/orgs/{v_org}/categories", json={"name": "AdvCat"}, headers=vh)
        ).json()["data"]["id"]
        v_skill = (
            await c.post(
                f"/orgs/{v_org}/skills",
                json={
                    "category_id": cat,
                    "name": "Victim Skill",
                    "description": "d" * 10,
                    "learning_content": "# secret content",
                    "difficulty": "beginner",
                    "tags": [],
                    "estimated_minutes": 5,
                },
                headers=vh,
            )
        ).json()["data"]["id"]
        v_proj = (
            await c.post(
                f"/orgs/{v_org}/projects",
                json={
                    "title": "Victim Project",
                    "description": "d",
                    "instructions": "i",
                    "rubric": [{"criterion": "Q", "max_score": 100}],
                },
                headers=vh,
            )
        ).json()["data"]["id"]
        await c.post(f"/orgs/{v_org}/projects/{v_proj}/publish", headers=vh)
        v_sub = (
            await c.post(f"/orgs/{v_org}/projects/{v_proj}/submissions", headers=vh)
        ).json()["data"]["id"]
        v_pack = (
            await c.post(
                f"/orgs/{v_org}/packs",
                json={"name": f"VPack {uuid.uuid4().hex[:6]}", "description": "d"},
                headers=vh,
            )
        ).json()["data"]["id"]
        v_brief = (
            await c.post(
                f"/orgs/{v_org}/briefs",
                json={
                    "title": "V Brief",
                    "client_name": "Acme",
                    "project_type": "brand_visuals",
                    "objective": "confidential objective",
                    "budget_range": "$50k",
                },
                headers=vh,
            )
        ).json()["data"]["id"]

        # ═══ B. Cross-tenant / cross-org IDOR matrix ═══
        section("B1. victim-org paths with attacker token")
        for verb, path, body in [
            ("GET", f"/orgs/{v_org}/skills", None),
            ("GET", f"/orgs/{v_org}/skills/{v_skill}", None),
            ("PUT", f"/orgs/{v_org}/skills/{v_skill}", {"name": "pwned"}),
            ("DELETE", f"/orgs/{v_org}/skills/{v_skill}", None),
            ("GET", f"/orgs/{v_org}/projects/{v_proj}", None),
            ("PUT", f"/orgs/{v_org}/projects/{v_proj}", {"title": "pwned"}),
            ("GET", f"/orgs/{v_org}/projects/{v_proj}/submissions", None),
            ("GET", f"/orgs/{v_org}/submissions/{v_sub}", None),
            ("POST", f"/orgs/{v_org}/submissions/{v_sub}/reviews",
             {"status": "approved", "score": 100, "feedback": "pwn"}),
            ("GET", f"/orgs/{v_org}/packs/{v_pack}", None),
            ("POST", f"/orgs/{v_org}/packs/{v_pack}/skills",
             {"skill_id": v_skill}),
            ("GET", f"/orgs/{v_org}/briefs/{v_brief}", None),
            ("PUT", f"/orgs/{v_org}/briefs/{v_brief}", {"title": "pwned"}),
            ("GET", f"/orgs/{v_org}/members", None),
            ("POST", f"/orgs/{v_org}/members", {"user_id": a_uid, "role": "owner"}),
            ("POST", f"/orgs/{v_org}/projects/{v_proj}/client-links",
             {"role": "approver", "expires_at": _exp()}),
            ("GET", f"/orgs/{v_org}/evaluation/tasks", None),
        ]:
            r = await c.request(verb, path, json=body, headers=ah)
            denied(r, f"{verb} {path.split(v_org)[-1] or '/org'} (victim org, attacker token)")

        section("B2. attacker-org paths with victim resource ids (parent confusion)")
        for verb, path, body in [
            ("GET", f"/orgs/{a_org}/skills/{v_skill}", None),
            ("PUT", f"/orgs/{a_org}/skills/{v_skill}", {"name": "pwned"}),
            ("GET", f"/orgs/{a_org}/projects/{v_proj}", None),
            ("GET", f"/orgs/{a_org}/submissions/{v_sub}", None),
            ("POST", f"/orgs/{a_org}/submissions/{v_sub}/reviews",
             {"status": "approved", "score": 100, "feedback": "x"}),
            ("GET", f"/orgs/{a_org}/packs/{v_pack}", None),
            ("GET", f"/orgs/{a_org}/briefs/{v_brief}", None),
            ("POST", f"/orgs/{a_org}/projects/{v_proj}/client-links",
             {"role": "approver", "expires_at": _exp()}),
        ]:
            r = await c.request(verb, path, json=body, headers=ah)
            denied(r, f"{verb} attacker-org path + victim id {path.rsplit('/',1)[-1][:8]}…")

        section("B3. victim tenant control-plane surface, attacker token")
        if v_tenant:
            for verb, path, body in [
                ("GET", f"/tenants/{v_tenant}/credits", None),
                ("GET", f"/tenants/{v_tenant}/credits/ledger", None),
                ("GET", f"/tenants/{v_tenant}/invoices", None),
                ("GET", f"/tenants/{v_tenant}/subscription", None),
                ("GET", f"/tenants/{v_tenant}/budgets", None),
                ("POST", f"/tenants/{v_tenant}/budgets",
                 {"scope_type": "tenant", "period": "monthly", "limit_minor": 1, "currency": "USD"}),
                ("GET", f"/tenants/{v_tenant}/branding", None),
                ("PUT", f"/tenants/{v_tenant}/branding", {"product_display_name": "PWNED"}),
                ("GET", f"/tenants/{v_tenant}/domains", None),
                ("POST", f"/tenants/{v_tenant}/domains", {"hostname": "pwn.example.com"}),
                ("GET", f"/tenants/{v_tenant}/members", None),
                ("POST", f"/tenants/{v_tenant}/members", {"user_id": a_uid, "role": "owner"}),
            ]:
                r = await c.request(verb, path, json=body, headers=ah)
                denied(r, f"{verb} tenant{path.split(v_tenant)[-1]} (attacker)")

        # ═══ C. Privilege escalation ═══
        section("C. platform endpoints as plain student")
        for verb, path, body in [
            ("GET", "/platform/tenants", None),
            ("GET", "/platform/plans", None),
            ("POST", f"/platform/tenants/{v_tenant or 'x'}/credits/adjust",
             {"currency": "USD", "amount_minor": 10_000_000, "reason": "pwn"}),
            ("POST", "/platform/billing/close-periods", None),
            ("GET", "/platform/audit-events", None),
            ("POST", "/platform/impersonation-grants",
             {"target_user_id": v_uid, "reason": "pwn", "expires_in_minutes": 30}),
        ]:
            r = await c.request(verb, path, json=body, headers=ah)
            denied(r, f"{verb} {path} as student", allow=(401, 403, 404, 405, 422))
        # self-promotion inside own org: change own role via member endpoint
        r = await c.post(f"/orgs/{a_org}/members", json={"user_id": v_uid, "role": "owner"}, headers=vh)
        denied(r, "victim adds self as OWNER to attacker org (non-member actor)")

        # ═══ D. Token attacks ═══
        section("D. token forgery / lifecycle")
        parts = a_tok.split(".")
        tampered = f"{parts[0]}.{parts[1]}.{'A' * len(parts[2])}"
        r = await c.get(f"/orgs/{a_org}/skills", headers={"Authorization": f"Bearer {tampered}"})
        check("tampered signature → 401", r.status_code == 401, f"got {r.status_code}")
        none_tok = pyjwt.encode({"sub": v_uid, "type": "access"}, key="", algorithm="none")
        r = await c.get(f"/orgs/{v_org}/skills", headers={"Authorization": f"Bearer {none_tok}"})
        check("alg=none token → 401", r.status_code == 401, f"got {r.status_code}")
        wrong_key = pyjwt.encode(
            {"sub": v_uid, "type": "access", "role": "admin"}, key="guessed-secret", algorithm="HS256"
        )
        r = await c.get(f"/orgs/{v_org}/skills", headers={"Authorization": f"Bearer {wrong_key}"})
        check("wrong-key signed token → 401", r.status_code == 401, f"got {r.status_code}")
        r = await c.get(f"/orgs/{a_org}/skills", headers={"Authorization": "Bearer " + "x" * 40})
        check("garbage token → 401", r.status_code == 401, f"got {r.status_code}")
        # guest portal token must not open product APIs
        link = await c.post(
            f"/orgs/{v_org}/projects/{v_proj}/client-links",
            json={"role": "approver", "expires_at": _exp()},
            headers=vh,
        )
        if link.status_code == 201:
            raw = link.json()["data"]["token"]
            g = await c.post("/client-portal/guest-session", json={"token": raw})
            gtok = g.json()["data"]["access_token"] if g.status_code == 200 else None
            if gtok:
                r = await c.get(
                    f"/orgs/{v_org}/projects/{v_proj}", headers={"Authorization": f"Bearer {gtok}"}
                )
                check("guest token blocked on product API", r.status_code in (401, 403),
                      f"got {r.status_code}")

        # ═══ E. Money / numeric input attacks (authorized surfaces) ═══
        section("E. hostile numeric input on OWN resources")
        a_tenant = (await c.get(f"/orgs/{a_org}", headers=ah)).json()["data"].get("tenant_id")
        if a_tenant:
            for label, body in [
                ("negative budget", {"scope_type": "tenant", "period": "monthly",
                                     "limit_minor": -100, "currency": "USD"}),
                ("float budget", {"scope_type": "tenant", "period": "monthly",
                                  "limit_minor": 10.5, "currency": "USD"}),
                ("overflow budget", {"scope_type": "tenant", "period": "monthly",
                                     "limit_minor": 2**63, "currency": "USD"}),
                ("NaN-string budget", {"scope_type": "tenant", "period": "monthly",
                                       "limit_minor": "NaN", "currency": "USD"}),
                ("bad currency", {"scope_type": "tenant", "period": "monthly",
                                  "limit_minor": 100, "currency": "US"}),
            ]:
                r = await c.post(f"/tenants/{a_tenant}/budgets", json=body, headers=ah)
                denied(r, f"budget: {label}", allow=(400, 403, 404, 422))
        for label, seats in [("negative seats", -5), ("float seats", 2.5), ("huge seats", 2**40)]:
            r = await c.post(
                f"/tenants/{a_tenant}/subscription/change" if a_tenant else "/x",
                json={"seats": seats, "proration_mode": "immediate"},
                headers=ah,
            )
            denied(r, f"plan change: {label}", allow=(400, 402, 403, 404, 409, 422))

        # ═══ F. Parser / payload attacks ═══
        section("F. parser attacks")
        r = await c.post(
            f"/orgs/{a_org}/projects",
            json={"title": "x\x00y", "description": "d", "instructions": "i",
                  "rubric": [{"criterion": "Q", "max_score": 100}]},
            headers=ah,
        )
        denied(r, "NUL byte in title", allow=(400, 422))
        deep = v = {}
        for _ in range(300):
            v["n"] = {}
            v = v["n"]
        r = await c.post(
            f"/orgs/{a_org}/categories", json={"name": "deep", "description": deep}, headers=ah
        )
        denied(r, "300-deep JSON body", allow=(400, 413, 422))
        r = await c.post(
            f"/orgs/{a_org}/categories", json={"name": "big", "description": "A" * 2_000_000},
            headers=ah,
        )
        denied(r, "2MB string field", allow=(400, 413, 422))
        raw_inf = (
            f'{{"category_id": "{cat}", "name": "inf", "description": "dddddddddd",'
            ' "learning_content": "x", "difficulty": "beginner", "tags": [],'
            ' "estimated_minutes": Infinity}'
        )
        r = await c.post(
            f"/orgs/{a_org}/skills",
            content=raw_inf,
            headers={**ah, "Content-Type": "application/json"},
        )
        denied(r, "bare Infinity token in JSON body", allow=(400, 422))
        raw_nan = raw_inf.replace("Infinity", "NaN")
        r = await c.post(
            f"/orgs/{a_org}/skills",
            content=raw_nan,
            headers={**ah, "Content-Type": "application/json"},
        )
        denied(r, "bare NaN token in JSON body", allow=(400, 422))

        # ═══ G. Anonymous surface: no auth at all ═══
        section("G. anonymous probes of protected surfaces")
        for verb, path in [
            ("GET", f"/orgs/{v_org}/skills"),
            ("GET", f"/tenants/{v_tenant or 'x'}/credits"),
            ("GET", "/platform/tenants"),
            ("GET", f"/orgs/{v_org}/members"),
        ]:
            r = await c.request(verb, path)
            check(f"anon {verb} {path.split('/')[1]}… → 401/403",
                  r.status_code in (401, 403), f"got {r.status_code}")

    # ═══ H. Session/refresh attacks ═══
    async with httpx.AsyncClient(base_url=API, timeout=30, trust_env=False) as c2:
        section("H. refresh rotation + revocation")
        email = f"adv-sess-{uuid.uuid4().hex[:10]}@test.com"
        r = await c2.post(
            "/auth/register",
            json={"email": email, "password": "Adv3rs4ry!x", "display_name": "Adv Sess"},
        )
        old_refresh = r.cookies.get("refresh_token")
        check("register sets refresh cookie", bool(old_refresh))
        # rotate: use the refresh once
        r2 = await c2.post("/auth/refresh", cookies={"refresh_token": old_refresh})
        check("refresh rotates", r2.status_code == 200, f"got {r2.status_code}")
        new_refresh = r2.cookies.get("refresh_token")
        # Pre-rotation REPLAY within the grace window is DESIGN (rotation-race
        # tolerance, refresh_reuse_grace_seconds); what security requires is
        # that the grace never survives an EXPLICIT revocation — asserted
        # below on the whole chain after logout.
        r3 = await c2.post("/auth/refresh", cookies={"refresh_token": old_refresh})
        check(
            "pre-rotation replay: graced (200) or rejected — never 5xx",
            r3.status_code in (200, 401, 403),
            f"got {r3.status_code}",
        )
        # logout revokes the live refresh; reuse after logout must be dead
        tok = r2.json().get("access_token")
        r4 = await c2.post(
            "/auth/logout",
            headers={"Authorization": f"Bearer {tok}"},
            cookies={"refresh_token": new_refresh},
        )
        check("logout accepted", r4.status_code in (200, 204), f"got {r4.status_code}")
        r5 = await c2.post("/auth/refresh", cookies={"refresh_token": new_refresh})
        check(
            "post-logout refresh rejected",
            r5.status_code in (401, 403),
            f"got {r5.status_code}",
        )
        # R88-91 class: logout must sweep the WHOLE chain — the rotation
        # PREDECESSOR (still inside its grace window) must be dead too, or a
        # stolen old cookie revives the session after explicit logout.
        r6 = await c2.post("/auth/refresh", cookies={"refresh_token": old_refresh})
        check(
            "post-logout replay of the GRACED predecessor rejected",
            r6.status_code in (401, 403),
            f"got {r6.status_code}",
        )

    print("\n".join(RESULTS))
    print("\n" + "=" * 50)
    print(f"PASSED {PASS}  FAILED {FAIL}")
    print("=" * 50)
    raise SystemExit(1 if FAIL else 0)


asyncio.run(main())
