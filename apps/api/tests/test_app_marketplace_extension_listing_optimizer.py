from app.services.app_marketplace_extension_listing_optimizer import (
    ListingOptimizerService, ListingData,
)


def test_perfect_listing():
    svc = ListingOptimizerService()
    listing = ListingData(
        title="Slack Integration Pro",
        short_description="Connect your workspace to Slack with real-time notifications and two-way sync for teams.",
        long_description="# Overview\n" + "Feature details. " * 50 + "\n## Installation\nSteps here.\n## Usage\nGuide.",
        category="communication", tags=["slack", "notifications", "sync"],
        screenshots=["s1.png", "s2.png", "s3.png", "s4.png", "s5.png"],
        icon_url="icon.png", demo_url="https://demo.example.com",
        documentation_url="https://docs.example.com",
        changelog="v1.0\nv1.1\nv1.2\nv1.3\nv1.4\nv1.5",
        pricing_info="Free / $9.99 Pro",
    )
    score = svc.analyze(listing)
    assert score.total >= 90
    assert score.grade == "A"


def test_empty_listing():
    svc = ListingOptimizerService()
    score = svc.analyze(ListingData())
    assert score.total == 0
    assert score.grade == "F"
    assert len(score.suggestions) > 5


def test_partial_listing():
    svc = ListingOptimizerService()
    listing = ListingData(
        title="My Extension", short_description="A good tool for developers",
        category="tools", tags=["dev"],
    )
    score = svc.analyze(listing)
    assert 20 <= score.total <= 50
    assert score.grade in ("D", "F")


def test_suggestions_actionable():
    svc = ListingOptimizerService()
    listing = ListingData(title="X")
    score = svc.analyze(listing)
    assert any("10-60" in s for s in score.suggestions)


def test_all_caps_penalty():
    svc = ListingOptimizerService()
    listing = ListingData(title="MY EXTENSION NAME HERE")
    score = svc.analyze(listing)
    assert any("ALL CAPS" in s for s in score.suggestions)


def test_sections_have_max():
    svc = ListingOptimizerService()
    score = svc.analyze(ListingData(title="Test Extension"))
    assert all("max" in v for v in score.sections.values())
    assert sum(v["max"] for v in score.sections.values()) == 100
