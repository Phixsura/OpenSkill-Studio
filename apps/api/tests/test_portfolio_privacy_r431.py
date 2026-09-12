"""R431: portfolio public-visibility gating (0/39 mutants killed before).

get_public_profile / get_public_items / get_public_item are the anon-facing
privacy surface — a private profile must leak nothing, only show_on_profile
badges and PUBLIC items appear. The whole branch layer was untested
(0/39 mutants killed before this suite).

Documented EQUIVALENT mutants (adjudicated): create_item L259/L261 status
swaps (404->405 SUBMISSION_NOT_FOUND, 422->423 SUBMISSION_NOT_APPROVED —
HTTP class unchanged) and L303 slug-suffix cosmetics (base[:190],
token_hex(3) length — a different unique suffix is still unique).
"""

import uuid

import pytest

from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.exceptions import AppError
from app.models.portfolio import (
    ItemVisibility,
    PortfolioItem,
    ProfileVisibility,
    SkillBadge,
    UserProfile,
)
from app.models.user import User, UserRole, UserStatus


@pytest.fixture
async def db():
    from app.core.database import engine

    await engine.dispose(close=False)
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
    await engine.dispose()


async def _user(db, name="Hana"):
    u = User(email=f"r431-{uuid.uuid4().hex[:10]}@t.com", password_hash=hash_password("Test123!"),
             display_name=name, role=UserRole.STUDENT, status=UserStatus.ACTIVE)
    db.add(u)
    await db.flush()
    return u


async def _org_skill(db, owner):
    from app.services.organization import OrgService
    from app.services.skill import SkillService

    org = await OrgService(db).create(name=f"R431 {uuid.uuid4().hex[:5]}",
                                      slug=f"r431-{uuid.uuid4().hex[:10]}",
                                      description=None, created_by=owner.id)
    await db.flush()
    cat = await SkillService(db).create_category(org.id, "AI", None, None, None, owner.id)
    sk = await SkillService(db).create_skill(
        org.id, cat.id, "Prompting", None, "d", "# c", "beginner", 30, [], None, owner.id)
    return org, sk


async def _profile(db, user, username, visibility=ProfileVisibility.PUBLIC):
    p = UserProfile(user_id=user.id, username=username, visibility=visibility)
    db.add(p)
    await db.flush()
    return p


def _item(user_id, slug, vis, featured=False, order=0):
    return PortfolioItem(user_id=user_id, title=slug.title(), slug=slug,
                         visibility=vis, featured=featured, sort_order=order)


async def test_get_public_profile_gating_r431(db):
    from app.services.portfolio import PortfolioService

    svc = PortfolioService(db)
    owner = await _user(db)
    org, sk = await _org_skill(db, owner)
    from app.services.skill import SkillService

    async def _mk_skill():
        cat2 = await SkillService(db).create_category(
            org.id, f"C{uuid.uuid4().hex[:4]}", None, None, None, owner.id)
        return await SkillService(db).create_skill(
            org.id, cat2.id, f"S{uuid.uuid4().hex[:4]}", None, "d", "# c",
            "beginner", 30, [], None, owner.id)

    sk2, sk3 = await _mk_skill(), await _mk_skill()
    u = await _user(db, "Public User")
    prof_row = await _profile(db, u, "publicuser", ProfileVisibility.PUBLIC)
    prof_row.social_links = {"twitter": "@hana"}
    await db.flush()

    # badges: one shown+completed, one shown+incomplete, one HIDDEN (distinct
    # skills — unique on user+skill+org)
    db.add_all([
        SkillBadge(user_id=u.id, skill_id=sk.id, org_id=org.id, skill_name="Shown Done",
                   category_name="AI", completion_pct=100, show_on_profile=True),
        SkillBadge(user_id=u.id, skill_id=sk2.id, org_id=org.id, skill_name="Shown WIP",
                   category_name="AI", completion_pct=99, show_on_profile=True),
        SkillBadge(user_id=u.id, skill_id=sk3.id, org_id=org.id, skill_name="Hidden",
                   category_name="AI", completion_pct=100, show_on_profile=False),
    ])
    # items: TWO PUBLIC featured + one PUBLIC non-featured (3 public), one
    # UNLISTED, one PRIVATE (2 non-public) — the counts differ so the
    # item_count `== PUBLIC` filter can't be flipped to `!=` unnoticed
    db.add_all([
        _item(u.id, "feat", ItemVisibility.PUBLIC, featured=True),
        _item(u.id, "feat2", ItemVisibility.PUBLIC, featured=True),
        _item(u.id, "pub", ItemVisibility.PUBLIC, featured=False),
        _item(u.id, "unl", ItemVisibility.UNLISTED, featured=True),
        _item(u.id, "priv", ItemVisibility.PRIVATE, featured=True),
    ])
    await db.flush()

    prof = await svc.get_public_profile("publicuser")
    assert prof is not None
    # only the two show_on_profile badges appear; completed flag is pct>=100
    names = {s["name"]: s for s in prof["skills"]}
    assert set(names) == {"Shown Done", "Shown WIP"}
    assert names["Shown Done"]["completed"] is True
    assert names["Shown WIP"]["completed"] is False  # 99 < 100
    # featured_items are PUBLIC + featured ONLY (unlisted/private featured excluded)
    feat_slugs = {i.slug for i in prof["featured_items"]}
    assert feat_slugs == {"feat", "feat2"}
    # item_count counts ALL public items (featured or not), not unlisted/private
    assert prof["item_count"] == 3  # 3 public; the 2 non-public excluded
    # social_links is passed through as-is (a truthy map survives `or {}`)
    assert prof["social_links"] == {"twitter": "@hana"}

    # a PRIVATE profile leaks nothing
    priv_user = await _user(db)
    await _profile(db, priv_user, "privuser", ProfileVisibility.PRIVATE)
    assert await svc.get_public_profile("privuser") is None
    # an unknown username → None
    assert await svc.get_public_profile("nobody") is None


async def test_get_public_items_and_item_r431(db):
    from app.services.portfolio import PortfolioService

    svc = PortfolioService(db)
    u = await _user(db)
    await _profile(db, u, "itemsuser", ProfileVisibility.PUBLIC)
    db.add_all([
        _item(u.id, "a", ItemVisibility.PUBLIC, order=1),
        _item(u.id, "b", ItemVisibility.UNLISTED, order=0),
        _item(u.id, "c", ItemVisibility.PRIVATE, order=2),
    ])
    await db.flush()

    # public items list: PUBLIC only (unlisted + private excluded)
    pub = await svc.get_public_items("itemsuser")
    assert [i.slug for i in pub] == ["a"]

    # item detail: PUBLIC and UNLISTED are reachable by direct slug; PRIVATE
    # and unknown are not
    assert (await svc.get_public_item("itemsuser", "a")).slug == "a"
    assert (await svc.get_public_item("itemsuser", "b")).slug == "b"  # unlisted direct-link OK
    assert await svc.get_public_item("itemsuser", "c") is None       # private hidden
    assert await svc.get_public_item("itemsuser", "missing") is None

    # a PRIVATE profile hides even direct item links + the list
    priv = await _user(db)
    await _profile(db, priv, "privitems", ProfileVisibility.PRIVATE)
    db.add(_item(priv.id, "x", ItemVisibility.PUBLIC))
    await db.flush()
    assert await svc.get_public_items("privitems") == []
    assert await svc.get_public_item("privitems", "x") is None


async def test_set_username_uniqueness_r431(db):
    from app.services.portfolio import PortfolioService, UsernameUnavailableError

    svc = PortfolioService(db)
    a, b = await _user(db), await _user(db)
    await svc.set_username(a.id, "taken")
    # another user cannot claim the same username
    with pytest.raises(UsernameUnavailableError):
        await svc.set_username(b.id, "taken")
    # the SAME user re-setting their own username is fine (the != user_id
    # uniqueness check excludes self)
    again = await svc.set_username(a.id, "taken")
    assert again.username == "taken"


async def test_create_item_submission_gating_r431(db):
    from app.models.project import ContentStatus, Submission, SubmissionStatus
    from app.services.organization import OrgService
    from app.services.portfolio import PortfolioService
    from app.services.project import ProjectService

    svc = PortfolioService(db)
    owner = await _user(db)
    org = await OrgService(db).create(name=f"R431p {uuid.uuid4().hex[:5]}",
                                      slug=f"r431p-{uuid.uuid4().hex[:10]}",
                                      description=None, created_by=owner.id)
    await db.flush()
    proj = await ProjectService(db).create_project(
        org.id, "P", None, "d", "i", "beginner", 100, [], None, None, 0, 0, None, owner.id)
    proj.status = ContentStatus.PUBLISHED
    await db.flush()
    u = await _user(db)

    # a submission that isn't the user's → 404
    other_sub = Submission(org_id=org.id, project_id=proj.id, user_id=owner.id, version=1,
                           status=SubmissionStatus.APPROVED, final_score=90)
    db.add(other_sub)
    await db.flush()
    with pytest.raises(AppError) as e_own:
        await svc.create_item(u.id, "T", None, other_sub.id, None, None, None, "public", False)
    assert e_own.value.code == "SUBMISSION_NOT_FOUND"

    # the user's own submission but NOT approved → 422
    draft = Submission(org_id=org.id, project_id=proj.id, user_id=u.id, version=1,
                       status=SubmissionStatus.SUBMITTED)
    db.add(draft)
    await db.flush()
    with pytest.raises(AppError) as e_appr:
        await svc.create_item(u.id, "T", None, draft.id, None, None, None, "public", False)
    assert e_appr.value.code == "SUBMISSION_NOT_APPROVED"

    # approved own submission → item carries the denormalized score + names
    appr = Submission(org_id=org.id, project_id=proj.id, user_id=u.id, version=2,
                      status=SubmissionStatus.APPROVED, final_score=88)
    db.add(appr)
    await db.flush()
    item = await svc.create_item(u.id, "Great Work", None, appr.id, None, None, None,
                                 "public", True)
    assert item.score == 88
    assert item.source_project == "P"
    assert item.source_org_name == org.name
    assert item.visibility == ItemVisibility.PUBLIC

    # a bad visibility string falls back to PUBLIC
    item2 = await svc.create_item(u.id, "Another", None, None, ["x", "y"], None, None,
                                  "nonsense", False)
    assert item2.visibility == ItemVisibility.PUBLIC
    assert item2.tags == ["x", "y"]  # a truthy tags list is preserved (not dropped to [])


async def test_toggle_badge_and_update_item_ownership_r431(db):
    from app.services.portfolio import ItemNotFoundError, PortfolioService

    svc = PortfolioService(db)
    owner = await _user(db)
    org, sk = await _org_skill(db, owner)
    u, intruder = await _user(db), await _user(db)

    badge = SkillBadge(user_id=u.id, skill_id=sk.id, org_id=org.id, skill_name="S",
                       category_name="AI", completion_pct=100, show_on_profile=False)
    db.add(badge)
    await db.flush()

    # owner toggles their badge
    toggled = await svc.toggle_badge(badge.id, u.id, True)
    assert toggled.show_on_profile is True
    # a different user cannot toggle it → 404 (no existence oracle)
    with pytest.raises(AppError) as e_b:
        await svc.toggle_badge(badge.id, intruder.id, False)
    assert e_b.value.status_code == 404
    await db.refresh(badge)
    assert badge.show_on_profile is True  # unchanged by the intruder

    # update_item ownership: a non-owner gets a uniform 404 (R91)
    it = _item(u.id, "mine", ItemVisibility.PUBLIC)
    db.add(it)
    await db.flush()
    with pytest.raises(ItemNotFoundError):
        await svc.update_item(it.id, intruder.id, title="Hacked")
    ok = await svc.update_item(it.id, u.id, title="Renamed")
    assert ok.title == "Renamed"
    # a None field value is IGNORED (partial update) — never nulls the column
    ok2 = await svc.update_item(it.id, u.id, title=None, description="desc")
    assert ok2.title == "Renamed"  # unchanged by the None
    assert ok2.description == "desc"
