from app.services.app_marketplace_extension_feedback_collector import (
    FeedbackCollector, FeedbackEntry,
)


def test_submit_and_get():
    fc = FeedbackCollector()
    fc.submit(FeedbackEntry("f1", "ext-1", "u1", "bug", "The app crashes on load"))
    fc.submit(FeedbackEntry("f2", "ext-1", "u2", "praise", "This extension is awesome and great!"))
    entries = fc.get_feedback("ext-1")
    assert len(entries) == 2


def test_sentiment_detection():
    fc = FeedbackCollector()
    fc.submit(FeedbackEntry("f1", "ext-2", "u1", "praise", "Love this great extension!"))
    fc.submit(FeedbackEntry("f2", "ext-2", "u2", "bug", "Terrible crash bug, broken"))
    fc.submit(FeedbackEntry("f3", "ext-2", "u3", "question", "How do I configure it?"))
    positive = fc.get_feedback("ext-2", sentiment="positive")
    negative = fc.get_feedback("ext-2", sentiment="negative")
    neutral = fc.get_feedback("ext-2", sentiment="neutral")
    assert len(positive) == 1
    assert len(negative) == 1
    assert len(neutral) == 1


def test_respond():
    fc = FeedbackCollector()
    fc.submit(FeedbackEntry("f1", "ext-3", "u1", "bug", "Error on save"))
    assert fc.respond("ext-3", "f1", "Fixed in v2.1.0") is True
    entries = fc.get_feedback("ext-3")
    assert entries[0].responded is True
    assert entries[0].response == "Fixed in v2.1.0"


def test_sentiment_breakdown():
    fc = FeedbackCollector()
    fc.submit(FeedbackEntry("f1", "ext-4", "u1", "praise", "Amazing tool, love it!"))
    fc.submit(FeedbackEntry("f2", "ext-4", "u2", "praise", "Great and helpful"))
    fc.submit(FeedbackEntry("f3", "ext-4", "u3", "bug", "Slow and broken"))
    fc.respond("ext-4", "f3", "Looking into it")
    breakdown = fc.get_sentiment_breakdown("ext-4")
    assert breakdown["total"] == 3
    assert breakdown["breakdown"]["positive"] == 2
    assert breakdown["satisfaction_score"] > 60
    assert breakdown["response_rate"] > 30


def test_top_categories():
    fc = FeedbackCollector()
    fc.submit(FeedbackEntry("f1", "ext-5", "u1", "bug", "crash"))
    fc.submit(FeedbackEntry("f2", "ext-5", "u2", "bug", "error"))
    fc.submit(FeedbackEntry("f3", "ext-5", "u3", "feature_request", "dark mode"))
    top = fc.get_top_categories("ext-5")
    assert top[0]["category"] == "bug"
    assert top[0]["count"] == 2
