"""R426: learning-composer budget-cut propagation + draft dependent-guard.

_propagate_budget_cuts and _pack_minutes drive time-budget truncation
(cutting a prereq must transitively cut its dependents); update_draft's
dependent guard stops a learner ending up with a pack whose prerequisite
was removed.
"""

import uuid

import pytest

from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.exceptions import AppError
from app.models.user import User, UserRole, UserStatus
from app.services.learning_composer import (
    DEFAULT_PACK_MINUTES,
    _pack_minutes,
)
from app.services.learning_composer import (
    LearningComposerService as Lc,
)


@pytest.fixture
async def db():
    from app.core.database import engine

    await engine.dispose(close=False)
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
    await engine.dispose()


def test_pack_minutes_zero_is_real_r426():
    # None → default, but an explicit 0 stays 0 (round-16 LOW: `value or 60`
    # inflated 0-minute packs to 60)
    assert _pack_minutes(None) == DEFAULT_PACK_MINUTES
    assert _pack_minutes(0) == 0
    assert _pack_minutes(45) == 45


def test_propagate_budget_cuts_transitive_r426():
    # chain A -> B -> C (A prereq of B, B prereq of C). Cut A → B and C must
    # transitively become cut_for_budget; only D (independent, 30 min) remains.
    def _e(eid, status, mins):
        return {"entity_id": eid, "status": status, "estimated_minutes": mins,
                "reason_code": None}

    entries = [
        _e("A", "cut_for_budget", 100),
        _e("B", "included", 50),
        _e("C", "included", 40),
        _e("D", "included", 30),
    ]
    edges = [("A", "B"), ("B", "C")]
    total = Lc._propagate_budget_cuts(entries, edges)
    by = {e["entity_id"]: e for e in entries}
    assert by["B"]["status"] == "cut_for_budget"
    assert by["C"]["status"] == "cut_for_budget"  # transitive, via B
    assert by["B"]["reason_code"] == "cut_for_budget"
    assert by["D"]["status"] == "included"
    assert total == 30  # only D remains included

    # a WAIVED prerequisite does NOT force a cut (the learner already has it)
    entries2 = [
        {"entity_id": "P", "status": "waived", "estimated_minutes": 100, "reason_code": None},
        {"entity_id": "Q", "status": "included", "estimated_minutes": 20, "reason_code": None},
    ]
    total2 = Lc._propagate_budget_cuts(entries2, [("P", "Q")])
    assert entries2[1]["status"] == "included"  # Q survives — P was waived, not cut
    assert total2 == 20

    # a DANGLING edge (endpoint not in entries) must be SKIPPED, never crash —
    # kills the `prereq is None or dependent is None` -> `and` mutant
    entries3 = [{"entity_id": "K", "status": "included", "estimated_minutes": 15,
                 "reason_code": None}]
    total3 = Lc._propagate_budget_cuts(entries3, [("MISSING", "K"), ("K", "ALSO_MISSING")])
    assert entries3[0]["status"] == "included"
    assert total3 == 15


async def _user(db):
    u = User(email=f"r426-{uuid.uuid4().hex[:10]}@t.com", password_hash=hash_password("Test123!"),
             display_name="R426", role=UserRole.ADMIN, status=UserStatus.ACTIVE)
    db.add(u)
    await db.flush()
    return u


async def _org(db, owner):
    from app.services.organization import OrgService

    o = await OrgService(db).create(name=f"R426 {uuid.uuid4().hex[:5]}",
                                    slug=f"r426-{uuid.uuid4().hex[:10]}",
                                    description=None, created_by=owner.id)
    await db.flush()
    return o


async def _draft(db, org, items, status="draft"):
    from app.models.composer import SolutionDraft

    d = SolutionDraft(
        org_id=org.id, draft_type="learning_path", engine_version="v1", status=status,
        payload={"items": items,
                 "estimated_total_minutes": sum(
                     i["estimated_minutes"] for i in items if i["status"] == "included")},
    )
    db.add(d)
    await db.flush()
    return d


def _item(eid, slug, name, mins, prereq_ids=None, status="included"):
    return {"entity_id": eid, "slug": slug, "name": name, "estimated_minutes": mins,
            "status": status, "reason_code": None, "prereq_ids": prereq_ids or [],
            "prereq_slugs": []}


async def test_update_draft_dependent_guard_r426(db):
    from app.services.learning_composer import LearningComposerService

    owner = await _user(db)
    org = await _org(db, owner)
    svc = LearningComposerService(db)

    # basic: pack P is a prerequisite of pack Q (by entity_id)
    items = [_item("P", "p", "Pack P", 40), _item("Q", "q", "Pack Q", 30, prereq_ids=["P"])]
    d = await _draft(db, org, items)

    # removing ONLY the prerequisite P (Q remains) → ITEM_HAS_DEPENDENTS
    with pytest.raises(AppError) as e_dep:
        await svc.update_draft(d.id, org.id, ["P"])
    assert e_dep.value.code == "ITEM_HAS_DEPENDENTS"

    # removing BOTH P and Q in the same request is allowed; budget recomputes
    updated = await svc.update_draft(d.id, org.id, ["P", "Q"])
    statuses = {i["entity_id"]: i["status"] for i in updated.payload["items"]}
    assert statuses["P"] == "removed_by_user"
    assert statuses["Q"] == "removed_by_user"
    assert updated.payload["estimated_total_minutes"] == 0  # nothing included

    # removing only the DEPENDENT Q is fine (P has no dependents left)
    items2 = [_item("P", "p", "Pack P", 40), _item("Q", "q", "Pack Q", 30, prereq_ids=["P"])]
    d2 = await _draft(db, org, items2)
    up2 = await svc.update_draft(d2.id, org.id, ["Q"])
    st2 = {i["entity_id"]: i["status"] for i in up2.payload["items"]}
    assert st2["Q"] == "removed_by_user"
    assert st2["P"] == "included"
    assert up2.payload["estimated_total_minutes"] == 40  # only P remains

    # removing an UNRELATED item must NOT flag a still-satisfied prereq pair:
    # P(prereq of Q), Q, R(independent). Remove R only → success, P & Q intact.
    # (kills the removed_ids `in remove AND included` -> `or` mutant, which
    # would sweep every included item into removed_ids and wrongly block Q.)
    items3 = [_item("P", "p", "P", 40), _item("Q", "q", "Q", 30, prereq_ids=["P"]),
              _item("R", "r", "R", 10)]
    d4 = await _draft(db, org, items3)
    up4 = await svc.update_draft(d4.id, org.id, ["R"])
    st4 = {i["entity_id"]: i["status"] for i in up4.payload["items"]}
    assert st4 == {"P": "included", "Q": "included", "R": "removed_by_user"}
    assert up4.payload["estimated_total_minutes"] == 70  # P + Q

    # LEGACY draft (no prereq_ids → prereq_slugs fallback): removing the
    # prereq slug alone must still block (kills the slug-comprehension and-gate
    # and the `prereq_slugs or []` -> `and []` mutant)
    legacy_p = _item("LP", "lp", "Legacy P", 20)
    legacy_p["prereq_ids"] = None
    legacy_q = _item("LQ", "lq", "Legacy Q", 25)
    legacy_q["prereq_ids"] = None
    legacy_q["prereq_slugs"] = ["lp"]
    d5 = await _draft(db, org, [legacy_p, legacy_q])
    with pytest.raises(AppError) as e_leg:
        await svc.update_draft(d5.id, org.id, ["LP"])
    assert e_leg.value.code == "ITEM_HAS_DEPENDENTS"

    # legacy + UNRELATED removal: removing LR must NOT sweep LP's slug into
    # removed_slugs (kills the removed_slugs `in remove AND included` -> `or`)
    lp2 = _item("LP2", "lp2", "LP2", 20)
    lp2["prereq_ids"] = None
    lq2 = _item("LQ2", "lq2", "LQ2", 25)
    lq2["prereq_ids"] = None
    lq2["prereq_slugs"] = ["lp2"]
    lr2 = _item("LR2", "lr2", "LR2", 5)
    lr2["prereq_ids"] = None
    d6 = await _draft(db, org, [lp2, lq2, lr2])
    up6 = await svc.update_draft(d6.id, org.id, ["LR2"])
    st6 = {i["entity_id"]: i["status"] for i in up6.payload["items"]}
    assert st6 == {"LP2": "included", "LQ2": "included", "LR2": "removed_by_user"}

    # a CONFIRMED draft cannot be edited
    d3 = await _draft(db, org, [_item("X", "x", "X", 10)], status="confirmed")
    with pytest.raises(AppError) as e_conf:
        await svc.update_draft(d3.id, org.id, ["X"])
    assert e_conf.value.code == "DRAFT_ALREADY_CONFIRMED"
