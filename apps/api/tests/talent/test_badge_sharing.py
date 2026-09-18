"""Badge sharing tests — pure logic, no DB needed."""

from datetime import UTC, datetime

from app.talent.services.badge_sharing import (
    SHARE_PLATFORMS,
    ShareLinks,
    generate_share_links,
)


class TestGenerateShareLinks:
    def test_basic_links(self):
        links = generate_share_links(
            credential_id="01ABC123",
            credential_name="AI Visual Design — Foundation",
            credential_type="AI Visual Design",
        )
        assert isinstance(links, ShareLinks)
        assert "01ABC123" in links.verify_url
        assert links.credential_id == "01ABC123"

    def test_linkedin_add_url(self):
        links = generate_share_links(
            credential_id="01ABC123",
            credential_name="Python Verified",
            credential_type="Python",
            issued_at=datetime(2026, 6, 15, tzinfo=UTC),
        )
        assert "linkedin.com/profile/add" in links.linkedin_add_url
        assert "Python+Verified" in links.linkedin_add_url or "Python%20Verified" in links.linkedin_add_url
        assert "issueYear=2026" in links.linkedin_add_url
        assert "issueMonth=6" in links.linkedin_add_url

    def test_linkedin_add_with_expiry(self):
        links = generate_share_links(
            credential_id="01ABC123",
            credential_name="Test Cred",
            credential_type="Test",
            issued_at=datetime(2026, 1, 1, tzinfo=UTC),
            expires_at=datetime(2027, 1, 1, tzinfo=UTC),
        )
        assert "expirationYear=2027" in links.linkedin_add_url

    def test_twitter_share_url(self):
        links = generate_share_links(
            credential_id="01ABC123",
            credential_name="AI Design",
            credential_type="AI Design",
        )
        assert "twitter.com/intent/tweet" in links.twitter_share_url
        assert "AI+Design" in links.twitter_share_url or "AI%20Design" in links.twitter_share_url

    def test_email_share_url(self):
        links = generate_share_links(
            credential_id="01ABC123",
            credential_name="Test",
            credential_type="Test",
        )
        assert links.email_share_url.startswith("mailto:")
        assert "subject=" in links.email_share_url

    def test_copy_url_has_utm(self):
        links = generate_share_links(
            credential_id="01ABC123",
            credential_name="Test",
            credential_type="Test",
        )
        assert "utm_source=copy" in links.copy_url
        assert "utm_medium=badge_share" in links.copy_url

    def test_custom_base_url(self):
        links = generate_share_links(
            credential_id="01ABC123",
            credential_name="Test",
            credential_type="Test",
            base_url="https://custom.example.com",
        )
        assert "custom.example.com" in links.verify_url

    def test_share_platforms_set(self):
        assert "linkedin" in SHARE_PLATFORMS
        assert "twitter" in SHARE_PLATFORMS
        assert "email" in SHARE_PLATFORMS
        assert "copy" in SHARE_PLATFORMS
