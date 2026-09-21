"""In-app messaging — candidate-employer communication for applications.

Features:
  - Threaded messages per application (employer ↔ candidate)
  - Message types: text, status_update, document_request, interview_details
  - Read receipts
  - Auto-messages on application state transitions
  - Message search
  - Attachment references (links to assets, not file upload)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

MESSAGE_TYPES = frozenset(
    {
        "text",
        "status_update",
        "document_request",
        "interview_details",
        "offer_details",
        "system",
    }
)


@dataclass(frozen=True, slots=True)
class ApplicationMessage:
    id: str
    application_id: str
    sender_id: str
    sender_role: str  # "candidate" or "employer"
    message_type: str
    content: str
    attachments: list[dict]  # [{name, url, type}]
    read_at: datetime | None
    created_at: datetime


@dataclass(frozen=True, slots=True)
class MessageThread:
    application_id: str
    total_messages: int
    unread_count: int
    last_message_at: datetime | None
    last_message_preview: str | None
    participants: list[str]


@dataclass(frozen=True, slots=True)
class MessageStats:
    total_threads: int
    unread_threads: int
    avg_response_time_hours: float | None
    total_messages_sent: int
    total_messages_received: int


class MessagingService:
    def create_message(
        self,
        *,
        message_id: str,
        application_id: str,
        sender_id: str,
        sender_role: str,
        message_type: str = "text",
        content: str,
        attachments: list[dict] | None = None,
    ) -> ApplicationMessage:
        """Create a new message in an application thread."""
        if message_type not in MESSAGE_TYPES:
            raise ValueError(f"Invalid message_type: {message_type}")
        if sender_role not in ("candidate", "employer"):
            raise ValueError(f"Invalid sender_role: {sender_role}")
        if not content or len(content) > 10000:
            raise ValueError("Content must be 1-10000 characters")

        return ApplicationMessage(
            id=message_id,
            application_id=application_id,
            sender_id=sender_id,
            sender_role=sender_role,
            message_type=message_type,
            content=content,
            attachments=attachments or [],
            read_at=None,
            created_at=datetime.now(UTC),
        )

    def create_system_message(
        self,
        *,
        message_id: str,
        application_id: str,
        content: str,
    ) -> ApplicationMessage:
        """Create a system-generated message (e.g., status change notification)."""
        return ApplicationMessage(
            id=message_id,
            application_id=application_id,
            sender_id="system",
            sender_role="employer",
            message_type="system",
            content=content,
            attachments=[],
            read_at=None,
            created_at=datetime.now(UTC),
        )

    def compute_thread_summary(
        self,
        messages: list[ApplicationMessage],
    ) -> MessageThread:
        """Compute thread summary from messages."""
        if not messages:
            return MessageThread(
                application_id="",
                total_messages=0,
                unread_count=0,
                last_message_at=None,
                last_message_preview=None,
                participants=[],
            )

        app_id = messages[0].application_id
        unread = sum(1 for m in messages if m.read_at is None)
        last = max(messages, key=lambda m: m.created_at)
        participants = list({m.sender_id for m in messages if m.sender_id != "system"})
        preview = last.content[:100] + "..." if len(last.content) > 100 else last.content

        return MessageThread(
            application_id=app_id,
            total_messages=len(messages),
            unread_count=unread,
            last_message_at=last.created_at,
            last_message_preview=preview,
            participants=participants,
        )

    def compute_stats(
        self,
        threads: list[MessageThread],
    ) -> MessageStats:
        """Compute messaging statistics."""
        total = len(threads)
        unread = sum(1 for t in threads if t.unread_count > 0)

        return MessageStats(
            total_threads=total,
            unread_threads=unread,
            avg_response_time_hours=None,
            total_messages_sent=sum(t.total_messages for t in threads),
            total_messages_received=0,
        )

    def search_messages(
        self,
        messages: list[ApplicationMessage],
        query: str,
    ) -> list[ApplicationMessage]:
        """Search messages by content (case-insensitive)."""
        q = query.lower()
        return [m for m in messages if q in m.content.lower()]
