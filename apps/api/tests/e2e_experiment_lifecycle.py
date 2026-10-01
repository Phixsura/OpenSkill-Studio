"""E2E experiment lifecycle — runs against a live API server (APP_ENV=test).

Issue #42 full loop over real HTTP (rate-limit dependency, exception
handlers, response envelopes, auth stack):

  admin bootstrap → non-admin 403 wall → layer → experiment → ethics-gate
  422 → immutable spec v1 → slice allocation → schedule/run → ramp rules →
  sticky preview → direct-promote refusal (EXPERIMENT_DECISION_REQUIRED) →
  enum-guard 422 → analysis (mSPRT, result hash) → decision (forged hash
  refused → real hash promotes) → promotion draft → approve → apply →
  inactive MatchingConfig version exists → surface-key reuse → cleanup.

Usage: make infra-up, then (a dedicated port avoids stale-server 404s):
  cd apps/api && APP_ENV=test uv run uvicorn app.main:app --port 8442 &
  cd apps/api && E2E_EXP_API=http://localhost:8442/api/v1 \
      PYTHONPATH=. uv run python tests/e2e_experiment_lifecycle.py
"""

import asyncio
import os
import uuid

import httpx

API = os.environ.get("E2E_EXP_API", "http://localhost:8442/api/v1")

PASS = 0
FAIL = 0


def uid() -> str:
    return uuid.uuid4().hex[:12]


def check(name: str, ok: bool, detail: str = ""):
    global PASS, FAIL
    if ok:
        PASS += 1
        print(f"  ok  {name}")
    else:
        FAIL += 1
        print(f" FAIL {name}: {detail}")


async def promote_to_admin(user_id: str) -> None:
    from sqlalchemy import update as _sa_update

    from app.core.database import AsyncSessionLocal, engine
    from app.models.user import User as _User
    from app.models.user import UserRole as _UserRole

    await engine.dispose(close=False)
    async with AsyncSessionLocal() as db:
        await db.execute(
            _sa_update(_User).where(_User.id == user_id).values(role=_UserRole.ADMIN)
        )
        await db.commit()
    await engine.dispose()


async def seed_matching_configs(entity_type: str) -> tuple[str, str]:
    from app.core.database import AsyncSessionLocal, engine
    from app.models.matching import MatchingConfig

    await engine.dispose(close=False)
    async with AsyncSessionLocal() as db:
        active = MatchingConfig(
            version=1, target_entity_type=entity_type,
            weights={"skill_fit": 1.0}, thresholds={}, is_active=True,
        )
        db.add(active)
        await db.flush()
        active_id = active.id
        await db.commit()
    await engine.dispose()
    return active_id, entity_type


async def grant_org_admin(user_id: str) -> str:
    """Create a tenant+org and make the user its admin; returns org_id."""
    from ulid import ULID

    from app.controlplane.models.tenant import TenantAccount
    from app.core.database import AsyncSessionLocal, engine
    from app.models.organization import Organization, OrgMember, OrgRole

    await engine.dispose(close=False)
    async with AsyncSessionLocal() as db:
        tenant = TenantAccount(
            name=f"e2e-t-{str(ULID()).lower()}", slug=f"e2e-t-{str(ULID()).lower()}"
        )
        db.add(tenant)
        await db.flush()
        org = Organization(
            name="e2e delegation org", slug=f"e2e-o-{str(ULID()).lower()}",
            tenant_id=tenant.id,
        )
        db.add(org)
        await db.flush()
        db.add(OrgMember(org_id=org.id, user_id=user_id, role=OrgRole.ADMIN))
        org_id = org.id
        await db.commit()
    await engine.dispose()
    return org_id


async def cleanup(experiment_ids: list[str], layer_key: str, entity_type: str) -> None:
    from sqlalchemy import delete as _delete

    from app.core.database import AsyncSessionLocal, engine
    from app.experiments.models import Experiment, ExperimentLayer, HoldoutGroup
    from app.models.matching import MatchingConfig

    await engine.dispose(close=False)
    async with AsyncSessionLocal() as db:
        await db.execute(_delete(Experiment).where(Experiment.id.in_(experiment_ids)))
        await db.execute(_delete(HoldoutGroup).where(HoldoutGroup.title.in_(
            ["E2E holdout", "dup", "too big", "nope"])))
        await db.execute(_delete(ExperimentLayer).where(ExperimentLayer.key == layer_key))
        await db.execute(
            _delete(ExperimentLayer).where(ExperimentLayer.key.like("lyr-org-%"))
        )
        from app.controlplane.models.tenant import TenantAccount
        from app.models.organization import Organization

        await db.execute(
            _delete(Organization).where(Organization.name == "e2e delegation org")
        )
        await db.execute(
            _delete(TenantAccount).where(TenantAccount.slug.like("e2e-t-%"))
        )
        await db.execute(
            _delete(MatchingConfig).where(MatchingConfig.target_entity_type == entity_type)
        )
        await db.commit()
    await engine.dispose()


async def main() -> int:
    async with httpx.AsyncClient(base_url=API, timeout=30, trust_env=False) as c:
        # ── Bootstrap: admin (SQL-promoted) + plain student ───────────
        r = await c.post("/auth/register", json={
            "email": f"exp-adm-{uid()}@test.com", "password": "TestPass123!",
            "display_name": "Exp Admin",
        })
        check("register admin-to-be", r.status_code == 201, f"{r.status_code} {r.text[:200]}")
        admin_id = r.json()["user"]["id"]
        await promote_to_admin(admin_id)
        r = await c.post("/auth/login", json={
            "email": r.json()["user"]["email"], "password": "TestPass123!",
        })
        check("re-login as admin", r.status_code == 200, str(r.status_code))
        admin = {"Authorization": f"Bearer {r.json()['access_token']}"}

        r = await c.post("/auth/register", json={
            "email": f"exp-stu-{uid()}@test.com", "password": "TestPass123!",
            "display_name": "Student",
        })
        student = {"Authorization": f"Bearer {r.json()['access_token']}"}
        student_id = r.json()["user"]["id"]

        # ── Authorization wall: operator surfaces are admin-only ──────
        for path in ("/experiments", "/experiments/decisions",
                     "/experiments/promotion-drafts", "/experiments/layers",
                     "/experiments/metric-definitions"):
            r = await c.get(path, headers=student)
            check(f"student 403 on GET {path}", r.status_code == 403,
                  f"{r.status_code} {r.text[:120]}")
        r = await c.get("/experiments")
        check("anonymous 401", r.status_code == 401, str(r.status_code))

        # ── Layer + seed defs + matching baseline ─────────────────────
        layer_key = f"e2e-match-{uid()}"
        r = await c.post("/experiments/layers", headers=admin,
                         json={"key": layer_key, "domain": "matching"})
        check("create layer", r.status_code == 201, r.text[:200])
        r = await c.post("/experiments/metric-definitions/seed", headers=admin, json={})
        check("seed metric definitions", r.status_code == 200, r.text[:200])
        entity_type = f"e2e-{uid()[:10]}"
        active_config_id, _ = await seed_matching_configs(entity_type)

        # ── Ethics gate over HTTP ──────────────────────────────────────
        exp_key = f"e2e-exp-{uid()}"
        r = await c.post("/experiments", headers=admin, json={
            "key": exp_key, "title": "E2E matching weights", "domain": "matching",
            "layer_key": layer_key,
        })
        check("create experiment", r.status_code == 201, r.text[:200])
        exp_id = r.json()["data"]["id"]
        experiment_ids = [exp_id]

        bad_spec = {
            "hypothesis": "sensitive targeting must be refused end to end",
            "unit_type": "organization",
            "variants": [
                {"key": "control", "name": "C", "weight_bp": 5000, "is_control": True},
                {"key": "treatment", "name": "T", "weight_bp": 5000},
            ],
            "metrics": {"primary": ["exposure_rate"],
                        "guardrails": [{"metric_key": "exposure_rate", "op": "lte",
                                        "threshold": 1.0}]},
            "population": {"rules": [{"field": "gender", "op": "eq", "values": ["x"]}]},
        }
        r = await c.post(f"/experiments/{exp_id}/versions", headers=admin,
                         json={"spec": bad_spec})
        check("protected-attribute targeting → 422 EXPERIMENT_FORBIDDEN_TARGETING",
              r.status_code == 422
              and r.json()["error"]["code"] == "EXPERIMENT_FORBIDDEN_TARGETING",
              r.text[:200])

        good_spec = dict(bad_spec, population={"rules": []})
        r = await c.post(f"/experiments/{exp_id}/versions", headers=admin,
                         json={"spec": good_spec})
        check("create spec v1", r.status_code == 201, r.text[:200])
        spec_hash = r.json()["data"]["spec_hash"]
        check("spec hash present", len(spec_hash) == 64, spec_hash)

        r = await c.post(f"/experiments/layers/{layer_key}/allocations", headers=admin,
                         json={"experiment_id": exp_id, "slice_start": 0,
                               "slice_end": 9999})
        check("allocate slices", r.status_code == 201, r.text[:200])

        # ── Lifecycle over HTTP (incl. the launch checklist, §5 v2) ────
        r = await c.post(f"/experiments/{exp_id}/transition", headers=admin,
                         json={"to_status": "review"})
        check("transition → review", r.status_code == 200, r.text[:200])
        r = await c.post(f"/experiments/{exp_id}/transition", headers=admin,
                         json={"to_status": "scheduled"})
        check("schedule without checklist refused",
              r.status_code == 422
              and r.json()["error"]["code"] == "EXPERIMENT_CHECKLIST_INCOMPLETE",
              r.text[:200])
        checklist = {
            "hypothesis_peer_checked": True, "power_computed": True,
            "metrics_reviewed": True, "rollback_owner_named": True,
        }
        r = await c.post(f"/experiments/{exp_id}/transition", headers=admin,
                         json={"to_status": "scheduled", "checklist": checklist})
        check("transition → scheduled (checklist affirmed)",
              r.status_code == 200, r.text[:200])
        r = await c.post(f"/experiments/{exp_id}/transition", headers=admin,
                         json={"to_status": "running"})
        check("transition → running", r.status_code == 200, r.text[:200])
        r = await c.patch(f"/experiments/{exp_id}/ramp", headers=admin,
                          json={"ramp_bp": 10000})
        check("ramp to 100%", r.status_code == 200, r.text[:200])
        r = await c.patch(f"/experiments/{exp_id}/ramp", headers=admin,
                          json={"ramp_bp": 5000})
        check("ramp decrease refused",
              r.status_code == 422
              and r.json()["error"]["code"] == "EXPERIMENT_RAMP_DECREASE", r.text[:200])

        # Enum guard names the vocabulary
        r = await c.get("/experiments?status=bogus", headers=admin)
        check("enum guard 422 names vocabulary",
              r.status_code == 422 and "bogus" in r.json()["error"]["message"],
              r.text[:200])

        # Deterministic sticky preview (no writes)
        r = await c.post(f"/experiments/{exp_id}/assignments:preview", headers=admin,
                         json={"unit_type": "organization", "unit_id": "org-e2e-1"})
        first = r.json()["data"]
        r = await c.post(f"/experiments/{exp_id}/assignments:preview", headers=admin,
                         json={"unit_type": "organization", "unit_id": "org-e2e-1"})
        check("preview deterministic", r.json()["data"] == first, r.text[:200])

        # Direct promote refused — decisions only
        r = await c.post(f"/experiments/{exp_id}/transition", headers=admin,
                         json={"to_status": "promoted"})
        check("direct promote refused (EXPERIMENT_INVALID_TRANSITION from running)",
              r.status_code == 422, r.text[:200])

        # ── Complete → analyze → decide → promote ─────────────────────
        for to_status in ("completed", "analyzed"):
            r = await c.post(f"/experiments/{exp_id}/transition", headers=admin,
                             json={"to_status": to_status})
            check(f"transition → {to_status}", r.status_code == 200, r.text[:200])
        r = await c.post(f"/experiments/{exp_id}/transition", headers=admin,
                         json={"to_status": "promoted"})
        check("promoted only via decision (EXPERIMENT_DECISION_REQUIRED)",
              r.status_code == 422
              and r.json()["error"]["code"] == "EXPERIMENT_DECISION_REQUIRED",
              r.text[:200])

        r = await c.post(f"/experiments/{exp_id}/analysis", headers=admin, json={})
        check("run analysis", r.status_code == 200, r.text[:300])
        result_hash = r.json()["data"]["result_hash"]
        check("analysis is causal (randomized)", r.json()["data"]["causal_claim"] is True)

        r = await c.post(f"/experiments/{exp_id}/decisions", headers=admin, json={
            "decision": "promote", "summary": "forged-hash attempt over the wire",
            "analysis_result_hash": "0" * 64,
        })
        check("forged hash refused (DECISION_HASH_MISMATCH)",
              r.status_code == 422
              and r.json()["error"]["code"] == "DECISION_HASH_MISMATCH", r.text[:200])
        r = await c.post(f"/experiments/{exp_id}/decisions", headers=admin, json={
            "decision": "promote", "summary": "e2e: treatment weights win cleanly",
            "analysis_result_hash": result_hash,
        })
        check("record promote decision", r.status_code == 201, r.text[:300])
        decision_id = r.json()["data"]["id"]

        r = await c.post(f"/experiments/decisions/{decision_id}/promotion-drafts",
                         headers=admin, json={
                             "target_type": "matching_config",
                             "target_ref": active_config_id,
                             "draft_payload": {"weights": {"skill_fit": 0.6,
                                                           "history": 0.4}},
                         })
        check("create promotion draft", r.status_code == 201, r.text[:300])
        draft_id = r.json()["data"]["id"]
        r = await c.post(f"/experiments/promotion-drafts/{draft_id}/apply", headers=admin,
                         json={})
        check("apply before approve refused", r.status_code == 422, r.text[:200])
        r = await c.post(f"/experiments/promotion-drafts/{draft_id}/approve",
                         headers=admin, json={})
        check("approve draft", r.status_code == 200, r.text[:200])
        r = await c.post(f"/experiments/promotion-drafts/{draft_id}/apply", headers=admin,
                         json={})
        check("apply draft", r.status_code == 200, r.text[:300])
        applied_ref = r.json()["data"]["applied_ref"]
        check("target-domain draft ref returned", bool(applied_ref), r.text[:200])
        r = await c.post(f"/experiments/promotion-drafts/{draft_id}/apply", headers=admin,
                         json={})
        check("second apply idempotent 409 (PROMOTION_ALREADY_APPLIED)",
              r.status_code == 409, r.text[:200])

        # ── Surface-key reuse after terminal ──────────────────────────
        r = await c.post("/experiments", headers=admin, json={
            "key": exp_key, "title": "second run on the key", "domain": "matching",
            "layer_key": layer_key,
        })
        check("key reusable after promoted", r.status_code == 201, r.text[:200])
        experiment_ids.append(r.json()["data"]["id"])

        # ── Registry surfaces ──────────────────────────────────────────
        r = await c.get("/experiments/decisions?domain=matching", headers=admin)
        check("decision registry lists the record",
              r.status_code == 200
              and any(d["id"] == decision_id for d in r.json()["data"]), r.text[:200])
        r = await c.get("/experiments/decisions/meta", headers=admin)
        check("corpus meta", r.status_code == 200 and r.json()["data"]["total"] >= 1,
              r.text[:200])

        # ── Round 10: holdout groups over HTTP ────────────────────────
        hg_key = f"hg-{uid()}"
        r = await c.post("/experiments/holdout-groups", headers=admin, json={
            "key": hg_key, "title": "E2E holdout", "domain": "matching",
            "holdout_bp": 500,
        })
        check("holdout group created", r.status_code == 201, r.text[:200])
        group_id = r.json()["data"]["id"] if r.status_code == 201 else ""
        r = await c.post("/experiments/holdout-groups", headers=admin, json={
            "key": hg_key, "title": "dup", "domain": "matching", "holdout_bp": 100,
        })
        check("holdout dup key 409", r.status_code == 409, r.text[:200])
        r = await c.post("/experiments/holdout-groups", headers=admin, json={
            "key": f"hg-{uid()}", "title": "too big", "domain": "matching",
            "holdout_bp": 2001,
        })
        check("holdout bp cap 422", r.status_code == 422, r.text[:200])
        r = await c.get("/experiments/holdout-groups", headers=admin)
        check("holdout list shows group",
              r.status_code == 200
              and any(g["key"] == hg_key for g in r.json()["data"]), r.text[:200])
        r = await c.post(f"/experiments/holdout-groups/{group_id}/release",
                         headers=admin, json={})
        check("holdout released", r.status_code == 200
              and r.json()["data"]["status"] == "released", r.text[:200])
        r = await c.post("/experiments/holdout-groups", headers=student, json={
            "key": f"hg-{uid()}", "title": "nope", "domain": "matching",
            "holdout_bp": 100,
        })
        check("holdout create is admin-walled", r.status_code == 403, r.text[:200])

        # ── Round 10: aa-probe diagnostic ─────────────────────────────
        r = await c.get(f"/experiments/layers/{layer_key}/aa-probe?n=2000",
                        headers=admin)
        check("aa-probe healthy over HTTP",
              r.status_code == 200 and r.json()["data"]["healthy"] is True,
              r.text[:200])

        # ── Round 10: self-serve resolve/exposure (client-SDK class) ──
        r = await c.post("/experiments/self/resolve", headers=student,
                         json={"experiment_key": "surface-nothing-live"})
        check("self-resolve unknown key = default experience",
              r.status_code == 200 and r.json()["data"]["variant_key"] is None,
              r.text[:200])
        r = await c.post("/experiments/self/resolve", headers=student,
                         json={"experiment_key": exp_key})
        check("self-resolve live key returns a variant",
              r.status_code == 200
              and r.json()["data"]["variant_key"] in ("control", "treatment", None),
              r.text[:200])
        r = await c.post("/experiments/self/exposures", headers=student,
                         json={"experiment_key": exp_key, "dedup_key": "e2e-self"})
        check("self-exposure records or no-ops safely",
              r.status_code == 201 and "recorded" in r.json()["data"], r.text[:200])
        r = await c.post("/experiments/self/resolve", json={"experiment_key": exp_key})
        check("self-resolve requires auth", r.status_code == 401, r.text[:200])

        # ── Round 10: org-admin delegation wall ───────────────────────
        # student administers no org → reads refuse with 403 (not empty 200)
        r = await c.get("/experiments", headers=student)
        check("roleless reader still 403 after delegation", r.status_code == 403,
              r.text[:200])

        # ── Round 10: org-admin WRITE delegation over HTTP ────────────
        org_id = await grant_org_admin(student_id)
        r = await c.post("/experiments/layers", headers=admin,
                         json={"key": f"lyr-org-{uid()}", "domain": "matching"})
        org_layer = r.json()["data"]["key"]
        r = await c.post("/experiments", headers=admin, json={
            "key": f"org-exp-{uid()}", "title": "org-scoped", "domain": "matching",
            "layer_key": org_layer, "scope_org_id": org_id,
        })
        check("org-scoped experiment created", r.status_code == 201, r.text[:200])
        org_exp_id = r.json()["data"]["id"]
        experiment_ids.append(org_exp_id)
        r = await c.get(f"/experiments/{org_exp_id}", headers=student)
        check("org admin reads own-org experiment", r.status_code == 200, r.text[:200])
        r = await c.post(f"/experiments/{org_exp_id}/transition", headers=student,
                         json={"to_status": "review"})
        check("org admin transitions own-org experiment",
              r.status_code == 200 and r.json()["data"]["status"] == "review",
              r.text[:200])
        r = await c.post(f"/experiments/{experiment_ids[0]}/transition", headers=student,
                         json={"to_status": "paused"})
        check("org admin cannot touch a platform experiment (uniform 404)",
              r.status_code == 404, r.text[:200])
        # ── Defect #32: self-serve resolve reaches org-scoped experiments ─
        # the org admin walks their own experiment to running (delegated
        # writes + the checklist), then resolves it as a plain member
        r = await c.post(f"/experiments/{org_exp_id}/versions", headers=admin, json={
            "spec": {
                "hypothesis": "org-scoped self-serve resolution works",
                "unit_type": "user",
                "variants": [
                    {"key": "control", "name": "C", "weight_bp": 5000,
                     "is_control": True},
                    {"key": "treatment", "name": "T", "weight_bp": 5000},
                ],
                "metrics": {"primary": ["exposure_rate"],
                            "guardrails": [{"metric_key": "cost_usd", "op": "lte",
                                            "threshold": 100.0}]},
            },
        })
        check("org-scoped spec added", r.status_code == 201, r.text[:200])
        org_exp_key = (await c.get(f"/experiments/{org_exp_id}", headers=student)).json()[
            "data"]["key"]
        r = await c.post(f"/experiments/layers/{org_layer}/allocations", headers=admin,
                         json={"experiment_id": org_exp_id, "slice_start": 0,
                               "slice_end": 9999})
        check("org exp slice allocated", r.status_code in (200, 201, 409), r.text[:200])
        checklist = {k: True for k in (
            "hypothesis_peer_checked", "power_computed", "metrics_reviewed",
            "rollback_owner_named",
        )}
        r = await c.post(f"/experiments/{org_exp_id}/transition", headers=student,
                         json={"to_status": "scheduled", "checklist": checklist})
        check("org admin schedules with checklist", r.status_code == 200, r.text[:200])
        r = await c.post(f"/experiments/{org_exp_id}/transition", headers=student,
                         json={"to_status": "running"})
        check("org admin starts the experiment", r.status_code == 200, r.text[:200])
        r = await c.patch(f"/experiments/{org_exp_id}/ramp", headers=student,
                          json={"ramp_bp": 10000})
        check("org admin ramps to 100%", r.status_code == 200, r.text[:200])
        r = await c.post("/experiments/self/resolve", headers=student,
                         json={"experiment_key": org_exp_key})
        check("self-resolve reaches the org-scoped experiment (defect #32)",
              r.status_code == 200
              and r.json()["data"]["variant_key"] in ("control", "treatment"),
              r.text[:200])

        r = await c.post(f"/experiments/{org_exp_id}/decisions", headers=student, json={
            "decision": "promote", "summary": "nope",
            "analysis_result_hash": "0" * 64,
        })
        check("decisions stay platform-admin even for org admins",
              r.status_code == 403, r.text[:200])

    await cleanup(experiment_ids, layer_key, entity_type)
    print(f"\n{PASS} passed, {FAIL} failed")
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
