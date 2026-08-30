"""E2E lifecycle test — runs against a live API server at localhost:8000.

Tests the full Skill Pack Registry workflow:
  Register → Create content → Pack → Publish → Registry → Install → Update → Diff → Fork → Export → Import → Learning Path → Cohort → Security
"""

import asyncio
import io
import json
import uuid
import zipfile

import httpx

API = "http://localhost:8000/api/v1"


def uid():
    return uuid.uuid4().hex[:8]


async def main():
    transport = httpx.AsyncHTTPTransport(retries=3)
    async with httpx.AsyncClient(base_url=API, timeout=30, transport=transport) as c:
        errors = []
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
        print("\n🔧 Setup: Register users and orgs")
        r1 = await c.post(
            "/auth/register",
            json={
                "email": f"e2e-admin-{uid()}@test.com",
                "password": "TestPass123!",
                "display_name": "Admin",
            },
        )
        check("Register admin", r1.status_code == 201, f"{r1.status_code}: {r1.text[:200]}")
        h1 = {"Authorization": f"Bearer {r1.json()['access_token']}"}

        r2 = await c.post(
            "/auth/register",
            json={
                "email": f"e2e-user-{uid()}@test.com",
                "password": "TestPass123!",
                "display_name": "User",
            },
        )
        check("Register user", r2.status_code == 201, f"{r2.status_code}")
        h2 = {"Authorization": f"Bearer {r2.json()['access_token']}"}

        o1 = (await c.post("/orgs", json={"name": f"Pub-{uid()}"}, headers=h1)).json()["data"]["id"]
        o2 = (await c.post("/orgs", json={"name": f"Con-{uid()}"}, headers=h2)).json()["data"]["id"]
        check("Create orgs", bool(o1 and o2))

        # ═══ 2. Create content ═══
        print("\n📦 Phase 1: Create content in Publisher Org")
        cat = (
            await c.post(f"/orgs/{o1}/categories", json={"name": f"Cat-{uid()}"}, headers=h1)
        ).json()["data"]["id"]
        check("Create category", bool(cat))

        s1 = (
            await c.post(
                f"/orgs/{o1}/skills",
                json={
                    "name": "Prompt Engineering",
                    "description": "Learn prompt engineering basics",
                    "difficulty": "beginner",
                    "category_id": cat,
                },
                headers=h1,
            )
        ).json()["data"]["id"]
        check("Create skill 1", bool(s1))

        s2 = (
            await c.post(
                f"/orgs/{o1}/skills",
                json={
                    "name": "Image Generation",
                    "description": "AI image gen techniques",
                    "difficulty": "intermediate",
                    "category_id": cat,
                },
                headers=h1,
            )
        ).json()["data"]["id"]
        check("Create skill 2", bool(s2))

        ex = await c.post(
            f"/orgs/{o1}/skills/{s1}/exercises",
            json={
                "title": "Write a Prompt",
                "description": "Write a basic prompt",
                "type": "text_answer",
                "config": {},
                "max_score": 100,
            },
            headers=h1,
        )
        check("Create exercise", ex.status_code == 201, f"{ex.status_code}")

        tmpl = (
            await c.post(
                f"/orgs/{o1}/project-templates",
                json={
                    "name": "Hero Shot",
                    "description": "Create a hero product shot",
                    "instructions": "Follow the brief...",
                    "rubric": [{"criterion": "Quality", "max_score": 100}],
                },
                headers=h1,
            )
        ).json()["data"]["id"]
        check("Create template", bool(tmpl))

        # ═══ 3. Pack CRUD ═══
        print("\n📦 Phase 2: Skill Pack CRUD")
        # visibility=public at create is rejected (R79 approval gate) — create
        # default-private; public is reached via submit-review → approve below.
        pk = await c.post(
            f"/orgs/{o1}/packs",
            json={
                "name": f"AI Photo Pack {uid()}",
                "summary": "AI photography training",
                "difficulty": "beginner",
                "scenario_tags": ["ecommerce"],
                "tool_tags": ["midjourney"],
                "learning_outcomes": ["Create hero images"],
                "provenance": {"author_name": "Test Author"},
            },
            headers=h1,
        )
        check("Create pack", pk.status_code == 201, f"{pk.status_code}: {pk.text[:200]}")
        pack_id = pk.json()["data"]["id"]
        check("Pack status=draft", pk.json()["data"]["status"] == "draft")

        # Add contents
        check(
            "Add skill 1",
            (
                await c.post(
                    f"/orgs/{o1}/packs/{pack_id}/skills",
                    json={"skill_id": s1, "sort_order": 0},
                    headers=h1,
                )
            ).status_code
            == 201,
        )
        check(
            "Add skill 2",
            (
                await c.post(
                    f"/orgs/{o1}/packs/{pack_id}/skills",
                    json={"skill_id": s2, "sort_order": 1},
                    headers=h1,
                )
            ).status_code
            == 201,
        )
        check(
            "Add template",
            (
                await c.post(
                    f"/orgs/{o1}/packs/{pack_id}/templates", json={"template_id": tmpl}, headers=h1
                )
            ).status_code
            == 201,
        )

        # List contents
        sk_list = await c.get(f"/orgs/{o1}/packs/{pack_id}/skills", headers=h1)
        check("List pack skills=2", len(sk_list.json()["data"]) == 2)
        tm_list = await c.get(f"/orgs/{o1}/packs/{pack_id}/templates", headers=h1)
        check("List pack templates=1", len(tm_list.json()["data"]) == 1)

        # ═══ 4. Publish Release ═══
        print("\n🚀 Phase 3: Publish Release")
        rel = await c.post(
            f"/orgs/{o1}/packs/{pack_id}/releases",
            json={"version": "1.0.0", "changelog": "Initial release"},
            headers=h1,
        )
        check("Publish v1.0.0", rel.status_code == 201, f"{rel.status_code}: {rel.text[:300]}")
        rd = rel.json()["data"]
        check("3 components", rd["component_count"] == 3, str(rd["component_count"]))
        check("Has SHA-256 checksum", len(rd.get("checksum", "")) == 64)

        # Verify manifest
        rel_det = await c.get(f"/orgs/{o1}/packs/{pack_id}/releases/1.0.0", headers=h1)
        check("Get release detail", rel_det.status_code == 200)
        m = rel_det.json()["data"]["manifest"]
        check("Manifest skills=2", len(m["skills"]) == 2)
        check("Manifest has exercises", any(len(s.get("exercises", [])) > 0 for s in m["skills"]))
        check("Manifest templates=1", len(m["project_templates"]) == 1)
        check("Manifest categories>=1", len(m["categories"]) >= 1)
        check("Manifest schema_version=1", m["schema_version"] == "1")

        # Pack auto-published
        pk2 = await c.get(f"/orgs/{o1}/packs/{pack_id}", headers=h1)
        check("Pack auto-published", pk2.json()["data"]["status"] == "published")

        # Take public via review flow (R79: public requires approval)
        sub = await c.post(f"/orgs/{o1}/packs/{pack_id}/submit-for-review", headers=h1)
        check("Submit for review", sub.status_code == 200, f"{sub.status_code}")
        apr = await c.post(f"/orgs/{o1}/packs/{pack_id}/approve", headers=h1)
        check(
            "Approve → public",
            apr.status_code == 200 and apr.json()["data"]["visibility"] == "public",
        )

        # ═══ 5. Public Registry ═══
        print("\n🌐 Phase 4: Public Registry")
        sr = await c.get("/registry/packs?search=Photo")
        check(
            "Registry search",
            sr.status_code == 200 and len(sr.json()["data"]) >= 1,
            f"found {len(sr.json().get('data', []))}",
        )

        sr2 = await c.get("/registry/packs?scenario=ecommerce")
        check("Filter by scenario", len(sr2.json()["data"]) >= 1)

        pr = await c.get(f"/registry/packs/{pack_id}")
        check("Public pack detail", pr.status_code == 200)
        check("Public detail name", pr.json()["data"]["name"].startswith("AI Photo Pack"))

        prr = await c.get(f"/registry/packs/{pack_id}/releases")
        check("Public releases", len(prr.json()["data"]) >= 1)

        # ═══ 6. Install ═══
        print("\n📥 Phase 5: Install in Consumer Org")
        inst = await c.post(f"/orgs/{o2}/installations", json={"pack_id": pack_id}, headers=h2)
        check("Install pack", inst.status_code == 201, f"{inst.status_code}: {inst.text[:300]}")
        inst_id = inst.json()["data"]["id"]
        check("Installed v1.0.0", inst.json()["data"]["installed_version"] == "1.0.0")

        # Verify content copied
        o2_skills = await c.get(f"/orgs/{o2}/skills", headers=h2)
        check(
            "Consumer org has skills>=2",
            len(o2_skills.json()["data"]) >= 2,
            str(len(o2_skills.json()["data"])),
        )

        # Duplicate blocked
        dup = await c.post(f"/orgs/{o2}/installations", json={"pack_id": pack_id}, headers=h2)
        check("Duplicate install 409", dup.status_code == 409)

        # List installations
        il = await c.get(f"/orgs/{o2}/installations", headers=h2)
        check("List installations", len(il.json()["data"]) >= 1)

        # ═══ 7. Update + Diff ═══
        print("\n🔄 Phase 6: Publish v1.1.0 + Update Check + Diff")
        s3 = (
            await c.post(
                f"/orgs/{o1}/skills",
                json={
                    "name": "Advanced Composition",
                    "description": "Advanced techniques",
                    "difficulty": "advanced",
                    "category_id": cat,
                },
                headers=h1,
            )
        ).json()["data"]["id"]
        await c.post(
            f"/orgs/{o1}/packs/{pack_id}/skills", json={"skill_id": s3, "sort_order": 2}, headers=h1
        )
        rel2 = await c.post(
            f"/orgs/{o1}/packs/{pack_id}/releases",
            json={"version": "1.1.0", "changelog": "Added advanced skill"},
            headers=h1,
        )
        check("Publish v1.1.0", rel2.status_code == 201)

        upd = await c.get(f"/orgs/{o2}/installations/{inst_id}", headers=h2)
        check("Update available", upd.json()["data"]["update_available"] is True)
        check("Latest=1.1.0", upd.json()["data"]["latest_version"] == "1.1.0")

        diff = await c.get(f"/orgs/{o2}/installations/{inst_id}/diff?version=1.1.0", headers=h2)
        check("Diff computed", diff.status_code == 200, f"{diff.status_code}: {diff.text[:300]}")
        check("Diff has added", len(diff.json()["data"].get("added", [])) >= 1)

        # ═══ 8. Fork ═══
        print("\n🔀 Phase 7: Fork")
        fk = await c.post(f"/orgs/{o2}/installations/{inst_id}/fork", headers=h2)
        check("Fork", fk.status_code == 200, f"{fk.status_code}")
        check("Status=forked", fk.json()["data"]["status"] == "forked")

        fk_det = await c.get(f"/orgs/{o2}/installations/{inst_id}", headers=h2)
        check("Forked no update", fk_det.json()["data"]["update_available"] is False)

        # ═══ 9. Export + Import ═══
        print("\n📤 Phase 8: Export & Import")
        exp = await c.get(f"/orgs/{o1}/packs/{pack_id}/releases/1.0.0/export", headers=h1)
        check("Export zip", exp.status_code == 200)
        check("Content-Type zip", exp.headers.get("content-type") == "application/zip")

        with zipfile.ZipFile(io.BytesIO(exp.content)) as zf:
            check("Zip has manifest", "openskill-pack.json" in zf.namelist())
            mj = json.loads(zf.read("openskill-pack.json"))
            check("Export manifest valid", mj["schema_version"] == "1")

        # Import into org3
        r3 = await c.post(
            "/auth/register",
            json={
                "email": f"e2e-imp-{uid()}@test.com",
                "password": "TestPass123!",
                "display_name": "Imp",
            },
        )
        h3 = {"Authorization": f"Bearer {r3.json()['access_token']}"}
        o3 = (await c.post("/orgs", json={"name": f"Imp-{uid()}"}, headers=h3)).json()["data"]["id"]

        imp = await c.post(
            f"/orgs/{o3}/packs/import",
            files={"file": ("pack.zip", exp.content, "application/zip")},
            headers=h3,
        )
        check("Import pack", imp.status_code == 201, f"{imp.status_code}: {imp.text[:300]}")
        check(
            "Imported name matches", imp.json()["data"]["pack"]["name"].startswith("AI Photo Pack")
        )

        # ═══ 10. Learning Paths ═══
        print("\n📋 Phase 9: Learning Paths")
        o2_sk = [
            s["id"] for s in (await c.get(f"/orgs/{o2}/skills", headers=h2)).json()["data"][:2]
        ]

        lp = await c.post(
            f"/orgs/{o2}/paths",
            json={"name": "AI Creator Path", "description": "Full track", "estimated_minutes": 480},
            headers=h2,
        )
        check("Create path", lp.status_code == 201, f"{lp.status_code}")
        path_id = lp.json()["data"]["id"]

        check(
            "Add section",
            (
                await c.post(
                    f"/orgs/{o2}/paths/{path_id}/items",
                    json={"item_type": "section", "section_title": "Fundamentals", "sort_order": 0},
                    headers=h2,
                )
            ).status_code
            == 201,
        )

        if o2_sk:
            check(
                "Add skill item",
                (
                    await c.post(
                        f"/orgs/{o2}/paths/{path_id}/items",
                        json={"item_type": "skill", "skill_id": o2_sk[0], "sort_order": 1},
                        headers=h2,
                    )
                ).status_code
                == 201,
            )
        if len(o2_sk) > 1:
            check(
                "Add optional item",
                (
                    await c.post(
                        f"/orgs/{o2}/paths/{path_id}/items",
                        json={
                            "item_type": "skill",
                            "skill_id": o2_sk[1],
                            "sort_order": 2,
                            "required": False,
                        },
                        headers=h2,
                    )
                ).status_code
                == 201,
            )

        items = await c.get(f"/orgs/{o2}/paths/{path_id}/items", headers=h2)
        check("List items>=2", len(items.json()["data"]) >= 2)

        check(
            "Publish path",
            (
                await c.put(f"/orgs/{o2}/paths/{path_id}", json={"status": "published"}, headers=h2)
            ).status_code
            == 200,
        )

        prog = await c.get(f"/orgs/{o2}/paths/{path_id}/my-progress", headers=h2)
        check("Progress endpoint", prog.status_code == 200)
        check("Progress pct=0", prog.json()["data"]["pct"] == 0)

        # ═══ 11. Cohort Assignment ═══
        print("\n👥 Phase 10: Cohort Path Assignment")
        coh = await c.post(f"/orgs/{o2}/cohorts", json={"name": f"Cohort-{uid()}"}, headers=h2)
        check("Create cohort", coh.status_code == 201)
        coh_id = coh.json()["data"]["id"]
        await c.put(f"/orgs/{o2}/cohorts/{coh_id}", json={"status": "active"}, headers=h2)

        asgn = await c.post(
            f"/orgs/{o2}/cohorts/{coh_id}/paths", json={"path_id": path_id}, headers=h2
        )
        check(
            "Assign path to cohort",
            asgn.status_code == 201,
            f"{asgn.status_code}: {asgn.text[:200]}",
        )

        cp = await c.get(f"/orgs/{o2}/cohorts/{coh_id}/paths", headers=h2)
        check("List cohort paths>=1", len(cp.json()["data"]) >= 1)

        check(
            "Unassign path",
            (await c.delete(f"/orgs/{o2}/cohorts/{coh_id}/paths/{path_id}", headers=h2)).status_code
            == 204,
        )

        # ═══ 12. Security ═══
        print("\n🔒 Phase 11: Cross-org Security")
        check(
            "Cross-org pack 404",
            (await c.get(f"/orgs/{o2}/packs/{pack_id}", headers=h2)).status_code == 404,
        )
        check(
            "Cross-org publish 403/404",
            (
                await c.post(
                    f"/orgs/{o2}/packs/{pack_id}/releases", json={"version": "9.9.9"}, headers=h2
                )
            ).status_code
            in (403, 404),
        )
        check(
            "Cross-org install 404",
            (await c.get(f"/orgs/{o1}/installations/{inst_id}", headers=h1)).status_code == 404,
        )
        check(
            "Cross-org path 404",
            (await c.get(f"/orgs/{o1}/paths/{path_id}", headers=h1)).status_code == 404,
        )

        # ═══ 13. Cleanup ═══
        print("\n🗑️  Phase 12: Remove installation")
        check(
            "Remove installation",
            (await c.delete(f"/orgs/{o2}/installations/{inst_id}", headers=h2)).status_code == 204,
        )

        # ═══ Summary ═══
        print(f"\n{'=' * 60}")
        print(f"  E2E RESULTS: {passed} passed, {len(errors)} failed")
        if errors:
            print(f"  FAILURES: {errors}")
        else:
            print("  ALL TESTS PASSED ✅")
        print(f"{'=' * 60}")

        return len(errors) == 0


if __name__ == "__main__":
    ok = asyncio.run(main())
    exit(0 if ok else 1)
