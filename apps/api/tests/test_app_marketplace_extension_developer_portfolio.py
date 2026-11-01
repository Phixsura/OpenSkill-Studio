from app.services.app_marketplace_extension_developer_portfolio import DeveloperPortfolioService


def test_create_and_get():
    svc = DeveloperPortfolioService()
    svc.create_or_update("dev-1", display_name="Alice", bio="Extension developer",
                         extensions=["ext-1", "ext-2"], total_installs=5000)
    p = svc.get("dev-1")
    assert p.display_name == "Alice"
    assert p.total_installs == 5000


def test_public_profile():
    svc = DeveloperPortfolioService()
    svc.create_or_update("dev-1", display_name="Bob", bio="Builder",
                         extensions=["a", "b", "c"], badges=["🏆"], avg_rating=4.8)
    pub = svc.get_public("dev-1")
    assert pub["extensions"] == 3
    assert pub["avg_rating"] == 4.8


def test_search():
    svc = DeveloperPortfolioService()
    svc.create_or_update("d1", display_name="Alice Chen")
    svc.create_or_update("d2", display_name="Bob Smith")
    results = svc.search("alice")
    assert len(results) == 1


def test_top_developers():
    svc = DeveloperPortfolioService()
    svc.create_or_update("d1", display_name="A", total_installs=100)
    svc.create_or_update("d2", display_name="B", total_installs=5000)
    svc.create_or_update("d3", display_name="C", total_installs=1000)
    top = svc.get_top_developers(2)
    assert top[0].display_name == "B"
    assert len(top) == 2
