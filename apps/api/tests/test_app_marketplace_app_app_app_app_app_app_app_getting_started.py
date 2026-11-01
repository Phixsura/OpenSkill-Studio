from app.services.app_marketplace_app_app_app_app_app_app_app_getting_started import get_guide, list_guides, recommend_guide

def test_guide():
    g = get_guide("build_app")
    assert g["title"] == "Build Your First App"
    assert g["step_count"] == 4

def test_list():
    assert len(list_guides()) == 3

def test_recommend():
    assert recommend_guide(has_app=False, has_api_key=False, has_deploy=False) == "build_app"
    assert recommend_guide(has_app=True, has_api_key=False, has_deploy=False) == "integrate_api"
    assert recommend_guide(has_app=True, has_api_key=True, has_deploy=False) == "deploy"
