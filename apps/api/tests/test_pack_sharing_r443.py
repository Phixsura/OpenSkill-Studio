"""R443: pack sharing (push-model) — share/revoke/target-remove guards.

share_pack gates on ownership/published/sharing_enabled/self/target and a
share limit; the share row IS the install-grant, so revoke (owner) and
remove_incoming (target, R172) both delete it.

Documented EQUIVALENT mutants (adjudicated): 404->405 / 422->423 / 409->410
HTTP status-class swaps, and L47 the FOR UPDATE lock-row predicate
(SkillPack.id == pack_id) — a serialization lock with no observable
single-session effect (the limit check queries PackShare.pack_id separately).
"""

import uuid

import pytest

from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
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
    u = User(email=f"r443-{uuid.uuid4().hex[:10]}@t.com", password_hash=hash_password("Test123!"),
             display_name="R443", role=UserRole.ADMIN, status=UserStatus.ACTIVE)
    db.add(u)
    await db.flush()
    return u


async def _org(db):
    from app.services.organization import OrgService

    owner = await _user(db)
    o = await OrgService(db).create(name=f"R443 {uuid.uuid4().hex[:5]}",
                                    slug=f"r443-{uuid.uuid4().hex[:10]}",
                                    description=None, created_by=owner.id)
    await db.flush()
    return o, owner


async def _pack(db, org, creator, *, status=PackStatus.PUBLISHED, sharing=True):
    p = SkillPack(owner_org_id=org.id, name="P", slug=f"p-{uuid.uuid4().hex[:10]}",
                  created_by=creator.id, status=status, visibility=PackVisibility.PUBLIC,
                  sharing_enabled=sharing)
    db.add(p)
    await db.flush()
    return p


async def test_share_pack_guards_r443(db):
    from app.exceptions import AppError
    from app.services.pack_sharing import PackSharingService

    org, owner = await _org(db)
    target, _ = await _org(db)
    svc = PackSharingService(db)

    # not the owner org → PACK_NOT_FOUND
    pack = await _pack(db, org, owner)
    with pytest.raises(AppError) as e_own:
        await svc.share_pack(target.id, pack.id, org.id, owner.id)
    assert e_own.value.code == "PACK_NOT_FOUND"

    # unpublished / sharing-disabled → specific 422s
    draft = await _pack(db, org, owner, status=PackStatus.DRAFT)
    with pytest.raises(AppError) as e_np:
        await svc.share_pack(org.id, draft.id, target.id, owner.id)
    assert e_np.value.code == "PACK_NOT_PUBLISHED"
    nos = await _pack(db, org, owner, sharing=False)
    with pytest.raises(AppError) as e_dis:
        await svc.share_pack(org.id, nos.id, target.id, owner.id)
    assert e_dis.value.code == "SHARING_DISABLED"

    # self-share → 422
    with pytest.raises(AppError) as e_self:
        await svc.share_pack(org.id, pack.id, org.id, owner.id)
    assert e_self.value.code == "SELF_SHARE"

    # unknown / archived target org → TARGET_ORG_NOT_FOUND
    with pytest.raises(AppError) as e_t:
        await svc.share_pack(org.id, pack.id, str(uuid.uuid4()), owner.id)
    assert e_t.value.code == "TARGET_ORG_NOT_FOUND"

    # a valid share, then a duplicate → 409
    share = await svc.share_pack(org.id, pack.id, target.id, owner.id)
    assert share.target_org_id == target.id
    with pytest.raises(AppError) as e_dup:
        await svc.share_pack(org.id, pack.id, target.id, owner.id)
    assert e_dup.value.code == "ALREADY_SHARED"


async def test_share_limit_r443(db, monkeypatch):
    from app.exceptions import AppError
    from app.services import pack_sharing
    from app.services.pack_sharing import PackSharingService

    # patch the limit down to 3 so the boundary is cheap to exercise with real
    # (FK-valid) target orgs — the `>= MAX` boundary is what we pin
    monkeypatch.setattr(pack_sharing, "MAX_SHARES_PER_PACK", 3)
    org, owner = await _org(db)
    svc = PackSharingService(db)
    pack = await _pack(db, org, owner)

    # share to exactly 3 distinct target orgs
    for _ in range(3):
        t, _tu = await _org(db)
        await svc.share_pack(org.id, pack.id, t.id, owner.id)
    # the 4th share is rejected AT the bound (kills the `>= MAX` -> `> MAX`)
    over, _ou = await _org(db)
    with pytest.raises(AppError) as e_lim:
        await svc.share_pack(org.id, pack.id, over.id, owner.id)
    assert e_lim.value.code == "SHARE_LIMIT_REACHED"


async def test_list_revoke_and_target_remove_r443(db):
    from app.exceptions import AppError
    from app.services.pack_sharing import PackSharingService

    org, owner = await _org(db)
    target, _ = await _org(db)
    svc = PackSharingService(db)
    pack = await _pack(db, org, owner)
    await svc.share_pack(org.id, pack.id, target.id, owner.id)

    # target sees the shared pack; owner org does not (it's not a target)
    assert [p.id for p in await svc.list_shared_packs(target.id)] == [pack.id]
    assert await svc.list_shared_packs(org.id) == []

    # only the OWNER org can revoke (a non-owner caller → PACK_NOT_FOUND)
    with pytest.raises(AppError) as e_own:
        await svc.revoke_share(target.id, pack.id, target.id)
    assert e_own.value.code == "PACK_NOT_FOUND"
    # revoke removes the share (drops from the target's list + install grant)
    await svc.revoke_share(org.id, pack.id, target.id)
    assert await svc.list_shared_packs(target.id) == []
    # revoking again → SHARE_NOT_FOUND
    with pytest.raises(AppError) as e_gone:
        await svc.revoke_share(org.id, pack.id, target.id)
    assert e_gone.value.code == "SHARE_NOT_FOUND"

    # R172 target-side removal of an unsolicited share
    await svc.share_pack(org.id, pack.id, target.id, owner.id)
    await svc.remove_incoming_share(target.id, pack.id)
    assert await svc.list_shared_packs(target.id) == []
    with pytest.raises(AppError) as e_rm:
        await svc.remove_incoming_share(target.id, pack.id)
    assert e_rm.value.code == "SHARE_NOT_FOUND"
