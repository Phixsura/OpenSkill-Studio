"""Pack import — validate and import a zip bundle into an organization."""

import hashlib
import io
import json
import zipfile

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import AppError
from app.models.skill_pack import PackStatus, PackVisibility, SkillPack, SkillPackRelease
from app.schemas.project import VALID_PROJECT_TYPES
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
            raise AppError(
                "TOO_MANY_FILES", f"Archive contains more than {MAX_FILE_COUNT} files", 422
            )

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
            raise AppError(
                "INVALID_MANIFEST", "Archive must contain manifest file openskill-pack.json", 422
            )

        try:
            manifest_bytes = zf.read("openskill-pack.json")
            manifest = json.loads(manifest_bytes)
        except (json.JSONDecodeError, KeyError, ValueError) as exc:
            # ValueError (not just JSONDecodeError): a JSON integer literal
            # longer than CPython's 4300-digit int-string limit raises a bare
            # ValueError from json.loads, NOT a JSONDecodeError — the narrower
            # except let it escape to a 500 (R70). RecursionError too: a
            # deeply nested manifest blows the C parser's recursion guard.
            log.warning("manifest_parse_failed", error=str(exc)[:200])
            raise AppError(
                "INVALID_MANIFEST",
                "Manifest file openskill-pack.json is not valid JSON or missing required fields",
                422,
            ) from exc
        except RecursionError:
            raise AppError(
                "INVALID_MANIFEST",
                "Manifest JSON is nested too deeply",
                422,
            ) from None

        # R92e: valid JSON whose TOP LEVEL is not an object (a bare list / string
        # / int / null / bool) parsed fine, then every downstream manifest.get()
        # / max_json_depth walk did `.get` on it → AttributeError 500. Require an
        # object here so the rest of validation can assume dict access.
        if not isinstance(manifest, dict):
            raise AppError(
                "INVALID_MANIFEST",
                "Manifest openskill-pack.json must be a JSON object",
                422,
            )

        # 6b0. Depth cap BEFORE the canonical dumps below: json.loads parses
        # ~900 levels while the recursive json.dumps (and every later
        # serializer — pydantic response echo of provenance, release
        # manifest reads) dies far shallower. A deep manifest must be a
        # clean 422 here, not a RecursionError 500 at the dumps call.
        from app.schemas.base import max_json_depth

        if max_json_depth(manifest) > 64:
            raise AppError(
                "INVALID_MANIFEST",
                "Manifest JSON is nested deeper than 64 levels",
                422,
            )

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

        # 6c. NUL scan: json.loads materializes a valid-JSON \u0000 escape into
        # a real NUL, which Postgres rejects in a JSONB/text column (22P05) as
        # an UntranslatableCharacterError → DBAPIError (not ValueError) → 500.
        # Every other JSONB write path screens for this; the import path did
        # not. Iterative walk (recursion-free — the manifest can nest deep).
        # R86: also reject non-finite floats in the SAME walk. json.loads
        # accepts the bare tokens NaN/Infinity/-Infinity and yields real
        # float('nan')/float('inf'); the default JSONB serializer re-emits them
        # verbatim for Postgres to reject with 22P02 (DBAPIError → 500) at the
        # manifest insert — parity with every other JSONB write surface, all of
        # which screen non-finite (reject_nonfinite_json). bool is an int, never
        # a float, so it needs no special-case.
        import math as _math

        _stack = [manifest]
        while _stack:
            _cur = _stack.pop()
            if isinstance(_cur, str):
                if "\x00" in _cur:
                    raise AppError(
                        "INVALID_MANIFEST",
                        "Manifest contains NUL characters that are not allowed",
                        422,
                    )
            elif isinstance(_cur, float):
                if not _math.isfinite(_cur):
                    raise AppError(
                        "INVALID_MANIFEST",
                        "Manifest contains NaN or Infinity values that are not allowed",
                        422,
                    )
            elif isinstance(_cur, dict):
                _stack.extend(_cur.keys())
                _stack.extend(_cur.values())
            elif isinstance(_cur, list):
                _stack.extend(_cur)

        # 8. Validate structure — the manifest is untrusted JSON, so every
        # container accessed with .get()/len()/iteration must be TYPE-CHECKED
        # first. A wrong-typed value (pack as a list, skills as strings, an
        # int name) would otherwise AttributeError/TypeError into a 500 deep
        # in create_pack instead of a clean 422 here.
        pack_meta = manifest.get("pack")
        if not isinstance(pack_meta, dict):
            raise AppError("INVALID_MANIFEST", "Manifest 'pack' must be an object", 422)
        skills = manifest.get("skills", [])
        templates = manifest.get("project_templates", [])
        if not isinstance(skills, list) or not isinstance(templates, list):
            raise AppError(
                "INVALID_MANIFEST", "Manifest 'skills'/'project_templates' must be arrays", 422
            )
        if any(not isinstance(s, dict) for s in skills) or any(
            not isinstance(t, dict) for t in templates
        ):
            raise AppError("INVALID_MANIFEST", "Each skill/template entry must be an object", 422)

        pack_name = pack_meta.get("name")
        if not pack_name or not isinstance(pack_name, str):
            raise AppError("INVALID_MANIFEST", "Manifest pack.name is required", 422)
        # Length-cap manifest strings that flow into capped VARCHAR columns —
        # create_pack writes them verbatim (only slug is truncated), so an
        # over-length name/summary → StringDataRightTruncation 500. Mirror the
        # publish-side bounds.
        if len(pack_name) > 200:
            raise AppError("INVALID_MANIFEST", "pack.name must be 200 characters or less", 422)
        _summary = pack_meta.get("summary")
        if _summary is not None and (not isinstance(_summary, str) or len(_summary) > 500):
            raise AppError("INVALID_MANIFEST", "pack.summary must be a string ≤500 chars", 422)
        _difficulty = pack_meta.get("metadata", {})
        _difficulty = _difficulty.get("difficulty") if isinstance(_difficulty, dict) else None
        if _difficulty is not None and (not isinstance(_difficulty, str) or len(_difficulty) > 20):
            raise AppError("INVALID_MANIFEST", "pack.metadata.difficulty invalid", 422)

        # 8b. Per-entry structural typing. Everything below (uniqueness sets,
        # Kahn's algorithm, size caps, create_pack kwargs) assumes hashable
        # string ids, list-of-dict exercises, string content, and dict
        # configs. Untrusted JSON violating any of those turned into
        # TypeError/AttributeError 500s (unhashable logical_id, exercises as
        # a string, int learning_content, string exercise config) — and an
        # int logical_id sailed through to a 201 with a non-string id in the
        # published manifest. Live-confirmed (R65): 10 hostile manifests →
        # 10 distinct 500s before this gate.
        for s in skills:
            lid = s.get("logical_id")
            if not isinstance(lid, str) or not lid or len(lid) > 200:
                raise AppError(
                    "INVALID_MANIFEST",
                    "Every skill logical_id must be a non-empty string (max 200 chars)",
                    422,
                )
            # R89: install (installation.py) reads skill_def["name"] with a hard
            # subscript — a manifest skill missing "name" imported fine (only
            # logical_id was checked) then KeyError-500'd every install. Require
            # a non-empty name <=200 (the Skill.name VARCHAR bound) here.
            _s_name = s.get("name")
            if not isinstance(_s_name, str) or not _s_name.strip() or len(_s_name) > 200:
                raise AppError(
                    "INVALID_MANIFEST",
                    f"Skill '{lid}' name must be a non-empty string (max 200 chars)",
                    422,
                )
            prereqs = s.get("prerequisites", [])
            if not isinstance(prereqs, list) or any(not isinstance(p, str) for p in prereqs):
                raise AppError(
                    "INVALID_MANIFEST",
                    f"Skill '{lid}' prerequisites must be a list of strings",
                    422,
                )
            exercises = s.get("exercises", [])
            if not isinstance(exercises, list) or any(not isinstance(ex, dict) for ex in exercises):
                raise AppError(
                    "INVALID_MANIFEST",
                    f"Skill '{lid}' exercises must be a list of objects",
                    422,
                )
            for ex in exercises:
                ex_lid = ex.get("logical_id")
                # 251, not 200: the platform's own export composes exercise
                # logical_ids as f"{skill.slug}/{title_slug[:50]}" (skill_pack.py)
                # — slug is legitimately up to 200 chars, so the composed id
                # reaches 200+1+50. A 200 cap rejected the platform's own
                # export→import roundtrip for long-slugged skills (R78).
                if ex_lid is not None and (not isinstance(ex_lid, str) or len(ex_lid) > 251):
                    raise AppError(
                        "INVALID_MANIFEST",
                        f"Exercise logical_id in skill '{lid}' must be a string (max 251 chars)",
                        422,
                    )
                # R89: install reads ex_def["title"] with a hard subscript —
                # a missing/oversized title KeyError/StringTruncation-500s the
                # install. Exercise.title is VARCHAR(200).
                _ex_title = ex.get("title")
                if not isinstance(_ex_title, str) or not _ex_title.strip() or len(_ex_title) > 200:
                    raise AppError(
                        "INVALID_MANIFEST",
                        f"Exercise title in skill '{lid}' must be a non-empty string (max 200 chars)",
                        422,
                    )
                if not isinstance(ex.get("config", {}), dict):
                    raise AppError(
                        "INVALID_MANIFEST",
                        f"Exercise config in skill '{lid}' must be an object",
                        422,
                    )
                # R86: max_score / sort_order flow verbatim into the Exercise
                # INTEGER columns at INSTALL time (installation.py) with only a
                # .get(..., default) — no type gate. A string/float/list value
                # imports fine (reaches PUBLISHED) then crashes every install
                # with a 500 (DataError at the integer column write). Type-gate
                # here so a malformed manifest is a clean 422 at import, never a
                # latent install-time 500. bool is an int subclass — exclude it
                # so a JSON true/false is not silently coerced to 1/0.
                _ms = ex.get("max_score")
                if _ms is not None and (
                    not isinstance(_ms, int) or isinstance(_ms, bool) or not (1 <= _ms <= 10000)
                ):
                    raise AppError(
                        "INVALID_MANIFEST",
                        f"Exercise max_score in skill '{lid}' must be an integer (1-10000)",
                        422,
                    )
                _so = ex.get("sort_order")
                if _so is not None and (not isinstance(_so, int) or isinstance(_so, bool)):
                    raise AppError(
                        "INVALID_MANIFEST",
                        f"Exercise sort_order in skill '{lid}' must be an integer",
                        422,
                    )
            # Skill sort_order lands in the Skill INTEGER column the same way.
            _s_so = s.get("sort_order")
            if _s_so is not None and (not isinstance(_s_so, int) or isinstance(_s_so, bool)):
                raise AppError(
                    "INVALID_MANIFEST",
                    f"Skill '{lid}' sort_order must be an integer",
                    422,
                )
            # R89f: estimated_minutes flows verbatim into Skill.estimated_minutes
            # (INTEGER). A non-int (e.g. "soon") is NOT a NUL/text fault — asyncpg
            # raises a client-side bind DataError with NO sqlstate at install, so
            # the R88 backstop can't catch it and every install 500s. Gate here
            # like the adjacent sort_order/max_score checks.
            _s_est = s.get("estimated_minutes")
            if _s_est is not None and (
                not isinstance(_s_est, int) or isinstance(_s_est, bool) or not (0 <= _s_est <= 9999)
            ):
                raise AppError(
                    "INVALID_MANIFEST",
                    f"Skill '{lid}' estimated_minutes must be an integer (0-9999)",
                    422,
                )
            lc = s.get("learning_content", "")
            # `is not None`, not truthiness (R78): falsy non-strings (0,
            # False, [], {}) skipped the isinstance gate via `lc and ...`
            # and 500'd downstream at the Text-column write.
            if lc is not None and not isinstance(lc, str):
                raise AppError(
                    "INVALID_MANIFEST",
                    f"Skill '{lid}' learning_content must be a string",
                    422,
                )
        for t in templates:
            t_lid = t.get("logical_id")
            if not isinstance(t_lid, str) or not t_lid or len(t_lid) > 200:
                raise AppError(
                    "INVALID_MANIFEST",
                    "Every template logical_id must be a non-empty string (max 200 chars)",
                    422,
                )
            # R89: install reads tmpl_def["name"] with a hard subscript — a
            # template missing "name" imported fine then KeyError-500'd every
            # install. ProjectTemplate.name is VARCHAR(200).
            _t_name = t.get("name")
            if not isinstance(_t_name, str) or not _t_name.strip() or len(_t_name) > 200:
                raise AppError(
                    "INVALID_MANIFEST",
                    f"Template '{t_lid}' name must be a non-empty string (max 200 chars)",
                    422,
                )
            # R89c: project_type flows verbatim into ProjectTemplate.project_type
            # which is VARCHAR(20). Import accepted any string, so a >20-char
            # value (or a bogus one) 500'd at install (StringDataRightTruncation).
            # Match the API schema: only the known project types are allowed.
            _t_ptype = t.get("project_type", "general")
            if _t_ptype is not None and _t_ptype not in VALID_PROJECT_TYPES:
                raise AppError(
                    "INVALID_MANIFEST",
                    f"Template '{t_lid}' project_type must be one of: "
                    f"{', '.join(sorted(VALID_PROJECT_TYPES))}",
                    422,
                )
            # R89f: max_score / suggested_minutes flow verbatim into the
            # ProjectTemplate INTEGER columns at install. A non-int value is a
            # client-side bind DataError (no sqlstate) that the backstop misses,
            # so the pack imports PUBLISHED then 500s every install. Gate both.
            _t_ms = t.get("max_score")
            if _t_ms is not None and (
                not isinstance(_t_ms, int) or isinstance(_t_ms, bool) or not (1 <= _t_ms <= 10000)
            ):
                raise AppError(
                    "INVALID_MANIFEST",
                    f"Template '{t_lid}' max_score must be an integer (1-10000)",
                    422,
                )
            _t_sm = t.get("suggested_minutes")
            if _t_sm is not None and (
                not isinstance(_t_sm, int) or isinstance(_t_sm, bool) or not (0 <= _t_sm <= 100000)
            ):
                raise AppError(
                    "INVALID_MANIFEST",
                    f"Template '{t_lid}' suggested_minutes must be an integer (0-100000)",
                    422,
                )

        # 8c. pack.metadata fields flow verbatim into create_pack kwargs and
        # then into typed columns/JSONB — type-gate them like the API schemas
        # (CreatePackRequest) do, or a string estimated_minutes / dict
        # learning_outcomes / int tag list 500s at flush.
        _meta = pack_meta.get("metadata", {})
        if not isinstance(_meta, dict):
            raise AppError("INVALID_MANIFEST", "pack.metadata must be an object", 422)
        _est = _meta.get("estimated_minutes")
        if _est is not None and (
            not isinstance(_est, int) or isinstance(_est, bool) or not (0 <= _est <= 9999)
        ):
            raise AppError(
                "INVALID_MANIFEST",
                "pack.metadata.estimated_minutes must be an integer (0-9999)",
                422,
            )
        _outcomes = _meta.get("learning_outcomes", [])
        if not isinstance(_outcomes, list) or any(
            not isinstance(o, str) or len(o) > 500 for o in _outcomes
        ):
            raise AppError(
                "INVALID_MANIFEST",
                "pack.metadata.learning_outcomes must be a list of strings (max 500 chars each)",
                422,
            )
        for _tag_field in ("scenario_tags", "tool_tags", "capability_tags"):
            _tags = _meta.get(_tag_field, [])
            if not isinstance(_tags, list) or any(
                not isinstance(x, str) or len(x) > 100 for x in _tags
            ):
                raise AppError(
                    "INVALID_MANIFEST",
                    f"pack.metadata.{_tag_field} must be a list of strings",
                    422,
                )
        _prov = pack_meta.get("provenance", {})
        if _prov is not None and not isinstance(_prov, dict):
            raise AppError("INVALID_MANIFEST", "pack.provenance must be an object", 422)

        # 8a. Enforce component count limits (same as publish_release)
        from app.services.skill_pack import MAX_SKILLS_PER_PACK, MAX_TEMPLATES_PER_PACK

        if len(skills) > MAX_SKILLS_PER_PACK:
            raise AppError(
                "TOO_MANY_SKILLS",
                f"Manifest contains {len(skills)} skills (max {MAX_SKILLS_PER_PACK})",
                422,
            )
        if len(templates) > MAX_TEMPLATES_PER_PACK:
            raise AppError(
                "TOO_MANY_TEMPLATES",
                f"Manifest contains {len(templates)} templates (max {MAX_TEMPLATES_PER_PACK})",
                422,
            )

        # 9. Check logical_id uniqueness (skills + templates + exercises)
        all_logical_ids: list[str] = []
        for s in skills:
            lid = s.get("logical_id")
            if not lid:
                raise AppError("INVALID_MANIFEST", "Every skill must have a logical_id", 422)
            all_logical_ids.append(lid)
            # Also collect exercise logical_ids
            for ex in s.get("exercises", []):
                ex_lid = ex.get("logical_id")
                if ex_lid:
                    all_logical_ids.append(ex_lid)
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

        # 10a. Validate category references (R86). A skill's
        # category_logical_id is resolved against the manifest's categories[]
        # at INSTALL time; installation.py raises CATEGORY_NOT_FOUND 422 when a
        # skill points at a category the manifest never defined. Import did not
        # check this, so a dangling reference imported fine and reached
        # PUBLISHED — then EVERY install (own org and any consumer) failed at
        # that gate, an unrecoverable published-but-uninstallable pack. Validate
        # here so the dangling reference is a clean 422 at import time. categories
        # is untrusted JSON — type-gate it (like skills/templates) before use.
        categories = manifest.get("categories", [])
        if not isinstance(categories, list) or any(not isinstance(cat, dict) for cat in categories):
            raise AppError(
                "INVALID_MANIFEST", "Manifest 'categories' must be a list of objects", 422
            )
        category_lids: set[str] = set()
        for cat in categories:
            c_lid = cat.get("logical_id")
            if not isinstance(c_lid, str) or not c_lid or len(c_lid) > 200:
                raise AppError(
                    "INVALID_MANIFEST",
                    "Every category logical_id must be a non-empty string (max 200 chars)",
                    422,
                )
            # R89c: SkillCategory.name and .slug are VARCHAR(100), not 200 —
            # install (installation.py) writes cat_def["name"]/["slug"] verbatim,
            # so a 100<len<=200 value passed import then 500'd at install
            # (StringDataRightTruncation). Cap at the real column bound.
            for _field in ("name", "slug"):
                _v = cat.get(_field)
                if not isinstance(_v, str) or not _v or len(_v) > 100:
                    raise AppError(
                        "INVALID_MANIFEST",
                        f"Category '{c_lid}' {_field} must be a non-empty string (max 100 chars)",
                        422,
                    )
            category_lids.add(c_lid)
        for s in skills:
            cat_ref = s.get("category_logical_id")
            if cat_ref is not None and cat_ref not in category_lids:
                raise AppError(
                    "INVALID_MANIFEST",
                    f"Skill '{s['logical_id']}' references category '{cat_ref}' "
                    "not defined in manifest categories",
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

        # 12a. Validate version format (same semver regex as publish_release).
        # Length-cap FIRST: the bare regex has no length bound, so a
        # 10k-char version passes it and then overflows the version VARCHAR
        # (publish enforces len<=50) — cap to match.
        import re as _re

        if not isinstance(version, str) or len(version) > 50:
            raise AppError(
                "INVALID_VERSION", "Version must be a string of 50 characters or less", 422
            )
        if not _re.match(r"^\d+\.\d+\.\d+(-[a-zA-Z0-9]+(\.[a-zA-Z0-9]+)*)?$", version):
            raise AppError(
                "INVALID_VERSION",
                f"Version '{version}' must be in semver format X.Y.Z",
                422,
            )

        # All metadata reads go through the TYPE-GATED _meta/_prov from 8c —
        # a non-dict pack.metadata must not AttributeError here.
        pack = await svc.create_pack(
            org_id=org_id,
            created_by=imported_by,
            name=pack_name,
            description=pack_meta.get("summary", ""),
            summary=pack_meta.get("summary"),
            visibility=PackVisibility.PRIVATE.value,
            difficulty=_difficulty,
            estimated_minutes=_est,
            learning_outcomes=_outcomes,
            scenario_tags=_meta.get("scenario_tags", []),
            tool_tags=_meta.get("tool_tags", []),
            capability_tags=_meta.get("capability_tags", []),
            provenance=_prov if _prov is not None else {},
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
