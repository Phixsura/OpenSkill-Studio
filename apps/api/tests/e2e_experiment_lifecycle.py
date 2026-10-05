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

RATE NOTE (round 259, corrected round 264): the anon surfaces carry
production limits (resolve 60/min, exposures 120/min per principal),
but APP_ENV=test SKIPS rate limiting entirely — this wall can never
429. The limits are config constants behind the env gate; their exact
values are production semantics outside any test's reach (wave-45
ledger).
"""

import asyncio
import os
import uuid

import httpx

API = os.environ.get("E2E_EXP_API", "http://localhost:8442/api/v1")

PASS = 0
FAIL = 0

# round 156: cleanup state lives at module level so the finally-wrapper can
# sweep debris even when the run CRASHES mid-flight — interrupted runs used
# to skip cleanup entirely and leave experiment corpses in the shared test
# DB (the round-155 residue incident)
STATE: dict = {"experiment_ids": [], "layer_key": "", "entity_type": ""}


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


async def drive_outbox(topic: str) -> None:
    """Drive the transactional outbox inline (the worker loop is not running
    in the E2E server) — same technique the outbox-driving suite uses."""
    from app.controlplane.worker import process_outbox_once
    from app.core.database import AsyncSessionLocal, engine

    await engine.dispose(close=False)
    async with AsyncSessionLocal() as db:
        await process_outbox_once(db, topics=[topic])
        await db.commit()
    await engine.dispose()


async def cleanup(experiment_ids: list[str], layer_key: str, entity_type: str) -> None:
    from sqlalchemy import delete as _delete
    from sqlalchemy import select as _select

    from app.core.database import AsyncSessionLocal, engine
    from app.experiments.models import Experiment, ExperimentLayer, HoldoutGroup
    from app.models.matching import MatchingConfig

    await engine.dispose(close=False)
    async with AsyncSessionLocal() as db:
        await db.execute(_delete(Experiment).where(Experiment.id.in_(experiment_ids)))
        await db.execute(_delete(HoldoutGroup).where(HoldoutGroup.title.in_(
            ["E2E holdout", "dup", "too big", "nope"])))
        # Round 94: layers can only drop once NOTHING hangs on them — a
        # crashed earlier run may have left orphan experiments (e.g. clones)
        # on historical lyr-org-% layers; delete riders first, always.
        doomed_layers = (
            (ExperimentLayer.key == layer_key)
            | ExperimentLayer.key.like("lyr-org-%")
            | ExperimentLayer.key.like("e2e-obs-%")  # round 200: obs lane
        )
        await db.execute(
            _delete(Experiment).where(
                Experiment.layer_key.in_(
                    (await db.execute(
                        _select(ExperimentLayer.key).where(doomed_layers)
                    )).scalars().all() or [""]
                )
            )
        )
        await db.execute(_delete(ExperimentLayer).where(doomed_layers))
        from app.controlplane.models.tenant import TenantAccount
        from app.models.organization import Organization

        await db.execute(
            _delete(Organization).where(Organization.name == "e2e delegation org")
        )
        await db.execute(
            _delete(TenantAccount).where(TenantAccount.slug.like("e2e-t-%"))
        )
        # Round 200: the observational section (round 199) seeds its own
        # tenant/org/project/users/submissions — sweep them too (the
        # round-155 residue law: E2E debris in the shared test DB is how
        # global-count flakes are born)
        from app.models.project import Project as _CleanProj
        from app.models.project import Submission as _CleanSub
        from app.models.user import User as _CleanUser

        obs_user_ids = (
            await db.execute(
                _select(_CleanUser.id).where(
                    _CleanUser.email.like("e2e-obs-%@example.com"))
            )
        ).scalars().all()
        if obs_user_ids:
            await db.execute(
                _delete(_CleanSub).where(_CleanSub.user_id.in_(obs_user_ids)))
        await db.execute(
            _delete(_CleanProj).where(_CleanProj.slug.like("obs-%")))
        if obs_user_ids:
            await db.execute(
                _delete(_CleanUser).where(_CleanUser.id.in_(obs_user_ids)))
        await db.execute(
            _delete(Organization).where(Organization.slug.like("e2e-obs-%")))
        await db.execute(
            _delete(TenantAccount).where(TenantAccount.slug.like("e2e-obs-%")))
        from app.experiments.models import (
            ExperimentIdentityLink as _CleanLink,
        )

        await db.execute(_delete(_CleanLink).where(
            _CleanLink.anonymous_id.like("E2EANON%")))
        await db.execute(
            _delete(MatchingConfig).where(MatchingConfig.target_entity_type == entity_type)
        )
        await db.commit()
    await engine.dispose()


async def main() -> int:
    experiment_ids = STATE["experiment_ids"]  # shared with the crash sweeper
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
        layer_key = STATE["layer_key"] = f"e2e-match-{uid()}"
        r = await c.post("/experiments/layers", headers=admin,
                         json={"key": layer_key, "domain": "matching"})
        check("create layer", r.status_code == 201, r.text[:200])
        r = await c.post("/experiments/metric-definitions/seed", headers=admin, json={})
        check("seed metric definitions", r.status_code == 200, r.text[:200])
        # Round 101/104: definition PATCH — platform-walled operational knobs
        r = await c.patch("/experiments/metric-definitions/run_latency_ms",
                          headers=admin, json={"cap_value": 120000})
        check("definition PATCH edits the cap",
              r.status_code == 200
              and float(r.json()["data"]["cap_value"]) == 120000,
              r.text[:200])
        r = await c.patch("/experiments/metric-definitions/run_latency_ms",
                          headers=admin, json={"clear_cap": True})
        check("definition PATCH clears the cap",
              r.status_code == 200 and r.json()["data"]["cap_value"] is None,
              r.text[:200])
        entity_type = STATE["entity_type"] = f"e2e-{uid()[:10]}"
        active_config_id, _ = await seed_matching_configs(entity_type)

        # ── Ethics gate over HTTP ──────────────────────────────────────
        exp_key = f"e2e-exp-{uid()}"
        r = await c.post("/experiments", headers=admin, json={
            "key": exp_key, "title": "E2E matching weights", "domain": "matching",
            "layer_key": layer_key,
        })
        check("create experiment", r.status_code == 201, r.text[:200])
        exp_id = r.json()["data"]["id"]
        experiment_ids.append(exp_id)

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
                         json={"to_status": "scheduled", "checklist": checklist,
                               "start_at": "2027-01-01T09:00:00Z"})
        check("transition → scheduled (checklist affirmed)",
              r.status_code == 200, r.text[:200])
        check("exp10: start_at echoes on the scheduled experiment",
              (r.json()["data"].get("start_at") or "").startswith("2027-01-01"),
              r.text[:200])
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

        # ── Round 131: scheduled ramp plan over the wire (exp14) ────────
        r = await c.patch(f"/experiments/{exp_id}/ramp-plan", headers=admin,
                          json={"plan": [
                              {"at": "2027-06-01T09:00:00Z", "ramp_bp": 4000},
                              {"at": "2027-06-03T09:00:00Z", "ramp_bp": 2000},
                          ]})
        check("non-increasing ramp plan refused over the wire",
              r.status_code == 422
              and r.json()["error"]["code"] == "EXPERIMENT_RAMP_DECREASE",
              r.text[:300])
        r = await c.patch(f"/experiments/{exp_id}/ramp-plan", headers=student,
                          json={"plan": None})
        check("ramp plan is platform-admin walled", r.status_code == 403,
              str(r.status_code))
        # NOTE: exp is at ramp 10000 here — plan targets cannot exceed it,
        # so the accept case clears instead (null plan round-trips)
        r = await c.patch(f"/experiments/{exp_id}/ramp-plan", headers=admin,
                          json={"plan": None})
        check("ramp plan clears to null over the wire",
              r.status_code == 200 and r.json()["data"]["ramp_plan"] is None,
              r.text[:300])

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

        r = await c.get(f"/experiments/{exp_id}/analysis/history", headers=admin)
        check("analysis history lists the recorded look over the wire",
              r.status_code == 200
              and len(r.json()["data"]) >= 1
              and r.json()["data"][0]["result_hash"] == result_hash,
              r.text[:300])
        check("the look carries its warnings for the evidence chain (234)",
              isinstance(r.json()["data"][0].get("warnings"), list),
              r.text[:300])

        # Round 92/93: clone + console text search over the wire
        clone_key = f"clone-{uid()}"
        r = await c.post(f"/experiments/{exp_id}/clone", headers=admin,
                         json={"key": clone_key})
        check("clone creates a draft copy with the source spec",
              r.status_code == 201
              and r.json()["data"]["status"] == "draft"
              and r.json()["data"]["key"] == clone_key,
              r.text[:300])
        clone_id = r.json()["data"]["id"]
        experiment_ids.append(clone_id)  # the cleanup must know the copy
        r = await c.get(f"/experiments?q={clone_key}", headers=admin)
        check("text search finds the clone by key",
              r.status_code == 200
              and any(e["id"] == clone_id for e in r.json()["data"]),
              r.text[:300])
        r = await c.get(f"/experiments?q={exp_key}", headers=admin)
        listed = next(e for e in r.json()["data"] if e["id"] == exp_id)
        check("round 146: the list injects last_exposure_at (data-flow badge)",
              "last_exposure_at" in listed,
              str(sorted(listed.keys()))[:300])
        r = await c.get("/experiments?q=%25", headers=admin)
        check("a bare %% wildcard is a literal (matches nothing here)",
              r.status_code == 200
              and all("%" in (e["key"] + e["title"]) for e in r.json()["data"]),
              r.text[:300])
        r = await c.post(f"/experiments/{exp_id}/clone", headers=student,
                         json={"key": f"c2-{uid()}"})
        check("clone is platform-admin walled", r.status_code == 403,
              str(r.status_code))

        # ── Round 119: §4.6 v3 multi-covariate CUPED over the wire ─────
        mcv_spec = dict(good_spec, variance_reduction={
            "method": "cuped",
            "covariate_metrics": ["exposure_rate", "run_latency_ms"],
            "lookback_days": 14,
        })
        r = await c.post(f"/experiments/{clone_id}/versions", headers=admin,
                         json={"spec": mcv_spec})
        check("multi-covariate spec accepted over the wire",
              r.status_code == 201 and len(r.json()["data"]["spec_hash"]) == 64,
              r.text[:300])
        both_forms = dict(mcv_spec, variance_reduction={
            "method": "cuped", "covariate_metric": "exposure_rate",
            "covariate_metrics": ["exposure_rate"], "lookback_days": 14,
        })
        r = await c.post(f"/experiments/{clone_id}/versions", headers=admin,
                         json={"spec": both_forms})
        check("both covariate forms refused (exactly-one validator)",
              r.status_code == 422, r.text[:300])
        # #63: an undefined metric key passes spec validation (definitions
        # may come later) but must refuse to SCHEDULE, naming the key
        typo_spec = dict(good_spec, metrics={
            "primary": ["typo_metric_e2e"],
            "guardrails": [{"metric_key": "exposure_rate", "op": "lte",
                            "threshold": 1.0}],
        })
        r = await c.post(f"/experiments/{clone_id}/versions", headers=admin,
                         json={"spec": typo_spec})
        check("typo'd metric key still versions (write comes before define)",
              r.status_code == 201, r.text[:300])
        r = await c.post(f"/experiments/{clone_id}/transition", headers=admin,
                         json={"to_status": "review"})
        check("clone reaches review", r.status_code == 200, r.text[:200])
        r = await c.post(f"/experiments/{clone_id}/transition", headers=admin,
                         json={"to_status": "scheduled", "checklist": checklist})
        check("scheduling an undefined metric key refused "
              "(EXPERIMENT_UNKNOWN_METRICS names it)",
              r.status_code == 422
              and r.json()["error"]["code"] == "EXPERIMENT_UNKNOWN_METRICS"
              and "typo_metric_e2e" in r.json()["error"]["message"],
              r.text[:300])
        # exp12: the covariates JSONB must survive the response model — the
        # #49/#51 serialization class only a wire read can prove
        from datetime import UTC as _UTC
        from datetime import datetime as _dt
        from datetime import timedelta as _tdlt

        from app.core.database import AsyncSessionLocal as SessionL
        from app.core.database import engine as _eng
        from app.experiments.models.metric import MetricSnapshot as _Snap

        cov_map = {
            "exposure_rate": {"sum": 3.0, "sum_sq": 5.0, "xy_sum": 2.5,
                              "xx": {"run_latency_ms": 7.0}},
            "run_latency_ms": {"sum": 9.0, "sum_sq": 41.0, "xy_sum": 6.0},
        }
        ws = _dt.now(_UTC) - _tdlt(days=1)
        await _eng.dispose(close=False)
        async with SessionL() as db:
            db.add(_Snap(experiment_id=exp_id, metric_key="exposure_rate",
                         variant_key="control", window_start=ws,
                         window_end=ws + _tdlt(days=1), n=5,
                         covariates=cov_map))
            await db.commit()
        await _eng.dispose()
        r = await c.get(f"/experiments/{exp_id}/metrics", headers=admin)
        cov_rows = [snap for snap in r.json().get("data", [])
                    if snap.get("covariates")]
        check("exp12 covariates JSONB round-trips over the wire",
              r.status_code == 200 and bool(cov_rows)
              and cov_rows[0]["covariates"] == cov_map,
              r.text[:300])

        # ── Round 127: §4.14 quantiles over the wire ───────────────────
        r = await c.patch("/experiments/metric-definitions/run_latency_ms",
                          headers=admin, json={"quantiles": [0.5, 0.95]})
        check("quantiles knob PATCHes and round-trips",
              r.status_code == 200
              and r.json()["data"]["spec"].get("quantiles") == [0.5, 0.95],
              r.text[:300])
        r = await c.patch("/experiments/metric-definitions/run_success_rate",
                          headers=admin, json={"quantiles": [0.5]})
        check("quantiles on a binary definition refused over the wire",
              r.status_code == 422, r.text[:300])
        hist = {"6": 10, "8": 5}
        await _eng.dispose(close=False)
        async with SessionL() as db:
            db.add(_Snap(experiment_id=exp_id, metric_key="run_latency_ms",
                         variant_key="control", window_start=ws,
                         window_end=ws + _tdlt(days=1), n=15,
                         value_histogram=hist))
            await db.commit()
        await _eng.dispose()
        r = await c.get(f"/experiments/{exp_id}/metrics", headers=admin)
        hist_rows = [snap for snap in r.json().get("data", [])
                     if snap.get("value_histogram")]
        check("exp13 value_histogram round-trips over the wire",
              r.status_code == 200 and bool(hist_rows)
              and hist_rows[0]["value_histogram"] == hist,
              r.text[:300])
        r = await c.patch("/experiments/metric-definitions/run_latency_ms",
                          headers=admin, json={"clear_quantiles": True})
        check("clear_quantiles strips the knob",
              r.status_code == 200
              and "quantiles" not in r.json()["data"]["spec"],
              r.text[:300])

        # ── Round 192: §4.15 KM knob over the wire ─────────────────────
        r = await c.patch("/experiments/metric-definitions/placement_outcome_rate",
                          headers=admin, json={"km": True})
        check("km knob PATCHes onto the talent time_to_event definition",
              r.status_code == 200
              and r.json()["data"]["spec"].get("km") is True,
              r.text[:300])
        r = await c.patch("/experiments/metric-definitions/retention_rate",
                          headers=admin, json={"km": True})
        check("km on a billing time_to_event refused over the wire (#70)",
              r.status_code == 422, r.text[:300])
        r = await c.patch("/experiments/metric-definitions/run_latency_ms",
                          headers=admin, json={"km": True})
        check("km on a continuous definition refused over the wire",
              r.status_code == 422, r.text[:300])
        r = await c.patch("/experiments/metric-definitions/placement_outcome_rate",
                          headers=admin, json={"km": False})
        check("km=False strips the knob",
              r.status_code == 200
              and "km" not in r.json()["data"]["spec"],
              r.text[:300])

        # ── Round 199: the OBSERVATIONAL lane over the wire ────────────
        # (ITS + synthetic control + causal_claim:false had zero live
        # coverage — everything below runs the real HTTP path, with the
        # roster/series seeded directly like the snapshot sections.)
        obs_layer = f"e2e-obs-{uid()}"
        r = await c.post("/experiments/layers", headers=admin,
                         json={"key": obs_layer, "domain": "learning"})
        check("create observational layer", r.status_code == 201, r.text[:200])
        obs_key = f"e2e-obs-{uid()}"
        r = await c.post("/experiments", headers=admin, json={
            "key": obs_key, "title": "E2E observational", "domain": "learning",
            "layer_key": obs_layer,
        })
        check("create observational experiment", r.status_code == 201,
              r.text[:200])
        obs_id = r.json()["data"]["id"]
        experiment_ids.append(obs_id)
        obs_spec = {
            "hypothesis": "revisions change after the intervention",
            "unit_type": "user",
            "analysis_type": "observational",
            "variants": [
                {"key": "control", "name": "C", "weight_bp": 5000,
                 "is_control": True},
                {"key": "treatment", "name": "T", "weight_bp": 5000},
            ],
            "metrics": {"primary": ["revision_count"],
                        "guardrails": [{"metric_key": "cost_usd", "op": "lte",
                                        "threshold": 100.0}]},
            "population": {"rules": []},
            # round 207: §4.6b auto covariate selection over the wire
            "variance_reduction": {"method": "cuped",
                                   "covariate_metrics": ["auto"],
                                   "lookback_days": 14},
        }
        bad_auto = dict(obs_spec, variance_reduction={
            "method": "cuped",
            "covariate_metrics": ["auto", "revision_count"],
            "lookback_days": 14,
        })
        r = await c.post(f"/experiments/{obs_id}/versions", headers=admin,
                         json={"spec": bad_auto})
        check("auto mixed with explicit covariates refused over the wire",
              r.status_code == 422, r.text[:300])
        r = await c.post(f"/experiments/{obs_id}/versions", headers=admin,
                         json={"spec": obs_spec})
        check("observational spec v1 (auto covariates pass the gate)",
              r.status_code == 201, r.text[:300])
        r = await c.post(f"/experiments/layers/{obs_layer}/allocations",
                         headers=admin,
                         json={"experiment_id": obs_id, "slice_start": 0,
                               "slice_end": 9999})
        check("observational slices", r.status_code == 201, r.text[:200])
        obs_checklist = {**checklist, "ethics_screened": True}
        for payload in ({"to_status": "review"},
                        {"to_status": "scheduled",
                         "checklist": obs_checklist},
                        {"to_status": "running"}):
            r = await c.post(f"/experiments/{obs_id}/transition",
                             headers=admin, json=payload)
            check(f"observational -> {payload['to_status']}",
                  r.status_code == 200, r.text[:300])

        from app.controlplane.models.tenant import TenantAccount as _Tenant
        from app.experiments.models import Experiment as _Exp
        from app.experiments.models import ExperimentAssignment as _Assign
        from app.models.organization import Organization as _Org
        from app.models.project import Project as _Proj
        from app.models.project import Submission as _Sub
        from app.models.project import SubmissionStatus as _SubStatus
        from app.models.user import User as _Usr
        from app.models.user import UserRole as _UsrRole
        from app.models.user import UserStatus as _UsrStatus

        obs_start = (_dt.now(_UTC) - _tdlt(days=3)).replace(
            hour=0, minute=0, second=0, microsecond=0)
        await _eng.dispose(close=False)
        async with SessionL() as db:
            exp_row = await db.get(_Exp, obs_id)
            exp_row.started_at = obs_start
            tenant = _Tenant(name=f"e2e-obs-{uid()}", slug=f"e2e-obs-{uid()}")
            db.add(tenant)
            await db.flush()
            obs_org = _Org(name=f"e2e-obs-{uid()}", slug=f"e2e-obs-{uid()}",
                           tenant_id=tenant.id)
            db.add(obs_org)
            await db.flush()
            proj = _Proj(org_id=obs_org.id, title="OBS",
                         slug=f"obs-{uid()}", description="d",
                         instructions="i",
                         rubric=[{"criterion": "c", "max_score": 5}])
            db.add(proj)
            await db.flush()
            users = {}
            for tag, variant in (("t", "treatment"), ("d0", "control"),
                                 ("d1", "control")):
                u = _Usr(email=f"e2e-obs-{tag}-{uid()}@example.com",
                         display_name=tag, role=_UsrRole.STUDENT,
                         status=_UsrStatus.ACTIVE)
                db.add(u)
                await db.flush()
                assignment = _Assign(experiment_id=obs_id,
                                     unit_type="user",
                                     unit_id=u.id, variant_key=variant,
                                     assigned_version=1, bucket=0,
                                     is_holdout=False)
                db.add(assignment)
                await db.flush()
                # the fold's as_of pinning only rosters units assigned
                # BEFORE window_end — backdate to the pre-period
                assignment.assigned_at = obs_start - _tdlt(hours=1)
                users[tag] = u
            # treated: steady 1/day pre, a 3-revision jump for 3 days post;
            # donor d0 tracks the pre exactly; d1 sits at 3/day throughout
            for off in range(-14, 0):
                for tag, ver in (("t", 2), ("d0", 2), ("d1", 4)):
                    db.add(_Sub(org_id=obs_org.id, project_id=proj.id,
                                user_id=users[tag].id,
                                status=_SubStatus.APPROVED, version=ver,
                                created_at=obs_start + _tdlt(days=off,
                                                             hours=6)))
            for off in range(3):
                db.add(_Sub(org_id=obs_org.id, project_id=proj.id,
                            user_id=users["t"].id,
                            status=_SubStatus.APPROVED, version=4,
                            created_at=obs_start + _tdlt(days=off, hours=6)))
            for off in range(14):
                for tag, ver in (("d0", 2), ("d1", 4)):
                    db.add(_Sub(org_id=obs_org.id, project_id=proj.id,
                                user_id=users[tag].id,
                                status=_SubStatus.APPROVED, version=ver,
                                created_at=obs_start + _tdlt(days=off,
                                                             hours=6)))
            await db.commit()
        await _eng.dispose()
        # round 229: NO seeded snapshots — a REAL window fold produces them
        # (covariates included), so the whole observational stack below
        # (comparisons, ITS, SC, auto selection) runs on folded data
        from app.experiments.services.metrics import (
            MetricService as MetricSvc,
        )

        await _eng.dispose(close=False)
        async with SessionL() as db:
            await MetricSvc(db).compute_experiment_window(
                obs_id,
                window_start=obs_start,
                window_end=obs_start + _tdlt(days=1),
            )
            await db.commit()
        await _eng.dispose()

        r = await c.post(f"/experiments/{obs_id}/analysis", headers=admin,
                         json={})
        check("observational analysis runs over the wire",
              r.status_code == 200, r.text[:300])
        obs_result = r.json()["data"]
        check("observational analysis is never a causal claim",
              obs_result.get("causal_claim") is False, str(obs_result)[:200])
        obs_metric = obs_result["metrics"]["revision_count"]
        check("ITS block rides the wire with the association caveat",
              "its" in obs_metric
              and "association only" in obs_metric["its"]["caveat"],
              str(obs_metric)[:300])
        check("synthetic-control block rides the wire with two donors",
              (obs_metric.get("synthetic_control") or {}).get("donors") == 2
              and (obs_metric.get("synthetic_control") or {}).get(
                  "placebo_p") is None,
              str(obs_metric.get("synthetic_control"))[:300])
        check("no km block without the knob",
              "km" not in obs_metric, str(obs_metric)[:200])
        # round 229 (#77 proven over the wire): the fold carried the
        # covariates, so the auto selection fires with exposed evidence
        check("auto selection fires over the wire after a real fold",
              "CUPED_AUTO_SELECTED" in obs_result.get("warnings", []),
              str(obs_result.get("warnings"))[:300])
        evidence = (obs_metric or {}).get("cuped_auto")
        check("the selection evidence (per-covariate r) rides the wire",
              isinstance(evidence, dict) and len(evidence) >= 1
              and all(isinstance(v, (int, float)) for v in evidence.values()),
              str(evidence)[:300])

        # ── Round 249: segment slices over the wire ────────────────────
        r = await c.get(f"/experiments/{obs_id}/analysis/history",
                        headers=admin)
        looks_before = len(r.json()["data"])
        r = await c.post(
            f"/experiments/{obs_id}/analysis?segment=org:zzzzzzzzzzzzzzzzzzzzzzzzzz",
            headers=admin, json={})
        check("segment slice analysis runs informationally",
              r.status_code == 200
              and r.json()["data"].get("segment")
              == "org:zzzzzzzzzzzzzzzzzzzzzzzzzz",
              r.text[:300])
        r = await c.get(f"/experiments/{obs_id}/analysis/history",
                        headers=admin)
        check("a segment run burns NO look budget",
              len(r.json()["data"]) == looks_before, r.text[:200])
        r = await c.get(f"/experiments/{obs_id}/segments", headers=admin)
        check("segments listing responds over the wire",
              r.status_code == 200, r.text[:200])

        # ── Round 211: §4.17 identity resolution over the wire ─────────
        r = await c.patch(f"/experiments/{obs_id}/ramp", headers=admin,
                          json={"ramp_bp": 10000})
        check("ramp the observational experiment for serving",
              r.status_code == 200, r.text[:200])
        anon_ulid = f"E2EANON{uid().upper()}"[:26]
        r = await c.post("/experiments/anon/resolve",
                         json={"experiment_key": obs_key,
                               "anonymous_id": anon_ulid})
        check("anonymous resolve needs NO auth and assigns",
              r.status_code == 200
              and r.json()["data"]["variant_key"] is not None,
              r.text[:300])
        anon_variant = r.json()["data"]["variant_key"]
        r = await c.post("/experiments/anon/resolve",
                         json={"experiment_key": obs_key,
                               "anonymous_id": anon_ulid})
        check("anonymous resolve is sticky",
              r.json()["data"]["variant_key"] == anon_variant, r.text[:200])
        r = await c.post("/experiments/self/identity-link", headers=student,
                         json={"anonymous_id": anon_ulid})
        check("identity link migrates the anon history",
              r.status_code == 200 and r.json()["data"]["migrated"] >= 1,
              r.text[:300])
        r = await c.post("/experiments/self/resolve", headers=student,
                         json={"experiment_key": obs_key})
        check("the logged-in user inherits the anon variant",
              r.json()["data"]["variant_key"] == anon_variant, r.text[:300])
        r = await c.post("/experiments/anon/resolve",
                         json={"experiment_key": obs_key,
                               "anonymous_id": anon_ulid})
        check("the anon id keeps serving the SAME experience post-link",
              r.json()["data"]["variant_key"] == anon_variant, r.text[:200])
        r = await c.post("/experiments/self/identity-link", headers=admin,
                         json={"anonymous_id": anon_ulid})
        check("rebinding a linked anon id to another user is 422",
              r.status_code == 422
              and r.json()["error"]["code"] == "EXPERIMENT_IDENTITY_CONFLICT",
              r.text[:300])
        r = await c.post("/experiments/self/identity-link", headers=student,
                         json={"anonymous_id": "a:b"})
        check("malformed anonymous ids refuse at the schema wall",
              r.status_code == 422, r.text[:200])
        # round 232: the support override is platform-admin only
        support_anon = f"E2EANON{uid().upper()}"[:26]
        r = await c.post("/experiments/self/identity-link", headers=student,
                         json={"anonymous_id": support_anon,
                               "user_id": admin_id})
        check("naming another user without admin is 403",
              r.status_code == 403, r.text[:200])
        r = await c.post("/experiments/self/identity-link", headers=admin,
                         json={"anonymous_id": support_anon,
                               "user_id": student_id})
        check("platform admin links on behalf of a user (support flow)",
              r.status_code == 200
              and r.json()["data"]["user_id"] == student_id,
              r.text[:300])
        # round 214 (#75): pre-login exposures record through the anon
        # namespace — after the link they land on the user's assignment
        r = await c.post("/experiments/anon/exposures",
                         json={"experiment_key": obs_key,
                               "anonymous_id": anon_ulid,
                               "dedup_key": f"e2e-anonexp-{anon_ulid}"})
        check("anonymous exposure records without auth",
              r.status_code == 201 and r.json()["data"]["recorded"] is True,
              r.text[:300])

        # round 243: a 20-way concurrent resolve STORM on one fresh anon id
        # — the ON-CONFLICT re-read must converge every racer on ONE
        # variant (the unique constraint is the arbiter, over real HTTP)
        storm_id = f"E2EANON{uid().upper()}"[:26]
        storm = await asyncio.gather(*[
            c.post("/experiments/anon/resolve",
                   json={"experiment_key": obs_key,
                         "anonymous_id": storm_id})
            for _ in range(20)
        ])
        storm_variants = {
            resp.json()["data"]["variant_key"] for resp in storm
        }
        check("20 concurrent resolves converge on one variant",
              all(resp.status_code == 200 for resp in storm)
              and len(storm_variants) == 1
              and None not in storm_variants,
              str([(resp.status_code,
                    resp.json()["data"].get("variant_key"))
                   for resp in storm[:5]])[:300])

        # round 244: a two-user LINK storm on one anon id — the PK is the
        # arbiter: exactly one identity wins, every losing racer gets the
        # typed 422, and the winner's claim is idempotent thereafter
        link_storm_id = f"E2EANON{uid().upper()}"[:26]
        link_storm = await asyncio.gather(*[
            c.post("/experiments/self/identity-link",
                   headers=(student if i % 2 == 0 else admin),
                   json={"anonymous_id": link_storm_id})
            for i in range(20)
        ])
        winners = [resp for resp in link_storm if resp.status_code == 200]
        losers = [resp for resp in link_storm if resp.status_code == 422]
        winner_users = {resp.json()["data"]["user_id"] for resp in winners}
        # round 253 (#78 over the wire): both identities hold the SAME
        # dedup key; the conflict fold must still link cleanly (the
        # colliding duplicate folds away server-side — never a 500)
        collide_anon = f"E2EANON{uid().upper()}"[:26]
        r = await c.post("/experiments/anon/resolve",
                         json={"experiment_key": obs_key,
                               "anonymous_id": collide_anon})
        check("collision setup: anon assigned", r.status_code == 200
              and r.json()["data"]["variant_key"] is not None, r.text[:200])
        r = await c.post("/experiments/anon/exposures",
                         json={"experiment_key": obs_key,
                               "anonymous_id": collide_anon,
                               "dedup_key": "e2e-shared-collision"})
        check("collision setup: anon exposure", r.status_code == 201
              and r.json()["data"]["recorded"] is True, r.text[:200])
        r = await c.post("/experiments/self/resolve", headers=admin,
                         json={"experiment_key": obs_key})
        check("collision setup: admin assigned", r.status_code == 200,
              r.text[:200])
        r = await c.post("/experiments/self/exposures", headers=admin,
                         json={"experiment_key": obs_key,
                               "dedup_key": "e2e-shared-collision"})
        check("collision setup: user exposure same key",
              r.status_code == 201, r.text[:200])
        r = await c.post("/experiments/self/identity-link", headers=admin,
                         json={"anonymous_id": collide_anon})
        check("#78: the dedup-colliding conflict fold links cleanly",
              r.status_code == 200
              and r.json()["data"]["conflicts"] == 1,
              r.text[:300])
        # round 263: §4.17 transparency over the wire — the listing shows
        # the caller exactly their links; unauthenticated is 401
        r = await c.get("/experiments/self/identity-links", headers=admin)
        check("identity-links listing shows the caller's links",
              r.status_code == 200
              and any(row["anonymous_id"] == collide_anon
                      for row in r.json()["data"]),
              r.text[:300])
        r = await c.get("/experiments/self/identity-links")
        check("identity-links listing requires auth",
              r.status_code == 401, r.text[:200])

        check("link storm: one identity wins, losers get the typed 422",
              len(winners) >= 1 and len(winner_users) == 1
              and len(winners) + len(losers) == 20
              and all(resp.json()["error"]["code"]
                      == "EXPERIMENT_IDENTITY_CONFLICT" for resp in losers),
              str([(resp.status_code) for resp in link_storm])[:200])

        # Round 87: the standing scorecard mirrors the newest look
        r = await c.get(f"/experiments/{exp_id}/analysis/latest", headers=admin)
        check("latest-look scorecard matches the run's hash",
              r.status_code == 200
              and (r.json()["data"] or {}).get("result_hash") == result_hash
              and (r.json()["data"] or {}).get("automated") is False,
              r.text[:300])

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
        # round 272: the FROZEN evidence rides the wire — the create
        # response and the GET both carry evidence.cited_warnings (a list),
        # so the decision packet (round 270) downloads real data
        check("frozen cited_warnings ride the create response",
              isinstance((r.json()["data"].get("evidence") or {})
                         .get("cited_warnings"), list),
              r.text[:300])
        r = await c.get(f"/experiments/decisions/{decision_id}",
                        headers=admin)
        check("frozen cited_warnings ride the decision GET",
              r.status_code == 200
              and isinstance((r.json()["data"].get("evidence") or {})
                             .get("cited_warnings"), list),
              r.text[:300])

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

        # ── Async apply through the outbox, over HTTP (round 29) ──────
        r = await c.post(f"/experiments/decisions/{decision_id}/promotion-drafts",
                         headers=admin, json={
                             "target_type": "matching_config",
                             "target_ref": active_config_id,
                             "draft_payload": {"weights": {"skill_fit": 0.5,
                                                           "history": 0.5}},
                         })
        check("second draft for async apply", r.status_code == 201, r.text[:300])
        async_draft_id = r.json()["data"]["id"]
        r = await c.post(
            f"/experiments/promotion-drafts/{async_draft_id}/approve",
            headers=admin, json={})
        check("approve async draft", r.status_code == 200, r.text[:200])
        r = await c.post(
            f"/experiments/promotion-drafts/{async_draft_id}/apply?background=true",
            headers=admin, json={})
        check("async apply parks in applying",
              r.status_code == 200 and r.json()["data"]["status"] == "applying",
              r.text[:300])
        r = await c.post(
            f"/experiments/promotion-drafts/{async_draft_id}/apply",
            headers=admin, json={})
        check("sync apply refused while in flight (409)",
              r.status_code == 409, r.text[:200])
        await drive_outbox("exp.apply_promotion")
        r = await c.get("/experiments/promotion-drafts?status=applied&limit=100",
                        headers=admin)
        applied_rows = [d for d in r.json()["data"] if d["id"] == async_draft_id]
        check("outbox handler landed the async apply",
              len(applied_rows) == 1 and bool(applied_rows[0]["applied_ref"]),
              r.text[:300])

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
        # Round 54: cross-experiment holdout measurement
        r = await c.get(
            f"/experiments/holdout-groups/{group_id}/report"
            "?metric_key=project_approval_rate", headers=admin)
        check("holdout report splits and carries the caveat",
              r.status_code == 200
              and set(r.json()["data"]["arms"]) == {"holdout", "general"}
              and "causal claim" in r.json()["data"]["caveat"],
              r.text[:300])
        r = await c.get(
            f"/experiments/holdout-groups/{group_id}/report?metric_key=exposure_rate",
            headers=admin)
        check("holdout report refuses non-reportable sources typed",
              r.status_code == 422, r.text[:200])
        r = await c.get(
            f"/experiments/holdout-groups/{group_id}/report"
            "?metric_key=project_approval_rate", headers=student)
        check("holdout report is admin-walled", r.status_code == 403,
              str(r.status_code))
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

        # ── Guardrail ops endpoints over HTTP (round 30) ──────────────
        r = await c.post(f"/experiments/{org_exp_id}/guardrails/evaluate",
                         headers=admin, json={})
        check("manual guardrail evaluate runs", r.status_code == 200, r.text[:200])
        r = await c.post(f"/experiments/{org_exp_id}/guardrails/incident",
                         headers=student, json={"reason": "nope"})
        check("incident trigger is platform-admin only", r.status_code == 403,
              r.text[:200])
        r = await c.post(f"/experiments/{org_exp_id}/guardrails/incident",
                         headers=admin, json={"reason": "e2e drill"})
        check("manual incident pauses immediately", r.status_code == 201, r.text[:200])
        r = await c.get(f"/experiments/{org_exp_id}", headers=student)
        check("incident left the experiment paused",
              r.json()["data"]["status"] == "paused", r.text[:200])
        r = await c.get(
            f"/experiments/{org_exp_id}/guardrails/events/export", headers=student)
        check("delegated guardrail CSV export with header row",
              r.status_code == 200
              and r.headers["content-type"].startswith("text/csv")
              and r.text.splitlines()[0].startswith("guardrail_key,metric_key"),
              f"{r.status_code} {r.text[:120]}")
        r = await c.get(f"/experiments/{org_exp_id}/analysis/latest", headers=student)
        check("delegated scorecard read (null before any run)",
              r.status_code == 200, r.text[:200])
        r = await c.get(f"/experiments/{exp_id}/analysis/latest", headers=student)
        check("scorecard outside scope is a uniform 404", r.status_code == 404,
              str(r.status_code))
        r = await c.get(f"/experiments/{org_exp_id}/guardrails/events", headers=student)
        check("org admin sees the incident event (delegated diagnostics)",
              r.status_code == 200
              and any(e["guardrail_key"] == "__incident__" for e in r.json()["data"]),
              r.text[:300])
        r = await c.post(f"/experiments/{org_exp_id}/transition", headers=student,
                         json={"to_status": "running"})
        check("org admin resumes after the drill", r.status_code == 200, r.text[:200])

        # Round 47: CSV export rides the same read scope as the JSON listing
        r = await c.get(f"/experiments/{org_exp_id}/metrics/export", headers=student)
        check("delegated CSV export returns text/csv with the header row",
              r.status_code == 200
              and r.headers["content-type"].startswith("text/csv")
              and r.text.splitlines()[0].startswith("metric_key,variant_key,segment"),
              f"{r.status_code} {r.headers.get('content-type')} {r.text[:120]}")
        r = await c.get(f"/experiments/{org_exp_id}/assignments/export",
                        headers=student)
        check("delegated assignments CSV export returns text/csv",
              r.status_code == 200
              and r.headers.get("content-type", "").startswith("text/csv")
              and r.text.splitlines()[0].startswith("unit_type,unit_id"),
              r.text[:200])
        r = await c.get(f"/experiments/{exp_id}/metrics/export", headers=student)
        check("CSV export outside scope is a uniform 404", r.status_code == 404,
              str(r.status_code))

        r = await c.post(f"/experiments/{org_exp_id}/decisions", headers=student, json={
            "decision": "promote", "summary": "nope",
            "analysis_result_hash": "0" * 64,
        })
        check("decisions stay platform-admin even for org admins",
              r.status_code == 403, r.text[:200])

    print(f"\n{PASS} passed, {FAIL} failed")
    return 1 if FAIL else 0


async def run() -> int:
    """round 156: cleanup ALWAYS runs — a mid-flight crash must not leave
    experiment corpses in the shared test DB."""
    try:
        return await main()
    finally:
        try:
            await cleanup(STATE["experiment_ids"], STATE["layer_key"],
                          STATE["entity_type"])
        except Exception as exc:  # noqa: BLE001 — report, never mask the run error
            print(f"cleanup failed, debris may remain: {exc!r}")


if __name__ == "__main__":
    raise SystemExit(asyncio.run(run()))
