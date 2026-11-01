from app.services.app_marketplace_app_app_app_app_app_app_app_gql_complexity import analyze_complexity

def test_simple():
    query = "{ users { id name email } }"
    r = analyze_complexity(query)
    assert r["allowed"]
    assert r["depth"] == 2
    assert r["complexity"] > 0

def test_complex():
    query = "{ users { edges { node { posts { edges { node { comments { edges { node { id } } } } } } } } } }"
    r = analyze_complexity(query, max_complexity=50, max_depth=4)
    assert not r["allowed"]
    assert r["depth"] > 4
