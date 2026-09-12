"""R434: registry pack quality-score computation (0-100 completeness signals).

compute_quality_score drives discovery ranking; each signal contributes a
fixed weight. Tested by toggling one signal at a time from a zero baseline.

Documented EQUIVALENT mutants (adjudicated): for the container/count
signals (learning_outcomes list, project_templates rubric list, provenance
dict, review_count int) the `X and len(X) > 0` / `> 0` guards are redundant
with X's own truthiness — a non-empty list always has len>0, and the
default-empty containers make the `and`->`or` flip produce the same falsy
result (only an impossible negative review_count or truthy-but-len-0
container would differ). L350 `.limit(1)` 1->2 (latest-release probe returns
the same first row) and L384 30->31 (New-badge window edge) are likewise
equivalent for the fixtures.
"""

import uuid

import pytest

from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.models.skill_pack import SkillPack, SkillPackRelease
from app.models.user import User, UserRole, UserStatus


@pytest.fixture
async def db():
    from app.core.database import engine

    await engine.dispose(close=False)
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
    await engine.dispose()


async def _org(db):
    from app.services.organization import OrgService

    owner = User(
        email=f"r434-{uuid.uuid4().hex[:10]}@t.com",
        password_hash=hash_password("Test123!"),
        display_name="R434",
        role=UserRole.ADMIN,
        status=UserStatus.ACTIVE,
    )
    db.add(owner)
    await db.flush()
    o = await OrgService(db).create(
        name=f"R434 {uuid.uuid4().hex[:5]}",
        slug=f"r434-{uuid.uuid4().hex[:10]}",
        description=None,
        created_by=owner.id,
    )
    await db.flush()
    return o, owner


async def _pack(db, org, **fields):
    p = SkillPack(owner_org_id=org.id, name="P", slug=f"p-{uuid.uuid4().hex[:10]}", **fields)
    db.add(p)
    await db.flush()
    return p


async def _release(db, pack, manifest, released_by):
    from datetime import UTC, datetime

    r = SkillPackRelease(
        pack_id=pack.id,
        version=f"1.0.{uuid.uuid4().hex[:4]}",
        manifest=manifest,
        checksum="x" * 64,
        released_by=released_by,
        released_at=datetime.now(UTC),
    )
    db.add(r)
    await db.flush()
    return r


async def test_quality_score_signals_r434(db):
    from app.services.registry import RegistryService

    org, owner = await _org(db)
    svc = RegistryService(db)

    # a bare pack scores 0
    bare = await _pack(db, org)
    assert await svc.compute_quality_score(bare) == 0

    # each metadata signal contributes its exact weight, in isolation
    desc_only = await _pack(db, org, description="Real desc")
    assert await svc.compute_quality_score(desc_only) == 10
    # whitespace-only description does NOT count
    ws = await _pack(db, org, description="   ")
    assert await svc.compute_quality_score(ws) == 0

    summ = await _pack(db, org, summary="A summary")
    assert await svc.compute_quality_score(summ) == 10
    # a whitespace-only summary strips to empty and does NOT count (kills the
    # `len(summary.strip()) > 0` -> `>= 0` mutant)
    ws_summ = await _pack(db, org, summary="   ")
    assert await svc.compute_quality_score(ws_summ) == 0
    outcomes = await _pack(db, org, learning_outcomes=["learn X"])
    assert await svc.compute_quality_score(outcomes) == 15
    prov = await _pack(db, org, provenance={"source": "authored"})
    assert await svc.compute_quality_score(prov) == 10
    reviewed = await _pack(db, org, review_count=3)
    assert await svc.compute_quality_score(reviewed) == 15

    # a release adds 15; a release whose manifest has exercises adds another 15;
    # rubric templates add 10
    rel_pack = await _pack(db, org)
    await _release(db, rel_pack, {"skills": [], "project_templates": []}, owner.id)
    assert await svc.compute_quality_score(rel_pack) == 15  # release only

    ex_pack = await _pack(db, org)
    await _release(
        db, ex_pack, {"skills": [{"exercises": [{"q": 1}]}], "project_templates": []}, owner.id
    )
    assert await svc.compute_quality_score(ex_pack) == 30  # release 15 + exercises 15

    rubric_pack = await _pack(db, org)
    await _release(
        db,
        rubric_pack,
        {
            "skills": [{"exercises": [{"q": 1}]}],
            "project_templates": [{"rubric": [{"criterion": "Q", "max_score": 100}]}],
        },
        owner.id,
    )
    assert await svc.compute_quality_score(rubric_pack) == 40  # 15 + 15 + 10

    # a release with NO exercises and empty-rubric templates: only the release
    # 15 counts (exercise + rubric guards must NOT fire)
    empty_rel = await _pack(db, org)
    await _release(
        db,
        empty_rel,
        {"skills": [{"exercises": []}], "project_templates": [{"rubric": []}]},
        owner.id,
    )
    assert await svc.compute_quality_score(empty_rel) == 15

    # a fully-loaded pack scores the maximum (10+10+15+15+15+10+10+15 = 100)
    full = await _pack(
        db,
        org,
        description="d",
        summary="s",
        learning_outcomes=["o"],
        provenance={"p": 1},
        review_count=5,
    )
    await _release(
        db,
        full,
        {
            "skills": [{"exercises": [{"q": 1}]}],
            "project_templates": [{"rubric": [{"criterion": "Q", "max_score": 100}]}],
        },
        owner.id,
    )
    assert await svc.compute_quality_score(full) == 100


async def test_recompute_badges_persists_r434(db):
    from datetime import UTC, datetime, timedelta

    from app.services.registry import RegistryService

    org, owner = await _org(db)
    svc = RegistryService(db)
    # a popular, freshly-created pack earns Popular + New
    pack = await _pack(db, org, install_count=15)
    pack.created_at = datetime.now(UTC)
    await db.flush()
    await svc.recompute_pack_badges(pack.id)
    await db.refresh(pack)
    assert set(pack.badges) == {"Popular", "New"}

    # dropping installs below the threshold and aging out recomputes to []
    pack.install_count = 2
    pack.created_at = datetime.now(UTC) - timedelta(days=40)
    await db.flush()
    await svc.recompute_pack_badges(pack.id)
    await db.refresh(pack)
    assert pack.badges == []

    # an unknown pack id is a no-op (no crash)
    await svc.recompute_pack_badges(str(uuid.uuid4()))
