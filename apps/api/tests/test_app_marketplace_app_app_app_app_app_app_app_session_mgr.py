from app.services.app_marketplace_app_app_app_app_app_app_app_session_mgr import SessionManager

def test_sessions():
    mgr = SessionManager(max_sessions_per_user=2)
    s1 = mgr.create(user_id="alice", ip="1.2.3.4", now=100)
    s2 = mgr.create(user_id="alice", ip="5.6.7.8", now=200)
    assert len(mgr.user_sessions("alice")) == 2
    # Third session evicts oldest
    s3 = mgr.create(user_id="alice", ip="9.0.1.2", now=300)
    assert len(mgr.user_sessions("alice")) == 2
    mgr.revoke(s3["session_id"])
    assert len(mgr.user_sessions("alice")) == 1
    assert mgr.stats()["total_sessions"] == 1
