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

    # ═══ I. Webhook forgery (anonymous MONEY surface) ═══
    async with httpx.AsyncClient(base_url=API, timeout=30, trust_env=False) as c:
        section("I. billing webhook forgery")
        evil = b'{"id":"evt_pwn","type":"topup.succeeded","data":{"tenant_id":"x","amount_minor":99999999,"currency":"USD"}}'
        r = await c.post("/billing/webhooks/mock", content=evil,
                         headers={"Content-Type": "application/json"})
        check("unsigned mock webhook → 401", r.status_code == 401, f"got {r.status_code}")
        r = await c.post("/billing/webhooks/mock", content=evil,
                         headers={"Content-Type": "application/json",
                                  "X-Mock-Signature": "f" * 64})
        check("forged-signature webhook → 401", r.status_code == 401, f"got {r.status_code}")
        r = await c.post("/billing/webhooks/mock", content=evil,
                         headers=httpx.Headers({b"Content-Type": b"application/json",
                                                b"X-Mock-Signature": b"\xff\xfe garbage"}))
        check("non-ASCII signature header → 401 not 500", r.status_code == 401,
              f"got {r.status_code}")
        r = await c.post("/billing/webhooks/manual", content=evil,
                         headers={"Content-Type": "application/json"})
        check("manual-provider webhook rejected", r.status_code in (401, 404),
              f"got {r.status_code}")
        r = await c.post("/billing/webhooks/doesnotexist", content=evil,
                         headers={"Content-Type": "application/json"})
        check("unknown provider webhook rejected", r.status_code in (401, 404),
              f"got {r.status_code}")
        r = await c.post("/billing/webhooks/stripe", content=b"A" * 100_000,
                         headers={"Content-Type": "application/json"})
        check("100KB unsigned stripe body → 4xx not 5xx", 400 <= r.status_code < 500,
              f"got {r.status_code}")

    # ═══ J. Marketplace money gates ═══
    async with httpx.AsyncClient(base_url=API, timeout=60, trust_env=False) as c:
        section("J. marketplace: pricing, licensing, seller boundaries")
        # victim publishes a workflow pack, then a PAID listing (DB-inserted:
        # entitlement gates are not the subject here — the LICENSE gate is)
        wf_def = {
            "schema_version": 1,
            "inputs": [{"key": "topic", "type": "text", "required": True}],
            "outputs": [{"key": "final", "type": "image", "from_step": "g", "from_port": "result"}],
            "steps": [
                {"id": "b", "type": "prompt_template", "name": "Build",
                 "config": {"template": "SECRET-PROMPT {{inputs.topic}}"},
                 "inputs": [], "outputs": [{"port": "prompt", "type": "prompt"}]},
                {"id": "g", "type": "provider_action", "name": "Gen",
                 "config": {"capability": "image_generation"},
                 "inputs": [{"port": "prompt", "type": "prompt"}],
                 "outputs": [{"port": "result", "type": "image"}]},
            ],
            "edges": [{"id": "e1", "from_step": "b", "from_port": "prompt",
                       "to_step": "g", "to_port": "prompt"}],
            "ui": {},
        }
        r = await c.post(f"/orgs/{v_org}/workflow-packs",
                         json={"name": f"VWF {uuid.uuid4().hex[:6]}"}, headers=vh)
        v_wf = r.json()["data"]["id"]
        r = await c.put(f"/orgs/{v_org}/workflow-packs/{v_wf}/definition",
                        json={"definition": wf_def}, headers=vh)
        check("victim wf definition accepted", r.status_code == 200, r.text[:120])
        await c.post(f"/orgs/{v_org}/workflow-packs/{v_wf}/releases",
                     json={"version": "1.0.0"}, headers=vh)
        await c.post(f"/orgs/{v_org}/workflow-packs/{v_wf}/submit-review", headers=vh)
        r = await c.post(f"/orgs/{v_org}/workflow-packs/{v_wf}/approve", headers=vh)
        check("victim wf pack approved (public)", r.status_code == 200, f"got {r.status_code}")

        from decimal import Decimal

        from app.controlplane.models.marketplace import MarketplaceListing
        from app.core.database import AsyncSessionLocal, engine

        async with AsyncSessionLocal() as s:
            listing = MarketplaceListing(
                product_type="workflow_pack", product_id=v_wf,
                seller_org_id=v_org, seller_tenant_id=v_tenant or v_org,
                offer_type="paid", price_minor=21494, currency="USD",
                platform_commission_pct=Decimal("30.00"), status="active",
            )
            s.add(listing)
            await s.commit()
            listing_id = listing.id
        await engine.dispose()

        # J1: anon preview of the PAID pack must be REDACTED (no prompt leak)
        r = await c.get(f"/registry/workflow-packs/{v_wf}/preview")
        check("paid pack preview redacted", r.status_code == 200
              and r.json()["data"]["definition"].get("redacted") is True, r.text[:120])
        check("paid pack preview leaks no prompt", "SECRET-PROMPT" not in r.text)
        # J2: attacker installs the paid pack WITHOUT a license → denied
        r = await c.post(f"/orgs/{a_org}/workflow-installations",
                         json={"pack_id": v_wf}, headers=ah)
        denied(r, "install paid-listed pack without license", allow=(402, 403, 404, 422))
        # J3: purchase with tampered client-side price fields → schema drops
        # them; credit purchase without balance charges the LISTING price
        r = await c.post(
            f"/orgs/{a_org}/marketplace/purchases",
            json={"listing_id": listing_id, "payment_method": "credit",
                  "amount_minor": 1, "price_minor": 1,
                  "idempotency_key": f"adv-{uuid.uuid4().hex[:12]}"},
            headers=ah,
        )
        if r.status_code == 402:
            check("price tamper ignored (charged listing price → 402 no balance)", True)
        elif r.status_code in (200, 201):
            amt = r.json()["data"].get("amount_minor")
            check("price tamper ignored (server-side price)", amt == 21494,
                  f"amount {amt}")
        else:
            check("purchase attempt clean 4xx", 400 <= r.status_code < 500,
                  f"got {r.status_code}: {r.text[:120]}")
        # J4: attacker lists the VICTIM's product from their own org
        r = await c.post(
            f"/orgs/{a_org}/marketplace/listings",
            json={"product_type": "workflow_pack", "product_id": v_wf,
                  "offer_type": "paid", "price_minor": 100, "currency": "USD",
                  "license_scope": "organization", "upgrade_policy": "all_versions"},
            headers=ah,
        )
        denied(r, "attacker lists victim's product", allow=(403, 404, 409, 422))
        # J5: platform money ops as student
        for verb, path in [
            ("POST", "/platform/purchases/PWNEDPURCHASEID0000000000/mark-paid"),
            ("POST", "/platform/purchases/PWNEDPURCHASEID0000000000/refund"),
        ]:
            r = await c.request(verb, path, json={"reason": "pwn"}, headers=ah)
            denied(r, f"{verb} {path.split('/')[2]} money op as student",
                   allow=(401, 403, 404, 422))
        # J6: victim tenant purchase history, attacker token
        if v_tenant:
            r = await c.get(f"/tenants/{v_tenant}/purchases", headers=ah)
            denied(r, "victim tenant purchases (attacker)")

        # ═══ K. Registry visibility ═══
        section("K. registry: private/draft leakage")
        for path in [
            f"/registry/packs/{v_pack}",
            f"/registry/packs/{v_pack}/releases",
            f"/registry/packs/{v_pack}/preview",
            f"/registry/packs/{v_pack}/reviews",
            f"/registry/packs/{v_pack}/discussions",
        ]:
            r = await c.get(path)
            check(f"anon {path.split(v_pack)[-1] or '/detail'} of PRIVATE pack → 404",
                  r.status_code == 404, f"got {r.status_code}")
        r = await c.post(f"/orgs/{v_org}/workflow-packs",
                         json={"name": f"Draft {uuid.uuid4().hex[:6]}"}, headers=vh)
        v_draft_wf = r.json()["data"]["id"]
        for path in [
            f"/registry/workflow-packs/{v_draft_wf}",
            f"/registry/workflow-packs/{v_draft_wf}/releases",
            f"/registry/workflow-packs/{v_draft_wf}/preview",
        ]:
            r = await c.get(path)
            check(f"anon draft wf {path.split(v_draft_wf)[-1] or '/detail'} → 404",
                  r.status_code == 404, f"got {r.status_code}")

        # ═══ L. Portal deep attacks ═══
        section("L. portal: role gate, cross-project, revocation, email binding")
        v_proj2 = (
            await c.post(
                f"/orgs/{v_org}/projects",
                json={"title": "Victim Project 2", "description": "d", "instructions": "i",
                      "rubric": [{"criterion": "Q", "max_score": 100}]},
                headers=vh,
            )
        ).json()["data"]["id"]
        # reviewer-role guest must not final-accept
        link_r = await c.post(
            f"/orgs/{v_org}/projects/{v_proj}/client-links",
            json={"role": "reviewer", "expires_at": _exp()}, headers=vh,
        )
        raw_r = link_r.json()["data"]["token"]
        g = await c.post("/client-portal/guest-session", json={"token": raw_r})
        rtok = g.json()["data"]["access_token"]
        r = await c.post(
            f"/client-portal/projects/{v_proj}/final-accept",
            json={"submission_id": v_sub, "comment": "pwn"},
            headers={"Authorization": f"Bearer {rtok}"},
        )
        check("reviewer guest final-accept → 403", r.status_code == 403, f"got {r.status_code}")
        # cross-project token use → uniform 404
        r = await c.get(
            f"/client-portal/projects/{v_proj2}/submissions",
            headers={"Authorization": f"Bearer {rtok}"},
        )
        check("guest token cross-PROJECT → 404", r.status_code == 404, f"got {r.status_code}")
        # email-bound link, wrong email → 401
        link_e = await c.post(
            f"/orgs/{v_org}/projects/{v_proj}/client-links",
            json={"role": "reviewer", "email": "cmo@acme.com", "expires_at": _exp()},
            headers=vh,
        )
        raw_e = link_e.json()["data"]["token"]
        r = await c.post("/client-portal/guest-session",
                         json={"token": raw_e, "email": "attacker@evil.com"})
        check("email-bound link + wrong email → 401", r.status_code == 401,
              f"got {r.status_code}")
        # revocation kills the live guest session on the NEXT request
        link_id = link_r.json()["data"]["id"]
        rv = await c.post(
            f"/orgs/{v_org}/projects/{v_proj}/client-links/{link_id}/revoke", headers=vh
        )
        check("revoke accepted", rv.status_code in (200, 204), f"got {rv.status_code}")
        r = await c.get(
            f"/client-portal/projects/{v_proj}/submissions",
            headers={"Authorization": f"Bearer {rtok}"},
        )
        check("revoked link's live token → 401", r.status_code == 401, f"got {r.status_code}")
        r = await c.post("/client-portal/guest-session", json={"token": raw_r})
        check("revoked link re-exchange → 401", r.status_code == 401, f"got {r.status_code}")

        # ═══ M. Auth edges ═══
        section("M. auth edges")
        r = await c.post("/auth/register",
                         json={"email": f"adv-long-{uuid.uuid4().hex[:8]}@t.com",
                               "password": "Xx1!" + "a" * 96, "display_name": "Long Pass"})
        check("100-char password → clean (no bcrypt-72 500)", r.status_code in (201, 422),
              f"got {r.status_code}")
        dup_email = f"adv-dup-{uuid.uuid4().hex[:8]}@t.com"
        await c.post("/auth/register", json={"email": dup_email, "password": "Adv3rs4ry!x",
                                             "display_name": "Dup One"})
        r = await c.post("/auth/register", json={"email": dup_email, "password": "Adv3rs4ry!x",
                                                 "display_name": "Dup Two"})
        check("duplicate email → 409/422", r.status_code in (409, 422), f"got {r.status_code}")
        r = await c.post("/auth/register", json={"email": dup_email.upper(),
                                                 "password": "Adv3rs4ry!x",
                                                 "display_name": "Dup Case"})
        check("case-variant duplicate email rejected", r.status_code in (409, 422),
              f"got {r.status_code}")
        r = await c.post("/auth/login", json={"email": dup_email, "password": "WrongPass1!"})
        check("wrong password login → 401", r.status_code == 401, f"got {r.status_code}")
        r = await c.post("/auth/login", json={"email": dup_email, "password": "x\x00y"})
        check("control-char password → 4xx not 500", 400 <= r.status_code < 500,
              f"got {r.status_code}")
        r = await c.post("/auth/change-password",
                         json={"old_password": "WrongPass1!", "new_password": "NewPass1!x"},
                         headers=ah)
        check("change-password wrong old → 4xx", 400 <= r.status_code < 500,
              f"got {r.status_code}")

        # ═══ N. Upload attacks ═══
        section("N. uploads: sniffing, traversal, IDOR")
        rd = await c.post(
            f"/orgs/{v_org}/projects/{v_proj}/deliverables",
            json={"name": "Img", "type": "image", "required": False}, headers=vh,
        )
        v_deliv = rd.json()["data"]["id"]
        import struct
        import zlib

        def _png():
            sig = b"\x89PNG\r\n\x1a\n"

            def chunk(t, d):
                crc = zlib.crc32(t + d) & 0xFFFFFFFF
                return struct.pack(">I", len(d)) + t + d + struct.pack(">I", crc)

            ihdr = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
            return sig + chunk(b"IHDR", ihdr) + chunk(
                b"IDAT", zlib.compress(b"\x00\xff\x00\x00")
            ) + chunk(b"IEND", b"")

        rf = await c.post(
            f"/orgs/{v_org}/submissions/{v_sub}/files",
            files={"file": ("real.png", _png(), "image/png")},
            data={"deliverable_id": v_deliv}, headers=vh,
        )
        v_file = rf.json()["data"]["id"] if rf.status_code == 201 else None
        check("victim uploads real file", v_file is not None, rf.text[:120])
        r = await c.post(
            f"/orgs/{v_org}/submissions/{v_sub}/files",
            files={"file": ("fake.png", b"#!/bin/sh\nrm -rf /", "image/png")},
            data={"deliverable_id": v_deliv}, headers=vh,
        )
        check("content-type spoof (shell as PNG) → 422", r.status_code == 422,
              f"got {r.status_code}")
        r = await c.post(
            f"/orgs/{v_org}/submissions/{v_sub}/files",
            files={"file": ("../../../etc/passwd.png", _png(), "image/png")},
            data={"deliverable_id": v_deliv}, headers=vh,
        )
        traversal_ok = r.status_code == 422 or (
            r.status_code == 201 and ".." not in r.json()["data"].get("file_name", "")
        )
        check("path-traversal filename neutralized", traversal_ok,
              f"got {r.status_code}: {r.text[:120]}")
        if v_file:
            r = await c.get(
                f"/orgs/{v_org}/submissions/{v_sub}/files/{v_file}/download", headers=ah
            )
            denied(r, "attacker downloads victim file (victim path)")

    # ═══ O. Invite-link lifecycle abuse ═══
    async with httpx.AsyncClient(base_url=API, timeout=30, trust_env=False) as c:
        section("O. invite links: reuse caps, deactivation, role ceiling")
        r = await c.post(
            f"/orgs/{v_org}/invite-links",
            json={"role": "student", "max_uses": 1, "expires_in_days": 7}, headers=vh,
        )
        check("owner mints student link", r.status_code in (200, 201), r.text[:120])
        code = r.json()["data"]["url"].rsplit("/", 1)[-1]
        link_id = r.json()["data"]["id"]
        j1h, _, _ = await register(c, "joiner1")
        r = await c.post("/invites/join", json={"code": code}, headers=j1h)
        check("first join via link succeeds", r.status_code in (200, 201), r.text[:120])
        j2h, _, _ = await register(c, "joiner2")
        r = await c.post("/invites/join", json={"code": code}, headers=j2h)
        denied(r, "max_uses=1 exhausted link second join", allow=(400, 403, 404, 409, 410, 422))
        r = await c.post(
            f"/orgs/{v_org}/invite-links",
            json={"role": "student", "max_uses": 10, "expires_in_days": 7}, headers=vh,
        )
        code2 = r.json()["data"]["url"].rsplit("/", 1)[-1]
        link2_id = r.json()["data"]["id"]
        r = await c.delete(f"/orgs/{v_org}/invite-links/{link2_id}", headers=vh)
        if r.status_code == 405:
            r = await c.put(
                f"/orgs/{v_org}/invite-links/{link2_id}",
                json={"is_active": False}, headers=vh,
            )
        check("link deactivated", r.status_code in (200, 204), f"got {r.status_code}")
        r = await c.post("/invites/join", json={"code": code2}, headers=j2h)
        denied(r, "deactivated link join", allow=(400, 403, 404, 409, 410, 422))
        r = await c.post("/invites/join", json={"code": "PWNEDCODE123"}, headers=j2h)
        denied(r, "garbage link code", allow=(400, 404, 422))
        r = await c.post("/invites/accept", json={"token": "PWNEDTOKEN" * 4}, headers=j2h)
        denied(r, "garbage email-invite token", allow=(400, 401, 404, 422))
        # role ceiling: joiner1 (student) mints an OWNER link → 403
        r = await c.post(
            f"/orgs/{v_org}/invite-links",
            json={"role": "owner", "max_uses": 1, "expires_in_days": 7}, headers=j1h,
        )
        denied(r, "student mints owner-role link", allow=(403, 404))
        # attacker (non-member) reads the org's invite links → denied
        r = await c.get(f"/orgs/{v_org}/invite-links", headers=ah)
        denied(r, "non-member lists invite links")

    # ═══ P. Impersonation abuse (real platform admin via DB) ═══
    async with httpx.AsyncClient(base_url=API, timeout=30, trust_env=False) as c:
        section("P. impersonation: privilege walls + revocation")
        from sqlalchemy import update as _sa_update

        from app.core.database import AsyncSessionLocal as _SessionLocal
        from app.core.database import engine as _eng
        from app.models.user import User as _User
        from app.models.user import UserRole as _UserRole

        admin_h, admin_uid, _ = await register(c, "padmin")
        async with _SessionLocal() as s:
            await s.execute(
                _sa_update(_User).where(_User.id == admin_uid).values(role=_UserRole.ADMIN)
            )
            await s.commit()
        await _eng.dispose()
        r = await c.post(
            "/platform/impersonation-grants",
            json={"target_user_id": v_uid, "reason": "support case", "expires_in_minutes": 30},
            headers=admin_h,
        )
        check("admin creates grant for plain user", r.status_code in (200, 201), r.text[:150])
        grant_id = r.json()["data"]["id"]
        r = await c.post(f"/platform/impersonation-grants/{grant_id}/token", headers=admin_h)
        check("admin mints imp token", r.status_code == 200, r.text[:150])
        imp_tok = r.json()["data"]["access_token"]
        imp_h = {"Authorization": f"Bearer {imp_tok}"}
        r = await c.get(f"/orgs/{v_org}/skills", headers=imp_h)
        check("imp token reads target's org", r.status_code == 200, f"got {r.status_code}")
        # imp session must be WALLED from the client portal
        r = await c.get(f"/client-portal/projects/{v_proj}/submissions", headers=imp_h)
        check("imp token blocked on client portal", r.status_code == 403,
              f"got {r.status_code}")
        # imp session cannot refresh (no refresh minted)
        r = await c.post("/auth/refresh", headers=imp_h)
        denied(r, "imp session refresh attempt", allow=(401, 403, 422))
        # grant against a PRIVILEGED target must be rejected
        r = await c.post(
            "/platform/impersonation-grants",
            json={"target_user_id": admin_uid, "reason": "pwn", "expires_in_minutes": 30},
            headers=admin_h,
        )
        denied(r, "grant targeting an admin", allow=(403, 422))
        # revoke the grant → existing token dies on the next request
        r = await c.post(f"/platform/impersonation-grants/{grant_id}/revoke", headers=admin_h)
        if r.status_code == 404:
            r = await c.delete(f"/platform/impersonation-grants/{grant_id}", headers=admin_h)
        check("grant revoked", r.status_code in (200, 204), f"got {r.status_code}")
        r = await c.get(f"/orgs/{v_org}/skills", headers=imp_h)
        check("revoked grant kills the LIVE imp token", r.status_code == 401,
              f"got {r.status_code}")
        r = await c.post(f"/platform/impersonation-grants/{grant_id}/token", headers=admin_h)
        denied(r, "mint on revoked grant", allow=(401, 404, 409, 422))
        # a plain attacker cannot mint from someone else's grant id
        r = await c.post(f"/platform/impersonation-grants/{grant_id}/token", headers=ah)
        denied(r, "student mints from admin's grant")

        # ═══ Q. Export / PII surfaces ═══
        section("Q. exports + PII")
        r = await c.post(f"/platform/tenants/{v_tenant or 'x'}/exports", headers=ah)
        denied(r, "student requests tenant PII export")
        r = await c.get(f"/platform/tenants/{v_tenant or 'x'}/exports/01FAKEEXPORT00000000000000",
                        headers=ah)
        denied(r, "student polls export download")
        # pack export: victim's PRIVATE pack by id, attacker org path
        r = await c.get(f"/orgs/{a_org}/packs/{v_pack}/export", headers=ah)
        denied(r, "export victim's private pack via own org")

        # ═══ R. Confidential match/profile surfaces ═══
        section("R. confidential surfaces (R88 class)")
        for verb, path in [
            ("GET", f"/orgs/{v_org}/requirement-profiles", ),
            ("POST", f"/orgs/{v_org}/requirement-profiles/from-brief/{v_brief}"),
            ("GET", f"/orgs/{a_org}/requirement-profiles/01FAKEPROFILE0000000000000"),
            ("GET", f"/orgs/{v_org}/match-runs"),
        ]:
            r = await c.request(verb, path, json={} if verb == "POST" else None, headers=ah)
            denied(r, f"{verb} {path.split('/', 3)[-1][:40]}",
                   allow=(401, 403, 404, 405, 422))

        # ═══ S. Review/discussion abuse ═══
        section("S. reviews + discussions")
        r = await c.post(f"/registry/packs/{v_pack}/reviews",
                         json={"rating": 1, "title": "pwn", "body": "trash"}, headers=ah)
        denied(r, "review a PRIVATE (unlisted) pack", allow=(401, 403, 404, 409, 422))
        r = await c.post(f"/registry/packs/{v_pack}/discussions",
                         json={"body": "spam"}, headers=ah)
        denied(r, "discuss a PRIVATE pack", allow=(401, 403, 404, 422))
        # anonymous writes
        r = await c.post(f"/registry/packs/{v_pack}/reviews",
                         json={"rating": 5, "title": "x", "body": "y"})
        check("anon review write → 401/403/404", r.status_code in (401, 403, 404),
              f"got {r.status_code}")

        # ═══ T. Org settings reserved namespace ═══
        section("T. org settings namespace")
        r = await c.put(f"/orgs/{a_org}/settings",
                        json={"settings": {"ai_evaluation": {"enabled": True,
                                                             "monthly_budget_usd": 999999}}},
                        headers=ah)
        denied(r, "reserved ai_evaluation key via generic settings", allow=(400, 403, 422))
        r = await c.put(f"/orgs/{v_org}/settings", json={"settings": {"theme": "dark"}},
                        headers=ah)
        denied(r, "attacker writes victim org settings")

    # ═══ U. LIVE HTTP race attacks ═══
    async with httpx.AsyncClient(base_url=API, timeout=60, trust_env=False) as c:
        section("U. live races: idempotency, max_uses, final-accept, unique slug")
        # U1: 8 parallel purchases with ONE idempotency key → ≤1 purchase
        ikey = f"race-{uuid.uuid4().hex[:16]}"

        async def _buy():
            return await c.post(
                f"/orgs/{a_org}/marketplace/purchases",
                json={"listing_id": listing_id, "payment_method": "credit",
                      "idempotency_key": ikey},
                headers=ah,
            )

        rs = await asyncio.gather(*[_buy() for _ in range(8)])
        codes = sorted(r.status_code for r in rs)
        ids = {r.json()["data"]["id"] for r in rs if r.status_code in (200, 201)}
        no_500 = all(r.status_code < 500 for r in rs)
        check("8-way purchase idempotency race: no 500s", no_500, f"codes={codes}")
        check("8-way purchase idempotency race: ≤1 purchase id", len(ids) <= 1,
              f"ids={ids} codes={codes}")

        # U2: invite link max_uses=1, 6 racers → exactly ONE join
        r = await c.post(
            f"/orgs/{v_org}/invite-links",
            json={"role": "student", "max_uses": 1, "expires_in_days": 7}, headers=vh,
        )
        rcode = r.json()["data"]["url"].rsplit("/", 1)[-1]
        racers = []
        for i in range(6):
            hh, _, _ = await register(c, f"racer{i}")
            racers.append(hh)

        async def _join(hh):
            return await c.post("/invites/join", json={"code": rcode}, headers=hh)

        rs = await asyncio.gather(*[_join(hh) for hh in racers])
        joins = [r for r in rs if r.status_code in (200, 201)]
        no_500 = all(r.status_code < 500 for r in rs)
        check("6-way max_uses=1 race: no 500s", no_500,
              f"codes={sorted(r.status_code for r in rs)}")
        check("6-way max_uses=1 race: exactly 1 join", len(joins) == 1,
              f"{len(joins)} joins")

        # U3: portal final-accept ×6 parallel → exactly one 201
        r = await c.post(
            f"/orgs/{v_org}/projects/{v_proj}/submissions/{v_sub}/submit", headers=vh
        )
        check("victim submits draft (U3 setup)", r.status_code == 200, r.text[:120])
        await c.post(
            f"/orgs/{v_org}/projects/{v_proj}/client-shares",
            json={"submission_id": v_sub}, headers=vh,
        )
        la = await c.post(
            f"/orgs/{v_org}/projects/{v_proj}/client-links",
            json={"role": "approver", "expires_at": _exp()}, headers=vh,
        )
        graw = la.json()["data"]["token"]
        g = await c.post("/client-portal/guest-session", json={"token": graw})
        atok = {"Authorization": f"Bearer {g.json()['data']['access_token']}"}

        async def _final():
            return await c.post(
                f"/client-portal/projects/{v_proj}/final-accept",
                json={"submission_id": v_sub, "comment": "race"}, headers=atok,
            )

        rs = await asyncio.gather(*[_final() for _ in range(6)])
        oks = [r for r in rs if r.status_code == 201]
        no_500 = all(r.status_code < 500 for r in rs)
        check("6-way final-accept race: no 500s", no_500,
              f"codes={sorted(r.status_code for r in rs)}")
        check("6-way final-accept race: exactly 1 acceptance", len(oks) == 1,
              f"{len(oks)} accepted")

        # U4: 6 parallel org creates with ONE slug → 1 winner, clean losers
        slug = f"race-slug-{uuid.uuid4().hex[:10]}"

        async def _mkorg(hh):
            return await c.post(
                "/orgs", json={"name": "Race Org X", "slug": slug, "description": "d"},
                headers=hh,
            )

        rs = await asyncio.gather(*[_mkorg(racers[i % len(racers)]) for i in range(6)])
        wins = [r for r in rs if r.status_code in (200, 201)]
        no_500 = all(r.status_code < 500 for r in rs)
        check("6-way same-slug org race: no 500s", no_500,
              f"codes={sorted(r.status_code for r in rs)}")
        check("6-way same-slug org race: exactly 1 winner", len(wins) == 1,
              f"{len(wins)} wins")

        # ═══ V. SSRF probes (webhook URLs) ═══
        section("V. SSRF: webhook URL blocklist")
        for target in [
            "http://localhost:6379/hook",
            "http://127.0.0.2/hook",
            "http://0.0.0.0/hook",
            "http://169.254.169.254/latest/meta-data/",
            "http://metadata.google.internal/computeMetadata/v1/",
            "http://10.0.0.5/internal",
            "http://[::1]:8000/api/v1/health",
            "http://2130706433/hook",
        ]:
            r = await c.post(
                f"/orgs/{a_org}/webhooks",
                json={"url": target, "events": ["pack.published"]}, headers=ah,
            )
            denied(r, f"webhook SSRF {target[:44]}", allow=(400, 403, 422))
        r = await c.post(
            f"/orgs/{a_org}/webhooks",
            json={"url": "https://example.com/hook", "events": ["pack.published"]},
            headers=ah,
        )
        check("public https webhook accepted (positive control)",
              r.status_code in (200, 201), f"got {r.status_code}: {r.text[:100]}")

        # ═══ W. HTTP protocol edges ═══
        section("W. protocol edges")
        r = await c.post(
            f"/orgs/{a_org}/categories",
            content=b'{"name": "first", "name": "second"}',
            headers={**ah, "Content-Type": "application/json"},
        )
        check("duplicate JSON keys: no 500, deterministic parse",
              r.status_code < 500, f"got {r.status_code}")
        r = await c.post(
            f"/orgs/{a_org}/categories", content=b'["not", "an", "object"]',
            headers={**ah, "Content-Type": "application/json"},
        )
        denied(r, "array where object expected", allow=(400, 422))
        r = await c.post(
            f"/orgs/{a_org}/categories", content=b'{"name": "tp"}',
            headers={**ah, "Content-Type": "text/plain"},
        )
        denied(r, "text/plain content-type on JSON route", allow=(400, 415, 422))
        r = await c.get(
            f"/orgs/{a_org}/skills",
            headers={**ah, "X-HTTP-Method-Override": "DELETE"},
        )
        check("method-override header ignored", r.status_code == 200, f"got {r.status_code}")
        r = await c.get(f"/orgs/{a_org}/%2e%2e/%2e%2e/platform/tenants", headers=ah)
        denied(r, "URL-encoded ../ path traversal", allow=(400, 401, 403, 404))
        r = await c.get(f"/orgs/{a_org}/skills?q=" + "A" * 20000, headers=ah)
        check("20KB query param: no 500", r.status_code < 500, f"got {r.status_code}")
        r = await c.request("HEAD", "/platform/tenants")
        check("anon HEAD on protected route: no body leak",
              r.status_code in (401, 403, 404, 405) and not r.content,
              f"got {r.status_code}, {len(r.content)}B body")

        # ═══ Y. Enumeration uniformity ═══
        section("Y. account enumeration")
        r1 = await c.post("/auth/login",
                          json={"email": f"ghost-{uuid.uuid4().hex[:8]}@nowhere-example.com",
                                "password": "Wrong1!xx"})
        r2 = await c.post("/auth/login", json={"email": dup_email, "password": "Wrong1!xx"})
        check(
            "login: unknown email vs wrong password INDISTINGUISHABLE",
            r1.status_code == r2.status_code
            and r1.json()["error"]["code"] == r2.json()["error"]["code"],
            f"{r1.status_code}/{r1.json()['error']['code']} vs "
            f"{r2.status_code}/{r2.json()['error']['code']}",
        )
        f1 = await c.post("/auth/forgot-password",
                          json={"email": f"ghost-{uuid.uuid4().hex[:8]}@nowhere-example.com"})
        f2 = await c.post("/auth/forgot-password", json={"email": dup_email})
        check("forgot-password: existence not disclosed",
              f1.status_code == f2.status_code, f"{f1.status_code} vs {f2.status_code}")

        # ═══ Z. Import bombs ═══
        section("Z. pack-import bombs")
        r = await c.post(
            f"/orgs/{a_org}/packs/import",
            files={"file": ("bomb.zip", b"PK\x03\x04" + b"A" * (6 * 1024 * 1024),
                            "application/zip")},
            headers=ah,
        )
        denied(r, "6MB corrupt zip import", allow=(400, 413, 422))
        import json as _json
        import zipfile
        from io import BytesIO

        deep = leaf = {}
        for _ in range(300):
            leaf["n"] = {}
            leaf = leaf["n"]
        zbuf = BytesIO()
        with zipfile.ZipFile(zbuf, "w") as z:
            z.writestr("manifest.json", _json.dumps({"pack": deep}))
        r = await c.post(
            f"/orgs/{a_org}/packs/import",
            files={"file": ("deep.zip", zbuf.getvalue(), "application/zip")},
            headers=ah,
        )
        denied(r, "300-deep manifest import", allow=(400, 413, 422))
        # zip bomb: tiny zip, huge decompressed member
        zbuf2 = BytesIO()
        with zipfile.ZipFile(zbuf2, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr("manifest.json", '{"pad": "' + "A" * (60 * 1024 * 1024) + '"}')
        r = await c.post(
            f"/orgs/{a_org}/packs/import",
            files={"file": ("zbomb.zip", zbuf2.getvalue(), "application/zip")},
            headers=ah,
        )
        denied(r, "60MB-decompressed zip bomb", allow=(400, 413, 422))

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
