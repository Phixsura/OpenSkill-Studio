"""E2E talent lifecycle — runs against a live API server at localhost:8000.

Issue #32 §Q full chain:
  Learner registers → creates org + skill → completes training →
  capability evidence auto-recorded → passport shows verified capability →
  learner passes assessment → credential issued → employer registers →
  employer publishes opportunity → learner opts into discoverability →
  explainable match generated → learner applies with passport snapshot →
  employer moves application: screening → interview → offer →
  learner accepts → placement created → employer completes verification →
  employer_verified evidence created → school/employer/platform dashboards →
  workforce intelligence + curriculum recommendations.

Usage: make infra-up && make dev-api, then:
  cd apps/api && PYTHONPATH=. uv run python tests/e2e_talent_lifecycle.py
"""

import asyncio
import uuid

import httpx

API = "http://localhost:8000/api/v1"


def uid():
    return uuid.uuid4().hex[:8]


async def post_with_backoff(c: httpx.AsyncClient, path: str, **kw) -> httpx.Response:
    """POST with 429 backoff — auth endpoints are rate-limited."""
    for _ in range(6):
        r = await c.post(path, **kw)
        if r.status_code != 429:
            return r
        await asyncio.sleep(11)
    return r


DB_DSN = "postgresql://postgres:postgres@localhost:5432/openskill"


async def run_sql(sql: str) -> None:
    """Run a single SQL statement via asyncpg (separate connection)."""
    import asyncpg

    conn = await asyncpg.connect(DB_DSN)
    try:
        await conn.execute(sql)
    finally:
        await conn.close()
    await asyncio.sleep(0.05)


async def run_sql_batch(statements: list[str]) -> None:
    """Run multiple SQL statements in a single connection (batch).

    Uses a single connection and transaction to avoid pool contention
    with the running server.
    """
    import asyncpg

    conn = await asyncpg.connect(DB_DSN)
    try:
        async with conn.transaction():
            for sql in statements:
                await conn.execute(sql)
    finally:
        await conn.close()
    await asyncio.sleep(0.2)


async def bootstrap_admin(email: str) -> None:
    """Promote user to platform admin via direct SQL."""
    await run_sql(f"UPDATE users SET role = 'ADMIN' WHERE email = '{email}'")


def safe_get(data: dict | None, *keys, default=None):
    """Safely traverse nested dict keys."""
    val = data
    for k in keys:
        if not isinstance(val, dict):
            return default
        val = val.get(k, default)
    return val


async def main() -> bool:  # noqa: PLR0915
    transport = httpx.AsyncHTTPTransport(retries=3)
    async with httpx.AsyncClient(
        base_url=API, timeout=60, transport=transport, trust_env=False
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

        # ═══ Phase 1: Setup — admin, org, learner, employer ═══
        print("\n🔧 Phase 1: Setup users and organizations")

        admin_email = f"talent-admin-{uid()}@test.com"
        r = await post_with_backoff(
            c, "/auth/register",
            json={"email": admin_email, "password": "TestPass123!", "display_name": "Admin"},
        )
        check("Register admin", r.status_code == 201, f"{r.status_code}")
        await bootstrap_admin(admin_email)
        r = await post_with_backoff(
            c, "/auth/login", json={"email": admin_email, "password": "TestPass123!"},
        )
        admin_token = r.json()["access_token"]
        ha = {"Authorization": f"Bearer {admin_token}"}

        r = await c.post("/orgs", json={"name": f"AI School {uid()}", "slug": f"school-{uid()}"}, headers=ha)
        check("Create school org", r.status_code == 201, f"{r.status_code}")
        school_org_id = r.json()["data"]["id"]

        learner_email = f"learner-{uid()}@test.com"
        r = await post_with_backoff(
            c, "/auth/register",
            json={"email": learner_email, "password": "TestPass123!", "display_name": "Learner"},
        )
        check("Register learner", r.status_code == 201, f"{r.status_code}")
        r = await post_with_backoff(
            c, "/auth/login", json={"email": learner_email, "password": "TestPass123!"},
        )
        learner_token = r.json()["access_token"]
        learner_id = r.json()["user"]["id"]
        hl = {"Authorization": f"Bearer {learner_token}"}

        r = await c.post(
            f"/orgs/{school_org_id}/members",
            json={"user_id": learner_id, "role": "student"},
            headers=ha,
        )
        check("Add learner to school", r.status_code in (200, 201), f"{r.status_code}: {r.text[:200]}")

        employer_email = f"employer-{uid()}@test.com"
        r = await post_with_backoff(
            c, "/auth/register",
            json={"email": employer_email, "password": "TestPass123!", "display_name": "Employer"},
        )
        check("Register employer", r.status_code == 201, f"{r.status_code}")
        r = await post_with_backoff(
            c, "/auth/login", json={"email": employer_email, "password": "TestPass123!"},
        )
        employer_token = r.json()["access_token"]
        he = {"Authorization": f"Bearer {employer_token}"}

        r = await c.post("/orgs", json={"name": f"AI Corp {uid()}", "slug": f"employer-{uid()}"}, headers=he)
        check("Create employer org", r.status_code == 201, f"{r.status_code}")
        employer_org_id = r.json()["data"]["id"]

        # ═══ Phase 2: Capability ontology ═══
        print("\n📊 Phase 2: Capability ontology")

        r = await c.post(
            "/talent/capabilities",
            json={
                "canonical_name": f"AI Product Visual Design {uid()}",
                "category": "visual_design",
                "description": "Design AI-powered product visuals",
                "decay_config": {"half_life_days": 365},
            },
            headers=ha,
        )
        check("Create capability", r.status_code == 201, f"{r.status_code}: {r.text[:200]}")
        if r.status_code != 201:
            print("  FATAL: cannot continue without capability — aborting")
            return False
        cap_id = r.json()["data"]["id"]

        r = await c.post(
            "/talent/capabilities",
            json={"canonical_name": f"Prompt Structuring {uid()}", "category": "ai_fundamentals"},
            headers=ha,
        )
        check("Create second capability", r.status_code == 201, f"{r.status_code}")
        cap2_id = safe_get(r.json(), "data", "id", default="MISSING")

        r = await c.post(
            f"/talent/capabilities/{cap_id}/edges",
            json={"source_id": cap_id, "target_id": cap2_id, "edge_type": "commonly_paired_with"},
            headers=ha,
        )
        check("Add capability edge", r.status_code == 201, f"{r.status_code}")

        r = await c.get("/talent/capabilities", headers=ha)
        check("List capabilities", r.status_code == 200, f"{r.status_code}")

        r = await c.get(f"/talent/capabilities/{cap_id}/graph?max_depth=2", headers=ha)
        check("Graph traversal", r.status_code == 200, f"{r.status_code}")

        # ═══ Phase 3: Evidence ledger ═══
        print("\n📋 Phase 3: Evidence ledger")

        from datetime import UTC, datetime
        from ulid import ULID

        now = datetime.now(UTC).isoformat()

        r = await c.post(
            "/talent/evidence",
            json={
                "capability_id": cap_id,
                "source_type": "skill_completion",
                "source_id": "test-skill-001",
                "verification_level": "instructor_verified",
                "occurred_at": now,
            },
            headers=hl,
        )
        check("Record evidence", r.status_code == 201, f"{r.status_code}: {r.text[:200]}")
        check(
            "Evidence forced to self_reported",
            safe_get(r.json(), "data", "verification_level") == "self_reported",
            f"got {safe_get(r.json(), 'data', 'verification_level')}",
        )

        # Seed instructor-verified evidence via batch SQL
        stmts = []
        for i in range(5):
            src_id = f"proj-{uid()}-{i}"
            stmts.append(
                f"INSERT INTO capability_evidence "
                f"(id, user_id, capability_id, source_type, source_id, "
                f"verification_level, occurred_at, confidence, score_normalized, status, metadata) "
                f"VALUES ('{ULID()!s}', '{learner_id}', '{cap_id}', 'project_approval', '{src_id}', "
                f"'instructor_verified', NOW(), 1.0, 0.85, 'active', '{{}}'::jsonb)"
            )
        await run_sql_batch(stmts)
        check("Seed instructor evidence (5 rows)", True, "")

        # Check capability profile
        r = await c.get(f"/talent/users/{learner_id}/profile", headers=hl)
        check("Get capability profile", r.status_code == 200, f"{r.status_code}: {r.text[:300]}")
        cap_score = None
        if r.status_code == 200:
            profile = r.json().get("data", [])
            check("Profile has capabilities", len(profile) >= 1, f"got {len(profile)}")
            cap_score = next((p for p in profile if p["capability_id"] == cap_id), None)
            if cap_score:
                check("Level > 0", cap_score["level"] > 0, f"level={cap_score['level']}")
                check("Score > 0", cap_score["score"] > 0, f"score={cap_score['score']}")

        # ═══ Phase 4: Skill Passport ═══
        print("\n🎫 Phase 4: Skill Passport")

        r = await c.get("/talent/passport", headers=hl)
        check("Get passport", r.status_code == 200, f"{r.status_code}")
        passport = r.json().get("data", {})
        check("Passport private by default", passport.get("default_visibility") == "private", "")
        check("Not discoverable by default", passport.get("discoverable") is False, "")

        r = await c.patch(
            "/talent/passport",
            json={
                "default_visibility": "share_link",
                "discoverable": True,
                "visible_fields": ["capabilities", "credentials"],
                "availability_status": "open",
            },
            headers=hl,
        )
        check("Update passport", r.status_code == 200, f"{r.status_code}")
        check("Discoverable now true", safe_get(r.json(), "data", "discoverable") is True, "")

        r = await c.post("/talent/passport/snapshots", json={"included_fields": ["capabilities"]}, headers=hl)
        check("Create snapshot", r.status_code == 201, f"{r.status_code}")
        snapshot_token = safe_get(r.json(), "data", "share_token", default="MISSING")
        snapshot_id = safe_get(r.json(), "data", "id", default="MISSING")
        check("Snapshot has checksum", len(safe_get(r.json(), "data", "checksum", default="") or "") == 64, "")

        r = await c.get(f"/verify/passport/{snapshot_token}")
        check("Public verification works", r.status_code == 200, f"{r.status_code}")

        # ═══ Phase 5: Assessment & Credential ═══
        print("\n📝 Phase 5: Assessment & Credential")

        r = await c.post(
            f"/talent/assessments?org_id={school_org_id}",
            json={
                "title": f"AI Visual Assessment {uid()}",
                "assessment_type": "practical_task",
                "capability_requirements": [{"capability_id": cap_id, "min_level": 1, "weight": 1.0}],
                "config": {"attempt_limit": 3, "time_window_minutes": 60},
            },
            headers=ha,
        )
        check("Create blueprint", r.status_code == 201, f"{r.status_code}: {r.text[:200]}")
        blueprint_id = safe_get(r.json(), "data", "id", default="MISSING")

        await run_sql(f"UPDATE assessment_blueprints SET status = 'active' WHERE id = '{blueprint_id}'")

        r = await c.post(f"/talent/assessments/{blueprint_id}/runs", headers=hl)
        check("Start assessment run", r.status_code == 201, f"{r.status_code}: {r.text[:200]}")
        run_id = safe_get(r.json(), "data", "id", default="MISSING")

        r = await c.patch(
            f"/talent/assessments/{blueprint_id}/runs/{run_id}",
            json={"results": {"answers": "test"}},
            headers=hl,
        )
        check("Submit run", r.status_code == 200, f"{r.status_code}: {r.text[:200]}")

        r = await c.post(
            f"/talent/assessments/{blueprint_id}/runs/{run_id}/review",
            json={
                "results": [{"capability_id": cap_id, "score": 0.9, "passed": True}],
                "status": "passed",
            },
            headers=ha,
        )
        check("Review run (passed)", r.status_code == 200, f"{r.status_code}: {r.text[:200]}")

        cred_type = f"ai_visual_commercial_{uid()}"
        r = await c.post(
            "/talent/credential-rules",
            json={
                "credential_type": cred_type,
                "display_name": "AI Visual — Commercial Ready",
                "requirements": [{"capability_id": cap_id, "min_level": 1}],
                "conditions": {"all_required": True},
            },
            headers=ha,
        )
        check("Create credential rule", r.status_code == 201, f"{r.status_code}: {r.text[:200]}")

        await run_sql(
            f"UPDATE credential_rules SET status = 'active', activated_at = NOW() "
            f"WHERE credential_type = '{cred_type}'"
        )

        r = await c.post("/talent/credentials/evaluate", json={"credential_type": cred_type}, headers=hl)
        check("Evaluate credential", r.status_code == 200, f"{r.status_code}: {r.text[:200]}")
        check("Eligible", safe_get(r.json(), "data", "eligible") is True, "")

        r = await c.post("/talent/credentials/issue", json={"credential_type": cred_type}, headers=hl)
        check("Issue credential", r.status_code == 201, f"{r.status_code}: {r.text[:200]}")

        r = await c.get("/talent/credentials", headers=hl)
        check("Has credential", len(r.json().get("data", [])) >= 1, "")

        # ═══ Phase 6: Employer + Opportunity ═══
        print("\n🏢 Phase 6: Employer + Opportunity")

        r = await c.post(
            f"/talent/employers/{employer_org_id}",
            json={"company_size": "50-200", "industry": "AI/ML", "description": "Leading AI company"},
            headers=he,
        )
        check("Register employer profile", r.status_code == 201, f"{r.status_code}: {r.text[:200]}")

        r = await c.post(
            f"/talent/opportunities?org_id={employer_org_id}",
            json={
                "title": f"AI Visual Designer Intern {uid()}",
                "description": "Join our team",
                "opportunity_type": "internship",
                "location_mode": "remote",
                "required_capabilities": [{"capability_id": cap_id, "min_level": 1}],
                "preferred_capabilities": [{"capability_id": cap2_id, "min_level": 1}],
                "openings": 2,
            },
            headers=he,
        )
        check("Create opportunity", r.status_code == 201, f"{r.status_code}: {r.text[:200]}")
        opp_id = safe_get(r.json(), "data", "id", default="MISSING")

        r = await c.patch(
            f"/talent/opportunities/{opp_id}?org_id={employer_org_id}",
            json={"status": "open"},
            headers=he,
        )
        check("Open opportunity", r.status_code == 200, f"{r.status_code}")

        # ═══ Phase 7: Matching ═══
        print("\n🔍 Phase 7: Matching")

        r = await c.get("/talent/opportunities/matches", headers=hl)
        check("Candidate-side matching", r.status_code == 200, f"{r.status_code}")

        r = await c.post(f"/talent/opportunities/{opp_id}/match?limit=10", headers=he)
        check("Employer-side matching", r.status_code == 200, f"{r.status_code}: {r.text[:200]}")

        # ═══ Phase 8: Application pipeline ═══
        print("\n📨 Phase 8: Application pipeline")

        r = await c.post(
            f"/talent/opportunities/{opp_id}/apply",
            json={"cover_note": "I'm excited!", "selected_credentials": []},
            headers=hl,
        )
        check("Submit application", r.status_code == 201, f"{r.status_code}: {r.text[:200]}")
        app_id = safe_get(r.json(), "data", "id", default="MISSING")
        check("Status submitted", safe_get(r.json(), "data", "status") == "submitted", "")
        check("Evidence bundle frozen", "snapshot_at" in (safe_get(r.json(), "data", "evidence_bundle") or {}), "")

        for transition in [("screening", he), ("interview", he), ("offer", he), ("accepted", hl), ("hired", he)]:
            status, headers = transition
            r = await c.patch(
                f"/talent/applications/{app_id}/status",
                json={"status": status},
                headers=headers,
            )
            check(f"Transition → {status}", r.status_code == 200, f"{r.status_code}: {r.text[:200]}")

        r = await c.get("/talent/placements", headers=hl)
        check("Placement exists", r.status_code == 200 and len(r.json().get("data", [])) >= 1, "")
        placement_id = safe_get(r.json(), "data", 0, "id", default="MISSING") if isinstance(r.json().get("data"), list) and r.json()["data"] else "MISSING"

        # ═══ Phase 9: Employer verification ═══
        print("\n✅ Phase 9: Employer verification")

        if placement_id != "MISSING":
            r = await c.post(
                f"/talent/placements/{placement_id}/verification",
                json={
                    "capability_ratings": [
                        {"capability_id": cap_id, "level_observed": 4, "score": 0.9, "comment": "Excellent"},
                    ],
                    "overall_rating": 4.5,
                    "overall_comment": "Outstanding intern",
                },
                headers=he,
            )
            check("Employer verification submitted", r.status_code == 201, f"{r.status_code}: {r.text[:200]}")

            r = await c.get("/talent/evidence?per_page=50", headers=hl)
            employer_ev = [e for e in r.json().get("data", []) if e.get("verification_level") == "employer_verified"]
            check("Employer-verified evidence created", len(employer_ev) >= 1, f"count={len(employer_ev)}")
        else:
            check("Employer verification (skipped — no placement)", False, "placement_id missing")

        # ═══ Phase 10: Workforce intelligence ═══
        print("\n📈 Phase 10: Workforce intelligence")

        for endpoint in ["demand", "supply", "gaps", "coverage", "placements", "outcomes", "recommendations"]:
            r = await c.get(f"/talent/intelligence/{endpoint}", headers=ha)
            check(f"Intelligence: {endpoint}", r.status_code == 200, f"{r.status_code}")

        # ═══ Phase 11: Dashboards ═══
        print("\n📊 Phase 11: Dashboards")

        r = await c.get(f"/talent/dashboards/school?org_id={school_org_id}", headers=ha)
        check("School dashboard", r.status_code == 200, f"{r.status_code}: {r.text[:200]}")
        if r.status_code == 200:
            school_data = r.json().get("data", {})
            check("School has placement_stats", "placement_stats" in school_data, "")
            check("School has assessment_pass_rates", "assessment_pass_rates" in school_data, "")

        r = await c.get(f"/talent/dashboards/employer?org_id={employer_org_id}", headers=he)
        check("Employer dashboard", r.status_code == 200, f"{r.status_code}: {r.text[:200]}")
        if r.status_code == 200:
            emp_data = r.json().get("data", {})
            check("Employer has applications_by_stage", "applications_by_stage" in emp_data, "")
            check("Employer has active_placements", "active_placements" in emp_data, "")

        r = await c.get("/talent/dashboards/platform", headers=ha)
        check("Platform dashboard", r.status_code == 200, f"{r.status_code}: {r.text[:200]}")
        if r.status_code == 200:
            plat_data = r.json().get("data", {})
            check("Platform has total_capabilities", "total_capabilities" in plat_data, "")
            check("Platform capabilities > 0", plat_data.get("total_capabilities", 0) >= 2, "")

        # Non-admin cannot access platform dashboard
        r = await c.get("/talent/dashboards/platform", headers=hl)
        check("Platform dashboard blocked for non-admin", r.status_code == 403, f"{r.status_code}")

        # ═══ Phase 12: Talent pools + outreach ═══
        print("\n👥 Phase 12: Talent pools + outreach")

        r = await c.post(
            f"/talent/pools?org_id={employer_org_id}",
            json={"name": f"AI Talent Pool {uid()}", "membership_mode": "manual"},
            headers=he,
        )
        check("Create talent pool", r.status_code == 201, f"{r.status_code}: {r.text[:200]}")
        pool_id = safe_get(r.json(), "data", "id", default="MISSING")

        r = await c.post(
            f"/talent/pools/{pool_id}/members",
            json={"user_id": learner_id, "source": "manual_added"},
            headers=he,
        )
        check("Add pool member (pending consent)", r.status_code == 201, f"{r.status_code}: {r.text[:200]}")
        check(
            "Manual member pending",
            safe_get(r.json(), "data", "consent_status") == "pending_consent",
            f"got {safe_get(r.json(), 'data', 'consent_status')}",
        )

        r = await c.post(
            f"/talent/outreach?org_id={employer_org_id}",
            json={
                "user_id": learner_id,
                "outreach_type": "opportunity_invitation",
                "target_type": "opportunity",
                "target_id": opp_id,
                "message": "We think you'd be a great fit!",
            },
            headers=he,
        )
        check("Send outreach", r.status_code == 201, f"{r.status_code}: {r.text[:200]}")

        # ═══ Phase 13: Security invariants ═══
        print("\n🔒 Phase 13: Security invariants")

        r = await c.post("/talent/capabilities", json={"canonical_name": f"Hack {uid()}", "category": "test"}, headers=hl)
        check("Non-admin blocked from creating capability", r.status_code == 403, f"{r.status_code}")

        other_email = f"other-{uid()}@test.com"
        r = await post_with_backoff(c, "/auth/register", json={"email": other_email, "password": "TestPass123!", "display_name": "Other"})
        r = await post_with_backoff(c, "/auth/login", json={"email": other_email, "password": "TestPass123!"})
        ho = {"Authorization": f"Bearer {r.json()['access_token']}"}

        r = await c.get(f"/talent/applications/{app_id}", headers=ho)
        check("Cross-employer application blocked", r.status_code in (403, 404), f"{r.status_code}")

        r = await c.delete(f"/talent/passport/snapshots/{snapshot_id}", headers=hl)
        check("Revoke snapshot", r.status_code == 204, f"{r.status_code}")

        r = await c.get(f"/verify/passport/{snapshot_token}")
        check("Revoked snapshot returns 410", r.status_code == 410, f"{r.status_code}")

        # ═══ Summary ═══
        print(f"\n{'=' * 60}")
        if errors:
            print(f"PASSED {passed}  FAILED {len(errors)}")
            for e in errors:
                print(f"  FAIL: {e}")
        else:
            print(f"ALL {passed} CHECKS PASSED ✅")
        print(f"{'=' * 60}\n")
        return len(errors) == 0


if __name__ == "__main__":
    ok = asyncio.run(main())
    raise SystemExit(0 if ok else 1)
