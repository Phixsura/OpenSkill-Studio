from app.services.app_marketplace_recommendation_engine import RecommendationEngine


def _setup() -> RecommendationEngine:
    re = RecommendationEngine()
    re.set_extension_metadata("slack", ["messaging", "notifications"], "communication")
    re.set_extension_metadata("github", ["git", "ci", "devtools"], "development")
    re.set_extension_metadata("jira", ["project", "tracking"], "management")
    re.set_extension_metadata("teams", ["messaging", "video"], "communication")
    re.set_extension_metadata("gitlab", ["git", "ci", "devtools"], "development")

    re.record_install("org-1", "slack")
    re.record_install("org-1", "github")
    re.record_install("org-2", "slack")
    re.record_install("org-2", "github")
    re.record_install("org-2", "jira")
    re.record_install("org-3", "slack")
    re.record_install("org-3", "teams")
    return re


def test_collaborative_filter():
    re = _setup()
    recs = re.collaborative_filter("org-1")
    ext_ids = [r.extension_id for r in recs]
    assert "jira" in ext_ids  # org-2 also uses slack+github AND jira


def test_content_based():
    re = _setup()
    recs = re.content_based("org-1")
    ext_ids = [r.extension_id for r in recs]
    # org-1 has slack (messaging) and github (git,ci,devtools)
    # teams has messaging overlap, gitlab has git/ci/devtools overlap
    assert "teams" in ext_ids or "gitlab" in ext_ids


def test_combined():
    re = _setup()
    recs = re.get_recommendations("org-1")
    assert len(recs) > 0
    assert all(r.score > 0 for r in recs)


def test_popular():
    re = _setup()
    popular = re.get_popular(3)
    assert popular[0] == "slack"  # installed by all 3 orgs


def test_exclude_installed():
    re = _setup()
    recs = re.collaborative_filter("org-1")
    installed = {"slack", "github"}
    assert all(r.extension_id not in installed for r in recs)


def test_empty_org():
    re = _setup()
    assert re.get_recommendations("new-org") == []
