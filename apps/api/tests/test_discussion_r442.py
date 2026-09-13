"""R442: pack discussion — two-level threading (R93a), public-pack gate,
reply-depth guard, ownership delete.

Documented EQUIVALENT mutants (adjudicated): 404->405 / 422->423 HTTP
status-class swaps and the per_page default 50->51 (fixtures stay under it).
"""

import uuid

import pytest

from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.exceptions import AppError
from app.models.skill_pack import PackStatus, PackVisibility, SkillPack
from app.models.user import User, UserRole, UserStatus


@pytest.fixture
async def db():
    from app.core.database import engine

    await engine.dispose(close=False)
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
    await engine.dispose()


async def _user(db):
    u = User(
        email=f"r442-{uuid.uuid4().hex[:10]}@t.com",
        password_hash=hash_password("Test123!"),
        display_name="R442",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
    )
    db.add(u)
    await db.flush()
    return u


async def _pack(db, *, status=PackStatus.PUBLISHED, vis=PackVisibility.PUBLIC):
    from app.services.organization import OrgService

    owner = await _user(db)
    org = await OrgService(db).create(
        name=f"R442 {uuid.uuid4().hex[:5]}",
        slug=f"r442-{uuid.uuid4().hex[:10]}",
        description=None,
        created_by=owner.id,
    )
    await db.flush()
    p = SkillPack(
        owner_org_id=org.id,
        name="P",
        slug=f"p-{uuid.uuid4().hex[:10]}",
        created_by=owner.id,
        status=status,
        visibility=vis,
    )
    db.add(p)
    await db.flush()
    return p


async def test_create_comment_gates_and_depth_r442(db):
    from app.services.discussion import DiscussionService

    svc = DiscussionService(db)
    pack = await _pack(db)
    u = await _user(db)

    # non-published / private pack → PACK_NOT_FOUND
    draft = await _pack(db, status=PackStatus.DRAFT)
    with pytest.raises(AppError) as e_np:
        await svc.create_comment(draft.id, u.id, "hi")
    assert e_np.value.code == "PACK_NOT_FOUND"
    priv = await _pack(db, vis=PackVisibility.PRIVATE)
    with pytest.raises(AppError):
        await svc.create_comment(priv.id, u.id, "hi")

    # top-level comment, then a reply to it
    top = await svc.create_comment(pack.id, u.id, "top-level")
    assert top.parent_id is None
    reply = await svc.create_comment(pack.id, u.id, "a reply", parent_id=top.id)
    assert reply.parent_id == top.id

    # a parent from a DIFFERENT pack → PARENT_NOT_FOUND
    other_pack = await _pack(db)
    other_top = await svc.create_comment(other_pack.id, u.id, "elsewhere")
    with pytest.raises(AppError) as e_par:
        await svc.create_comment(pack.id, u.id, "x", parent_id=other_top.id)
    assert e_par.value.code == "PARENT_NOT_FOUND"

    # replying to a REPLY (L3) is rejected — two-level model (R93a)
    with pytest.raises(AppError) as e_depth:
        await svc.create_comment(pack.id, u.id, "deep", parent_id=reply.id)
    assert e_depth.value.code == "REPLY_DEPTH_EXCEEDED"

    # a bogus parent id → PARENT_NOT_FOUND
    with pytest.raises(AppError):
        await svc.create_comment(pack.id, u.id, "x", parent_id=str(uuid.uuid4()))


async def test_list_comments_threading_r442(db):
    from app.services.discussion import DiscussionService

    svc = DiscussionService(db)
    pack = await _pack(db)
    a, b = await _user(db), await _user(db)

    t1 = await svc.create_comment(pack.id, a.id, "first")
    t2 = await svc.create_comment(pack.id, b.id, "second")
    r1 = await svc.create_comment(pack.id, b.id, "reply to first", parent_id=t1.id)
    r2 = await svc.create_comment(pack.id, a.id, "another reply to first", parent_id=t1.id)

    threads, total = await svc.list_comments(pack.id)
    assert total == 2  # top-level count only (replies not counted)
    by_id = {t["id"]: t for t in threads}
    # t1 carries its two replies in creation order; t2 has none
    assert [r["id"] for r in by_id[t1.id]["replies"]] == [r1.id, r2.id]
    assert by_id[t2.id]["replies"] == []
    # top-level ordered by creation asc
    assert [t["id"] for t in threads] == [t1.id, t2.id]

    # pagination is over TOP-LEVEL comments; page 2 (per_page 1) → the 2nd
    p2, p2_total = await svc.list_comments(pack.id, page=2, per_page=1)
    assert p2_total == 2
    assert [t["id"] for t in p2] == [t2.id]
    # its replies still attach on page 1
    p1, _ = await svc.list_comments(pack.id, page=1, per_page=1)
    assert [t["id"] for t in p1] == [t1.id]
    assert len(p1[0]["replies"]) == 2


async def test_delete_comment_ownership_r442(db):
    from app.services.discussion import DiscussionService

    svc = DiscussionService(db)
    pack = await _pack(db)
    a, b = await _user(db), await _user(db)
    c = await svc.create_comment(pack.id, a.id, "mine")

    # a non-author → 403
    with pytest.raises(AppError) as e_own:
        await svc.delete_comment(c.id, b.id, pack.id)
    assert e_own.value.status_code == 403
    # a wrong pack_id scopes it out → 404
    other = await _pack(db)
    with pytest.raises(AppError) as e_scope:
        await svc.delete_comment(c.id, a.id, other.id)
    assert e_scope.value.code == "COMMENT_NOT_FOUND"
    # a bogus id → 404
    with pytest.raises(AppError):
        await svc.delete_comment(str(uuid.uuid4()), a.id, pack.id)
    # the author deletes their own comment
    await svc.delete_comment(c.id, a.id, pack.id)
    threads, total = await svc.list_comments(pack.id)
    assert total == 0
