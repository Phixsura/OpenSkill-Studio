"""Candidate notes tests — schema validation, no DB needed."""

from pydantic import ValidationError

from app.talent.api.candidate_notes import (
    CreateNoteRequest,
    NoteResponse,
    UpdateNoteRequest,
)


class TestCreateNoteRequest:
    def test_valid_request(self):
        req = CreateNoteRequest(
            note_text="Great candidate for the AI role",
            tags=["strong", "follow-up"],
        )
        assert req.note_text == "Great candidate for the AI role"
        assert req.tags == ["strong", "follow-up"]

    def test_empty_text_rejected(self):
        try:
            CreateNoteRequest(note_text="", tags=[])
            raise AssertionError("Should reject empty text")
        except ValidationError:
            pass

    def test_max_length(self):
        req = CreateNoteRequest(note_text="x" * 5000, tags=[])
        assert len(req.note_text) == 5000

    def test_over_max_length_rejected(self):
        try:
            CreateNoteRequest(note_text="x" * 5001, tags=[])
            raise AssertionError("Should reject over-length text")
        except ValidationError:
            pass

    def test_default_tags_empty(self):
        req = CreateNoteRequest(note_text="note")
        assert req.tags == []

    def test_optional_opportunity_id(self):
        req = CreateNoteRequest(
            note_text="note",
            opportunity_id="01J123",
        )
        assert req.opportunity_id == "01J123"


class TestUpdateNoteRequest:
    def test_partial_update(self):
        req = UpdateNoteRequest(note_text="updated text")
        assert req.note_text == "updated text"
        assert req.tags is None

    def test_tags_only_update(self):
        req = UpdateNoteRequest(tags=["new-tag"])
        assert req.note_text is None
        assert req.tags == ["new-tag"]


class TestNoteResponse:
    def test_from_dict(self):
        resp = NoteResponse(
            id="01J123",
            org_id="org1",
            candidate_user_id="user1",
            author_id="author1",
            opportunity_id=None,
            note_text="A note",
            tags=["tag1"],
        )
        assert resp.id == "01J123"
        assert resp.candidate_user_id == "user1"
