from app.services.app_marketplace_extension_mktplace_feedback import MktplaceFeedbackService

def test_submit():
    svc = MktplaceFeedbackService()
    fb = svc.submit("u1", "bug", "Login page broken", 2)
    assert fb.category == "bug"
    assert fb.rating == 2

def test_nps():
    svc = MktplaceFeedbackService()
    svc.submit("u1", "praise", "Love it!", 5)
    svc.submit("u2", "praise", "Great!", 5)
    svc.submit("u3", "bug", "Broken", 1)
    nps = svc.get_nps()
    # 2 promoters, 1 detractor, 3 total: (2-1)/3*100 = 33.3
    assert nps == 33.3

def test_respond():
    svc = MktplaceFeedbackService()
    fb = svc.submit("u1", "feature", "Dark mode please")
    svc.respond(fb.feedback_id, "in_progress", "Working on it!")
    assert fb.status == "in_progress"

def test_invalid():
    svc = MktplaceFeedbackService()
    try:
        svc.submit("u1", "invalid", "msg")
        assert False
    except ValueError:
        pass
