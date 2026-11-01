from app.services.app_support_info import build_support_info

def test_with_email():
    s = build_support_info(email="dev@x.com")
    assert s["has_support"] is True
    assert len(s["channels"]) == 1

def test_all_channels():
    s = build_support_info(email="a@b.c", docs_url="https://docs.x.com", issues_url="https://github.com/x/issues")
    assert len(s["channels"]) == 3

def test_no_support():
    s = build_support_info()
    assert s["has_support"] is False
