"""R441: notification create/suppress/list/mark + preferences merge.

create() suppresses via a TYPE->PREF-KEY mapping (R113[L1]); mark_read is
ownership-scoped; preferences merge stored over defaults.
"""

import uuid

import pytest

from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.exceptions import AppError
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
    u = User(email=f"r441-{uuid.uuid4().hex[:10]}@t.com", password_hash=hash_password("Test123!"),
             display_name="R441", role=UserRole.STUDENT, status=UserStatus.ACTIVE)
    db.add(u)
    await db.flush()
    return u


async def test_create_suppression_and_truncation_r441(db):
    from app.services.notification import NotificationService

    svc = NotificationService(db)
    u = await _user(db)

    # a normal notification is created; title truncated to 200 chars
    n = await svc.create(u.id, "pack.updated", "x" * 250)
    assert n is not None
    assert len(n.title) == 200
    assert n.data == {}  # None data defaults to {} (kills the `data or {}` -> `and`)

    # opting OUT of the mapped pref key ('pack_update') suppresses pack.updated
    await svc.update_preferences(u.id, {"pack_update": False})
    suppressed = await svc.create(u.id, "pack.updated", "Update")
    assert suppressed is None
    # …but a type mapped to a DIFFERENT pref key ('review') is unaffected
    still = await svc.create(u.id, "pack.approved", "Approved")
    assert still is not None
    # opting out of 'review' suppresses both approved and rejected
    await svc.update_preferences(u.id, {"review": False})
    assert await svc.create(u.id, "pack.approved", "A") is None
    assert await svc.create(u.id, "pack.rejected", "R") is None


async def test_list_and_mark_read_r441(db):
    from app.services.notification import NotificationService

    svc = NotificationService(db)
    u, other = await _user(db), await _user(db)
    n1 = await svc.create(u.id, "pack.updated", "One")
    n2 = await svc.create(u.id, "pack.updated", "Two")
    await svc.create(other.id, "pack.updated", "Theirs")

    # list is scoped to the user and unread-only by default
    rows, total = await svc.list_notifications(u.id)
    assert total == 2
    assert {r.id for r in rows} == {n1.id, n2.id}

    # mark_read on someone else's notification → 404 (ownership)
    with pytest.raises(AppError) as e_own:
        await svc.mark_read(n1.id, other.id)
    assert e_own.value.status_code == 404

    # mark one read → unread list shrinks; include_read shows it again
    await svc.mark_read(n1.id, u.id)
    unread, unread_total = await svc.list_notifications(u.id)
    assert unread_total == 1 and unread[0].id == n2.id
    all_rows, all_total = await svc.list_notifications(u.id, include_read=True)
    assert all_total == 2

    # mark_all_read returns the count of rows flipped (only the still-unread one)
    flipped = await svc.mark_all_read(u.id)
    assert flipped == 1
    # a second mark_all_read flips nothing
    assert await svc.mark_all_read(u.id) == 0


async def test_preferences_merge_r441(db):
    from app.services.notification import NotificationService

    svc = NotificationService(db)
    u = await _user(db)

    # defaults when nothing stored
    assert await svc.get_preferences(u.id) == {"pack_update": True, "review": True}

    # update merges: an explicit False overrides, unmentioned keys keep default
    await svc.update_preferences(u.id, {"pack_update": False})
    got = await svc.get_preferences(u.id)
    assert got["pack_update"] is False
    assert got["review"] is True  # default fills the gap

    # a second update keeps the earlier key and adds the new one
    await svc.update_preferences(u.id, {"review": False})
    final = await svc.get_preferences(u.id)
    assert final["pack_update"] is False and final["review"] is False
