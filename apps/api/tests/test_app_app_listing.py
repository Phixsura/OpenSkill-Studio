"""Tests for App Listing — create, publish, ratings, search."""

import pytest

from app.services.app_app_listing import AppAppListing, ListingStatus


class TestCreateListing:
    def test_create(self):
        l = AppAppListing()
        listing = l.create_listing("inst-1", "l1", "My App", "A great app", "tools", tags=["api", "dev"])
        assert listing.name == "My App"
        assert listing.status == ListingStatus.DRAFT

    def test_duplicate(self):
        l = AppAppListing()
        l.create_listing("inst-1", "l1", "App", "Desc", "tools")
        with pytest.raises(ValueError, match="already exists"):
            l.create_listing("inst-1", "l1", "App2", "Desc2", "tools")


class TestPublish:
    def test_publish(self):
        l = AppAppListing()
        l.create_listing("inst-1", "l1", "App", "Description", "tools")
        listing = l.publish("inst-1", "l1")
        assert listing.status == ListingStatus.PUBLISHED

    def test_publish_no_description(self):
        l = AppAppListing()
        l.create_listing("inst-1", "l1", "App", "", "tools")
        with pytest.raises(ValueError, match="description"):
            l.publish("inst-1", "l1")

    def test_unlist(self):
        l = AppAppListing()
        l.create_listing("inst-1", "l1", "App", "Desc", "tools")
        listing = l.unlist("inst-1", "l1")
        assert listing.status == ListingStatus.UNLISTED


class TestInstalls:
    def test_record(self):
        l = AppAppListing()
        l.create_listing("inst-1", "l1", "App", "Desc", "tools")
        l.record_install("inst-1", "l1")
        l.record_install("inst-1", "l1")
        assert l.get_listing("inst-1", "l1").install_count == 2


class TestRatings:
    def test_rating(self):
        l = AppAppListing()
        l.create_listing("inst-1", "l1", "App", "Desc", "tools")
        l.record_rating("inst-1", "l1", 5.0)
        l.record_rating("inst-1", "l1", 3.0)
        listing = l.get_listing("inst-1", "l1")
        assert listing.avg_rating == 4.0
        assert listing.rating_count == 2

    def test_invalid_rating(self):
        l = AppAppListing()
        l.create_listing("inst-1", "l1", "App", "Desc", "tools")
        with pytest.raises(ValueError, match="between 1 and 5"):
            l.record_rating("inst-1", "l1", 6)


class TestSearch:
    def test_search_by_name(self):
        l = AppAppListing()
        l.create_listing("inst-1", "l1", "Analytics Tool", "Track data", "tools")
        l.publish("inst-1", "l1")
        l.create_listing("inst-1", "l2", "Chat Widget", "Chat with users", "ui")
        l.publish("inst-1", "l2")
        results = l.search("inst-1", query="analytics")
        assert len(results) == 1

    def test_search_by_category(self):
        l = AppAppListing()
        l.create_listing("inst-1", "l1", "App A", "Desc", "tools")
        l.publish("inst-1", "l1")
        l.create_listing("inst-1", "l2", "App B", "Desc", "ui")
        l.publish("inst-1", "l2")
        results = l.search("inst-1", category="tools")
        assert len(results) == 1

    def test_only_published(self):
        l = AppAppListing()
        l.create_listing("inst-1", "l1", "App", "Desc", "tools")
        results = l.search("inst-1")
        assert len(results) == 0


class TestIsolation:
    def test_cross_installation(self):
        l = AppAppListing()
        l.create_listing("inst-1", "l1", "App", "Desc", "tools")
        with pytest.raises(KeyError):
            l.get_listing("inst-2", "l1")
