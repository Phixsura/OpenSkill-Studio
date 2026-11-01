from app.services.app_marketplace_app_app_app_app_collaborators import build_collaborators_list

def test_collaborators():
    collabs = [
        {"id": "u1", "name": "Alice", "email": "a@b.com", "role": "owner"},
        {"id": "u2", "name": "Bob", "email": "b@b.com", "role": "contributor"},
        {"id": "u3", "name": "Charlie", "email": "c@b.com", "role": "maintainer"},
    ]
    r = build_collaborators_list(collaborators=collabs, app_name="SuperApp")
    assert r["total"] == 3
    assert r["collaborators"][0]["role"] == "owner"
    assert r["collaborators"][0]["can_publish"]
    assert r["collaborators"][2]["role"] == "contributor"
    assert not r["collaborators"][2]["can_deploy"]
