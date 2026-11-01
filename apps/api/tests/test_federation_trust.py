"""Tests for federation trust policy evaluation logic (unit, no DB)."""

import pytest

from app.services.federation_trust import FederationTrustService


class TestMatchesConditions:
    """Unit tests for TrustPolicy condition matching (static method, no DB)."""

    def test_no_conditions_matches_all(self):
        assert FederationTrustService._matches_conditions(None, {"name": "anything"}) is True
        assert FederationTrustService._matches_conditions({}, {"name": "anything"}) is True

    def test_no_artifact_matches(self):
        assert FederationTrustService._matches_conditions({"categories": ["ai"]}, None) is True

    def test_category_filter_matches(self):
        conditions = {"categories": ["ai", "design"]}
        assert FederationTrustService._matches_conditions(
            conditions, {"category": "ai", "name": "test"}
        ) is True

    def test_category_filter_rejects(self):
        conditions = {"categories": ["ai", "design"]}
        assert FederationTrustService._matches_conditions(
            conditions, {"category": "finance", "name": "test"}
        ) is False

    def test_min_version_passes(self):
        conditions = {"min_version": "1.0"}
        assert FederationTrustService._matches_conditions(
            conditions, {"version": "2.0.0"}
        ) is True

    def test_min_version_rejects(self):
        conditions = {"min_version": "2.0"}
        assert FederationTrustService._matches_conditions(
            conditions, {"version": "1.5.0"}
        ) is False

    def test_required_tags_matches(self):
        conditions = {"required_tags": ["react", "typescript"]}
        assert FederationTrustService._matches_conditions(
            conditions, {"tags": ["react", "typescript", "frontend"]}
        ) is True

    def test_required_tags_rejects_partial(self):
        conditions = {"required_tags": ["react", "typescript"]}
        assert FederationTrustService._matches_conditions(
            conditions, {"tags": ["react"]}
        ) is False

    def test_required_tags_rejects_empty(self):
        conditions = {"required_tags": ["react"]}
        assert FederationTrustService._matches_conditions(
            conditions, {"tags": []}
        ) is False

    def test_combined_conditions(self):
        conditions = {"categories": ["ai"], "min_version": "1.0", "required_tags": ["ml"]}
        # All match
        assert FederationTrustService._matches_conditions(
            conditions, {"category": "ai", "version": "2.0", "tags": ["ml", "data"]}
        ) is True
        # Category fails
        assert FederationTrustService._matches_conditions(
            conditions, {"category": "web", "version": "2.0", "tags": ["ml"]}
        ) is False
        # Version fails
        assert FederationTrustService._matches_conditions(
            conditions, {"category": "ai", "version": "0.5", "tags": ["ml"]}
        ) is False
        # Tags fail
        assert FederationTrustService._matches_conditions(
            conditions, {"category": "ai", "version": "2.0", "tags": ["data"]}
        ) is False
