"""R447: skill-pack release export — zip contents, manifest, filename slug.

Documented EQUIVALENT: L40 404->405 status-class swap and L43 json.dumps
indent=2->3 (formatting only; the manifest round-trips identically).
"""

import io
import json
import uuid
import zipfile

import pytest

from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.exceptions import AppError
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


async def _release(db, manifest, version="1.0.0"):
    from app.services.organization import OrgService

    owner = User(email=f"r447-{uuid.uuid4().hex[:10]}@t.com",
                 password_hash=hash_password("Test123!"), display_name="R447",
                 role=UserRole.ADMIN, status=UserStatus.ACTIVE)
    db.add(owner)
    await db.flush()
    org = await OrgService(db).create(name=f"R447 {uuid.uuid4().hex[:5]}",
                                      slug=f"r447-{uuid.uuid4().hex[:10]}",
                                      description=None, created_by=owner.id)
    await db.flush()
    pack = SkillPack(owner_org_id=org.id, name="P", slug=f"p-{uuid.uuid4().hex[:8]}",
                     created_by=owner.id)
    db.add(pack)
    await db.flush()
    rel = SkillPackRelease(pack_id=pack.id, version=version, manifest=manifest,
                           checksum="x" * 64, released_by=owner.id)
    db.add(rel)
    await db.flush()
    return pack, rel


async def test_export_release_r447(db):
    from app.services.pack_export import PackExportService

    svc = PackExportService(db)
    manifest = {"pack": {"name": "My Cool Pack!"}, "skills": [{"name": "S"}]}
    pack, rel = await _release(db, manifest, version="2.1.0")

    # unknown version → RELEASE_NOT_FOUND
    with pytest.raises(AppError) as e_nf:
        await svc.export_release(pack.id, "9.9.9")
    assert e_nf.value.code == "RELEASE_NOT_FOUND"

    zip_bytes, filename = await svc.export_release(pack.id, "2.1.0")
    # filename is slugified from the manifest pack name + version
    assert filename == "my-cool-pack-2.1.0.zip"
    # the zip contains exactly the manifest json under the canonical name
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        assert zf.namelist() == ["openskill-pack.json"]
        loaded = json.loads(zf.read("openskill-pack.json"))
    assert loaded == manifest  # round-trips the manifest verbatim


async def test_export_filename_fallback_r447(db):
    from app.services.pack_export import PackExportService

    svc = PackExportService(db)
    # a manifest with no pack name → filename falls back to 'pack'
    pack, _ = await _release(db, {"pack": {}}, version="1.0.0")
    _, filename = await svc.export_release(pack.id, "1.0.0")
    assert filename == "pack-1.0.0.zip"
    # a name that slugs to empty (all punctuation) also falls back to 'pack'
    pack2, _ = await _release(db, {"pack": {"name": "!!!"}}, version="1.0.0")
    _, filename2 = await svc.export_release(pack2.id, "1.0.0")
    assert filename2 == "pack-1.0.0.zip"
