"""Credential pathway tests — stackable credentials (N2)."""

import pytest
from pydantic import ValidationError

from app.talent.models.credential_pathway import PATHWAY_STATUSES
from app.talent.schemas.credential_pathway import (
    CreatePathwayRequest,
    PathwayProgressResponse,
    PathwayResponse,
    UpdatePathwayRequest,
)


class TestPathwayConstants:
    def test_statuses(self):
        assert "active" in PATHWAY_STATUSES
        assert "archived" in PATHWAY_STATUSES


class TestCreatePathwayRequest:
    def test_valid_request(self):
        req = CreatePathwayRequest(
            name="AI Visual Master",
            pathway_credential_type="AI Visual — Master",
            prerequisite_credential_types=["AI Visual — Foundation", "AI Visual — Commercial"],
        )
        assert req.name == "AI Visual Master"
        assert req.prerequisite_count is None
        assert req.auto_issue is True

    def test_rejects_single_prerequisite(self):
        with pytest.raises(ValidationError):
            CreatePathwayRequest(
                name="Bad",
                pathway_credential_type="X",
                prerequisite_credential_types=["only-one"],
            )

    def test_rejects_empty_prerequisite_types(self):
        with pytest.raises(ValidationError):
            CreatePathwayRequest(
                name="Bad",
                pathway_credential_type="X",
                prerequisite_credential_types=["valid", ""],
            )

    def test_custom_prerequisite_count(self):
        req = CreatePathwayRequest(
            name="Elective Path",
            pathway_credential_type="Elective — Complete",
            prerequisite_credential_types=["A", "B", "C", "D", "E"],
            prerequisite_count=3,
        )
        assert req.prerequisite_count == 3

    def test_rejects_zero_prerequisite_count(self):
        with pytest.raises(ValidationError):
            CreatePathwayRequest(
                name="Bad",
                pathway_credential_type="X",
                prerequisite_credential_types=["A", "B"],
                prerequisite_count=0,
            )


class TestUpdatePathwayRequest:
    def test_valid_status(self):
        req = UpdatePathwayRequest(status="archived")
        assert req.status == "archived"

    def test_invalid_status(self):
        with pytest.raises(ValidationError):
            UpdatePathwayRequest(status="deleted")

    def test_partial_update(self):
        req = UpdatePathwayRequest(name="Updated Name")
        assert req.name == "Updated Name"
        assert req.status is None


class TestPathwayResponse:
    def test_from_attributes(self):
        assert PathwayResponse.model_config.get("from_attributes") is True


class TestPathwayProgressResponse:
    def test_complete(self):
        progress = PathwayProgressResponse(
            completed=True,
            pathway_id="path1",
            pathway_name="Master Path",
            target_credential_type="Master",
            required_count=2,
            earned_count=2,
            earned_credentials=[
                {"credential_type": "A", "issued_at": "2026-01-01"},
                {"credential_type": "B", "issued_at": "2026-02-01"},
            ],
            missing_credential_types=[],
        )
        assert progress.completed is True
        assert progress.earned_count == 2
        assert progress.missing_credential_types == []

    def test_partial(self):
        progress = PathwayProgressResponse(
            completed=False,
            pathway_id="path1",
            pathway_name="Master Path",
            target_credential_type="Master",
            required_count=3,
            earned_count=1,
            earned_credentials=[{"credential_type": "A", "issued_at": None}],
            missing_credential_types=["B", "C"],
        )
        assert progress.completed is False
        assert len(progress.missing_credential_types) == 2


class TestCredentialPathwayServiceValidation:
    """Test service validation logic (no DB)."""

    def test_prerequisite_count_default_to_all(self):
        # When prerequisite_count is None, it should default to len(prerequisites)
        # This is tested via the service, but we verify the schema allows None
        req = CreatePathwayRequest(
            name="Test",
            pathway_credential_type="Test — Master",
            prerequisite_credential_types=["A", "B", "C"],
        )
        assert req.prerequisite_count is None

    def test_n_of_m_pattern(self):
        # "earn 2 of 4 electives"
        req = CreatePathwayRequest(
            name="Elective Path",
            pathway_credential_type="Elective — Complete",
            prerequisite_credential_types=["A", "B", "C", "D"],
            prerequisite_count=2,
        )
        assert req.prerequisite_count == 2
        assert len(req.prerequisite_credential_types) == 4

    def test_max_20_prerequisites(self):
        # 20 should be allowed
        types = [f"type_{i}" for i in range(20)]
        req = CreatePathwayRequest(
            name="Big Path",
            pathway_credential_type="Big — Master",
            prerequisite_credential_types=types,
        )
        assert len(req.prerequisite_credential_types) == 20
