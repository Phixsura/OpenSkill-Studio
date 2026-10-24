from app.services.app_marketplace_app_app_search_index import SearchIndex

def test_index_and_search():
    idx = SearchIndex()
    idx.index(doc_id="1", title="Python SDK", body="Build apps with Python", tags=["sdk"])
    idx.index(doc_id="2", title="TypeScript SDK", body="Build apps with TypeScript", tags=["sdk"])
    idx.index(doc_id="3", title="API Reference", body="REST API documentation")
    r = idx.search(query="Python SDK")
    assert r["total"] >= 1
    assert r["results"][0]["id"] == "1"

def test_no_results():
    idx = SearchIndex()
    idx.index(doc_id="1", title="Hello", body="World")
    r = idx.search(query="zzzznotfound")
    assert r["total"] == 0
