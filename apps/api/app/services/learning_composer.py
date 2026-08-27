"""Learning solution composer (ADR-013, Issue #21 Part E).

Composes a DRAFT learning path from reusable Skill Packs via the shared
matching pipeline. Nothing is hidden (R8): budget cuts, waived prerequisites,
and unfillable gaps are all first-class payload rows with reason codes.

The composer NEVER auto-installs packs and NEVER publishes/assigns — a human
confirm materializes a DRAFT LearningPath, and uninstalled packs become
SECTION placeholders (red line: no auto-install).
"""

from datetime import UTC, datetime

import structlog
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import AppError
from app.models.composer import SolutionDraft
from app.models.learning_path import LearningPath, LearningPathItem, PathItemType
from app.models.skill import ContentStatus, ProgressStatus, Skill, SkillProgress
from app.models.skill_pack import (
    InstallStatus,
    PackStatus,
    PackVisibility,
    SkillPack,
    SkillPackInstallation,
)
from app.services.matching import ENGINE_VERSION, MatchingEngine, MatchSpec
from app.services.requirement_profile import RequirementProfileService

log = structlog.get_logger()

DEFAULT_PACK_MINUTES = 60
MAX_PREREQ_DEPTH = 5
# Defensive cap mirroring ck_wfpack_definition_size — the payload is
# server-generated, but prereq expansion could balloon it pathologically
MAX_DRAFT_PAYLOAD_BYTES = 262_144


def check_draft_payload_size(payload: dict) -> None:
    import json

    size = len(json.dumps(payload, ensure_ascii=False, default=str).encode())
    if size > MAX_DRAFT_PAYLOAD_BYTES:
        raise AppError(
            "DRAFT_TOO_LARGE",
            f"Composed draft payload exceeds {MAX_DRAFT_PAYLOAD_BYTES // 1024}KB",
            422,
        )


def _pack_minutes(value: int | None) -> int:
    """0 is a real duration — only None falls back to the default.

    `value or DEFAULT_PACK_MINUTES` silently coerced explicit 0-minute packs
    to 60, inflating budgets and truncation decisions (round-16 LOW).
    """
    return DEFAULT_PACK_MINUTES if value is None else value


class LearningComposerService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Compose ───────────────────────────────────────────

    async def compose(self, org_id: str, profile_id: str, created_by: str) -> SolutionDraft:
        profile_svc = RequirementProfileService(self.db)
        profile = await profile_svc.get_profile(profile_id, org_id)
        if profile.status != "confirmed":
            raise AppError(
                "PROFILE_NOT_CONFIRMED",
                "Requirement profile must be confirmed before composing",
                422,
            )
        requirement = RequirementProfileService.build_match_requirement(profile)

        engine = MatchingEngine(self.db)
        run, results, _ = await engine.run(
            MatchSpec(
                org_id=org_id,
                target_entity_type="skill_pack",
                requirement=requirement,
                context_type=profile.context_type.value,
                requirement_profile_id=profile.id,
                created_by=created_by,
                limit=50,
                record_impressions=False,  # composer-internal — user never sees this list
            )
        )
        ranked_ids = [r.entity_id for r in results if r.rank is not None]

        # Load ranked packs preserving order
        packs_by_id: dict[str, SkillPack] = {}
        if ranked_ids:
            packs_r = await self.db.execute(select(SkillPack).where(SkillPack.id.in_(ranked_ids)))
            packs_by_id = {p.id: p for p in packs_r.scalars().all()}
        ranked_packs = [packs_by_id[pid] for pid in ranked_ids if pid in packs_by_id]

        gaps: list[dict] = []

        # ── Greedy weighted set cover over requested capabilities ──
        wanted_caps = list(
            dict.fromkeys(
                (requirement.get("required_capabilities") or [])
                + (requirement.get("preferred_capabilities") or [])
            )
        )

        # The match ranks by relevance and caps at limit=50, but SET COVER is a
        # coverage problem: a capability whose ONLY eligible pack ranks 51st
        # would be falsely reported NO_CONTENT_AVAILABLE ("content exists but
        # you didn't look"). Backfill ranked_packs with the cheapest eligible
        # pack for each requested capability the ranked window missed, so the
        # greedy loop can always reach real coverage. Ranked packs keep their
        # order (relevance-first); backfill packs append (coverage safety net).
        if wanted_caps:
            covered_by_ranked = {
                cap
                for p in ranked_packs
                for cap in (p.capability_tags or [])
                if cap in set(wanted_caps)
            }
            missing_caps = [c for c in wanted_caps if c not in covered_by_ranked]
            if missing_caps:
                from sqlalchemy import or_

                from app.services.matching.candidates import _pack_eligibility_filter

                have_ids = set(packs_by_id.keys())
                backfill_r = await self.db.execute(
                    select(SkillPack)
                    .where(
                        _pack_eligibility_filter(SkillPack, org_id),
                        SkillPack.status != PackStatus.ARCHIVED,
                        or_(*(SkillPack.capability_tags.contains([c]) for c in missing_caps)),
                    )
                    .order_by(SkillPack.estimated_minutes.asc().nullslast(), SkillPack.id.asc())
                )
                for p in backfill_r.scalars().all():
                    if p.id not in have_ids:
                        ranked_packs.append(p)
                        have_ids.add(p.id)
        selected: list[SkillPack] = []
        if wanted_caps:
            uncovered = set(wanted_caps)
            available = list(ranked_packs)
            while uncovered and available:
                best, best_ratio, best_cover = None, 0.0, set()
                for pack in available:
                    cover = uncovered & set(pack.capability_tags or [])
                    if not cover:
                        continue
                    minutes = _pack_minutes(pack.estimated_minutes)
                    ratio = len(cover) / max(minutes, 1)
                    if ratio > best_ratio:
                        best, best_ratio, best_cover = pack, ratio, cover
                if best is None:
                    break  # no pack covers anything remaining
                selected.append(best)
                available.remove(best)
                uncovered -= best_cover
            for cap in sorted(uncovered):
                gaps.append({"code": "NO_CONTENT_AVAILABLE", "capability": cap})
        else:
            # No capability requirements: top-5 ranked packs
            selected = ranked_packs[:5]

        # ── Prerequisite expansion (cycle-checked, depth-bounded) ──
        ordered_entries, prereq_edges, unresolved_prereqs = await self._expand_prerequisites(
            org_id, selected, profile.user_id
        )
        # Unresolvable prereq slugs are surfaced, never silently dropped (R8)
        for slug in unresolved_prereqs:
            gaps.append({"code": "PREREQ_NOT_FOUND", "slug": slug})

        # ── Budget truncation (required-first is implicit: prereqs sort first) ──
        # Only a HUMAN-entered time_budget may drive hard cuts (R14):
        # build_match_requirement demotes extracted budgets to _soft_time_budget,
        # which is surfaced as an advisory gap instead of truncating items.
        time_budget = requirement.get("time_budget")
        soft_budget = requirement.get("_soft_time_budget")
        if soft_budget is not None and time_budget is None:
            gaps.append(
                {
                    "code": "SOFT_TIME_BUDGET",
                    "minutes": soft_budget,
                    "detail": (
                        "An AI-extracted time budget was not applied — confirm it "
                        "on the requirement profile to enable budget truncation"
                    ),
                }
            )
        total_minutes = 0
        if isinstance(time_budget, int | float) and time_budget > 0:
            budget = int(time_budget)
            running = 0
            for entry in ordered_entries:
                if entry["status"] != "included":
                    continue
                minutes = _pack_minutes(entry["estimated_minutes"])
                if running + minutes > budget:
                    entry["status"] = "cut_for_budget"
                    entry["reason_code"] = "cut_for_budget"
                else:
                    running += minutes
            # Propagate cuts to dependents: an item whose (transitive)
            # prerequisite was cut must be cut too — never materialize a
            # dependent without its required prereq (R8: visible, not silent).
            running = self._propagate_budget_cuts(ordered_entries, prereq_edges)
            total_minutes = running
            # 'Nothing fits' means NO item is included — not running == 0,
            # which a legitimately 0-minute included pack also satisfies
            # (that would emit a contradictory gap alongside included items)
            nothing_included = not any(e["status"] == "included" for e in ordered_entries)
            if nothing_included and any(e["status"] == "cut_for_budget" for e in ordered_entries):
                minimum = min(
                    _pack_minutes(e["estimated_minutes"])
                    for e in ordered_entries
                    if e["status"] == "cut_for_budget"
                )
                gaps.append({"code": "BUDGET_INFEASIBLE", "minimum_minutes": minimum})
        else:
            total_minutes = sum(
                _pack_minutes(e["estimated_minutes"])
                for e in ordered_entries
                if e["status"] == "included"
            )

        payload = {
            "items": ordered_entries,
            "gaps": gaps,
            "estimated_total_minutes": total_minutes,
            "match_run_id": run.id,
        }
        check_draft_payload_size(payload)
        draft = SolutionDraft(
            org_id=org_id,
            draft_type="learning_path",
            requirement_profile_id=profile.id,
            match_run_id=run.id,
            payload=payload,
            engine_version=ENGINE_VERSION,
            created_by=created_by,
        )
        self.db.add(draft)
        await self.db.flush()
        log.info(
            "learning_draft_composed",
            draft_id=draft.id,
            org_id=org_id,
            items=len(ordered_entries),
            gaps=len(gaps),
        )
        return draft

    @staticmethod
    def _propagate_budget_cuts(
        entries: list[dict], prereq_edges: list[tuple[str, str]]
    ) -> int:
        """Cut any entry whose (transitive) prerequisite was cut for budget.

        Waived prerequisites don't force cuts (the learner already has them).
        Returns the recomputed running total of included minutes.
        """
        status_by_id = {e["entity_id"]: e for e in entries}
        # Iterate to a fixed point (edges are acyclic; ≤N passes)
        changed = True
        while changed:
            changed = False
            for prereq_id, dependent_id in prereq_edges:
                prereq = status_by_id.get(prereq_id)
                dependent = status_by_id.get(dependent_id)
                if prereq is None or dependent is None:
                    continue
                if prereq["status"] == "cut_for_budget" and dependent["status"] == "included":
                    dependent["status"] = "cut_for_budget"
                    dependent["reason_code"] = "cut_for_budget"
                    changed = True
        return sum(
            _pack_minutes(e["estimated_minutes"])
            for e in entries
            if e["status"] == "included"
        )

    async def _expand_prerequisites(
        self, org_id: str, selected: list[SkillPack], user_id: str | None
    ) -> tuple[list[dict], list[tuple[str, str]], list[str]]:
        """Expand prerequisite_packs recursively, topo-sort, mark waived items.

        Returns (entries, prereq_edges, unresolved_slugs) — edges as
        (prereq_id, dependent_id); unresolved_slugs are prereq slugs that
        resolved to no visible published pack (surfaced as PREREQ_NOT_FOUND
        gaps, never silently dropped — R8).
        """
        # Collect the full node set (selected + transitive prereqs)
        packs: dict[str, SkillPack] = {p.id: p for p in selected}
        prereq_edges: list[tuple[str, str]] = []  # (prereq_id, dependent_id)
        unresolved: list[str] = []
        in_progress: set[str] = set()

        async def resolve_slug(slug: str) -> SkillPack | None:
            # Deterministic pick among same-slug packs: own-org pack wins,
            # then oldest (ULID asc) — slug is only unique per owner org.
            r = await self.db.execute(
                select(SkillPack)
                .where(
                    SkillPack.slug == slug,
                    SkillPack.status == PackStatus.PUBLISHED,
                )
                .order_by(SkillPack.id.asc())
            )
            candidates = list(r.scalars().all())
            for candidate in candidates:
                if candidate.owner_org_id == org_id:
                    return candidate
            for candidate in candidates:
                if candidate.visibility in (PackVisibility.PUBLIC, PackVisibility.UNLISTED):
                    return candidate
            return None

        async def visit(pack: SkillPack, depth: int, path: set[str]) -> None:
            if depth > MAX_PREREQ_DEPTH:
                return
            for entry in pack.prerequisite_packs or []:
                slug = entry if isinstance(entry, str) else entry.get("slug", "")
                if not slug:
                    continue
                prereq = await resolve_slug(slug)
                if prereq is None:
                    if slug not in unresolved:
                        unresolved.append(slug)
                    continue
                if prereq.id in path:
                    raise AppError(
                        "PREREQ_CYCLE",
                        f"Prerequisite cycle detected involving pack '{prereq.name}'",
                        422,
                    )
                prereq_edges.append((prereq.id, pack.id))
                if prereq.id not in packs:
                    packs[prereq.id] = prereq
                    await visit(prereq, depth + 1, path | {prereq.id})

        for pack in selected:
            await visit(pack, 1, {pack.id})
        _ = in_progress  # cycle detection handled via path sets

        # Waived check: user completed ALL of the pack's installed content.
        # Any-one-skill waiving silently dropped whole packs (and their
        # capability coverage) after a single completed lesson (audit MEDIUM).
        waived_ids: set[str] = set()
        if user_id:
            for pack_id in packs:
                total_r = await self.db.execute(
                    select(func.count(Skill.id)).where(
                        Skill.org_id == org_id,
                        Skill.origin_pack_id == pack_id,
                        Skill.status != ContentStatus.ARCHIVED,
                    )
                )
                total = total_r.scalar_one()
                if total == 0:
                    continue  # pack not installed locally — nothing to waive
                done_r = await self.db.execute(
                    select(func.count(SkillProgress.id))
                    .join(Skill, Skill.id == SkillProgress.skill_id)
                    .where(
                        Skill.org_id == org_id,
                        Skill.origin_pack_id == pack_id,
                        Skill.status != ContentStatus.ARCHIVED,
                        SkillProgress.user_id == user_id,
                        SkillProgress.status == ProgressStatus.COMPLETED,
                    )
                )
                if done_r.scalar_one() >= total:
                    waived_ids.add(pack_id)

        # Kahn topo sort: prereqs first; stable order preserves selection rank
        order_hint = {pid: i for i, pid in enumerate(packs.keys())}
        indegree = {pid: 0 for pid in packs}
        adj: dict[str, list[str]] = {pid: [] for pid in packs}
        for prereq_id, dependent_id in prereq_edges:
            if prereq_id in indegree and dependent_id in indegree:
                adj[prereq_id].append(dependent_id)
                indegree[dependent_id] += 1
        queue = sorted(
            [pid for pid, d in indegree.items() if d == 0], key=lambda p: order_hint[p]
        )
        topo: list[str] = []
        while queue:
            node = queue.pop(0)
            topo.append(node)
            for nxt in adj[node]:
                indegree[nxt] -= 1
                if indegree[nxt] == 0:
                    queue.append(nxt)
            queue.sort(key=lambda p: order_hint[p])

        # Cycle members that were ALL pre-selected slip past visit()'s path
        # check (it never recurses into already-known packs) — Kahn would then
        # silently drop them from the path (audit MEDIUM). Fail loudly instead.
        if len(topo) != len(packs):
            leftover = [packs[pid].name for pid in packs if pid not in set(topo)]
            raise AppError(
                "PREREQ_CYCLE",
                f"Prerequisite cycle detected involving: {', '.join(sorted(leftover))}",
                422,
            )

        # Per-item prerequisite references (resolved edges only) — persisted
        # in the payload so update_draft can protect dependents after the
        # compose transaction is gone. Entity IDs are the authoritative key:
        # slugs are only unique per owner org, and a draft can hold an
        # own-org fork and the public original under the SAME slug. Slugs
        # stay in the payload for display.
        prereq_slugs_by_id: dict[str, list[str]] = {}
        prereq_ids_by_id: dict[str, list[str]] = {}
        for prereq_id, dependent_id in prereq_edges:
            slugs = prereq_slugs_by_id.setdefault(dependent_id, [])
            slug = packs[prereq_id].slug
            if slug not in slugs:
                slugs.append(slug)
            ids = prereq_ids_by_id.setdefault(dependent_id, [])
            if prereq_id not in ids:
                ids.append(prereq_id)

        entries: list[dict] = []
        for order, pack_id in enumerate(topo):
            pack = packs[pack_id]
            entry: dict = {
                "family": "skill_pack",
                "entity_id": pack.id,
                "name": pack.name,
                "slug": pack.slug,
                "order": order,
                "required": True,
                "status": "waived" if pack.id in waived_ids else "included",
                "estimated_minutes": pack.estimated_minutes,
                "prereq_slugs": prereq_slugs_by_id.get(pack.id, []),
                "prereq_ids": prereq_ids_by_id.get(pack.id, []),
            }
            if pack.id in waived_ids:
                entry["reason_code"] = "waived"
                entry["evidence"] = "Learner already completed this pack's skills"
            entries.append(entry)
        return entries, prereq_edges, unresolved

    # ── Confirm (materialize) ─────────────────────────────

    async def claim_draft_for_confirm(self, draft_id: str, org_id: str) -> None:
        """Atomically claim a draft for confirmation (race-safe).

        A read-then-act status check lets two concurrent confirms both pass
        and both materialize (orphaned duplicate entities). The conditional
        UPDATE claims the row with a transient internal 'confirming' status —
        never exposed via the API — so exactly ONE request wins; the loser's
        rowcount is 0 → DRAFT_ALREADY_CONFIRMED 409.
        """
        result = await self.db.execute(
            update(SolutionDraft)
            .where(
                SolutionDraft.id == draft_id,
                SolutionDraft.org_id == org_id,
                SolutionDraft.status == "draft",
            )
            .values(status="confirming")
        )
        if result.rowcount == 0:
            raise AppError(
                "DRAFT_ALREADY_CONFIRMED", "Draft was already confirmed or discarded", 409
            )

    async def release_draft_claim(self, draft_id: str) -> None:
        """Revert a claimed draft to 'draft' after a failed materialization
        so the draft isn't stuck in the transient 'confirming' status."""
        await self.db.execute(
            update(SolutionDraft)
            .where(SolutionDraft.id == draft_id, SolutionDraft.status == "confirming")
            .values(status="draft")
        )

    async def confirm(self, draft_id: str, org_id: str, confirmed_by: str) -> LearningPath:
        draft = await self.get_draft(draft_id, org_id)
        if draft.draft_type != "learning_path":
            raise AppError("WRONG_DRAFT_TYPE", "Draft is not a learning-path draft", 422)
        # Conditional-UPDATE claim BEFORE materialization (race-safe: the
        # loser of two concurrent confirms gets rowcount 0 → 409)
        await self.claim_draft_for_confirm(draft_id, org_id)
        try:
            return await self._materialize(draft, org_id, confirmed_by)
        except BaseException:
            # Revert the claim so the draft isn't stuck in 'confirming'
            try:
                await self.release_draft_claim(draft_id)
            except Exception:
                # Session unusable (aborted transaction) — rolling back also
                # discards the uncommitted claim, so the draft stays 'draft'.
                await self.db.rollback()
            raise

    async def _materialize(
        self, draft: SolutionDraft, org_id: str, confirmed_by: str
    ) -> LearningPath:
        draft_id = draft.id
        # Name from the profile goal when available
        name = f"Composed Path {datetime.now(UTC).strftime('%Y-%m-%d')}"
        if draft.requirement_profile_id:
            from app.models.matching import RequirementProfile

            profile = await self.db.get(RequirementProfile, draft.requirement_profile_id)
            goal = (profile.structured_requirements or {}).get("goal") if profile else None
            if goal:
                name = str(goal)[:200]

        import re as _re
        import secrets as _secrets

        slug_base = _re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")[:190]
        path = LearningPath(
            org_id=org_id,
            name=name,
            slug=f"{slug_base or 'composed-path'}-{_secrets.token_hex(3)}",
            description="Composed from a confirmed requirement profile",
            status=ContentStatus.DRAFT,
            estimated_minutes=draft.payload.get("estimated_total_minutes"),
            created_by=confirmed_by,
        )
        self.db.add(path)
        await self.db.flush()

        sort_order = 0
        for item in draft.payload.get("items", []):
            if item.get("status") != "included":
                continue  # cut_for_budget / waived / removed_by_user never materialize
            pack_id = item["entity_id"]
            # Installed? → expand into org-local skills created by the install
            install_r = await self.db.execute(
                select(SkillPackInstallation).where(
                    SkillPackInstallation.org_id == org_id,
                    SkillPackInstallation.pack_id == pack_id,
                    SkillPackInstallation.status == InstallStatus.ACTIVE,
                )
            )
            installed = install_r.scalar_one_or_none() is not None
            if installed:
                skills_r = await self.db.execute(
                    select(Skill)
                    .where(
                        Skill.org_id == org_id,
                        Skill.origin_pack_id == pack_id,
                        Skill.status != ContentStatus.ARCHIVED,
                    )
                    .order_by(Skill.sort_order, Skill.id)
                )
                skills = list(skills_r.scalars().all())
            else:
                skills = []

            if installed and skills:
                # Section heading for the pack, then its skills
                self.db.add(
                    LearningPathItem(
                        path_id=path.id,
                        item_type=PathItemType.SECTION,
                        section_title=item["name"][:200],
                        sort_order=sort_order,
                        required=False,
                    )
                )
                sort_order += 1
                for skill in skills:
                    self.db.add(
                        LearningPathItem(
                            path_id=path.id,
                            item_type=PathItemType.SKILL,
                            skill_id=skill.id,
                            sort_order=sort_order,
                            required=bool(item.get("required", True)),
                        )
                    )
                    sort_order += 1
            else:
                # NOT installed → placeholder section. The composer NEVER
                # auto-installs (red line).
                self.db.add(
                    LearningPathItem(
                        path_id=path.id,
                        item_type=PathItemType.SECTION,
                        section_title=f"Install pack: {item['name']}"[:200],
                        sort_order=sort_order,
                        required=False,
                    )
                )
                sort_order += 1

        draft.status = "confirmed"
        draft.confirmed_by = confirmed_by
        draft.confirmed_at = datetime.now(UTC)
        draft.materialized_entity_id = path.id
        await self.db.flush()
        log.info("learning_draft_confirmed", draft_id=draft_id, path_id=path.id)
        return path

    # ── Draft management ──────────────────────────────────

    async def get_draft(self, draft_id: str, org_id: str) -> SolutionDraft:
        draft = await self.db.get(SolutionDraft, draft_id)
        if draft is None or draft.org_id != org_id:
            raise AppError("DRAFT_NOT_FOUND", "Solution draft not found", 404)
        return draft

    async def list_drafts(
        self, org_id: str, draft_type: str | None = None, page: int = 1, per_page: int = 20
    ) -> tuple[list[SolutionDraft], int]:
        from sqlalchemy import func

        base = select(SolutionDraft).where(SolutionDraft.org_id == org_id)
        if draft_type:
            base = base.where(SolutionDraft.draft_type == draft_type)
        total_r = await self.db.execute(select(func.count()).select_from(base.subquery()))
        total = total_r.scalar_one()
        result = await self.db.execute(
            base.order_by(SolutionDraft.created_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
        return list(result.scalars().all()), total

    async def update_draft(
        self, draft_id: str, org_id: str, remove_entity_ids: list[str]
    ) -> SolutionDraft:
        draft = await self.get_draft(draft_id, org_id)
        if draft.status != "draft":
            raise AppError("DRAFT_ALREADY_CONFIRMED", "Only open drafts can be edited", 409)
        payload = dict(draft.payload or {})
        remove = set(remove_entity_ids)

        # Removing a prerequisite while a dependent REMAINS included would
        # materialize the dependent without its prereq. compose() persists
        # each item's prereq_slugs in the payload for exactly this check;
        # removing prereq + dependent in the SAME request is allowed.
        current_items = payload.get("items", [])
        # Only removals that take effect matter (waived/cut items keep their
        # status below, so "removing" them changes nothing for dependents)
        removed_ids = {
            item.get("entity_id")
            for item in current_items
            if item.get("entity_id") in remove and item.get("status") == "included"
        }
        removed_slugs = {
            item.get("slug")
            for item in current_items
            if item.get("entity_id") in remove
            and item.get("status") == "included"
            and item.get("slug")
        }
        for item in current_items:
            if item.get("entity_id") in remove or item.get("status") != "included":
                continue  # the dependent is removed too / already inactive
            # Guard by entity_id (unambiguous — slugs can collide between an
            # own-org fork and the public original in the same draft); fall
            # back to slugs only for drafts composed before prereq_ids existed
            prereq_ids = item.get("prereq_ids")
            if prereq_ids is not None:
                slug_by_id = {
                    x.get("entity_id"): x.get("slug") for x in current_items if x.get("slug")
                }
                blocking = {
                    slug_by_id.get(pid, pid) for pid in prereq_ids if pid in removed_ids
                }
            else:
                blocking = removed_slugs & set(item.get("prereq_slugs") or [])
            if blocking:
                raise AppError(
                    "ITEM_HAS_DEPENDENTS",
                    (
                        f"Cannot remove prerequisite pack(s) {', '.join(sorted(blocking))}: "
                        f"'{item.get('name')}' still depends on them — remove the "
                        "dependent in the same request or keep the prerequisite"
                    ),
                    409,
                )

        items = []
        for item in current_items:
            entry = dict(item)
            if entry.get("entity_id") in remove and entry.get("status") == "included":
                entry["status"] = "removed_by_user"
                entry["reason_code"] = "removed_by_user"
            items.append(entry)
        payload["items"] = items
        payload["estimated_total_minutes"] = sum(
            _pack_minutes(e.get("estimated_minutes"))
            for e in items
            if e.get("status") == "included"
        )
        # Conditional write: a concurrent confirm may have claimed the draft
        # after our read — the same read-check-blind-write race the confirm
        # path closed. rowcount 0 = the draft is no longer editable.
        result = await self.db.execute(
            update(SolutionDraft)
            .where(
                SolutionDraft.id == draft_id,
                SolutionDraft.org_id == org_id,
                SolutionDraft.status == "draft",
            )
            .values(payload=payload)
        )
        if result.rowcount == 0:
            raise AppError("DRAFT_ALREADY_CONFIRMED", "Only open drafts can be edited", 409)
        await self.db.refresh(draft)
        return draft

    async def discard(self, draft_id: str, org_id: str) -> SolutionDraft:
        draft = await self.get_draft(draft_id, org_id)
        if draft.status != "draft":
            raise AppError("DRAFT_ALREADY_CONFIRMED", "Only open drafts can be discarded", 409)
        # Conditional: loses cleanly against a concurrent confirm's claim
        result = await self.db.execute(
            update(SolutionDraft)
            .where(
                SolutionDraft.id == draft_id,
                SolutionDraft.org_id == org_id,
                SolutionDraft.status == "draft",
            )
            .values(status="discarded")
        )
        if result.rowcount == 0:
            raise AppError("DRAFT_ALREADY_CONFIRMED", "Only open drafts can be discarded", 409)
        await self.db.refresh(draft)
        return draft
