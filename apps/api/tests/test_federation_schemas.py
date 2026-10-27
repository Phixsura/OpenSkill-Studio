"""Tests for federation Pydantic schemas — validation rules."""

import pytest
from pydantic import ValidationError

from app.schemas.federation import (
    AddPeerRequest,
    CreateResidencyPolicyRequest,
    CreateTrustPolicyRequest,
    FederatedSearchRequest,
    UpdatePeerRequest,
)


class TestAddPeerRequest:
    def test_valid_https_uri(self):
        r = AddPeerRequest(instance_uri="https://school-b.openskill.io")
        assert r.instance_uri == "https://school-b.openskill.io"

    def test_strips_trailing_slash(self):
        r = AddPeerRequest(instance_uri="https://school-b.openskill.io/")
        assert r.instance_uri == "https://school-b.openskill.io"

    def test_rejects_http(self):
        with pytest.raises(ValidationError, match="https://"):
            AddPeerRequest(instance_uri="http://insecure.example.com")

    def test_rejects_empty(self):
        with pytest.raises(ValidationError):
            AddPeerRequest(instance_uri="")

    def test_rejects_too_long(self):
        with pytest.raises(ValidationError, match="500"):
            AddPeerRequest(instance_uri="https://" + "a" * 500 + ".com")


class TestUpdatePeerRequest:
    def test_valid_trust_status(self):
        r = UpdatePeerRequest(trust_status="trusted")
        assert r.trust_status == "trusted"

    def test_rejects_invalid_trust_status(self):
        with pytest.raises(ValidationError, match="trust_status"):
            UpdatePeerRequest(trust_status="invalid_status")

    def test_all_valid_statuses(self):
        for status in ("pending", "trusted", "suspended", "revoked"):
            r = UpdatePeerRequest(trust_status=status)
            assert r.trust_status == status


class TestCreateTrustPolicyRequest:
    def test_valid_policy(self):
        r = CreateTrustPolicyRequest(artifact_type="all", action="accept")
        assert r.artifact_type == "all"
        assert r.action == "accept"
        assert r.priority == 0
        assert r.enabled is True

    def test_rejects_invalid_artifact_type(self):
        with pytest.raises(ValidationError, match="artifact_type"):
            CreateTrustPolicyRequest(artifact_type="invalid", action="accept")

    def test_rejects_invalid_action(self):
        with pytest.raises(ValidationError, match="action"):
            CreateTrustPolicyRequest(artifact_type="all", action="invalid")

    def test_valid_with_conditions(self):
        r = CreateTrustPolicyRequest(
            artifact_type="registry_artifact",
            action="mirror",
            conditions={"categories": ["ai"]},
            priority=10,
        )
        assert r.conditions == {"categories": ["ai"]}
        assert r.priority == 10

    def test_priority_bounds(self):
        with pytest.raises(ValidationError):
            CreateTrustPolicyRequest(artifact_type="all", action="accept", priority=-1)
        with pytest.raises(ValidationError):
            CreateTrustPolicyRequest(artifact_type="all", action="accept", priority=1001)

    def test_all_artifact_types(self):
        for t in ("registry_artifact", "credential", "opportunity",
                   "marketplace_listing", "ecosystem_observation", "all"):
            r = CreateTrustPolicyRequest(artifact_type=t, action="accept")
            assert r.artifact_type == t

    def test_all_actions(self):
        for a in ("accept", "mirror", "reject"):
            r = CreateTrustPolicyRequest(artifact_type="all", action=a)
            assert r.action == a


class TestCreateResidencyPolicyRequest:
    def test_valid_policy(self):
        r = CreateResidencyPolicyRequest(
            policy_type="region_restrict",
            conditions={"allowed_regions": ["EU", "US"]},
        )
        assert r.policy_type == "region_restrict"
        assert r.enforcement == "block"

    def test_rejects_invalid_policy_type(self):
        with pytest.raises(ValidationError, match="policy_type"):
            CreateResidencyPolicyRequest(
                policy_type="invalid",
                conditions={},
            )

    def test_rejects_invalid_enforcement(self):
        with pytest.raises(ValidationError, match="enforcement"):
            CreateResidencyPolicyRequest(
                policy_type="region_restrict",
                conditions={},
                enforcement="invalid",
            )

    def test_all_enforcement_types(self):
        for e in ("block", "warn", "audit_only"):
            r = CreateResidencyPolicyRequest(
                policy_type="region_restrict",
                conditions={},
                enforcement=e,
            )
            assert r.enforcement == e


class TestFederatedSearchRequest:
    def test_valid_search(self):
        r = FederatedSearchRequest(query="react")
        assert r.query == "react"
        assert r.include_remote is True
        assert r.max_peers == 5
        assert r.timeout_ms == 3000

    def test_rejects_empty_query(self):
        with pytest.raises(ValidationError):
            FederatedSearchRequest(query="")

    def test_max_peers_bounds(self):
        with pytest.raises(ValidationError):
            FederatedSearchRequest(query="test", max_peers=0)
        with pytest.raises(ValidationError):
            FederatedSearchRequest(query="test", max_peers=21)

    def test_timeout_bounds(self):
        with pytest.raises(ValidationError):
            FederatedSearchRequest(query="test", timeout_ms=100)
        with pytest.raises(ValidationError):
            FederatedSearchRequest(query="test", timeout_ms=60000)
