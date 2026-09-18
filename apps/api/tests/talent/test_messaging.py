"""Messaging service tests — pure logic, no DB needed."""

from datetime import UTC, datetime

import pytest

from app.talent.services.messaging import (
    MESSAGE_TYPES,
    ApplicationMessage,
    MessagingService,
)

svc = MessagingService()


def _msg(**kw) -> ApplicationMessage:
    defaults = {
        "id": "m1",
        "application_id": "a1",
        "sender_id": "u1",
        "sender_role": "candidate",
        "message_type": "text",
        "content": "Hello",
        "attachments": [],
        "read_at": None,
        "created_at": datetime.now(UTC),
    }
    defaults.update(kw)
    return ApplicationMessage(**defaults)


class TestMessageTypes:
    def test_all_types(self):
        assert "text" in MESSAGE_TYPES
        assert "interview_details" in MESSAGE_TYPES
        assert "system" in MESSAGE_TYPES
        assert len(MESSAGE_TYPES) == 6


class TestCreateMessage:
    def test_valid_message(self):
        m = svc.create_message(
            message_id="m1",
            application_id="a1",
            sender_id="u1",
            sender_role="candidate",
            content="Hi",
        )
        assert m.content == "Hi"
        assert m.message_type == "text"
        assert m.read_at is None

    def test_invalid_type(self):
        with pytest.raises(ValueError, match="Invalid message_type"):
            svc.create_message(
                message_id="m1",
                application_id="a1",
                sender_id="u1",
                sender_role="candidate",
                message_type="invalid",
                content="Hi",
            )

    def test_invalid_role(self):
        with pytest.raises(ValueError, match="Invalid sender_role"):
            svc.create_message(
                message_id="m1",
                application_id="a1",
                sender_id="u1",
                sender_role="admin",
                content="Hi",
            )

    def test_empty_content(self):
        with pytest.raises(ValueError, match="Content"):
            svc.create_message(
                message_id="m1",
                application_id="a1",
                sender_id="u1",
                sender_role="candidate",
                content="",
            )

    def test_with_attachments(self):
        m = svc.create_message(
            message_id="m1",
            application_id="a1",
            sender_id="u1",
            sender_role="employer",
            content="See attached",
            attachments=[{"name": "resume.pdf", "url": "https://..."}],
        )
        assert len(m.attachments) == 1


class TestSystemMessage:
    def test_creates_system_message(self):
        m = svc.create_system_message(
            message_id="m1",
            application_id="a1",
            content="Application moved to interview stage",
        )
        assert m.sender_id == "system"
        assert m.message_type == "system"


class TestThreadSummary:
    def test_empty_thread(self):
        t = svc.compute_thread_summary([])
        assert t.total_messages == 0
        assert t.unread_count == 0

    def test_with_messages(self):
        now = datetime.now(UTC)
        msgs = [
            _msg(id="1", content="Hi", created_at=now),
            _msg(
                id="2",
                sender_id="u2",
                sender_role="employer",
                content="Hello",
                read_at=now,
                created_at=now,
            ),
        ]
        t = svc.compute_thread_summary(msgs)
        assert t.total_messages == 2
        assert t.unread_count == 1
        assert len(t.participants) == 2

    def test_preview_truncation(self):
        msgs = [_msg(content="A" * 200)]
        t = svc.compute_thread_summary(msgs)
        assert t.last_message_preview is not None
        assert len(t.last_message_preview) <= 103  # 100 + "..."


class TestSearch:
    def test_finds_matching(self):
        msgs = [
            _msg(id="1", content="Python programming"),
            _msg(id="2", content="JavaScript basics"),
            _msg(id="3", content="Advanced Python"),
        ]
        results = svc.search_messages(msgs, "python")
        assert len(results) == 2

    def test_case_insensitive(self):
        msgs = [_msg(content="HELLO WORLD")]
        results = svc.search_messages(msgs, "hello")
        assert len(results) == 1

    def test_no_results(self):
        msgs = [_msg(content="Hello")]
        results = svc.search_messages(msgs, "xyz")
        assert len(results) == 0
