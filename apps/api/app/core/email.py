"""Email sender abstraction. Phase 1: console only."""

from abc import ABC, abstractmethod

import structlog

log = structlog.get_logger()


class EmailSender(ABC):
    @abstractmethod
    async def send(self, to: str, subject: str, html: str) -> None: ...


class ConsoleEmailSender(EmailSender):
    """Development: print emails to console log."""

    async def send(self, to: str, subject: str, html: str) -> None:
        log.info("email_sent", to=to, subject=subject, body_preview=html[:200])


def get_email_sender() -> EmailSender:
    """Return the email sender appropriate for the current environment."""
    # Phase 2+: return ResendEmailSender() for production
    return ConsoleEmailSender()
