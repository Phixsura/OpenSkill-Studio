"""Workflow pack installation service (ADR-010).

Mirrors app/services/installation.py semantics for the workflow-pack family:
install/upgrade/rollback/fork/remove with the capability gate (ADR-011) —
installation NEVER auto-connects providers; unsatisfied capabilities are a
hard 422 with structured gaps.
"""

import structlog
from sqlalchemy import delete as sa_delete
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import AppError
from app.models.skill_pack import InstallStatus, PackStatus, PackVisibility
from app.models.workflow_pack import (
    WorkflowPack,
    WorkflowPackInstallation,
    WorkflowPackRelease,
)
from app.models.workflow_run import WorkflowStepBinding
from app.services.provider import ProviderService
from app.services.workflow_pack import _parse_semver

log = structlog.get_logger()


class WorkflowInstallationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Install ───────────────────────────────────────────

    async def install(
        self,
        org_id: str,
        pack_id: str,
        version: str | None,
        installed_by: str,
    ) -> WorkflowPackInstallation:
        pack = await self.db.get(WorkflowPack, pack_id)
        if pack is None:
            raise AppError("WORKFLOW_PACK_NOT_FOUND", "Workflow pack not found", 404)

        # Only PUBLISHED packs are installable. Same code for status/visibility
        # failures to prevent pack-id enumeration (mirror installation.py).
        if pack.status != PackStatus.PUBLISHED:
            raise AppError("WORKFLOW_PACK_NOT_FOUND", "Workflow pack not found", 404)
        if pack.visibility == PackVisibility.PRIVATE and pack.owner_org_id != org_id:
            raise AppError("WORKFLOW_PACK_NOT_FOUND", "Workflow pack not found", 404)
        # PUBLIC packs must be approved (or predate the approval flow)
        if (
            pack.visibility == PackVisibility.PUBLIC
            and pack.owner_org_id != org_id
            and pack.review_status not in (None, "approved")
        ):
            raise AppError("WORKFLOW_PACK_NOT_FOUND", "Workflow pack not found", 404)

        release = await self._resolve_release(pack_id, version)
        if release is None:
            raise AppError("RELEASE_NOT_FOUND", "No release found for this pack", 404)

        # ── Capability gate (ADR-011): hard failure, never auto-connect ──
        await self._capability_gate(org_id, release)

        # Already installed?
        existing_r = await self.db.execute(
            select(WorkflowPackInstallation).where(
                WorkflowPackInstallation.org_id == org_id,
                WorkflowPackInstallation.pack_id == pack_id,
            )
        )
        existing = existing_r.scalar_one_or_none()
        if existing is not None:
            if existing.status != InstallStatus.REMOVED:
                raise AppError(
                    "ALREADY_INSTALLED", "Workflow pack already installed in this organization", 409
                )
            # Reactivate the removed installation
            existing.release_id = release.id
            existing.installed_version = release.version
            existing.status = InstallStatus.ACTIVE
            existing.local_definition = None
            existing.locally_modified = False
            existing.installed_by = installed_by
            await self.db.flush()
            await self._rebuild_bindings(existing, release)
            await self._bump_install_count(pack_id, +1)
            await self.db.refresh(existing)
            log.info("workflow_pack_reinstalled", installation_id=existing.id, org_id=org_id)
            return existing

        install = WorkflowPackInstallation(
            org_id=org_id,
            pack_id=pack_id,
            release_id=release.id,
            installed_version=release.version,
            installed_by=installed_by,
        )
        self.db.add(install)
        await self.db.flush()
        await self._rebuild_bindings(install, release)
        await self._bump_install_count(pack_id, +1)
        log.info(
            "workflow_pack_installed",
            installation_id=install.id,
            org_id=org_id,
            pack_id=pack_id,
            version=release.version,
        )
        return install

    # ── Reads ─────────────────────────────────────────────

    async def list_installations(
        self, org_id: str, page: int = 1, per_page: int = 20
    ) -> tuple[list[WorkflowPackInstallation], int]:
        base = select(WorkflowPackInstallation).where(
            WorkflowPackInstallation.org_id == org_id,
            WorkflowPackInstallation.status != InstallStatus.REMOVED,
        )
        total_r = await self.db.execute(select(func.count()).select_from(base.subquery()))
        total = total_r.scalar_one()
        result = await self.db.execute(
            base.order_by(WorkflowPackInstallation.installed_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
        return list(result.scalars().all()), total

    async def get_installation(
        self, installation_id: str, org_id: str
    ) -> WorkflowPackInstallation:
        inst = await self.db.get(WorkflowPackInstallation, installation_id)
        if inst is None or inst.org_id != org_id or inst.status == InstallStatus.REMOVED:
            raise AppError("INSTALLATION_NOT_FOUND", "Workflow installation not found", 404)
        return inst

    # ── Upgrade / rollback (same method — any released version) ──

    async def upgrade(
        self, installation_id: str, org_id: str, target_version: str
    ) -> WorkflowPackInstallation:
        inst = await self.get_installation(installation_id, org_id)
        if inst.status == InstallStatus.FORKED:
            raise AppError(
                "CANNOT_UPGRADE_FORKED",
                "Forked installations track a local definition — upgrade is not applicable",
                422,
            )
        if inst.pack_id is None:
            raise AppError("WORKFLOW_PACK_NOT_FOUND", "Original pack no longer exists", 404)

        release = await self._resolve_release(inst.pack_id, target_version)
        if release is None:
            raise AppError("RELEASE_NOT_FOUND", f"No release {target_version} for this pack", 404)
        if release.id == inst.release_id:
            raise AppError("ALREADY_ON_VERSION", f"Already on version {target_version}", 409)

        # Re-run the capability gate against the target release
        await self._capability_gate(org_id, release)

        inst.release_id = release.id
        inst.installed_version = release.version
        await self.db.flush()
        # Rebuild binding suggestions (unconfirmed) for the new definition
        await self._rebuild_bindings(inst, release)
        await self.db.refresh(inst)
        log.info(
            "workflow_installation_upgraded",
            installation_id=installation_id,
            version=release.version,
        )
        return inst

    # ── Fork ──────────────────────────────────────────────

    async def fork(self, installation_id: str, org_id: str) -> WorkflowPackInstallation:
        inst = await self.get_installation(installation_id, org_id)
        if inst.status == InstallStatus.FORKED:
            raise AppError("ALREADY_FORKED", "Installation is already forked", 409)
        definition = await self._effective_definition(inst)
        inst.local_definition = definition
        inst.status = InstallStatus.FORKED
        inst.locally_modified = False
        await self.db.flush()
        await self.db.refresh(inst)
        log.info("workflow_installation_forked", installation_id=installation_id)
        return inst

    # ── Remove ────────────────────────────────────────────

    async def remove(self, installation_id: str, org_id: str) -> None:
        inst = await self.get_installation(installation_id, org_id)
        inst.status = InstallStatus.REMOVED
        await self.db.execute(
            sa_delete(WorkflowStepBinding).where(
                WorkflowStepBinding.installation_id == installation_id
            )
        )
        if inst.pack_id:
            await self._bump_install_count(inst.pack_id, -1)
        await self.db.flush()
        log.info("workflow_installation_removed", installation_id=installation_id)

    # ── Bindings ──────────────────────────────────────────

    async def list_bindings(
        self, installation_id: str, org_id: str
    ) -> list[WorkflowStepBinding]:
        await self.get_installation(installation_id, org_id)
        result = await self.db.execute(
            select(WorkflowStepBinding)
            .where(WorkflowStepBinding.installation_id == installation_id)
            .order_by(WorkflowStepBinding.step_id)
        )
        return list(result.scalars().all())

    async def confirm_binding(
        self,
        installation_id: str,
        org_id: str,
        step_id: str,
        offering_id: str,
        binding_mode: str,
        confirmed_by: str,
    ) -> WorkflowStepBinding:
        inst = await self.get_installation(installation_id, org_id)
        if binding_mode not in ("auto", "preferred", "pinned"):
            raise AppError("INVALID_BINDING_MODE", "Binding mode must be auto, preferred, or pinned", 422)

        # The step must exist in the effective definition and declare a capability
        definition = await self._effective_definition(inst)
        step = next((s for s in definition.get("steps", []) if s["id"] == step_id), None)
        if step is None or step.get("type") != "provider_action":
            raise AppError("STEP_NOT_FOUND", "No provider_action step with this id", 404)
        capability = step.get("config", {}).get("capability", "")

        # The offering must belong to this org and serve the step's capability
        provider_svc = ProviderService(self.db)
        offering = await provider_svc.get_offering(offering_id, org_id)
        if offering.capability_key != capability:
            raise AppError(
                "CAPABILITY_MISMATCH",
                f"Offering serves '{offering.capability_key}' but the step requires '{capability}'",
                422,
            )

        binding_r = await self.db.execute(
            select(WorkflowStepBinding).where(
                WorkflowStepBinding.installation_id == installation_id,
                WorkflowStepBinding.step_id == step_id,
            )
        )
        binding = binding_r.scalar_one_or_none()
        if binding is None:
            binding = WorkflowStepBinding(
                org_id=org_id,
                installation_id=installation_id,
                step_id=step_id,
            )
            self.db.add(binding)
        binding.offering_id = offering_id
        binding.binding_mode = binding_mode
        binding.confirmed_by = confirmed_by
        binding.reasons = [
            {"code": "HUMAN_CONFIRMED", "label": f"Confirmed offering {offering.model_name}"}
        ]
        binding.gaps = []
        await self.db.flush()
        return binding

    # ── Diff ──────────────────────────────────────────────

    async def compute_diff(self, installation_id: str, org_id: str, to_version: str) -> dict:
        inst = await self.get_installation(installation_id, org_id)
        if inst.pack_id is None:
            raise AppError("WORKFLOW_PACK_NOT_FOUND", "Original pack no longer exists", 404)
        current = await self._effective_definition(inst)
        target_release = await self._resolve_release(inst.pack_id, to_version)
        if target_release is None:
            raise AppError("RELEASE_NOT_FOUND", f"No release {to_version} for this pack", 404)
        target = target_release.manifest.get("definition", {})
        return self._diff_definitions(current, target)

    @staticmethod
    def _diff_definitions(current: dict, target: dict) -> dict:
        cur_steps = {s["id"]: s for s in current.get("steps", [])}
        tgt_steps = {s["id"]: s for s in target.get("steps", [])}
        added = sorted(set(tgt_steps) - set(cur_steps))
        removed = sorted(set(cur_steps) - set(tgt_steps))
        changed = sorted(
            sid for sid in set(cur_steps) & set(tgt_steps) if cur_steps[sid] != tgt_steps[sid]
        )

        cur_inputs = {i["key"]: i for i in current.get("inputs", [])}
        tgt_inputs = {i["key"]: i for i in target.get("inputs", [])}
        inputs_added = sorted(set(tgt_inputs) - set(cur_inputs))
        inputs_removed = sorted(set(cur_inputs) - set(tgt_inputs))
        inputs_changed = sorted(
            k for k in set(cur_inputs) & set(tgt_inputs) if cur_inputs[k] != tgt_inputs[k]
        )

        cur_edges = {e["id"] for e in current.get("edges", [])}
        tgt_edges = {e["id"] for e in target.get("edges", [])}
        return {
            "steps": {"added": added, "removed": removed, "changed": changed},
            "inputs": {
                "added": inputs_added,
                "removed": inputs_removed,
                "changed": inputs_changed,
            },
            "edges": {
                "added_count": len(tgt_edges - cur_edges),
                "removed_count": len(cur_edges - tgt_edges),
            },
        }

    # ── Internals ─────────────────────────────────────────

    async def _resolve_release(
        self, pack_id: str, version: str | None
    ) -> WorkflowPackRelease | None:
        if version:
            result = await self.db.execute(
                select(WorkflowPackRelease).where(
                    WorkflowPackRelease.pack_id == pack_id,
                    WorkflowPackRelease.version == version,
                )
            )
            return result.scalar_one_or_none()
        result = await self.db.execute(
            select(WorkflowPackRelease).where(WorkflowPackRelease.pack_id == pack_id)
        )
        releases = list(result.scalars().all())
        if not releases:
            return None
        return max(releases, key=lambda r: _parse_semver(r.version))

    async def _capability_gate(self, org_id: str, release: WorkflowPackRelease) -> None:
        """Hard install gate: unsatisfied capabilities → 422 with gaps (never auto-connect)."""
        required = (release.manifest.get("dependencies") or {}).get("requires_capabilities", [])
        if not required:
            return
        provider_svc = ProviderService(self.db)
        gaps = await provider_svc.check_capabilities(org_id, required)
        if gaps:
            raise AppError(
                "CAPABILITY_UNSATISFIED",
                "Organization is missing required provider capabilities for this workflow",
                422,
                details=gaps,
            )

    async def _effective_definition(self, inst: WorkflowPackInstallation) -> dict:
        if inst.local_definition is not None:
            return inst.local_definition
        if inst.release_id is None:
            raise AppError("NO_DEFINITION", "Installation has no release or local definition", 422)
        release = await self.db.get(WorkflowPackRelease, inst.release_id)
        if release is None:
            raise AppError("NO_DEFINITION", "Release no longer exists", 422)
        return release.manifest.get("definition", {})

    async def _rebuild_bindings(
        self, inst: WorkflowPackInstallation, release: WorkflowPackRelease
    ) -> None:
        """Delete + recreate unconfirmed binding suggestions per provider_action step."""
        await self.db.execute(
            sa_delete(WorkflowStepBinding).where(
                WorkflowStepBinding.installation_id == inst.id
            )
        )
        definition = release.manifest.get("definition", {})
        provider_svc = ProviderService(self.db)
        for step in definition.get("steps", []):
            if step.get("type") != "provider_action":
                continue
            config = step.get("config", {})
            capability = config.get("capability", "")
            required = set(config.get("required_features", []))
            offerings = await provider_svc.list_offerings(inst.org_id, capability_key=capability)
            best = None
            for off in sorted(
                offerings,
                key=lambda o: (o.cost_per_call_usd is None, o.cost_per_call_usd or 0, o.id),
            ):
                if required <= set(off.features or []):
                    best = off
                    break
            reasons = []
            gaps = []
            if best is not None:
                reasons.append(
                    {
                        "code": "AUTO_SUGGESTED",
                        "label": f"Cheapest active offering: {best.model_name}",
                    }
                )
            else:
                gaps.append(
                    {
                        "code": "NO_ELIGIBLE_PROVIDER",
                        "label": f"No active offering for '{capability}'"
                        + (f" with features {sorted(required)}" if required else ""),
                    }
                )
            self.db.add(
                WorkflowStepBinding(
                    org_id=inst.org_id,
                    installation_id=inst.id,
                    step_id=step["id"],
                    binding_mode=config.get("binding_mode", "auto"),
                    offering_id=best.id if best else None,
                    reasons=reasons,
                    gaps=gaps,
                    confirmed_by=None,  # suggestions are unconfirmed (D5)
                )
            )
        await self.db.flush()

    async def _bump_install_count(self, pack_id: str, delta: int) -> None:
        if delta > 0:
            await self.db.execute(
                update(WorkflowPack)
                .where(WorkflowPack.id == pack_id)
                .values(install_count=WorkflowPack.install_count + delta)
            )
        else:
            await self.db.execute(
                update(WorkflowPack)
                .where(WorkflowPack.id == pack_id)
                .values(install_count=func.greatest(WorkflowPack.install_count + delta, 0))
            )
