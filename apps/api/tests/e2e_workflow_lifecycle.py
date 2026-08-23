"""E2E workflow lifecycle test — runs against a live API server at localhost:8000.

Issue #21 full loop:
  Publish workflow pack → Registry → Capability gate → Install → Bindings
  → Run (mock provider) → Review gate decide → Complete → Audit trail
  → Requirement profile → Match → Production draft → Learning draft → Confirm
  → Creator shortlist → Offer → Accept → Cross-org security → Cleanup

Usage: make infra-up && make dev-api, then:
  cd apps/api && PYTHONPATH=. uv run python tests/e2e_workflow_lifecycle.py
"""

import asyncio
import uuid

import httpx

API = "http://localhost:8000/api/v1"


def uid():
    return uuid.uuid4().hex[:8]


def _definition() -> dict:
    """prompt_template → provider_action(image_generation) → review_gate → output."""
    return {
        "schema_version": 1,
        "inputs": [
            {"key": "product_name", "type": "text", "required": True},
        ],
        "outputs": [
            {"key": "final", "type": "image", "from_step": "deliver", "from_port": "final"},
        ],
        "steps": [
            {
                "id": "build_prompt",
                "type": "prompt_template",
                "name": "Build prompt",
                "config": {"template": "Professional photo of {{inputs.product_name}}"},
                "inputs": [],
                "outputs": [{"port": "prompt", "type": "prompt"}],
            },
            {
                "id": "generate",
                "type": "provider_action",
                "name": "Generate key visual",
                "config": {"capability": "image_generation", "binding_mode": "auto"},
                "inputs": [{"port": "prompt", "type": "prompt"}],
                "outputs": [{"port": "result", "type": "image"}],
            },
            {
                "id": "qa_gate",
                "type": "review_gate",
                "name": "Brand QA",
                "config": {"instructions": "Check brand consistency", "due_days": 7},
                "inputs": [{"port": "subject", "type": "image"}],
                "outputs": [
                    {"port": "decision", "type": "selection"},
                    {"port": "passed", "type": "image"},
                ],
            },
            {
                "id": "deliver",
                "type": "output",
                "name": "Deliver",
                "config": {},
                "inputs": [{"port": "final", "type": "image"}],
                "outputs": [{"port": "final", "type": "image"}],
            },
        ],
        "edges": [
            {"id": "e1", "from_step": "build_prompt", "from_port": "prompt", "to_step": "generate", "to_port": "prompt"},
            {"id": "e2", "from_step": "generate", "from_port": "result", "to_step": "qa_gate", "to_port": "subject"},
            {"id": "e3", "from_step": "qa_gate", "from_port": "passed", "to_step": "deliver", "to_port": "final"},
        ],
        "ui": {"positions": {"build_prompt": [0, 0], "generate": [280, 0], "qa_gate": [560, 0], "deliver": [840, 0]}},
    }


async def main() -> bool:  # noqa: PLR0915
    transport = httpx.AsyncHTTPTransport(retries=3)
    async with httpx.AsyncClient(base_url=API, timeout=30, transport=transport) as c:
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

        # ═══ 1. Setup ═══
        print("\n🔧 Setup: users + orgs")
        r1 = await c.post("/auth/register", json={
            "email": f"wf-pub-{uid()}@test.com", "password": "TestPass123!", "display_name": "Publisher",
        })
        check("Register publisher", r1.status_code == 201, f"{r1.status_code}: {r1.text[:200]}")
        h1 = {"Authorization": f"Bearer {r1.json()['access_token']}"}

        r2 = await c.post("/auth/register", json={
            "email": f"wf-con-{uid()}@test.com", "password": "TestPass123!", "display_name": "Consumer",
        })
        check("Register consumer", r2.status_code == 201, f"{r2.status_code}")
        h2 = {"Authorization": f"Bearer {r2.json()['access_token']}"}
        u2_id = r2.json()["user"]["id"]

        o1 = (await c.post("/orgs", json={"name": f"WfPub-{uid()}"}, headers=h1)).json()["data"]["id"]
        o2 = (await c.post("/orgs", json={"name": f"WfCon-{uid()}"}, headers=h2)).json()["data"]["id"]
        check("Create orgs", bool(o1 and o2))

        # ═══ 2. Publish workflow pack ═══
        print("\n📦 Phase 1: Publisher creates + publishes workflow pack")
        rp = await c.post(f"/orgs/{o1}/workflow-packs", json={
            "name": f"Hero Image Workflow {uid()}",
            "summary": "E-commerce hero image production",
            "workflow_type": "production",
            "scenario_tags": ["ecommerce"],
        }, headers=h1)
        check("Create workflow pack", rp.status_code == 201, f"{rp.status_code}: {rp.text[:200]}")
        pack_id = rp.json()["data"]["id"]

        rd = await c.put(f"/orgs/{o1}/workflow-packs/{pack_id}/definition",
                         json={"definition": _definition()}, headers=h1)
        check("Set definition", rd.status_code == 200, f"{rd.status_code}: {rd.text[:300]}")
        check("Capability tags derived", rd.json()["data"]["capability_tags"] == ["image_generation"])

        rv = await c.post(f"/orgs/{o1}/workflow-packs/validate",
                          json={"definition": _definition()}, headers=h1)
        check("Dry-run validate ok", rv.status_code == 200 and rv.json()["data"]["valid"])

        rr = await c.post(f"/orgs/{o1}/workflow-packs/{pack_id}/releases", json={
            "version": "1.0.0",
            "changelog": "Initial release",
            "dependencies": {
                "requires_capabilities": [{"capability": "image_generation", "features": []}],
            },
        }, headers=h1)
        check("Publish 1.0.0", rr.status_code == 201, f"{rr.status_code}: {rr.text[:200]}")
        check("Checksum is sha256", len(rr.json()["data"]["checksum"]) == 64)
        check("Step count 4", rr.json()["data"]["step_count"] == 4)

        await c.post(f"/orgs/{o1}/workflow-packs/{pack_id}/submit-review", headers=h1)
        ra = await c.post(f"/orgs/{o1}/workflow-packs/{pack_id}/approve", headers=h1)
        check("Approve → public", ra.status_code == 200 and ra.json()["data"]["visibility"] == "public")

        # ═══ 3. Registry ═══
        print("\n🌐 Phase 2: Consumer browses registry")
        rg = await c.get(f"/registry/workflow-packs/{pack_id}")
        check("Registry detail public", rg.status_code == 200, f"{rg.status_code}")
        rpre = await c.get(f"/registry/workflow-packs/{pack_id}/preview")
        check("Preview available", rpre.status_code == 200)
        check("Preview excludes ui block", "ui" not in rpre.json()["data"].get("definition", {}))

        # ═══ 4. Capability gate + install ═══
        print("\n🔌 Phase 3: Capability gate → provider setup → install")
        ri_fail = await c.post(f"/orgs/{o2}/workflow-installations",
                               json={"pack_id": pack_id, "version": "1.0.0"}, headers=h2)
        check("Install blocked without offering", ri_fail.status_code == 422
              and ri_fail.json()["error"]["code"] == "CAPABILITY_UNSATISFIED",
              f"{ri_fail.status_code}: {ri_fail.text[:200]}")

        adapters = (await c.get("/providers/adapters", headers=h2)).json()["data"]
        mock_id = next(a for a in adapters if a["key"] == "mock")["id"]
        rc = await c.post(f"/orgs/{o2}/provider-connections",
                          json={"adapter_id": mock_id, "name": "Mock Provider"}, headers=h2)
        check("Create mock connection", rc.status_code == 201, f"{rc.status_code}")
        conn_id = rc.json()["data"]["id"]

        ro = await c.post(f"/orgs/{o2}/provider-offerings", json={
            "connection_id": conn_id, "capability_key": "image_generation", "model_name": "mock-image-v1",
        }, headers=h2)
        check("Create offering", ro.status_code == 201, f"{ro.status_code}")

        ri = await c.post(f"/orgs/{o2}/workflow-installations",
                          json={"pack_id": pack_id, "version": "1.0.0"}, headers=h2)
        check("Install succeeds with offering", ri.status_code == 201, f"{ri.status_code}: {ri.text[:200]}")
        install_id = ri.json()["data"]["id"]

        rb = await c.get(f"/orgs/{o2}/workflow-installations/{install_id}/bindings", headers=h2)
        check("Binding suggestion created", rb.status_code == 200 and len(rb.json()["data"]) == 1,
              f"{rb.status_code}: {rb.text[:200]}")

        # ═══ 5. Run + review gate ═══
        print("\n▶️  Phase 4: Run the workflow (mock provider + human gate)")
        rrun = await c.post(f"/orgs/{o2}/workflow-runs", json={
            "installation_id": install_id,
            "inputs": {"product_name": "ceramic mug"},
            "idempotency_key": f"e2e-{uid()}",
        }, headers=h2)
        check("Create run", rrun.status_code == 201, f"{rrun.status_code}: {rrun.text[:200]}")
        run_id = rrun.json()["data"]["id"]

        # Poll until suspended at the review gate
        run_data = None
        for _ in range(40):
            rget = await c.get(f"/orgs/{o2}/workflow-runs/{run_id}", headers=h2)
            run_data = rget.json()["data"]
            if run_data["status"] in ("waiting_review", "failed", "completed"):
                break
            await asyncio.sleep(0.3)
        check("Run suspends at review gate", run_data is not None and run_data["status"] == "waiting_review",
              f"status={run_data['status'] if run_data else None} error={run_data.get('error') if run_data else None}")

        gen = next((s for s in run_data["step_runs"] if s["step_id"] == "generate"), {})
        check("Mock provider executed", str(gen.get("output", {}).get("result", "")).startswith("mock-asset-"))
        check("actual_offering_used recorded", bool(gen.get("offering_id")))

        rrev = await c.get(f"/orgs/{o2}/step-reviews", headers=h2)
        review = next((rv for rv in rrev.json()["data"]
                       if any(s["id"] == rv["step_run_id"] for s in run_data["step_runs"])), None)
        check("Open review exists with due date", review is not None and bool(review.get("due_at")))

        rdec = await c.post(f"/orgs/{o2}/step-reviews/{review['id']}/decide",
                            json={"decision": "approved", "note": "LGTM"}, headers=h2)
        check("Decide approve (sync validate-then-accept)", rdec.status_code == 200)

        rdup = await c.post(f"/orgs/{o2}/step-reviews/{review['id']}/decide",
                            json={"decision": "rejected"}, headers=h2)
        check("Double-decide → 409", rdup.status_code == 409
              and rdup.json()["error"]["code"] == "WF_REVIEW_ALREADY_DECIDED")

        for _ in range(40):
            rget = await c.get(f"/orgs/{o2}/workflow-runs/{run_id}", headers=h2)
            run_data = rget.json()["data"]
            if run_data["status"] in ("completed", "failed"):
                break
            await asyncio.sleep(0.3)
        check("Run completes after approval", run_data["status"] == "completed",
              f"status={run_data['status']} error={run_data.get('error')}")
        check("Run outputs present", bool(run_data.get("outputs")))
        event_types = {e["event_type"] for e in run_data["events"]}
        check("Audit trail complete", {
            "run_created", "run_started", "review_requested", "review_decided", "run_completed",
        } <= event_types, f"events={sorted(event_types)}")

        # ═══ 6. Matching + production draft ═══
        print("\n🎯 Phase 5: Requirement profile → match → production draft")
        rprof = await c.post(f"/orgs/{o2}/requirement-profiles", json={
            "context_type": "production",
            "structured_requirements": {
                "goal": "15s product hero visuals",
                "scenario": "ecommerce",
                "required_capabilities": ["image_generation"],
                "output_type": "image",
            },
        }, headers=h2)
        check("Create profile from form", rprof.status_code == 201, f"{rprof.status_code}: {rprof.text[:200]}")
        prof_id = rprof.json()["data"]["id"]
        await c.post(f"/orgs/{o2}/requirement-profiles/{prof_id}/confirm", headers=h2)

        rm = await c.post(f"/orgs/{o2}/match", json={
            "requirement_profile_id": prof_id, "target_entity_type": "workflow_pack", "limit": 50,
        }, headers=h2)
        check("Match run", rm.status_code == 200, f"{rm.status_code}: {rm.text[:200]}")
        match_data = rm.json()["data"]
        ranked_ids = [x["entity_id"] for x in match_data["results"]]
        check("Installed pack ranked", pack_id in ranked_ids)
        top = next((x for x in match_data["results"] if x["entity_id"] == pack_id), {})
        check("Result has reasons", len(top.get("reasons", [])) > 0)
        check("Engine + config versions recorded",
              match_data["engine_version"] == "1.0.0" and match_data["config_version"] >= 1)

        rdraft = await c.post(f"/orgs/{o2}/drafts/production-solution",
                              json={"profile_id": prof_id}, headers=h2)
        check("Production draft composed", rdraft.status_code == 201, f"{rdraft.status_code}: {rdraft.text[:300]}")
        chain = rdraft.json()["data"]["payload"].get("workflow_chain", [])
        check("Draft has workflow chain", any(w["entity_id"] == pack_id for w in chain))

        # ═══ 7. Learning draft → confirm → path ═══
        print("\n📚 Phase 6: Learning profile → draft → confirmed path")
        rlprof = await c.post(f"/orgs/{o2}/requirement-profiles", json={
            "context_type": "learning",
            "structured_requirements": {"goal": "Learn AI e-commerce visuals"},
        }, headers=h2)
        lprof_id = rlprof.json()["data"]["id"]
        await c.post(f"/orgs/{o2}/requirement-profiles/{lprof_id}/confirm", headers=h2)

        rldraft = await c.post(f"/orgs/{o2}/drafts/learning-path",
                               json={"profile_id": lprof_id}, headers=h2)
        check("Learning draft composed", rldraft.status_code == 201, f"{rldraft.status_code}: {rldraft.text[:300]}")
        ldraft_id = rldraft.json()["data"]["id"]

        rconf = await c.post(f"/orgs/{o2}/drafts/{ldraft_id}/confirm", headers=h2)
        check("Confirm learning draft", rconf.status_code == 200, f"{rconf.status_code}: {rconf.text[:300]}")
        path_id = rconf.json()["data"]["materialized_entity_id"]
        rpath = await c.get(f"/orgs/{o2}/paths/{path_id}", headers=h2)
        check("Materialized learning path exists", rpath.status_code == 200)

        rconf2 = await c.post(f"/orgs/{o2}/drafts/{ldraft_id}/confirm", headers=h2)
        check("Double-confirm → 422", rconf2.status_code == 422)

        # ═══ 8. Creator shortlist → offer → accept ═══
        print("\n👥 Phase 7: Creator shortlist (human assigns, creator accepts)")
        rproj = await c.post(f"/orgs/{o2}/projects", json={
            "title": f"Hero Shot Production {uid()}",
            "description": "Produce hero shots for the client",
            "instructions": "Follow the brand brief",
            "rubric": [{"criterion": "Quality", "max_score": 100}],
        }, headers=h2)
        check("Create project", rproj.status_code == 201, f"{rproj.status_code}: {rproj.text[:200]}")
        proj_id = rproj.json()["data"]["id"]

        rtprof = await c.post(f"/orgs/{o2}/requirement-profiles", json={
            "context_type": "talent_matching",
            "structured_requirements": {"goal": "Find a hero-shot creator"},
        }, headers=h2)
        tprof_id = rtprof.json()["data"]["id"]
        await c.post(f"/orgs/{o2}/requirement-profiles/{tprof_id}/confirm", headers=h2)

        rshort = await c.get(
            f"/orgs/{o2}/projects/{proj_id}/creator-shortlist?profile_id={tprof_id}", headers=h2)
        check("Shortlist generated", rshort.status_code == 200, f"{rshort.status_code}: {rshort.text[:200]}")

        roffer = await c.post(f"/orgs/{o2}/creator-assignments", json={
            "project_id": proj_id, "user_id": u2_id,
        }, headers=h2)
        check("Offer assignment (human action)", roffer.status_code == 201, f"{roffer.status_code}: {roffer.text[:200]}")
        assign_id = roffer.json()["data"]["id"]
        check("Assignment starts as offer", roffer.json()["data"]["status"] == "offered")

        raccept = await c.post(f"/orgs/{o2}/creator-assignments/{assign_id}/respond",
                               json={"accept": True}, headers=h2)
        check("Creator accepts", raccept.status_code == 200
              and raccept.json()["data"]["status"] == "accepted")

        # ═══ 9. Cross-org security ═══
        print("\n🔒 Phase 8: Cross-org isolation")
        rsec1 = await c.get(f"/orgs/{o1}/workflow-runs/{run_id}", headers=h1)
        check("Publisher cannot see consumer run", rsec1.status_code == 404)
        rsec2 = await c.get(f"/orgs/{o1}/workflow-installations/{install_id}", headers=h1)
        check("Publisher cannot see consumer install", rsec2.status_code == 404)
        rsec3 = await c.get(f"/orgs/{o1}/requirement-profiles/{prof_id}", headers=h1)
        check("Publisher cannot see consumer profile", rsec3.status_code == 404)

        # ═══ 10. Cleanup ═══
        print("\n🧹 Phase 9: Cleanup")
        rdel = await c.delete(f"/orgs/{o2}/workflow-installations/{install_id}", headers=h2)
        check("Uninstall", rdel.status_code == 204)

        # ═══ Summary ═══
        total = passed + len(errors)
        print(f"\n{'='*50}")
        print(f"  {passed}/{total} checks passed")
        if errors:
            print("  Failures:")
            for e in errors:
                print(f"    ❌ {e}")
        print("=" * 50)
        return not errors


if __name__ == "__main__":
    ok = asyncio.run(main())
    exit(0 if ok else 1)
