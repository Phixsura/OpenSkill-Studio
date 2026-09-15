"""Portfolio showcase tests — pure logic, no DB needed."""

from datetime import UTC, datetime

from app.talent.services.portfolio_showcase import (
    PORTFOLIO_ITEM_TYPES,
    PORTFOLIO_VISIBILITY,
    PortfolioItem,
    PortfolioShowcaseService,
)

svc = PortfolioShowcaseService()


def _item(**kw) -> PortfolioItem:
    defaults = {
        "id": "i1", "user_id": "u1", "item_type": "project",
        "title": "Test", "description": "Desc", "url": "https://example.com",
        "image_url": None, "capability_ids": ["c1"],
        "visibility": "public", "pinned": False, "sort_order": 0,
        "created_at": datetime.now(UTC),
    }
    defaults.update(kw)
    return PortfolioItem(**defaults)


class TestConstants:
    def test_item_types(self):
        assert "project" in PORTFOLIO_ITEM_TYPES
        assert "case_study" in PORTFOLIO_ITEM_TYPES
        assert len(PORTFOLIO_ITEM_TYPES) == 10

    def test_visibility(self):
        assert "private" in PORTFOLIO_VISIBILITY
        assert "public" in PORTFOLIO_VISIBILITY


class TestAssessQuality:
    def test_empty_portfolio(self):
        q = svc.assess_quality([])
        assert q.quality_score == 0.0
        assert "first portfolio item" in q.suggestions[0].lower()

    def test_good_portfolio(self):
        items = [
            _item(id="1", item_type="commercial_deliverable", url="https://a.com", image_url="https://img.com", capability_ids=["c1", "c2"]),
            _item(id="2", item_type="open_source", url="https://b.com", capability_ids=["c3"]),
            _item(id="3", url="https://c.com", capability_ids=["c4", "c5"]),
            _item(id="4", url="https://d.com", capability_ids=["c6"]),
            _item(id="5", url="https://e.com"),
        ]
        q = svc.assess_quality(items)
        assert q.quality_score > 60
        assert q.has_commercial_work is True
        assert q.has_open_source is True
        assert q.total_items == 5

    def test_private_portfolio_suggestions(self):
        items = [_item(id="1", visibility="private")]
        q = svc.assess_quality(items)
        assert any("public" in s.lower() for s in q.suggestions)

    def test_no_urls_suggestion(self):
        items = [_item(id="1", url=None)]
        q = svc.assess_quality(items)
        assert any("url" in s.lower() for s in q.suggestions)

    def test_capability_coverage(self):
        items = [
            _item(id="1", capability_ids=["c1", "c2"]),
            _item(id="2", capability_ids=["c3", "c4", "c5"]),
        ]
        q = svc.assess_quality(items)
        assert q.capability_coverage == 5


class TestReorder:
    def test_reorder_items(self):
        items = [
            {"id": "a", "sort_order": 0},
            {"id": "b", "sort_order": 1},
            {"id": "c", "sort_order": 2},
        ]
        result = svc.reorder_items(items, ["c", "a", "b"])
        assert result[0]["id"] == "c"
        assert result[0]["sort_order"] == 0
        assert result[1]["id"] == "a"

    def test_preserves_unmentioned(self):
        items = [
            {"id": "a", "sort_order": 0},
            {"id": "b", "sort_order": 1},
        ]
        result = svc.reorder_items(items, ["b"])
        assert len(result) == 2
        assert result[0]["id"] == "b"
