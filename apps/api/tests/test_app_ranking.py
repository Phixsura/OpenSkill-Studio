"""App ranking service tests."""

import pytest
from app.services.app_ranking import compute_ranking_score, rank_apps

def test_baseline():
    score = compute_ranking_score()
    assert 0 <= score <= 100

def test_popular_app_higher():
    pop = compute_ranking_score(install_count=1000)
    unpop = compute_ranking_score(install_count=0)
    assert pop > unpop

def test_healthy_app_higher():
    healthy = compute_ranking_score(health_score=100)
    unhealthy = compute_ranking_score(health_score=20)
    assert healthy > unhealthy

def test_recent_app_higher():
    recent = compute_ranking_score(days_since_update=1)
    old = compute_ranking_score(days_since_update=365)
    assert recent > old

def test_rated_app_higher():
    rated = compute_ranking_score(rating=4.5, rating_count=50)
    unrated = compute_ranking_score(rating=0, rating_count=0)
    assert rated > unrated

def test_score_bounded():
    max_score = compute_ranking_score(install_count=100000, health_score=100, days_since_update=0, rating=5.0, rating_count=100)
    assert max_score <= 100

def test_rank_apps_order():
    apps = [
        {"name": "unpopular", "install_count": 0},
        {"name": "popular", "install_count": 5000},
        {"name": "mid", "install_count": 100},
    ]
    ranked = rank_apps(apps)
    assert ranked[0]["name"] == "popular"
    assert ranked[-1]["name"] == "unpopular"

def test_rank_apps_adds_score():
    apps = [{"name": "a", "install_count": 10}]
    ranked = rank_apps(apps)
    assert "_ranking_score" in ranked[0]
