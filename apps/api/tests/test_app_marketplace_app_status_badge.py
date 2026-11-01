from app.services.app_marketplace_app_status_badge import generate_badge_svg

def test_badge():
    r = generate_badge_svg(label="MyApp", status="operational")
    assert r["content_type"] == "image/svg+xml"
    assert "<svg" in r["svg"]
    assert "#22c55e" in r["svg"]  # green for operational
    assert "MyApp" in r["svg"]

def test_xss():
    r = generate_badge_svg(label="<script>", status="op")
    assert "<script>" not in r["svg"]
    assert "&lt;script&gt;" in r["svg"]

def test_markdown():
    r = generate_badge_svg(label="Status", status="degraded")
    assert "![Status]" in r["markdown"]
