"""Tests for App Feedback Collector — ratings, sentiment, summary, moderation."""

import pytest

from app.services.app_feedback_collector import (
    AppFeedbackCollector,
    FeedbackStatus,
    Sentiment,
    classify_sentiment,
)


class TestSentiment:
    def test_high_rating_positive(self):
        assert classify_sentiment(5, "great") == Sentiment.POSITIVE

    def test_low_rating_negative(self):
        assert classify_sentiment(1, "terrible") == Sentiment.NEGATIVE

    def test_neutral_rating_neutral(self):
        assert classify_sentiment(3, "it exists") == Sentiment.NEUTRAL

    def test_neutral_with_neg_words(self):
        assert classify_sentiment(3, "has a bug") == Sentiment.NEGATIVE

    def test_neutral_with_pos_words(self):
        assert classify_sentiment(3, "works fine") == Sentiment.POSITIVE


class TestSubmit:
    def test_submit_valid(self):
        c = AppFeedbackCollector()
        fb = c.submit("app-1", "user-1", 5, "Love it!")
        assert fb.rating == 5
        assert fb.sentiment == Sentiment.POSITIVE
        assert fb.status == FeedbackStatus.VISIBLE

    def test_invalid_rating_low(self):
        c = AppFeedbackCollector()
        with pytest.raises(ValueError, match="1 and 5"):
            c.submit("app-1", "user-1", 0)

    def test_invalid_rating_high(self):
        c = AppFeedbackCollector()
        with pytest.raises(ValueError):
            c.submit("app-1", "user-1", 6)

    def test_empty_user_rejected(self):
        c = AppFeedbackCollector()
        with pytest.raises(ValueError, match="user_id"):
            c.submit("app-1", "", 5)

    def test_unique_ids(self):
        c = AppFeedbackCollector()
        f1 = c.submit("app-1", "u1", 5)
        f2 = c.submit("app-1", "u2", 4)
        assert f1.feedback_id != f2.feedback_id


class TestSummary:
    def test_summary_stats(self):
        c = AppFeedbackCollector()
        c.submit("app-1", "u1", 5, "great")
        c.submit("app-1", "u2", 4, "good")
        c.submit("app-1", "u3", 2, "bad")
        s = c.get_summary("app-1")
        assert s.total_count == 3
        assert s.avg_rating == pytest.approx(3.67, abs=0.01)

    def test_distribution(self):
        c = AppFeedbackCollector()
        c.submit("app-1", "u1", 5)
        c.submit("app-1", "u2", 5)
        c.submit("app-1", "u3", 3)
        s = c.get_summary("app-1")
        assert s.distribution[5] == 2
        assert s.distribution[3] == 1
        assert s.distribution[1] == 0

    def test_sentiment_breakdown(self):
        c = AppFeedbackCollector()
        c.submit("app-1", "u1", 5)
        c.submit("app-1", "u2", 1)
        c.submit("app-1", "u3", 3)
        s = c.get_summary("app-1")
        assert s.sentiment_breakdown.get("positive", 0) >= 1
        assert s.sentiment_breakdown.get("negative", 0) >= 1

    def test_empty_summary(self):
        c = AppFeedbackCollector()
        s = c.get_summary("app-x")
        assert s.total_count == 0
        assert s.avg_rating == 0.0

    def test_recent_in_summary(self):
        c = AppFeedbackCollector()
        for i in range(10):
            c.submit("app-1", f"u{i}", 4)
        s = c.get_summary("app-1")
        assert len(s.recent) == 5  # capped at 5


class TestModeration:
    def test_flag(self):
        c = AppFeedbackCollector()
        fb = c.submit("app-1", "u1", 1, "spam")
        assert c.flag("app-1", fb.feedback_id) is True
        assert fb.status == FeedbackStatus.FLAGGED

    def test_hide(self):
        c = AppFeedbackCollector()
        fb = c.submit("app-1", "u1", 1, "spam")
        c.hide("app-1", fb.feedback_id)
        assert fb.status == FeedbackStatus.HIDDEN

    def test_hidden_excluded_from_summary(self):
        c = AppFeedbackCollector()
        fb = c.submit("app-1", "u1", 1, "spam")
        c.submit("app-1", "u2", 5, "great")
        c.hide("app-1", fb.feedback_id)
        s = c.get_summary("app-1")
        assert s.total_count == 1
        assert s.avg_rating == 5.0

    def test_hidden_excluded_from_listing(self):
        c = AppFeedbackCollector()
        fb = c.submit("app-1", "u1", 1)
        c.hide("app-1", fb.feedback_id)
        visible = c.get_feedback("app-1", visible_only=True)
        assert len(visible) == 0

    def test_flag_nonexistent(self):
        c = AppFeedbackCollector()
        assert c.flag("app-1", "fake") is False


class TestAvgRating:
    def test_avg(self):
        c = AppFeedbackCollector()
        c.submit("app-1", "u1", 5)
        c.submit("app-1", "u2", 3)
        assert c.get_avg_rating("app-1") == 4.0

    def test_empty_avg(self):
        c = AppFeedbackCollector()
        assert c.get_avg_rating("app-x") == 0.0
