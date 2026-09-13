"""Saved search tests — schema validation, service logic, constants."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from app.talent.models.saved_search import (
    NOTIFY_FREQUENCIES,
    SEARCH_TYPES,
)
from app.talent.schemas.saved_search import (
    CreateSavedSearchRequest,
    SavedSearchResponse,
    SavedSearchRunResponse,
    UpdateSavedSearchRequest,
)


class TestConstants:
    def test_search_types(self):
        assert "candidate" in SEARCH_TYPES
        assert "opportunity" in SEARCH_TYPES
        assert len(SEARCH_TYPES) == 2

    def test_notify_frequencies(self):
        assert "never" in NOTIFY_FREQUENCIES
        assert "daily" in NOTIFY_FREQUENCIES
        assert "weekly" in NOTIFY_FREQUENCIES
        assert "on_new_match" in NOTIFY_FREQUENCIES
        assert len(NOTIFY_FREQUENCIES) == 4


class TestCreateSchema:
    def test_valid_candidate_search(self):
        req = CreateSavedSearchRequest(
            name="Senior AI Designers",
            search_type="candidate",
            search_criteria={"opportunity_id": "opp123", "limit": 20},
        )
        assert req.name == "Senior AI Designers"
        assert req.search_type == "candidate"
        assert req.notify_frequency == "never"

    def test_valid_opportunity_search(self):
        req = CreateSavedSearchRequest(
            name="Remote AI Jobs",
            search_type="opportunity",
            search_criteria={"q": "AI", "location_mode": "remote"},
            notify_frequency="weekly",
        )
        assert req.search_type == "opportunity"
        assert req.notify_frequency == "weekly"

    def test_invalid_search_type(self):
        with pytest.raises(ValidationError, match="search_type"):
            CreateSavedSearchRequest(
                name="Test",
                search_type="invalid",
                search_criteria={},
            )

    def test_invalid_notify_frequency(self):
        with pytest.raises(ValidationError, match="notify_frequency"):
            CreateSavedSearchRequest(
                name="Test",
                search_type="candidate",
                search_criteria={},
                notify_frequency="hourly",
            )

    def test_name_too_long(self):
        with pytest.raises(ValidationError):
            CreateSavedSearchRequest(
                name="x" * 201,
                search_type="candidate",
                search_criteria={},
            )

    def test_name_empty(self):
        with pytest.raises(ValidationError):
            CreateSavedSearchRequest(
                name="",
                search_type="candidate",
                search_criteria={},
            )

    def test_description_optional(self):
        req = CreateSavedSearchRequest(
            name="Test",
            search_type="candidate",
            search_criteria={},
        )
        assert req.description is None

    def test_with_description(self):
        req = CreateSavedSearchRequest(
            name="Test",
            description="Looking for AI talent",
            search_type="candidate",
            search_criteria={"capability_ids": ["cap1"]},
        )
        assert req.description == "Looking for AI talent"


class TestUpdateSchema:
    def test_partial_update(self):
        req = UpdateSavedSearchRequest(name="Updated Name")
        assert req.name == "Updated Name"
        assert req.search_criteria is None

    def test_update_notify_frequency(self):
        req = UpdateSavedSearchRequest(notify_frequency="daily")
        assert req.notify_frequency == "daily"

    def test_invalid_notify_frequency(self):
        with pytest.raises(ValidationError, match="notify_frequency"):
            UpdateSavedSearchRequest(notify_frequency="every_minute")

    def test_update_criteria(self):
        req = UpdateSavedSearchRequest(
            search_criteria={"q": "new query", "location_mode": "hybrid"}
        )
        assert req.search_criteria["q"] == "new query"


class TestResponseSchema:
    def test_from_dict(self):
        resp = SavedSearchResponse(
            id="search1",
            org_id="org1",
            name="My Search",
            description=None,
            search_type="opportunity",
            search_criteria={"q": "test"},
            notify_frequency="never",
            last_run_at=None,
            result_count=0,
            created_by="user1",
        )
        assert resp.id == "search1"
        assert resp.result_count == 0

    def test_run_response(self):
        now = datetime.now(UTC)
        resp = SavedSearchRunResponse(
            search_id="search1",
            results=[{"id": "r1", "title": "Result"}],
            result_count=1,
            run_at=now,
        )
        assert resp.result_count == 1
        assert len(resp.results) == 1

    def test_with_last_run(self):
        now = datetime.now(UTC)
        resp = SavedSearchResponse(
            id="search1",
            org_id="org1",
            name="Search",
            description="Desc",
            search_type="candidate",
            search_criteria={},
            notify_frequency="weekly",
            last_run_at=now,
            result_count=42,
            created_by="user1",
        )
        assert resp.last_run_at == now
        assert resp.result_count == 42
