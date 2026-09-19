"""Opportunity bookmark tests — schemas and constants."""

from pydantic import ValidationError

from app.talent.schemas.bookmark import BookmarkRequest, BookmarkResponse


class TestBookmarkRequest:
    def test_valid_with_notes(self):
        req = BookmarkRequest(notes="Interesting role")
        assert req.notes == "Interesting role"

    def test_valid_without_notes(self):
        req = BookmarkRequest()
        assert req.notes is None

    def test_notes_max_length(self):
        req = BookmarkRequest(notes="x" * 500)
        assert len(req.notes) == 500

    def test_notes_too_long(self):
        try:
            BookmarkRequest(notes="x" * 501)
            raise AssertionError("Should reject >500 chars")
        except ValidationError:
            pass

    def test_empty_notes(self):
        req = BookmarkRequest(notes="")
        assert req.notes == ""


class TestBookmarkResponse:
    def test_from_dict(self):
        data = {
            "id": "01ABC",
            "user_id": "u1",
            "opportunity_id": "o1",
            "notes": "Test",
            "created_at": None,
        }
        resp = BookmarkResponse(**data)
        assert resp.id == "01ABC"
        assert resp.opportunity_id == "o1"

    def test_none_notes(self):
        data = {
            "id": "01ABC",
            "user_id": "u1",
            "opportunity_id": "o1",
            "notes": None,
        }
        resp = BookmarkResponse(**data)
        assert resp.notes is None

    def test_from_attributes_config(self):
        assert BookmarkResponse.model_config.get("from_attributes") is True


class TestBookmarkModel:
    def test_table_name(self):
        from app.talent.models.bookmark import OpportunityBookmark

        assert OpportunityBookmark.__tablename__ == "talent_opportunity_bookmarks"

    def test_unique_constraint_exists(self):
        from app.talent.models.bookmark import OpportunityBookmark

        constraints = [
            c.name
            for c in OpportunityBookmark.__table__.constraints
            if hasattr(c, "name") and c.name
        ]
        assert "uq_user_opportunity_bookmark" in constraints
