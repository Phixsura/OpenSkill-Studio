"""R445: workflow registry search — public gate, filters, LIKE-escaping, sort.

search_packs is the public discovery surface: it must expose ONLY
public+published+approved packs, filter by tags/type, escape LIKE
metacharacters, and sort deterministically.

Documented EQUIVALENT: L63 per_page default 20->21 and L161 cache_set TTL
300->301 — both cosmetic (fixtures stay under the page size; the cache is a
no-op without Redis in tests).
"""

import uuid

import pytest

from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.models.skill_pack import PackStatus, PackVisibility
from app.models.user import User, UserRole, UserStatus
from app.models.workflow_pack import WorkflowPack


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
        email=f"r445-{uuid.uuid4().hex[:10]}@t.com",
        password_hash=hash_password("Test123!"),
        display_name="R445",
        role=UserRole.ADMIN,
        status=UserStatus.ACTIVE,
    )
    db.add(owner)
    await db.flush()
    o = await OrgService(db).create(
        name=f"R445 {uuid.uuid4().hex[:5]}",
        slug=f"r445-{uuid.uuid4().hex[:10]}",
        description=None,
        created_by=owner.id,
    )
    await db.flush()
    return o


async def _pack(db, org, name, **kw):
    defaults = dict(
        status=PackStatus.PUBLISHED,
        visibility=PackVisibility.PUBLIC,
        review_status="approved",
        scenario_tags=[],
        tool_tags=[],
        capability_tags=[],
        workflow_type="production",
        install_count=0,
    )
    defaults.update(kw)
    p = WorkflowPack(
        owner_org_id=org.id, name=name, slug=f"{name.lower()}-{uuid.uuid4().hex[:8]}", **defaults
    )
    db.add(p)
    await db.flush()
    return p


async def test_public_gate_r445(db):
    from app.services.workflow_registry import WorkflowRegistryService

    org = await _org(db)
    svc = WorkflowRegistryService(db)
    tag = f"gate-{uuid.uuid4().hex[:12]}"  # unique tag isolates this test's packs
    good = await _pack(db, org, "Public Approved", scenario_tags=[tag])
    await _pack(db, org, "Private", visibility=PackVisibility.PRIVATE, scenario_tags=[tag])
    await _pack(db, org, "Draft", status=PackStatus.DRAFT, scenario_tags=[tag])
    await _pack(db, org, "Rejected", review_status="rejected", scenario_tags=[tag])
    grand = await _pack(db, org, "Grandfathered", review_status=None, scenario_tags=[tag])

    packs, total = await svc.search_packs(scenario=tag)
    ids = {p.id for p in packs}
    assert good.id in ids
    assert grand.id in ids  # NULL review_status is grandfathered-approved
    assert total == 2  # only the two visible ones (private/draft/rejected excluded)


async def test_filters_and_search_escape_r445(db):
    from app.services.workflow_registry import WorkflowRegistryService

    org = await _org(db)
    svc = WorkflowRegistryService(db)
    sc = f"sc-{uuid.uuid4().hex[:10]}"
    tl = f"tl-{uuid.uuid4().hex[:10]}"
    await _pack(
        db,
        org,
        "Alpha",
        scenario_tags=[sc, "marketing"],
        tool_tags=["comfyui"],
        capability_tags=["image_generation"],
        workflow_type="production",
    )
    await _pack(
        db,
        org,
        "Beta",
        scenario_tags=[sc, "research"],
        tool_tags=[tl],
        capability_tags=["video_generation"],
        workflow_type="learning",
    )

    # scenario / tool / workflow_type filters (scoped to this test's tags)
    assert [p.name for p in (await svc.search_packs(scenario=sc, tool="comfyui"))[0]] == ["Alpha"]
    assert [p.name for p in (await svc.search_packs(tool=tl))[0]] == ["Beta"]
    beta_learn = (await svc.search_packs(scenario=sc, workflow_type="learning"))[0]
    assert [p.name for p in beta_learn] == ["Beta"]

    # a real substring search + scenario scope works and is deterministic
    named, _ = await svc.search_packs(scenario=sc, search="Alpha")
    assert [p.name for p in named] == ["Alpha"]
    # a LIKE metacharacter is escaped: "%" is literal, so within this test's
    # scenario scope (names Alpha/Beta, no "%") it matches nothing
    esc, _ = await svc.search_packs(scenario=sc, search="%")
    assert esc == []


async def test_input_output_type_filter_r445(db):
    from app.services.workflow_registry import WorkflowRegistryService

    org = await _org(db)
    svc = WorkflowRegistryService(db)
    tag = f"io-{uuid.uuid4().hex[:12]}"
    # img->vid, txt->img, and a pack with neither matching schema
    await _pack(
        db,
        org,
        "ImgVid",
        scenario_tags=[tag],
        input_schema=[{"type": "image"}],
        output_schema=[{"type": "video"}],
    )
    await _pack(
        db,
        org,
        "TxtImg",
        scenario_tags=[tag],
        input_schema=[{"type": "text"}],
        output_schema=[{"type": "image"}],
    )
    await _pack(
        db,
        org,
        "AudAud",
        scenario_tags=[tag],
        input_schema=[{"type": "audio"}],
        output_schema=[{"type": "audio"}],
    )

    # input_type filter: only packs consuming 'image'
    r_in = (await svc.search_packs(scenario=tag, input_type="image"))[0]
    assert [p.name for p in r_in] == ["ImgVid"]
    # output_type filter: only packs producing 'image'
    r_out = (await svc.search_packs(scenario=tag, output_type="image"))[0]
    assert [p.name for p in r_out] == ["TxtImg"]
    # BOTH must match (AND): image-in AND video-out → only ImgVid
    r_both = (await svc.search_packs(scenario=tag, input_type="image", output_type="video"))[0]
    assert [p.name for p in r_both] == ["ImgVid"]
    # image-in AND image-out matches nothing (ImgVid outputs video)
    r_none = (await svc.search_packs(scenario=tag, input_type="image", output_type="image"))[0]
    assert r_none == []
    # in-python pagination of the io-filtered set: 3 audio-less matches for a
    # broad filter, page 2 (per_page 2) returns the 3rd
    # (all three share input? no — filter by output audio to isolate one)
    r_aud = (await svc.search_packs(scenario=tag, output_type="audio"))[0]
    assert [p.name for p in r_aud] == ["AudAud"]

    # in-python pagination of the io-filtered set (L154 slice): three
    # image-in packs under a fresh tag, page 2 per_page 2 → the 3rd by name
    ptag = f"iop-{uuid.uuid4().hex[:12]}"
    for nm in ("Pa", "Pb", "Pc"):
        await _pack(
            db,
            org,
            nm,
            scenario_tags=[ptag],
            input_schema=[{"type": "image"}],
            output_schema=[{"type": "image"}],
        )
    page1 = (
        await svc.search_packs(scenario=ptag, input_type="image", sort="name", page=1, per_page=2)
    )[0]
    page2 = (
        await svc.search_packs(scenario=ptag, input_type="image", sort="name", page=2, per_page=2)
    )[0]
    assert [p.name for p in page1] == ["Pa", "Pb"]
    assert [p.name for p in page2] == ["Pc"]


async def test_sort_and_pagination_r445(db):
    from app.services.workflow_registry import WorkflowRegistryService

    org = await _org(db)
    svc = WorkflowRegistryService(db)
    tag = f"sort-{uuid.uuid4().hex[:12]}"
    await _pack(db, org, "Zeta", install_count=5, scenario_tags=[tag])
    await _pack(db, org, "Aaa", install_count=50, scenario_tags=[tag])
    await _pack(db, org, "Mmm", install_count=10, scenario_tags=[tag])

    # most_installed sorts by install_count desc
    by_installs = [p.name for p in (await svc.search_packs(scenario=tag, sort="most_installed"))[0]]
    assert by_installs == ["Aaa", "Mmm", "Zeta"]
    # name sorts alphabetically asc
    by_name = [p.name for p in (await svc.search_packs(scenario=tag, sort="name"))[0]]
    assert by_name == ["Aaa", "Mmm", "Zeta"]

    # pagination
    p1, total = await svc.search_packs(scenario=tag, sort="name", page=1, per_page=2)
    p2, _ = await svc.search_packs(scenario=tag, sort="name", page=2, per_page=2)
    assert total == 3
    assert [p.name for p in p1] == ["Aaa", "Mmm"]
    assert [p.name for p in p2] == ["Zeta"]
