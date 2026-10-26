from app.services.app_marketplace_extension_sharing import ExtensionSharingService


def test_create_share():
    svc = ExtensionSharingService()
    link = svc.create_share_link("ext-1")
    assert "ext-1" in link.url
    assert "iframe" in link.embed_code


def test_record_view():
    svc = ExtensionSharingService()
    link = svc.create_share_link("ext-1")
    svc.record_view(link.link_id, "twitter")
    svc.record_view(link.link_id, "twitter")
    svc.record_view(link.link_id, "linkedin")
    assert link.views == 3
    referrals = svc.get_referral_stats("ext-1")
    assert referrals["twitter"] == 2


def test_conversion():
    svc = ExtensionSharingService()
    link = svc.create_share_link("ext-1")
    for _ in range(10):
        svc.record_view(link.link_id)
    svc.record_install(link.link_id)
    stats = svc.get_share_stats(link.link_id)
    assert stats["conversion_rate"] == 10.0


def test_social_urls():
    svc = ExtensionSharingService()
    urls = svc.get_social_urls("ext-1", "Slack Bot")
    assert "twitter" in urls["twitter"]
    assert "Slack Bot" in urls["twitter"]
