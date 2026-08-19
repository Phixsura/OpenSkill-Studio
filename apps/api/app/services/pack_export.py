"""Pack export — download a release as a portable zip bundle."""

import io
import json
import zipfile

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import AppError
from app.models.skill_pack import SkillPackRelease

log = structlog.get_logger()


class PackExportService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def export_release(self, pack_id: str, version: str) -> tuple[bytes, str]:
        """Export a release as a zip archive.

        Returns (zip_bytes, filename).
        The zip contains:
          openskill-pack.json  — the release manifest
        Assets are NOT included in this phase (text-only export).
        """
        # Look up by pack_id + version
        from sqlalchemy import select

        result = await self.db.execute(
            select(SkillPackRelease).where(
                SkillPackRelease.pack_id == pack_id,
                SkillPackRelease.version == version,
            )
        )
        release = result.scalar_one_or_none()
        if release is None:
            raise AppError("RELEASE_NOT_FOUND", "Release not found", 404)

        manifest = release.manifest
        manifest_json = json.dumps(manifest, indent=2, ensure_ascii=False)

        # Build zip in memory
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("openskill-pack.json", manifest_json)

        buf.seek(0)
        pack_name = manifest.get("pack", {}).get("name", "pack").lower().replace(" ", "-")
        filename = f"{pack_name}-{version}.zip"

        log.info("pack_exported", pack_id=pack_id, version=version, size=buf.getbuffer().nbytes)
        return buf.getvalue(), filename
