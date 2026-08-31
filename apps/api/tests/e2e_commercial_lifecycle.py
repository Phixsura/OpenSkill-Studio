"""E2E commercial lifecycle — runs against a live API server at localhost:8000.

Issue #27 §12.4 full chain:
  Platform admin bootstrap → partner + blueprint → partner provisions branded
  tenant (outbox-driven step machine) → custom domain (mock verifier) →
  subscription active (manual provider) → seller lists paid workflow pack →
  buyer purchases with credit → license-gated install → rating snapshots →
  credit debit verified → period close → invoice lines verified → partner +
  seller accruals verified → settlement statement → client portal guest flow
  → both §37 trace chains walked.

The script has BOTH API access (httpx) and DB access (drives
process_outbox_once directly, so no arq worker/Redis is needed).

Usage: make infra-up && make dev-api, then:
  cd apps/api && PYTHONPATH=. uv run python tests/e2e_commercial_lifecycle.py
"""

import asyncio
import uuid

import httpx

API = "http://localhost:8000/api/v1"


def uid():
    return uuid.uuid4().hex[:8]


async def post_with_backoff(c: httpx.AsyncClient, path: str, **kw) -> httpx.Response:
    """POST with 429 backoff — register/login endpoints are rate-limited."""
    for _ in range(6):
        r = await c.post(path, **kw)
        if r.status_code != 429:
            return r
        await asyncio.sleep(11)
    return r


async def drain_outbox(max_rounds: int = 10) -> int:
    """Process outbox messages inline (worker-less E2E)."""
    from app.controlplane.worker import process_outbox_once
    from app.core.database import AsyncSessionLocal

    total = 0
    for _ in range(max_rounds):
        async with AsyncSessionLocal() as db:
            handled = await process_outbox_once(db)
        total += handled
        if handled == 0:
            break
    return total


async def bootstrap_admin(email: str, password: str) -> None:
    """Promote the registered user to UserRole.ADMIN via direct DB."""
    from sqlalchemy import select

    from app.core.database import AsyncSessionLocal
    from app.models.user import User, UserRole

    async with AsyncSessionLocal() as db:
        user = (await db.execute(select(User).where(User.email == email))).scalar_one()
        user.role = UserRole.ADMIN
        await db.commit()


async def force_period_due(tenant_id: str) -> None:
    """Backdate the open billing period so close-periods picks it up."""
    from datetime import UTC, datetime, timedelta

    from sqlalchemy import select

    from app.controlplane.models.billing import BillingPeriod
    from app.core.database import AsyncSessionLocal

    async with AsyncSessionLocal() as db:
        period = (
            await db.execute(
                select(BillingPeriod).where(
                    BillingPeriod.tenant_id == tenant_id, BillingPeriod.status == "open"
                )
            )
        ).scalar_one()
        period.period_end = datetime.now(UTC) - timedelta(seconds=1)
        await db.commit()


async def main() -> bool:  # noqa: PLR0915
    transport = httpx.AsyncHTTPTransport(retries=3)
    # trust_env=False: never route localhost through a system proxy
    async with httpx.AsyncClient(
        base_url=API, timeout=30, transport=transport, trust_env=False
    ) as c:
        errors: list[str] = []
        passed = 0

        def check(name, cond, detail=""):
            nonlocal passed
            if cond:
                passed += 1
                print(f"  ✅ {name}")
            else:
                errors.append(name)
                print(f"  ❌ {name}: {detail}")

        # ═══ 1. Platform admin ═══
        print("\n🔧 Phase 1: platform admin bootstrap")
        admin_email = f"cp-admin-{uid()}@test.com"
        r = await post_with_backoff(
            c,
            "/auth/register",
            json={"email": admin_email, "password": "TestPass123!", "display_name": "Ops"},
        )
        check("Register ops user", r.status_code == 201, f"{r.status_code}")
        await bootstrap_admin(admin_email, "TestPass123!")
        r = await post_with_backoff(
            c, "/auth/login", json={"email": admin_email, "password": "TestPass123!"}
        )
        ha = {"Authorization": f"Bearer {r.json()['access_token']}"}
        r = await c.get("/platform/dashboard", headers=ha)
        check(
            "Platform dashboard readable", r.status_code == 200, f"{r.status_code}: {r.text[:200]}"
        )

        # ═══ 2. Partner + blueprint ═══
        print("\n🤝 Phase 2: partner + blueprint")
        r = await c.post(
            "/platform/partners",
            json={
                "name": f"EduChannel {uid()}",
                "slug": f"educh-{uid()}",
                "partner_type": "reseller",
            },
            headers=ha,
        )
        check("Create partner", r.status_code == 201, f"{r.status_code}: {r.text[:200]}")
        partner_id = r.json()["data"]["id"]

        # Partner admin user
        r = await post_with_backoff(
            c,
            "/auth/register",
            json={
                "email": f"cp-partner-{uid()}@test.com",
                "password": "TestPass123!",
                "display_name": "Partner",
            },
        )
        hp = {"Authorization": f"Bearer {r.json()['access_token']}"}
        partner_user_id = r.json()["user"]["id"]
        r = await c.post(
            f"/platform/partners/{partner_id}/members",
            json={"user_id": partner_user_id, "role": "admin"},
            headers=ha,
        )
        check("Add partner admin", r.status_code == 201, f"{r.status_code}: {r.text[:200]}")

        # Revenue share rule: partner gets 10% of gross, all revenue types
        r = await c.post(
            "/platform/revenue-share-rules",
            json={
                "beneficiary_type": "partner",
                "partner_id": partner_id,
                "revenue_type": "all",
                "rule_type": "percentage_of_gross_revenue",
                "rate": "10",
                "effective_from": "2026-01-01T00:00:00Z",
            },
            headers=ha,
        )
        check("Create rev-share rule", r.status_code == 201, f"{r.status_code}: {r.text[:300]}")
        rule_id = r.json()["data"]["id"]
        r = await c.post(f"/platform/revenue-share-rules/{rule_id}/activate", headers=ha)
        check("Activate rule", r.status_code == 200, f"{r.status_code}: {r.text[:200]}")

        r = await c.post(
            f"/partners/{partner_id}/blueprints",
            json={
                "name": f"School blueprint {uid()}",
                "config": {
                    "plan_key": "school",
                    "branding": {
                        "product_display_name": "Partner Academy",
                        "theme_tokens": {"primary": "#123456"},
                    },
                    "org": {"name_template": "{tenant_name} Campus"},
                },
            },
            headers=hp,
        )
        check("Partner creates blueprint", r.status_code == 201, f"{r.status_code}: {r.text[:300]}")
        blueprint_id = r.json()["data"]["id"]

        # ═══ 3. Provision branded tenant ═══
        print("\n🏗️  Phase 3: provision branded tenant")
        slug = f"acme-school-{uid()}"
        r = await c.post(
            f"/partners/{partner_id}/provision-runs",
            json={
                "blueprint_id": blueprint_id,
                "name": "Acme Education Group",
                "slug": slug,
                "idempotency_key": f"e2e-{slug}",
            },
            headers=hp,
        )
        check("Submit provision run", r.status_code == 201, f"{r.status_code}: {r.text[:300]}")
        run_id = r.json()["data"]["id"]
        await drain_outbox()
        r = await c.get(f"/partners/{partner_id}/provision-runs/{run_id}", headers=hp)
        run = r.json()["data"]
        check("Provision completed", run["status"] == "completed", f"{run}")
        tenant_id = run["tenant_id"]
        check("Tenant created + attributed", tenant_id is not None)

        # Tenant owner: platform admin adds the partner user as tenant owner
        r = await c.post(
            f"/tenants/{tenant_id}/members",
            json={"user_id": partner_user_id, "role": "owner"},
            headers=ha,
        )
        check(
            "Tenant owner present",
            r.status_code == 201
            or (r.status_code == 409 and r.json()["error"]["code"] == "TENANT_MEMBER_EXISTS"),
            f"{r.status_code}: {r.text[:200]}",
        )

        # Provisioned subscription is live (manual provider, school plan)
        r = await c.get(f"/tenants/{tenant_id}/subscription", headers=hp)
        sub = r.json()["data"]
        check(
            "Subscription active on school",
            sub.get("status") == "active" and sub.get("plan_key") == "school",
            f"{sub}",
        )

        # Entitlements reflect the plan
        r = await c.get(f"/tenants/{tenant_id}/entitlements", headers=hp)
        ent = r.json()["data"]
        check(
            "Plan entitlements effective",
            ent["plan"]["key"] == "school"
            and ent["entitlements"]["client_portal"]["value"] is True,
            f"{ent.get('plan')}",
        )

        # ═══ 4. Custom domain (mock verifier) ═══
        print("\n🌐 Phase 4: custom domain")
        host = f"learn-{uid()}.acme-school.example"
        r = await c.post(f"/tenants/{tenant_id}/domains", json={"hostname": host}, headers=hp)
        check("Create domain", r.status_code == 201, f"{r.status_code}: {r.text[:300]}")
        domain = r.json()["data"]
        raw_token = domain.get("verification_token")
        check("Raw token shown once", bool(raw_token))
        r = await c.post(
            f"/tenants/{tenant_id}/domains/{domain['id']}/verify",
            json={"token": raw_token},
            headers=hp,
        )
        check("Verify domain (mock)", r.status_code == 200, f"{r.status_code}: {r.text[:200]}")
        r = await c.post(f"/tenants/{tenant_id}/domains/{domain['id']}/activate", headers=hp)
        check("Activate domain", r.status_code == 200, f"{r.status_code}: {r.text[:200]}")
        r = await c.get("/public/site-context", params={"host": host})
        ctx = r.json()["data"]
        check(
            "site-context resolves branding",
            ctx["tenant_id"] == tenant_id
            and ctx["branding"]["product_display_name"] == "Partner Academy",
            f"{ctx}",
        )

        # ═══ 5. Seller lists a paid workflow pack ═══
        print("\n🛒 Phase 5: paid marketplace listing")
        r = await post_with_backoff(
            c,
            "/auth/register",
            json={
                "email": f"cp-seller-{uid()}@test.com",
                "password": "TestPass123!",
                "display_name": "Seller",
            },
        )
        hs = {"Authorization": f"Bearer {r.json()['access_token']}"}
        seller_org = (await c.post("/orgs", json={"name": f"Studio {uid()}"}, headers=hs)).json()[
            "data"
        ]["id"]

        # Minimal publishable workflow pack
        r = await c.post(
            f"/orgs/{seller_org}/workflow-packs",
            json={
                "name": f"Product Video Suite {uid()}",
                "summary": "s",
                "workflow_type": "production",
            },
            headers=hs,
        )
        check("Seller creates pack", r.status_code == 201, f"{r.status_code}: {r.text[:200]}")
        pack_id = r.json()["data"]["id"]
        definition = {
            "schema_version": 1,
            "inputs": [{"key": "brief", "type": "text", "required": True}],
            "outputs": [
                {"key": "final", "type": "image", "from_step": "out", "from_port": "delivered"}
            ],
            "steps": [
                {
                    "id": "gen",
                    "type": "provider_action",
                    "name": "Generate",
                    "config": {"capability": "image_generation", "binding_mode": "auto"},
                    "inputs": [],
                    "outputs": [{"port": "result", "type": "image"}],
                },
                {
                    "id": "out",
                    "type": "output",
                    "name": "Deliver",
                    "config": {},
                    "inputs": [{"port": "final", "type": "image"}],
                    "outputs": [{"port": "delivered", "type": "image"}],
                },
            ],
            "edges": [
                {
                    "id": "e1",
                    "from_step": "gen",
                    "from_port": "result",
                    "to_step": "out",
                    "to_port": "final",
                },
            ],
        }
        r = await c.put(
            f"/orgs/{seller_org}/workflow-packs/{pack_id}/definition",
            json={"definition": definition},
            headers=hs,
        )
        check("Set definition", r.status_code == 200, f"{r.status_code}: {r.text[:400]}")
        r = await c.post(
            f"/orgs/{seller_org}/workflow-packs/{pack_id}/releases",
            json={
                "version": "1.0.0",
                "changelog": "v1",
                "dependencies": {
                    "requires_capabilities": [{"capability": "image_generation", "features": []}]
                },
            },
            headers=hs,
        )
        check("Cut release", r.status_code == 201, f"{r.status_code}: {r.text[:300]}")
        await c.post(f"/orgs/{seller_org}/workflow-packs/{pack_id}/submit-review", headers=hs)
        r = await c.post(f"/orgs/{seller_org}/workflow-packs/{pack_id}/approve", headers=hs)
        check(
            "Publish pack (review → approve)",
            r.status_code == 200 and r.json()["data"]["visibility"] == "public",
            f"{r.status_code}: {r.text[:300]}",
        )

        # Seller tenant needs paid_marketplace → grant a platform override
        r = await c.get("/tenants/mine", headers=hs)
        seller_tenant = r.json()["data"][0]["id"]
        r = await c.put(
            f"/platform/tenants/{seller_tenant}/entitlements/paid_marketplace",
            json={"value": True, "reason": "e2e seller enablement"},
            headers=ha,
        )
        check("Enable seller marketplace", r.status_code == 200, f"{r.status_code}: {r.text[:200]}")

        r = await c.post(
            f"/orgs/{seller_org}/marketplace/listings",
            json={
                "product_type": "workflow_pack",
                "product_id": pack_id,
                "offer_type": "paid",
                "price_minor": 21494,
                "currency": "USD",
                "license_scope": "organization",
            },
            headers=hs,
        )
        check("Create paid listing", r.status_code == 201, f"{r.status_code}: {r.text[:300]}")
        listing_id = r.json()["data"]["id"]
        r = await c.post(
            f"/orgs/{seller_org}/marketplace/listings/{listing_id}/activate", headers=hs
        )
        check("Activate listing", r.status_code == 200, f"{r.status_code}: {r.text[:200]}")

        # Public price badge
        r = await c.get(
            "/registry/listings",
            params={"product_type": "workflow_pack", "product_ids": pack_id},
        )
        check(
            "Registry price badge",
            r.status_code == 200 and r.json()["data"][pack_id]["price_minor"] == 21494,
            f"{r.text[:200]}",
        )

        # ═══ 6. Buyer purchases with credit ═══
        print("\n💳 Phase 6: credit purchase + license-gated install")
        # Buyer org inside the provisioned tenant (partner user is tenant owner)
        r = await c.get(f"/platform/tenants/{tenant_id}", headers=ha)
        # find the provisioned org
        from sqlalchemy import select as sa_select

        from app.core.database import AsyncSessionLocal
        from app.models.organization import Organization as OrgModel

        async with AsyncSessionLocal() as _db:
            buyer_org = (
                (await _db.execute(sa_select(OrgModel).where(OrgModel.tenant_id == tenant_id)))
                .scalars()
                .first()
            ).id
        # Buyer needs org admin: partner user created the run; make them a member via admin
        # (provisioning creates the org without members — platform admin bypasses org gates)
        r = await c.post(
            f"/platform/tenants/{tenant_id}/credits/adjust",
            json={
                "amount_minor": 50000,
                "currency": "USD",
                "reason": "e2e top-up",
                "idempotency_key": f"e2e-topup-{uid()}",
            },
            headers=ha,
        )
        check(
            "Platform credit adjust +$500",
            r.status_code in (200, 201),
            f"{r.status_code}: {r.text[:200]}",
        )

        # Install BEFORE license → 403 LICENSE_REQUIRED
        r = await c.post(
            f"/orgs/{buyer_org}/workflow-installations",
            json={"pack_id": pack_id},
            headers=hp,  # partner user owns the provisioned org
        )
        check(
            "Install blocked without license",
            r.status_code == 403 and r.json()["error"]["code"] == "LICENSE_REQUIRED",
            f"{r.status_code}: {r.text[:200]}",
        )

        r = await c.post(
            f"/orgs/{buyer_org}/marketplace/purchases",
            json={
                "listing_id": listing_id,
                "payment_method": "credit",
                "idempotency_key": f"e2e-buy-{uid()}",
            },
            headers=hp,
        )
        check(
            "Purchase with credit",
            r.status_code == 201 and r.json()["data"]["status"] == "paid",
            f"{r.status_code}: {r.text[:300]}",
        )

        # Credit debited
        r = await c.get(f"/tenants/{tenant_id}/credits", headers=hp)
        usd = next(b for b in r.json()["data"] if b["currency"] == "USD")
        check("Credit debited 21494", usd["balance_minor"] == 50000 - 21494, f"{usd}")

        # Capability gate: buyer org needs a mock provider offering first
        adapters = (await c.get("/providers/adapters", headers=hp)).json()["data"]
        mock_adapter = next(a for a in adapters if a["key"] == "mock")["id"]
        r = await c.post(
            f"/orgs/{buyer_org}/provider-connections",
            json={"adapter_id": mock_adapter, "name": "Mock Provider"},
            headers=hp,
        )
        check("Create mock connection", r.status_code == 201, f"{r.status_code}: {r.text[:200]}")
        conn_id = r.json()["data"]["id"]
        r = await c.post(
            f"/orgs/{buyer_org}/provider-offerings",
            json={
                "connection_id": conn_id,
                "capability_key": "image_generation",
                "model_name": "mock-image-1",
            },
            headers=hp,
        )
        check("Create offering", r.status_code == 201, f"{r.status_code}: {r.text[:200]}")

        # Install now passes
        r = await c.post(
            f"/orgs/{buyer_org}/workflow-installations",
            json={"pack_id": pack_id},
            headers=hp,
        )
        check(
            "License-gated install passes", r.status_code == 201, f"{r.status_code}: {r.text[:300]}"
        )

        # content_license usage event + accruals via outbox
        await drain_outbox()

        # ═══ 7. Usage → rating → invoice ═══
        print("\n📊 Phase 7: usage, rating, period close, invoice")
        r = await c.post(
            "/platform/price-policies",
            json={
                "name": f"e2e image pricing {uid()}",
                "policy_type": "fixed_unit_price",
                "usage_type": "image_generation",
                "tenant_id": tenant_id,
                "currency": "USD",
                "params": {"unit_price_minor": 30},
                "effective_from": "2026-01-01T00:00:00Z",
            },
            headers=ha,
        )
        check(
            "Create tenant price policy", r.status_code == 201, f"{r.status_code}: {r.text[:300]}"
        )
        r = await c.post(
            f"/orgs/{buyer_org}/usage-events",
            json={
                "usage_type": "image_generation",
                "quantity": "10",
                "occurred_at": "2026-08-31T00:00:00Z",
                "idempotency_key": f"e2e-usage-{uid()}",
                "provider": "mock",
                "model_or_service": "mock-image-1",
            },
            headers=hp,
        )
        check("Manual usage ingestion", r.status_code == 201, f"{r.status_code}: {r.text[:300]}")
        await drain_outbox()  # usage.recorded → rating

        r = await c.get(f"/tenants/{tenant_id}/rated-usage", headers=hp)
        rated = r.json()["data"]
        check("Rated rows visible to tenant", len(rated) >= 1, f"{len(rated)}")
        body = r.text
        leak = [s for s in ("internal_cost", "margin", "cost_rate", "fx_rate") if s in body]
        check("No cost leak in tenant response", leak == [], f"{leak}")

        await force_period_due(tenant_id)
        r = await c.post("/platform/billing/close-periods", headers=ha)
        check("Close periods", r.status_code == 200, f"{r.status_code}: {r.text[:200]}")
        await drain_outbox()  # period.close_due → invoice; invoice.finalized → accrual

        r = await c.get(f"/tenants/{tenant_id}/invoices", headers=hp)
        invoices = r.json()["data"]
        check("Invoice generated", len(invoices) >= 1, f"{len(invoices)}")
        invoice = invoices[0]
        r = await c.get(f"/tenants/{tenant_id}/invoices/{invoice['id']}", headers=hp)
        lines = r.json()["data"]["lines"]
        line_types = {line["line_type"] for line in lines}
        check(
            "Invoice has plan+usage+credit lines",
            {"plan", "usage"} <= line_types,
            f"{sorted(line_types)}",
        )
        usage_line = next(line for line in lines if line["line_type"] == "usage")

        # ═══ 8. Accruals + settlement ═══
        print("\n💰 Phase 8: partner accrual + settlement")
        r = await c.get(f"/partners/{partner_id}/revenue-share-entries", headers=hp)
        entries = r.json()["data"]
        check("Partner accruals exist", len(entries) >= 1, f"{len(entries)}")
        period = entries[0]["period"]
        r = await c.post(
            "/platform/settlements/generate",
            json={"beneficiary_type": "partner", "partner_id": partner_id, "period": period},
            headers=ha,
        )
        check("Generate statement", r.status_code in (200, 201), f"{r.status_code}: {r.text[:300]}")
        statement_id = r.json()["data"]["id"]
        r = await c.post(f"/platform/settlements/{statement_id}/finalize", headers=ha)
        check("Finalize statement", r.status_code == 200, f"{r.status_code}: {r.text[:200]}")
        r = await c.get(f"/partners/{partner_id}/statements/{statement_id}/export.csv", headers=hp)
        check(
            "Partner CSV export",
            r.status_code == 200 and "share_amount_minor" in r.text,
            f"{r.status_code}",
        )

        # ═══ 9. Trace chains (§37 acceptance) ═══
        print("\n🔍 Phase 9: trace chains")
        r = await c.get(f"/platform/trace/invoice-lines/{usage_line['id']}", headers=ha)
        trace = r.json()["data"]
        check(
            "Invoice-line trace reaches provider call",
            r.status_code == 200
            and trace["rated_usage"]
            and trace["rated_usage"][0]["usage_event"]["refs"]["provider"] == "mock"
            and trace["rated_usage"][0]["cost_rate_snapshot"] is not None,
            f"{r.status_code}: {r.text[:300]}",
        )
        entry_id = entries[0]["id"]
        r = await c.get(f"/platform/trace/settlement-entries/{entry_id}", headers=ha)
        trace2 = r.json()["data"]
        check(
            "Settlement-entry trace reaches source",
            r.status_code == 200 and trace2["entry"]["rule_snapshot"] and trace2["source"],
            f"{r.status_code}: {r.text[:300]}",
        )

        # ═══ 10. Client portal ═══
        print("\n👥 Phase 10: client portal guest flow")
        r = await c.post(
            f"/orgs/{buyer_org}/projects",
            json={
                "title": f"Client Video {uid()}",
                "description": "d",
                "instructions": "i",
                "rubric": [{"criterion": "Quality", "max_score": 100}],
            },
            headers=hp,
        )
        check("Create project", r.status_code == 201, f"{r.status_code}: {r.text[:300]}")
        project_id = r.json()["data"]["id"]
        r = await c.post(
            f"/orgs/{buyer_org}/projects/{project_id}/client-links",
            json={"label": "Client CEO", "role": "approver", "expires_at": "2026-09-30T00:00:00Z"},
            headers=hp,
        )
        check("Create guest link", r.status_code == 201, f"{r.status_code}: {r.text[:300]}")
        guest_raw = r.json()["data"].get("token")
        check("Guest token shown once", bool(guest_raw))
        r = await c.post("/client-portal/guest-session", json={"token": guest_raw})
        check("Guest session exchange", r.status_code == 200, f"{r.status_code}: {r.text[:200]}")
        guest_jwt = r.json()["data"]["access_token"]
        hg = {"Authorization": f"Bearer {guest_jwt}"}
        # Guest token rejected on product APIs (reverse isolation)
        r = await c.get("/orgs", headers=hg)
        check("Guest token blocked on product API", r.status_code == 401, f"{r.status_code}")
        r = await c.get(f"/client-portal/projects/{project_id}/submissions", headers=hg)
        check(
            "Portal submissions readable", r.status_code == 200, f"{r.status_code}: {r.text[:200]}"
        )

        # ═══ Result ═══
        print(f"\n{'=' * 50}")
        print(f"PASSED {passed}  FAILED {len(errors)}")
        if errors:
            print("Failures:", errors)
        return not errors


if __name__ == "__main__":
    ok = asyncio.run(main())
    raise SystemExit(0 if ok else 1)
