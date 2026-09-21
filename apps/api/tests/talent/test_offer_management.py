"""Offer management tests — pure logic, no DB needed."""

from app.talent.services.offer_management import (
    OFFER_STATUSES,
    OFFER_TRANSITIONS,
    OfferManagementService,
)

svc = OfferManagementService.__new__(OfferManagementService)


class TestOfferStatuses:
    def test_all_statuses_defined(self):
        assert len(OFFER_STATUSES) == 8

    def test_terminal_statuses_have_no_transitions(self):
        for s in ("accepted", "declined", "expired", "withdrawn"):
            assert OFFER_TRANSITIONS[s] == set()


class TestValidateTransition:
    def test_draft_to_sent(self):
        assert svc.validate_transition("draft", "sent")

    def test_sent_to_accepted(self):
        assert svc.validate_transition("sent", "accepted")

    def test_invalid_transition(self):
        assert not svc.validate_transition("accepted", "sent")

    def test_countered_to_sent(self):
        assert svc.validate_transition("countered", "sent")


class TestCreateOfferData:
    def test_creates_structure(self):
        data = svc.create_offer_data(
            application_id="app1",
            role_title="AI Designer",
            compensation_text="$50k-60k",
            expiry_days=14,
        )
        assert data["application_id"] == "app1"
        assert data["role_title"] == "AI Designer"
        assert data["status"] == "draft"
        assert data["negotiation_history"] == []
        assert "expires_at" in data

    def test_default_conditions_empty(self):
        data = svc.create_offer_data(application_id="a", role_title="r")
        assert data["conditions"] == []

    def test_custom_sections(self):
        data = svc.create_offer_data(
            application_id="a",
            role_title="r",
            custom_sections=[{"title": "Benefits", "content": "Health"}],
        )
        assert len(data["custom_sections"]) == 1


class TestCounterOffer:
    def test_adds_to_history(self):
        data = svc.create_offer_data(application_id="a", role_title="r")
        updated = svc.add_counter_offer(data, {"salary": "$65k"})
        assert updated["status"] == "countered"
        assert len(updated["negotiation_history"]) == 1
        assert updated["negotiation_history"][0]["details"]["salary"] == "$65k"


class TestOfferAnalytics:
    def test_empty_offers(self):
        result = svc.compute_offer_analytics([])
        assert result.total_offers == 0
        assert result.acceptance_rate == 0.0

    def test_with_offers(self):
        offers = [
            {"status": "accepted", "negotiation_history": [{"type": "counter"}]},
            {"status": "declined", "negotiation_history": []},
            {"status": "accepted", "negotiation_history": []},
        ]
        result = svc.compute_offer_analytics(offers)
        assert result.total_offers == 3
        assert abs(result.acceptance_rate - 0.667) < 0.01

    def test_negotiation_rounds(self):
        offers = [
            {"status": "accepted", "negotiation_history": [1, 2]},
            {"status": "accepted", "negotiation_history": []},
        ]
        result = svc.compute_offer_analytics(offers)
        assert result.avg_negotiation_rounds == 1.0
