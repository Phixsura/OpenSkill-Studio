"""Public pack registry — search, filter, browse published packs."""

import hashlib
from datetime import UTC, datetime

import structlog
from sqlalchemy import String, cast, func, literal_column, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import cache_get, cache_set
from app.exceptions import AppError
from app.models.skill_pack import (
    PackStatus,
    PackVisibility,
    SkillPack,
    SkillPackRelease,
)

log = structlog.get_logger()


def _compute_badges(pack: "SkillPack", now: datetime, thirty_days_ago: datetime) -> list[str]:
    """Derive badge list from pack state. Pure function, no DB."""
    badges: list[str] = []
    if pack.install_count >= 10:
        badges.append("Popular")
    if pack.created_at and pack.created_at >= thirty_days_ago:
        badges.append("New")
    return badges


def _parse_semver(version: str) -> tuple[int, int, int, str]:
    """Parse 'X.Y.Z' or 'X.Y.Z-prerelease' into a comparable tuple.

    Pre-release versions sort BEFORE the release (1.0.0-alpha < 1.0.0).
    """
    base, _, prerelease = version.partition("-")
    parts = base.split(".")
    pre_key = prerelease if prerelease else "~"  # '~' > all ASCII letters
    return (int(parts[0]), int(parts[1]), int(parts[2]), pre_key)


class RegistryService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def search_packs(
        self,
        search: str | None = None,
        scenario: str | None = None,
        tool: str | None = None,
        difficulty: str | None = None,
        category: str | None = None,
        sort: str = "newest",
        page: int = 1,
        per_page: int = 20,
        min_rating: float | None = None,
        max_results: int | None = None,
    ) -> tuple[list[SkillPack], int]:
        """Search public, published packs.

        Uses PostgreSQL full-text search (to_tsvector + websearch_to_tsquery)
        with an ILIKE fallback so substring and random-token searches still work.
        Results are cached in Redis for 5 minutes.

        Supports simultaneous faceted filters: scenario, tool, difficulty,
        category, min_rating. max_results caps the total returned (default 50).
        """
        effective_per_page = min(per_page, max_results) if max_results else per_page
        # ── Check cache ──
        # Canonical JSON key, not a raw ':'-join: a ':'-join collides when a
        # user-controlled value itself contains ':' (search='a:b' vs
        # scenario='b' → same string), serving one query's results for
        # another. JSON preserves field boundaries. (Mirrors
        # workflow_registry._cache_key.)
        import json as _json

        cache_key_src = _json.dumps(
            {
                "search": search, "scenario": scenario, "tool": tool,
                "difficulty": difficulty, "category": category, "sort": sort,
                "page": page, "per_page": effective_per_page,
                "min_rating": min_rating, "max_results": max_results,
            },
            sort_keys=True, default=str,
        )
        cache_key = f"registry:search:{hashlib.sha256(cache_key_src.encode()).hexdigest()}"
        cached = await cache_get(cache_key)
        if cached is not None:
            # Re-hydrate from cache: fetch packs by id list
            pack_ids = cached.get("ids", [])
            if pack_ids:
                # Re-apply access-control filters on cache hit to prevent
                # serving archived/private/rejected packs from stale cache
                result = await self.db.execute(
                    select(SkillPack).where(
                        SkillPack.id.in_(pack_ids),
                        SkillPack.status == PackStatus.PUBLISHED,
                        SkillPack.visibility == PackVisibility.PUBLIC,
                        or_(
                            SkillPack.review_status.is_(None),
                            SkillPack.review_status == "approved",
                        ),
                    )
                )
                packs_by_id = {p.id: p for p in result.scalars().all()}
                filtered = [packs_by_id[pid] for pid in pack_ids if pid in packs_by_id]
                # Return the cached catalog TOTAL (across all pages), not the
                # page length — otherwise has_more computes False and
                # pagination dead-ends at page 1 for the cache TTL.
                return filtered, cached.get("total", len(filtered))
            return [], cached.get("total", 0)

        # ── Build query ──
        base = select(SkillPack).where(
            SkillPack.visibility == PackVisibility.PUBLIC,
            SkillPack.status == PackStatus.PUBLISHED,
            or_(
                SkillPack.review_status.is_(None),
                SkillPack.review_status == "approved",
            ),
        )

        _ilike_fallback = None  # set if FTS is used, for fallback on DB error

        if search and search.strip():
            # Full-text search on the STORED search_tsv column (computed once
            # at write time, migration b9ca3e445203) OR-combined with ILIKE
            # for substring / random-token matches that word-based FTS misses.
            #
            # Plan note (verified with EXPLAIN): because the tsquery match is
            # OR-ed with unanchored ILIKEs, Postgres CANNOT use the GIN index
            # ix_skill_packs_search_tsv for this predicate — the whole OR is
            # evaluated as a per-row Filter. The scan is instead bounded by a
            # Bitmap Index Scan on ix_packs_visibility_status (public +
            # published only), so cost grows with the size of the published
            # catalog, not the whole table. The GIN index only accelerates a
            # future FTS-only path; acceptable at Phase 1 catalog sizes.
            search_vector = literal_column("skill_packs.search_tsv")
            # Escape LIKE wildcards to prevent CPU-intensive pattern matching
            escaped = search.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
            term = f"%{escaped}%"
            ilike_cond = or_(
                SkillPack.name.ilike(term),
                SkillPack.summary.ilike(term),
                SkillPack.description.ilike(term),
                cast(SkillPack.scenario_tags, String).ilike(term),
                cast(SkillPack.tool_tags, String).ilike(term),
                cast(SkillPack.capability_tags, String).ilike(term),
            )
            # Combine FTS and ILIKE — FTS failure is caught at query execution time
            fts_cond = search_vector.op("@@")(
                func.websearch_to_tsquery("simple", search)
            )
            base = base.where(or_(fts_cond, ilike_cond))
            # Store ILIKE-only fallback for use if FTS fails at execution time
            _ilike_fallback = ilike_cond

        if scenario:
            base = base.where(SkillPack.scenario_tags.contains([scenario]))

        if tool:
            base = base.where(SkillPack.tool_tags.contains([tool]))

        if difficulty:
            base = base.where(SkillPack.difficulty == difficulty)

        if category:
            from app.models.pack_category import PackCategory, PackCategoryAssignment

            base = base.where(
                SkillPack.id.in_(
                    select(PackCategoryAssignment.pack_id).join(
                        PackCategory, PackCategory.id == PackCategoryAssignment.category_id
                    ).where(PackCategory.slug == category)
                )
            )

        if min_rating is not None:
            base = base.where(SkillPack.average_rating >= min_rating)

        # Sort
        if sort in ("most_installed", "popular"):
            base = base.order_by(SkillPack.install_count.desc())
        elif sort == "recently_updated":
            base = base.order_by(SkillPack.updated_at.desc())
        elif sort == "name":
            base = base.order_by(SkillPack.name.asc())
        else:  # newest
            base = base.order_by(SkillPack.created_at.desc())

        try:
            total_r = await self.db.execute(select(func.count()).select_from(base.subquery()))
            total = total_r.scalar_one()
            offset = (page - 1) * effective_per_page
            result = await self.db.execute(base.offset(offset).limit(effective_per_page))
            packs = list(result.scalars().all())
        except Exception:
            if _ilike_fallback is not None:
                # FTS query failed (bad search syntax) — rebuild with ILIKE only
                log.warning("fts_query_failed_fallback_to_ilike", search=search)
                base = select(SkillPack).where(
                    SkillPack.visibility == PackVisibility.PUBLIC,
                    SkillPack.status == PackStatus.PUBLISHED,
                    or_(SkillPack.review_status.is_(None), SkillPack.review_status == "approved"),
                    _ilike_fallback,
                ).order_by(SkillPack.created_at.desc())
                total_r = await self.db.execute(select(func.count()).select_from(base.subquery()))
                total = total_r.scalar_one()
                offset = (page - 1) * effective_per_page
                result = await self.db.execute(base.offset(offset).limit(effective_per_page))
                packs = list(result.scalars().all())
            else:
                raise

        # ── Populate cache ──
        await cache_set(cache_key, {"ids": [p.id for p in packs], "total": total}, ttl=300)

        # ── Compute and persist badges ──
        from datetime import timedelta

        now = datetime.now(UTC)
        thirty_days_ago = now - timedelta(days=30)
        modified: list[SkillPack] = []
        for pack in packs:
            badges = _compute_badges(pack, now, thirty_days_ago)
            if badges != (pack.badges or []):
                pack.badges = badges
                modified.append(pack)
        # Flush any badge updates without committing (caller controls commit)
        if modified:
            await self.db.flush()
            # Refresh modified packs so server-side onupdate columns
            # (e.g. updated_at) are eagerly loaded before Pydantic serialisation.
            for pack in modified:
                await self.db.refresh(pack)

        return packs, total

    async def get_public_pack(self, pack_id: str) -> SkillPack:
        """Get a public or unlisted pack by ID. Cached for 1 minute."""
        pack = await self.db.get(SkillPack, pack_id)
        if pack is None:
            raise AppError("PACK_NOT_FOUND", "Pack not found", 404)
        if pack.status != PackStatus.PUBLISHED:
            raise AppError("PACK_NOT_FOUND", "Pack not found", 404)
        if pack.visibility == PackVisibility.PRIVATE:
            raise AppError("PACK_NOT_FOUND", "Pack not found", 404)
        # A PUBLIC pack whose review regressed to rejected/pending must 404
        # by ID too — the list/search path already filters on review_status
        # (NULL or approved), so serving it by direct id was an inconsistency
        # that surfaced rejected content. Mirrors workflow_registry.
        if pack.visibility == PackVisibility.PUBLIC and pack.review_status not in (
            None,
            "approved",
        ):
            raise AppError("PACK_NOT_FOUND", "Pack not found", 404)
        return pack

    async def get_public_releases(self, pack_id: str) -> list[SkillPackRelease]:
        """List releases for a public pack."""
        from sqlalchemy.orm import defer

        await self.get_public_pack(pack_id)  # verify accessible
        result = await self.db.execute(
            select(SkillPackRelease)
            .where(SkillPackRelease.pack_id == pack_id)
            .options(defer(SkillPackRelease.manifest))
        )
        releases = list(result.scalars().all())
        releases.sort(key=lambda r: _parse_semver(r.version), reverse=True)
        return releases

    async def list_categories(self) -> list[dict]:
        """Return pack categories as a tree structure."""
        from app.models.pack_category import PackCategory

        result = await self.db.execute(
            select(PackCategory).order_by(PackCategory.sort_order)
        )
        categories = list(result.scalars().all())

        # Build tree: group children by parent_id
        by_parent: dict[str | None, list[dict]] = {}
        cat_dicts = {}
        for cat in categories:
            d = {
                "id": cat.id,
                "name": cat.name,
                "slug": cat.slug,
                "icon": cat.icon,
                "sort_order": cat.sort_order,
                "children": [],
            }
            cat_dicts[cat.id] = d
            by_parent.setdefault(cat.parent_id, []).append(d)

        # Attach children to parents
        for cat in categories:
            if cat.parent_id and cat.parent_id in cat_dicts:
                cat_dicts[cat.parent_id]["children"].append(cat_dicts[cat.id])

        # Return only root nodes (parent_id is None)
        return by_parent.get(None, [])

    async def compute_quality_score(self, pack: "SkillPack") -> int:
        """Score 0-100 based on content completeness signals."""
        from app.models.skill_pack import SkillPackRelease

        score = 0

        # +10 has description
        if pack.description and len(pack.description.strip()) > 0:
            score += 10

        # +10 has summary
        if pack.summary and len(pack.summary.strip()) > 0:
            score += 10

        # +15 has learning outcomes
        if pack.learning_outcomes and len(pack.learning_outcomes) > 0:
            score += 15

        # +15 has releases
        release_r = await self.db.execute(
            select(func.count()).where(SkillPackRelease.pack_id == pack.id)
        )
        release_count = release_r.scalar_one()
        if release_count > 0:
            score += 15

        # +15 exercise_count > 0 (check via latest release manifest)
        latest_r = await self.db.execute(
            select(SkillPackRelease)
            .where(SkillPackRelease.pack_id == pack.id)
            .order_by(SkillPackRelease.released_at.desc())
            .limit(1)
        )
        latest = latest_r.scalar_one_or_none()
        if latest and latest.manifest:
            total_exercises = sum(
                len(s.get("exercises", []))
                for s in latest.manifest.get("skills", [])
            )
            if total_exercises > 0:
                score += 15

            # +10 has rubric templates
            templates = latest.manifest.get("project_templates", [])
            has_rubric = any(
                t.get("rubric") and len(t.get("rubric", [])) > 0
                for t in templates
            )
            if has_rubric:
                score += 10

        # +10 has provenance
        if pack.provenance and len(pack.provenance) > 0:
            score += 10

        # +15 review_count > 0
        if pack.review_count and pack.review_count > 0:
            score += 15

        return score

    async def recompute_pack_badges(self, pack_id: str) -> None:
        """Recompute and persist badges for a single pack."""
        from datetime import timedelta

        pack = await self.db.get(SkillPack, pack_id)
        if pack is None:
            return
        now = datetime.now(UTC)
        thirty_days_ago = now - timedelta(days=30)
        badges = _compute_badges(pack, now, thirty_days_ago)
        if badges != (pack.badges or []):
            pack.badges = badges
            await self.db.flush()

    async def get_installed_by(self, pack_id: str) -> dict:
        """Return anonymized count of organizations that have installed this pack."""
        from app.models.skill_pack import InstallStatus, SkillPackInstallation

        await self.get_public_pack(pack_id)  # verify accessible

        result = await self.db.execute(
            select(func.count(SkillPackInstallation.org_id.distinct())).where(
                SkillPackInstallation.pack_id == pack_id,
                SkillPackInstallation.status != InstallStatus.REMOVED,
            )
        )
        count = result.scalar_one()
        return {
            "pack_id": pack_id,
            "organization_count": count,
            "message": f"{count} organization{'s' if count != 1 else ''} use{'s' if count == 1 else ''} this pack",
        }

    async def get_pack_preview(self, pack_id: str) -> dict:
        """Build a curriculum preview from the latest release manifest."""
        await self.get_public_pack(pack_id)  # verify accessible

        result = await self.db.execute(
            select(SkillPackRelease)
            .where(SkillPackRelease.pack_id == pack_id)
            .order_by(SkillPackRelease.released_at.desc())
            .limit(1)
        )
        release = result.scalar_one_or_none()
        if release is None:
            raise AppError("NO_RELEASES", "This pack has no releases yet", 404)

        manifest = release.manifest or {}

        # Extract skills. Every entry from the import path is untrusted JSON —
        # a non-dict skill, or a non-list exercises value, must be skipped, not
        # crash the anon preview with AttributeError/TypeError (R87 hardening,
        # same class as the R86e rubric 500).
        # R92c: the manifest is untrusted JSON (import path). PackPreviewResponse
        # types name/description/difficulty/title as str|None, so a NON-string
        # value (e.g. an int description) that reached the response model raised
        # a pydantic ValidationError at serialization — an anon-registry preview
        # 500 with no sqlstate (not caught by the DBAPIError backstop). R86e/R87d
        # hardened the rubric SHAPE; this hardens the string FIELD TYPES too.
        # Coerce: a required str field → "" when not a str, optional → None.
        def _s(v):
            return v if isinstance(v, str) else None

        def _req_s(v):
            return v if isinstance(v, str) else ""

        raw_skills = manifest.get("skills", [])
        skills = []
        total_exercises = 0
        for s in raw_skills:
            if not isinstance(s, dict):
                continue
            exercises = s.get("exercises")
            if not isinstance(exercises, list):
                exercises = []
            total_exercises += len(exercises)
            prereqs = s.get("prerequisites", [])
            if not isinstance(prereqs, list):
                prereqs = []
            skills.append({
                "name": _req_s(s.get("name")),
                "description": _s(s.get("description")),
                "difficulty": _s(s.get("difficulty")),
                "exercise_count": len(exercises),
                "exercises": [
                    {"title": _req_s(e.get("title"))} for e in exercises if isinstance(e, dict)
                ],
                # prerequisites is list[str] in the schema — drop non-str entries.
                "prerequisites": [p for p in prereqs if isinstance(p, str)],
            })

        # Extract templates
        raw_templates = manifest.get("project_templates", [])
        templates = []
        for t in raw_templates:
            # A template entry from the import path is untrusted JSON — it may
            # not even be a dict. Skip anything that is not a dict rather than
            # AttributeError on t.get (R87 fix-of-fix on R86e).
            if not isinstance(t, dict):
                continue
            # ProjectTemplate.rubric is a LIST of {criterion, max_score} dicts
            # (models/project.py:425, JSONB list), and the published manifest
            # stores it verbatim (skill_pack.py). Treating it as a dict with a
            # "criteria" key raised AttributeError ('list' has no .get) →
            # anon-registry preview 500 for ANY pack whose template has a rubric
            # (R86e). Count only when the shape is genuinely sized: a legacy
            # dict form {criteria: [...]} counts its list, but criteria of a
            # non-list type (int/None/str via the untrusted import path) must
            # NOT reach len() — that re-introduced the 500 (R87). Default 0.
            rubric = t.get("rubric")
            if isinstance(rubric, list):
                criteria_count = len(rubric)
            elif isinstance(rubric, dict) and isinstance(rubric.get("criteria"), list):
                criteria_count = len(rubric["criteria"])
            else:
                criteria_count = 0
            templates.append({
                "name": _req_s(t.get("name")),
                "description": _s(t.get("description")),
                "rubric_criteria_count": criteria_count,
            })

        # Extract categories (skip non-dict entries — untrusted import shape)
        raw_categories = manifest.get("categories", [])
        categories = [
            {"name": _req_s(c.get("name"))}
            for c in raw_categories
            if isinstance(c, dict)
        ]

        return {
            "skills": skills,
            "templates": templates,
            "categories": categories,
            "total_skills": len(skills),
            "total_exercises": total_exercises,
            "total_templates": len(templates),
        }
