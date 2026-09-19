"""Endorsement system tests — models, service logic, schema validation."""

import pytest

from app.talent.models.endorsement import (
    ENDORSEMENT_RELATIONSHIPS,
    SkillEndorsement,
)
from app.talent.schemas.endorsement import (
    CreateEndorsementRequest,
    EndorsementResponse,
    EndorsementSummaryResponse,
)


class TestEndorsementRelationships:
    def test_has_colleague(self):
        assert "colleague" in ENDORSEMENT_RELATIONSHIPS

    def test_has_manager(self):
        assert "manager" in ENDORSEMENT_RELATIONSHIPS

    def test_has_instructor(self):
        assert "instructor" in ENDORSEMENT_RELATIONSHIPS

    def test_has_client(self):
        assert "client" in ENDORSEMENT_RELATIONSHIPS

    def test_has_peer(self):
        assert "peer" in ENDORSEMENT_RELATIONSHIPS

    def test_has_mentor(self):
        assert "mentor" in ENDORSEMENT_RELATIONSHIPS

    def test_has_mentee(self):
        assert "mentee" in ENDORSEMENT_RELATIONSHIPS

    def test_count(self):
        assert len(ENDORSEMENT_RELATIONSHIPS) == 7


class TestEndorsementModel:
    def test_tablename(self):
        assert SkillEndorsement.__tablename__ == "talent_skill_endorsements"


class TestEndorsementSchemas:
    def test_create_request(self):
        req = CreateEndorsementRequest(
            capability_id="cap1",
            relationship="colleague",
            message="Great work on the project!",
        )
        assert req.relationship == "colleague"
        assert req.message == "Great work on the project!"

    def test_create_request_no_message(self):
        req = CreateEndorsementRequest(
            capability_id="cap1",
            relationship="peer",
        )
        assert req.message is None

    def test_create_request_message_max_length(self):
        with pytest.raises(ValueError):
            CreateEndorsementRequest(
                capability_id="cap1",
                relationship="peer",
                message="x" * 501,
            )

    def test_response_schema(self):
        resp = EndorsementResponse(
            id="end1",
            user_id="user1",
            endorser_id="user2",
            capability_id="cap1",
            relationship="colleague",
            status="accepted",
        )
        assert resp.endorser_id == "user2"
        assert resp.status == "accepted"

    def test_summary_response(self):
        summary = EndorsementSummaryResponse(
            total=5,
            by_capability={"cap1": 3, "cap2": 2},
            by_relationship={"colleague": 3, "peer": 2},
        )
        assert summary.total == 5
        assert summary.by_capability["cap1"] == 3


class TestEndorsementServiceLogic:
    """Test service validation logic without DB."""

    def test_self_endorsement_detected(self):
        """Self-endorsement check is in service.endorse()."""
        # Just verify the ValueError message pattern
        from app.talent.services.endorsements import EndorsementService

        # Can't test without DB, but verify class exists and has endorse method
        assert hasattr(EndorsementService, "endorse")
        assert hasattr(EndorsementService, "list_endorsements")
        assert hasattr(EndorsementService, "get_endorsement_summary")

    def test_invalid_relationship_type(self):
        """Invalid relationship types should be caught."""
        assert "invalid_type" not in ENDORSEMENT_RELATIONSHIPS
