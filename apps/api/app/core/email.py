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
    # R113[H1]: silently returning the console sender in production meant
    # every email (verification, password reset, billing notices) was
    # log-only and undelivered with zero signal. Until a real provider
    # lands (Phase 2+), production logs LOUDLY per send so ops can see the
    # gap — and the boot log warns once.
    from app.config import settings

    if settings.app_env == "production":
        log.error(
            "email_sender_unconfigured",
            detail="No production email provider configured — emails are NOT delivered",
        )
    return ConsoleEmailSender()
