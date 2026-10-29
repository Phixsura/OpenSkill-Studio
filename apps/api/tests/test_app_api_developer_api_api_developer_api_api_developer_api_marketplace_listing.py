import pytest
from app.services.app_api_developer_api_api_developer_api_api_developer_api_marketplace_listing import AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiMarketplaceListing

class TestMarketplaceListing:
    def test_create(self):
        m = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiMarketplaceListing()
        l = m.create("inst-1", "l1", "My App", "Great app", "devtools", "free")
        assert l.status == "draft"

    def test_publish(self):
        m = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiMarketplaceListing()
        m.create("inst-1", "l1", "App", "Description", "analytics", "freemium")
        l = m.publish("inst-1", "l1")
        assert l.status == "published"

    def test_install(self):
        m = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiMarketplaceListing()
        m.create("inst-1", "l1", "App", "Desc", "security", "paid")
        m.publish("inst-1", "l1")
        m.install("inst-1", "l1")
        assert m.popular("inst-1")[0].installs == 1

    def test_install_unpublished_rejected(self):
        m = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiMarketplaceListing()
        m.create("inst-1", "l1", "App", "Desc", "devtools", "free")
        with pytest.raises(ValueError, match="published"):
            m.install("inst-1", "l1")

    def test_by_category(self):
        m = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiMarketplaceListing()
        m.create("inst-1", "l1", "A", "D", "devtools", "free")
        m.create("inst-1", "l2", "B", "D", "analytics", "free")
        m.publish("inst-1", "l1")
        m.publish("inst-1", "l2")
        assert len(m.by_category("inst-1", "devtools")) == 1

    def test_isolation(self):
        m = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiMarketplaceListing()
        m.create("inst-1", "l1", "A", "D", "devtools", "free")
        assert len(m.all_listings("inst-2")) == 0
