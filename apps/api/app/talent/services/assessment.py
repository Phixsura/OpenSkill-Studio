"""Assessment & credential services (ADR-015 D5).

AssessmentService: blueprint CRUD, run lifecycle (start → submit → review).
CredentialService: rule versioning, eligibility evaluation, issuance, revocation.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.talent.models.assessment import (
    AssessmentBlueprint,
    AssessmentRun,
    Credential,
    CredentialRule,
)
from app.talent.services.evidence import EvidenceService
from app.talent.services.scoring import CapabilityScore, compute_capability_profile

# ---------------------------------------------------------------------------
# AssessmentService
# ---------------------------------------------------------------------------


class AssessmentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ---- Blueprint CRUD ----

    async def create_blueprint(
        self,
        *,
        org_id: str,
        title: str,
        assessment_type: str,
        capability_requirements: list[dict] | None = None,
        config: dict | None = None,
        description: str | None = None,
        created_by: str | None = None,
    ) -> AssessmentBlueprint:
        bp = AssessmentBlueprint(
            org_id=org_id,
            title=title,
            description=description,
            assessment_type=assessment_type,
            capability_requirements=capability_requirements or [],
            config=config or {},
            created_by=created_by,
        )
        self.db.add(bp)
        await self.db.flush()
        return bp

    async def get_blueprint(self, blueprint_id: str) -> AssessmentBlueprint | None:
        return await self.db.get(AssessmentBlueprint, blueprint_id)

    async def list_blueprints(
        self,
        org_id: str,
        *,
        status: str = "active",
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[AssessmentBlueprint], int]:
        q = select(AssessmentBlueprint).where(
            AssessmentBlueprint.org_id == org_id,
            AssessmentBlueprint.status == status,
        )
        count_q = select(func.count()).select_from(q.subquery())
        total = (await self.db.execute(count_q)).scalar() or 0

        q = q.order_by(AssessmentBlueprint.created_at.desc()).limit(limit).offset(offset)
        result = await self.db.execute(q)
        return list(result.scalars().all()), total

    async def update_blueprint(
        self,
        blueprint_id: str,
        **fields: object,
    ) -> AssessmentBlueprint | None:
        bp = await self.db.get(AssessmentBlueprint, blueprint_id)
        if not bp:
            return None
        if bp.status != "draft":
            raise ValueError("Only draft blueprints can be updated")
        for key, value in fields.items():
            if hasattr(bp, key):
                setattr(bp, key, value)
        await self.db.flush()
        return bp

    # ---- Run lifecycle ----

    async def start_run(
        self,
        blueprint_id: str,
        user_id: str,
        org_id: str,
    ) -> AssessmentRun:
        """Start a new assessment attempt.

        Checks attempt limits, sets deadline from config.time_window_minutes,
        and snapshots the blueprint version.
        """
        bp = await self.db.get(AssessmentBlueprint, blueprint_id)
        if not bp:
            raise ValueError("Blueprint not found")
        if bp.status != "active":
            raise ValueError("Blueprint is not active")

        # Check attempt limit
        attempt_limit = (bp.config or {}).get("attempt_limit")
        existing_count_q = select(func.count()).where(
            AssessmentRun.blueprint_id == blueprint_id,
            AssessmentRun.user_id == user_id,
        )
        existing_count = (await self.db.execute(existing_count_q)).scalar() or 0
        if attempt_limit is not None and existing_count >= attempt_limit:
            raise ValueError("ATTEMPT_LIMIT_REACHED")

        now = datetime.now(UTC)
        deadline_at = None
        time_window = (bp.config or {}).get("time_window_minutes")
        if time_window:
            deadline_at = now + timedelta(minutes=int(time_window))

        run = AssessmentRun(
            blueprint_id=blueprint_id,
            blueprint_version=bp.version,
            user_id=user_id,
            org_id=org_id,
            attempt_number=existing_count + 1,
            status="in_progress",
            started_at=now,
            deadline_at=deadline_at,
        )
        self.db.add(run)
        await self.db.flush()
        return run

    async def submit_run(
        self,
        run_id: str,
        user_id: str,
        *,
        results: dict | None = None,
        project_id: str | None = None,
    ) -> AssessmentRun:
        """Submit an in-progress run."""
        run = await self.db.get(AssessmentRun, run_id)
        if not run:
            raise ValueError("Run not found")
        if run.user_id != user_id:
            raise ValueError("Run does not belong to this user")
        if run.status != "in_progress":
            raise ValueError(f"Cannot submit run in status '{run.status}'")

        # Check deadline
        now = datetime.now(UTC)
        if run.deadline_at and now > run.deadline_at:
            run.status = "expired"
            await self.db.flush()
            raise ValueError("Assessment deadline has passed")

        run.status = "submitted"
        run.submitted_at = now
        run.results = results
        if project_id:
            run.project_id = project_id
        await self.db.flush()
        return run

    async def review_run(
        self,
        run_id: str,
        reviewer_id: str,
        *,
        results: list[dict],
        status: str,
    ) -> AssessmentRun:
        """Review a submitted run. status must be 'passed' or 'failed'.

        On 'passed': auto-generates CapabilityEvidence for each blueprint
        capability. If config.auto_issue_credential is set, triggers
        credential evaluation.
        """
        if status not in ("passed", "failed"):
            raise ValueError("Review status must be 'passed' or 'failed'")

        run = await self.db.get(AssessmentRun, run_id)
        if not run:
            raise ValueError("Run not found")
        if run.status not in ("submitted", "under_review"):
            raise ValueError(f"Cannot review run in status '{run.status}'")

        run.status = status
        run.results = results
        run.reviewed_by = reviewer_id
        run.reviewed_at = datetime.now(UTC)
        await self.db.flush()

        if status == "passed":
            await self._generate_assessment_evidence(run)

            bp = await self.db.get(AssessmentBlueprint, run.blueprint_id)
            if bp and (bp.config or {}).get("auto_issue_credential"):
                cred_type = (bp.config or {}).get("credential_type")
                if cred_type:
                    cred_svc = CredentialService(self.db)
                    evaluation = await cred_svc.evaluate(cred_type, run.user_id)
                    if evaluation["eligible"]:
                        await cred_svc.issue_credential(
                            cred_type, run.user_id, org_id=run.org_id
                        )

        return run

    async def _generate_assessment_evidence(self, run: AssessmentRun) -> None:
        """Generate CapabilityEvidence rows for a passed assessment."""
        bp = await self.db.get(AssessmentBlueprint, run.blueprint_id)
        if not bp:
            return

        ev_svc = EvidenceService(self.db)
        now = datetime.now(UTC)

        # Map results by capability_id for score lookup
        result_map: dict[str, float] = {}
        for r in (run.results or []):
            cap_id = r.get("capability_id")
            if cap_id and r.get("passed"):
                result_map[cap_id] = float(r.get("score", 0.8))

        for req in bp.capability_requirements or []:
            cap_id = req.get("capability_id")
            if not cap_id:
                continue
            score = result_map.get(cap_id, 0.8)
            await ev_svc.record_evidence(
                user_id=run.user_id,
                capability_id=cap_id,
                source_type="assessment_result",
                source_id=run.id,
                verification_level="assessment_verified",
                occurred_at=now,
                org_id=run.org_id,
                score_normalized=score,
                confidence=0.9,
                metadata={
                    "blueprint_id": bp.id,
                    "blueprint_version": run.blueprint_version,
                    "attempt_number": run.attempt_number,
                },
            )


# ---------------------------------------------------------------------------
# CredentialService
# ---------------------------------------------------------------------------


class CredentialService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_rule(
        self,
        *,
        credential_type: str,
        display_name: str,
        requirements: list[dict],
        conditions: dict | None = None,
        description: str | None = None,
        org_id: str | None = None,
    ) -> CredentialRule:
        """Create a new credential rule version (auto-incremented)."""
        # Find the latest version for this credential_type
        latest_q = (
            select(func.max(CredentialRule.version))
            .where(CredentialRule.credential_type == credential_type)
        )
        latest_version = (await self.db.execute(latest_q)).scalar() or 0

        rule = CredentialRule(
            credential_type=credential_type,
            version=latest_version + 1,
            display_name=display_name,
            description=description,
            requirements=requirements,
            conditions=conditions or {},
            org_id=org_id,
        )
        self.db.add(rule)
        await self.db.flush()
        return rule

    async def activate_rule(self, rule_id: str) -> CredentialRule:
        """Activate a rule, retiring the previous active version."""
        rule = await self.db.get(CredentialRule, rule_id)
        if not rule:
            raise ValueError("Rule not found")
        if rule.status != "draft":
            raise ValueError("Only draft rules can be activated")

        # Retire the current active version of this credential_type
        active_q = select(CredentialRule).where(
            CredentialRule.credential_type == rule.credential_type,
            CredentialRule.status == "active",
        )
        result = await self.db.execute(active_q)
        for active_rule in result.scalars().all():
            active_rule.status = "retired"

        rule.status = "active"
        rule.activated_at = datetime.now(UTC)
        await self.db.flush()
        return rule

    async def evaluate(
        self,
        credential_type: str,
        user_id: str,
    ) -> dict:
        """Evaluate whether a user meets the requirements for a credential.

        Returns {"eligible": bool, "met": [...], "unmet": [...], "rule_id": ...}.
        """
        # Load active rule
        rule_q = select(CredentialRule).where(
            CredentialRule.credential_type == credential_type,
            CredentialRule.status == "active",
        )
        result = await self.db.execute(rule_q)
        rule = result.scalar_one_or_none()
        if not rule:
            return {"eligible": False, "met": [], "unmet": [], "rule_id": None,
                    "reason": "No active rule for this credential type"}

        # Load user's capability profile
        profile = await compute_capability_profile(self.db, user_id)
        profile_map: dict[str, CapabilityScore] = {s.capability_id: s for s in profile}

        met: list[dict] = []
        unmet: list[dict] = []
        all_required = (rule.conditions or {}).get("all_required", True)

        for req in rule.requirements:
            cap_id = req.get("capability_id")
            min_level = req.get("min_level", 0)
            assessment_blueprint_id = req.get("assessment_blueprint_id")
            required = req.get("required", True)

            if cap_id:
                # Check capability level
                cap_score = profile_map.get(cap_id)
                if cap_score and cap_score.level >= min_level:
                    met.append({
                        "capability_id": cap_id,
                        "required_level": min_level,
                        "achieved_level": cap_score.level,
                    })
                else:
                    entry = {
                        "capability_id": cap_id,
                        "required_level": min_level,
                        "achieved_level": cap_score.level if cap_score else 0,
                        "required": required,
                    }
                    unmet.append(entry)

            elif assessment_blueprint_id:
                # Check if user has a passed assessment run
                passed_q = select(func.count()).where(
                    AssessmentRun.blueprint_id == assessment_blueprint_id,
                    AssessmentRun.user_id == user_id,
                    AssessmentRun.status == "passed",
                )
                passed = (await self.db.execute(passed_q)).scalar() or 0
                if passed > 0:
                    met.append({"assessment_blueprint_id": assessment_blueprint_id, "passed": True})
                else:
                    unmet.append({
                        "assessment_blueprint_id": assessment_blueprint_id,
                        "passed": False,
                        "required": required,
                    })

        # Determine eligibility
        if all_required:
            required_unmet = [u for u in unmet if u.get("required", True)]
            eligible = len(required_unmet) == 0
        else:
            # any_required: at least one met
            eligible = len(met) > 0

        # Check additional conditions
        conditions = rule.conditions or {}
        min_evidence_count = conditions.get("min_evidence_count")
        if min_evidence_count and eligible:
            total_evidence = sum(s.evidence_count for s in profile)
            if total_evidence < min_evidence_count:
                eligible = False
                unmet.append({
                    "condition": "min_evidence_count",
                    "required": min_evidence_count,
                    "actual": total_evidence,
                })

        return {
            "eligible": eligible,
            "met": met,
            "unmet": unmet,
            "rule_id": rule.id,
            "rule_version": rule.version,
        }

    async def issue_credential(
        self,
        credential_type: str,
        user_id: str,
        *,
        org_id: str | None = None,
    ) -> Credential:
        """Issue a credential after verifying eligibility.

        Supersedes any existing active credential of the same type for the user.
        Generates CapabilityEvidence with source_type='credential'.
        """
        evaluation = await self.evaluate(credential_type, user_id)
        if not evaluation["eligible"]:
            raise ValueError(
                f"User does not meet requirements for '{credential_type}': "
                f"{evaluation['unmet']}"
            )

        rule_id = evaluation["rule_id"]
        rule = await self.db.get(CredentialRule, rule_id) if rule_id else None

        # Supersede existing active credential of same type
        existing_q = select(Credential).where(
            Credential.user_id == user_id,
            Credential.credential_type == credential_type,
            Credential.status == "active",
        )
        result = await self.db.execute(existing_q)
        for existing in result.scalars().all():
            existing.status = "superseded"

        # Compute validity
        conditions = (rule.conditions or {}) if rule else {}
        validity_days = conditions.get("validity_days")
        now = datetime.now(UTC)
        expires_at = now + timedelta(days=validity_days) if validity_days else None

        credential = Credential(
            credential_type=credential_type,
            version=rule.version if rule else 1,
            credential_rule_id=rule_id,
            issuer_org_id=org_id,
            user_id=user_id,
            capabilities=[
                {
                    "capability_id": m["capability_id"],
                    "required_level": m["required_level"],
                    "achieved_level": m["achieved_level"],
                }
                for m in evaluation["met"]
                if "capability_id" in m
            ],
            evidence_references=[
                {"type": "evaluation", "rule_id": rule_id, "evaluated_at": now.isoformat()}
            ],
            expires_at=expires_at,
        )
        self.db.add(credential)
        await self.db.flush()

        # Generate evidence for each capability in the credential
        ev_svc = EvidenceService(self.db)
        for cap in credential.capabilities:
            await ev_svc.record_evidence(
                user_id=user_id,
                capability_id=cap["capability_id"],
                source_type="credential",
                source_id=credential.id,
                verification_level="assessment_verified",
                occurred_at=now,
                org_id=org_id,
                score_normalized=min(cap["achieved_level"] / 5.0, 1.0),
                confidence=0.95,
                metadata={
                    "credential_type": credential_type,
                    "credential_version": credential.version,
                },
            )

        return credential

    async def revoke_credential(
        self,
        credential_id: str,
        reason: str | None = None,
    ) -> Credential:
        """Revoke an active credential."""
        credential = await self.db.get(Credential, credential_id)
        if not credential:
            raise ValueError("Credential not found")
        if credential.status != "active":
            raise ValueError(f"Cannot revoke credential in status '{credential.status}'")

        credential.status = "revoked"
        credential.revoked_at = datetime.now(UTC)
        credential.revoked_reason = reason
        await self.db.flush()
        return credential

    async def list_user_credentials(
        self,
        user_id: str,
        *,
        status: str | None = None,
    ) -> list[Credential]:
        """List credentials for a user, optionally filtered by status."""
        q = select(Credential).where(Credential.user_id == user_id)
        if status:
            q = q.where(Credential.status == status)
        q = q.order_by(Credential.issued_at.desc())
        result = await self.db.execute(q)
        return list(result.scalars().all())
