"""Pack import — validate and import a zip bundle into an organization."""

import hashlib
import io
import json
import zipfile

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import AppError
from app.models.skill_pack import PackStatus, PackVisibility, SkillPack, SkillPackRelease
from app.services.skill_pack import SkillPackService

log = structlog.get_logger()

MAX_ARCHIVE_SIZE = 100 * 1024 * 1024  # 100 MB
MAX_DECOMPRESSED_SIZE = 1024 * 1024 * 1024  # 1 GB
MAX_FILE_COUNT = 500
FORBIDDEN_PATTERNS = ("..", "\\", "/etc/", "/dev/", "/proc/")
SUPPORTED_SCHEMA_VERSIONS = {"1"}


class PackImportService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def import_pack(
        self, org_id: str, file_bytes: bytes, imported_by: str
    ) -> tuple[SkillPack, SkillPackRelease]:
        """Import a pack from a zip archive.

        Returns (pack, release) created in the target org.
        The pack is created as draft/private.
        """
        # 1. Size check
        if len(file_bytes) > MAX_ARCHIVE_SIZE:
            raise AppError(
                "ARCHIVE_TOO_LARGE",
                f"Archive exceeds {MAX_ARCHIVE_SIZE // (1024 * 1024)}MB limit",
                413,
            )

        # 2. Open zip
        try:
            zf = zipfile.ZipFile(io.BytesIO(file_bytes), "r")
        except zipfile.BadZipFile:
            raise AppError("INVALID_ARCHIVE", "File is not a valid zip archive", 422) from None

        # 3. File count check
        entries = zf.namelist()
        if len(entries) > MAX_FILE_COUNT:
            raise AppError("TOO_MANY_FILES", f"Archive contains more than {MAX_FILE_COUNT} files", 422)

        # 4. Path traversal check
        for entry in entries:
            if any(p in entry for p in FORBIDDEN_PATTERNS):
                raise AppError("MALICIOUS_ARCHIVE", f"Forbidden path pattern in: {entry}", 422)
            if entry.startswith("/"):
                raise AppError("MALICIOUS_ARCHIVE", f"Absolute path detected: {entry}", 422)

        # 5. Decompression size check
        total_size = sum(info.file_size for info in zf.infolist())
        if total_size > MAX_DECOMPRESSED_SIZE:
            raise AppError(
                "DECOMPRESSION_BOMB",
                f"Decompressed size exceeds {MAX_DECOMPRESSED_SIZE // (1024 * 1024)}MB limit",
                422,
            )

        # 6. Find and parse manifest
        if "openskill-pack.json" not in entries:
            raise AppError("INVALID_MANIFEST", "Archive must contain manifest file openskill-pack.json", 422)

        try:
            manifest_bytes = zf.read("openskill-pack.json")
            manifest = json.loads(manifest_bytes)
        except (json.JSONDecodeError, KeyError) as exc:
            log.warning("manifest_parse_failed", error=str(exc))
            raise AppError(
                "INVALID_MANIFEST",
                "Manifest file openskill-pack.json is not valid JSON or missing required fields",
                422,
            ) from exc

        # 6b. Manifest size limit (same as publish_release)
        max_manifest = 10_000_000  # 10 MB
        canonical = json.dumps(manifest, sort_keys=True, ensure_ascii=True)
        if len(canonical.encode()) > max_manifest:
            raise AppError(
                "MANIFEST_TOO_LARGE",
                f"Manifest exceeds {max_manifest // 1_000_000}MB limit",
                422,
            )

        # 7. Validate schema version
        schema_version = manifest.get("schema_version")
        if schema_version not in SUPPORTED_SCHEMA_VERSIONS:
            raise AppError(
                "UNSUPPORTED_SCHEMA",
                f"Schema version '{schema_version}' is not supported. Supported: {SUPPORTED_SCHEMA_VERSIONS}",
                422,
            )

        # 8. Validate structure
        pack_meta = manifest.get("pack", {})
        skills = manifest.get("skills", [])
        templates = manifest.get("project_templates", [])

        if not pack_meta.get("name"):
            raise AppError("INVALID_MANIFEST", "Manifest pack.name is required", 422)

        # 9. Check logical_id uniqueness
        all_logical_ids: list[str] = []
        for s in skills:
            lid = s.get("logical_id")
            if not lid:
                raise AppError("INVALID_MANIFEST", "Every skill must have a logical_id", 422)
            all_logical_ids.append(lid)
        for t in templates:
            lid = t.get("logical_id")
            if not lid:
                raise AppError("INVALID_MANIFEST", "Every template must have a logical_id", 422)
            all_logical_ids.append(lid)

        if len(all_logical_ids) != len(set(all_logical_ids)):
            raise AppError("DUPLICATE_LOGICAL_ID", "Duplicate logical_id found in manifest", 422)

        # 10. Validate prerequisite references
        skill_lids = {s["logical_id"] for s in skills}
        for s in skills:
            for prereq in s.get("prerequisites", []):
                if prereq not in skill_lids:
                    raise AppError(
                        "INVALID_PREREQUISITE",
                        f"Prerequisite '{prereq}' not found in manifest skills",
                        422,
                    )

        # 10b. Cycle detection using Kahn's algorithm (topological sort)
        in_degree: dict[str, int] = {lid: 0 for lid in skill_lids}
        adjacency: dict[str, list[str]] = {lid: [] for lid in skill_lids}
        for s in skills:
            lid = s["logical_id"]
            for prereq in s.get("prerequisites", []):
                # Edge: prereq -> lid (lid depends on prereq)
                adjacency[prereq].append(lid)
                in_degree[lid] += 1

        queue = [lid for lid, deg in in_degree.items() if deg == 0]
        visited_count = 0
        while queue:
            node = queue.pop()
            visited_count += 1
            for neighbor in adjacency[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if visited_count != len(skill_lids):
            raise AppError(
                "PREREQUISITE_CYCLE",
                "Circular prerequisites detected in manifest",
                422,
            )

        # 11. Strip runtime fields (safety)
        runtime_keys = {"user_id", "submission_id", "attempt_id", "review_id", "progress_id"}
        for s in skills:
            for key in runtime_keys:
                s.pop(key, None)
            for ex in s.get("exercises", []):
                for key in runtime_keys:
                    ex.pop(key, None)

        # 11b. Validate field sizes (same limits as Pydantic API schemas)
        max_learning_content = 100_000
        max_config_size = 20_000
        valid_exercise_types = {"multiple_choice", "text_answer", "code_submission", "file_upload"}

        for s in skills:
            lc = s.get("learning_content", "")
            if lc and len(lc) > max_learning_content:
                raise AppError(
                    "CONTENT_TOO_LARGE",
                    f"Skill '{s.get('logical_id')}' learning_content exceeds {max_learning_content} chars",
                    422,
                )
            for ex in s.get("exercises", []):
                ex_type = ex.get("type", "text_answer")
                if ex_type not in valid_exercise_types:
                    raise AppError(
                        "INVALID_EXERCISE_TYPE",
                        f"Exercise type '{ex_type}' is not valid. Allowed: {', '.join(sorted(valid_exercise_types))}",
                        422,
                    )
                config = ex.get("config", {})
                config_str = json.dumps(config) if config else ""
                if len(config_str) > max_config_size:
                    raise AppError(
                        "CONFIG_TOO_LARGE",
                        f"Exercise config in '{s.get('logical_id')}' exceeds {max_config_size} chars",
                        422,
                    )
                # MCQ must have non-empty correct answer list
                if ex_type == "multiple_choice":
                    correct = config.get("correct", [])
                    if not correct:
                        raise AppError(
                            "MCQ_NO_CORRECT_ANSWER",
                            f"MCQ exercise in '{s.get('logical_id')}' must have non-empty correct answer list",
                            422,
                        )

        # 11c. Reject empty manifests (no content to install)
        if not skills and not templates:
            raise AppError(
                "EMPTY_MANIFEST",
                "Manifest must contain at least one skill or template",
                422,
            )

        zf.close()

        # 12. Create pack + release

        svc = SkillPackService(self.db)
        pack_name = pack_meta["name"]
        version = manifest.get("version", "1.0.0")

        # 12a. Validate version format (same semver regex as publish_release)
        import re as _re

        if not _re.match(r"^\d+\.\d+\.\d+(-[a-zA-Z0-9]+(\.[a-zA-Z0-9]+)*)?$", version):
            raise AppError(
                "INVALID_VERSION",
                f"Version '{version}' must be in semver format X.Y.Z",
                422,
            )

        pack = await svc.create_pack(
            org_id=org_id,
            created_by=imported_by,
            name=pack_name,
            description=pack_meta.get("summary", ""),
            summary=pack_meta.get("summary"),
            visibility=PackVisibility.PRIVATE.value,
            difficulty=pack_meta.get("metadata", {}).get("difficulty"),
            estimated_minutes=pack_meta.get("metadata", {}).get("estimated_minutes"),
            learning_outcomes=pack_meta.get("metadata", {}).get("learning_outcomes", []),
            scenario_tags=pack_meta.get("metadata", {}).get("scenario_tags", []),
            tool_tags=pack_meta.get("metadata", {}).get("tool_tags", []),
            capability_tags=pack_meta.get("metadata", {}).get("capability_tags", []),
            provenance=pack_meta.get("provenance", {}),
        )

        # Create release directly from the manifest
        canonical = json.dumps(manifest, sort_keys=True, ensure_ascii=True)
        checksum = hashlib.sha256(canonical.encode()).hexdigest()

        release = SkillPackRelease(
            pack_id=pack.id,
            version=version,
            manifest=manifest,
            changelog="Imported from archive",
            checksum=checksum,
            component_count=len(skills) + len(templates),
            released_by=imported_by,
        )
        self.db.add(release)
        pack.status = PackStatus.PUBLISHED
        await self.db.flush()
        await self.db.refresh(pack)
        await self.db.refresh(release)

        log.info(
            "pack_imported",
            org_id=org_id,
            pack_id=pack.id,
            version=version,
            skills=len(skills),
            templates=len(templates),
        )
        return pack, release
