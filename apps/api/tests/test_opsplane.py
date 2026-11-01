"""Operations plane tests (ADR-018).

Tests run without DB using the noop lifespan pattern.
"""

import pytest


class TestInfrastructureModels:

    def test_region_status_enum(self):
        from app.opsplane.models.infrastructure import RegionStatus
        assert RegionStatus.ACTIVE.value == "active"
        assert RegionStatus.DRAINING.value == "draining"
        assert len(RegionStatus) == 4

    def test_cell_status_enum(self):
        from app.opsplane.models.infrastructure import CellStatus
        assert CellStatus.HEALTHY.value == "healthy"
        assert CellStatus.OFFLINE.value == "offline"
        assert len(CellStatus) == 5

    def test_service_status_enum(self):
        from app.opsplane.models.infrastructure import ServiceStatus
        assert ServiceStatus.RUNNING.value == "running"
        assert len(ServiceStatus) == 5


class TestReliabilityModels:

    def test_slo_status_enum(self):
        from app.opsplane.models.reliability import SloStatus
        assert SloStatus.MET.value == "met"
        assert SloStatus.BREACHED.value == "breached"
        assert len(SloStatus) == 4

    def test_incident_severity_enum(self):
        from app.opsplane.models.reliability import OpsIncidentSeverity
        for sev in ("sev1", "sev2", "sev3", "sev4"):
            assert OpsIncidentSeverity(sev).value == sev

    def test_incident_status_enum(self):
        from app.opsplane.models.reliability import OpsIncidentStatus
        assert OpsIncidentStatus.DETECTED.value == "detected"
        assert OpsIncidentStatus.CLOSED.value == "closed"
        assert len(OpsIncidentStatus) == 7

    def test_failover_status_enum(self):
        from app.opsplane.models.reliability import FailoverStatus
        assert FailoverStatus.TRIGGERED.value == "triggered"
        assert FailoverStatus.ROLLED_BACK.value == "rolled_back"
        assert len(FailoverStatus) == 6

    def test_recovery_plan_status_enum(self):
        from app.opsplane.models.reliability import RecoveryPlanStatus
        assert len(RecoveryPlanStatus) == 4

    def test_detection_rule_status_enum(self):
        from app.opsplane.models.reliability import DetectionRuleStatus
        assert len(DetectionRuleStatus) == 3


class TestGovernanceModels:

    def test_policy_status_enum(self):
        from app.opsplane.models.governance import PolicyStatus
        assert PolicyStatus.DRAFT.value == "draft"
        assert PolicyStatus.ACTIVE.value == "active"
        assert len(PolicyStatus) == 4

    def test_playbook_status_enum(self):
        from app.opsplane.models.governance import PlaybookStatus
        assert len(PlaybookStatus) == 4

    def test_playbook_run_status_enum(self):
        from app.opsplane.models.governance import PlaybookRunStatus
        assert PlaybookRunStatus.PENDING_APPROVAL.value == "pending_approval"
        assert len(PlaybookRunStatus) == 7

    def test_cost_category_enum(self):
        from app.opsplane.models.governance import CostCategory
        assert CostCategory.AI_INFERENCE.value == "ai_inference"
        assert CostCategory.COMPUTE.value == "compute"
        assert len(CostCategory) == 7

    def test_game_day_status_enum(self):
        from app.opsplane.models.governance import GameDayStatus
        assert len(GameDayStatus) == 4

    def test_healing_action_status_enum(self):
        from app.opsplane.models.governance import HealingActionStatus
        assert HealingActionStatus.PROPOSED.value == "proposed"
        assert HealingActionStatus.APPROVED.value == "approved"
        assert len(HealingActionStatus) == 6


class TestResponseSchemas:

    def test_region_response(self):
        from app.opsplane.api.v1.operations import RegionResponse
        assert RegionResponse.model_config.get("from_attributes") is True

    def test_cell_response(self):
        from app.opsplane.api.v1.operations import CellResponse
        assert CellResponse.model_config.get("from_attributes") is True

    def test_slo_response(self):
        from app.opsplane.api.v1.operations import SloResponse
        assert SloResponse.model_config.get("from_attributes") is True

    def test_incident_response(self):
        from app.opsplane.api.v1.operations import OpsIncidentResponse
        assert OpsIncidentResponse.model_config.get("from_attributes") is True

    def test_failover_response(self):
        from app.opsplane.api.v1.operations import FailoverResponse
        assert FailoverResponse.model_config.get("from_attributes") is True

    def test_policy_response(self):
        from app.opsplane.api.v1.operations import PolicyResponse
        assert PolicyResponse.model_config.get("from_attributes") is True

    def test_playbook_response(self):
        from app.opsplane.api.v1.operations import PlaybookResponse
        assert PlaybookResponse.model_config.get("from_attributes") is True

    def test_budget_response(self):
        from app.opsplane.api.v1.operations import BudgetResponse
        assert BudgetResponse.model_config.get("from_attributes") is True

    def test_game_day_response(self):
        from app.opsplane.api.v1.operations import GameDayResponse
        assert GameDayResponse.model_config.get("from_attributes") is True

    def test_healing_response(self):
        from app.opsplane.api.v1.operations import HealingResponse
        assert HealingResponse.model_config.get("from_attributes") is True

    def test_compliance_response(self):
        from app.opsplane.api.v1.operations import ComplianceResponse
        assert ComplianceResponse.model_config.get("from_attributes") is True

    def test_detection_rule_response(self):
        from app.opsplane.api.v1.operations import DetectionRuleResponse
        assert DetectionRuleResponse.model_config.get("from_attributes") is True

    def test_recovery_plan_response(self):
        from app.opsplane.api.v1.operations import RecoveryPlanResponse
        assert RecoveryPlanResponse.model_config.get("from_attributes") is True

    def test_service_response(self):
        from app.opsplane.api.v1.operations import ServiceResponse
        assert ServiceResponse.model_config.get("from_attributes") is True


class TestServiceErrors:

    def test_region_not_found(self):
        from app.opsplane.services.infrastructure import RegionNotFoundError
        err = RegionNotFoundError()
        assert err.status_code == 404
        assert err.code == "REGION_NOT_FOUND"

    def test_cell_not_found(self):
        from app.opsplane.services.infrastructure import CellNotFoundError
        err = CellNotFoundError()
        assert err.status_code == 404

    def test_slo_not_found(self):
        from app.opsplane.services.reliability import SloNotFoundError
        err = SloNotFoundError()
        assert err.status_code == 404

    def test_incident_not_found(self):
        from app.opsplane.services.reliability import IncidentNotFoundError
        err = IncidentNotFoundError()
        assert err.status_code == 404
        assert err.code == "OPS_INCIDENT_NOT_FOUND"

    def test_policy_not_found(self):
        from app.opsplane.services.governance import PolicyNotFoundError
        err = PolicyNotFoundError()
        assert err.status_code == 404

    def test_playbook_not_found(self):
        from app.opsplane.services.governance import PlaybookNotFoundError
        err = PlaybookNotFoundError()
        assert err.status_code == 404
