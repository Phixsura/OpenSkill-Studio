from app.services.app_marketplace_app_app_featured_banner import build_featured_banner

def test_banner():
    r = build_featured_banner(title="SDK v3 is here!", subtitle="New features",
                               cta_label="Learn More", cta_href="/blog/sdk-v3")
    assert r["title"] == "SDK v3 is here!"
    assert r["cta_href"] == "/blog/sdk-v3"
    assert r["dismissible"]

def test_bad_href():
    r = build_featured_banner(title="X", subtitle="Y", cta_label="Z",
                               cta_href="javascript:alert(1)")
    assert r["cta_href"] == "#"
