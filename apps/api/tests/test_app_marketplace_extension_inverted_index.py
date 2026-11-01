from app.services.app_marketplace_extension_inverted_index import InvertedIndexService


def test_index_and_search():
    idx = InvertedIndexService()
    idx.index_document("d1", "Python is a great programming language")
    idx.index_document("d2", "JavaScript runs in the browser")
    idx.index_document("d3", "Python and JavaScript are popular")
    results = idx.search("python")
    assert len(results) >= 1
    assert results[0].doc_id in ("d1", "d3")


def test_tf_idf_ranking():
    idx = InvertedIndexService()
    idx.index_document("d1", "python python python guide")  # high TF
    idx.index_document("d2", "python basics")  # low TF
    idx.index_document("d3", "javascript guide")  # no match
    results = idx.search("python")
    assert results[0].doc_id == "d1"  # higher TF = ranked first


def test_boolean_and():
    idx = InvertedIndexService()
    idx.index_document("d1", "fast python code")
    idx.index_document("d2", "fast javascript code")
    idx.index_document("d3", "slow python script")
    results = idx.search_and(["fast", "python"])
    assert results == ["d1"]


def test_boolean_or():
    idx = InvertedIndexService()
    idx.index_document("d1", "python guide")
    idx.index_document("d2", "javascript tutorial")
    idx.index_document("d3", "rust manual")
    results = idx.search_or(["python", "javascript"])
    assert set(results) == {"d1", "d2"}


def test_phrase_search():
    idx = InvertedIndexService(use_stopwords=False)
    idx.index_document("d1", "the quick brown fox jumps")
    idx.index_document("d2", "quick fox brown jumps")  # not consecutive
    results = idx.search_phrase("quick brown fox")
    assert "d1" in results
    assert "d2" not in results


def test_stopwords_filtered():
    idx = InvertedIndexService(use_stopwords=True)
    idx.index_document("d1", "this is a test")
    assert idx.get_term_frequency("this") == 0
    assert idx.get_term_frequency("test") == 1


def test_update_document():
    idx = InvertedIndexService()
    idx.index_document("d1", "original content")
    idx.index_document("d1", "updated content here")
    results = idx.search("original")
    assert len(results) == 0
    results = idx.search("updated")
    assert len(results) == 1


def test_highlights():
    idx = InvertedIndexService()
    idx.index_document("d1", "Python is great for data science and machine learning")
    results = idx.search("python")
    assert len(results) == 1
    assert len(results[0].highlights) > 0


def test_empty_query():
    idx = InvertedIndexService()
    idx.index_document("d1", "some text")
    assert idx.search("") == []


def test_stats():
    idx = InvertedIndexService()
    idx.index_document("d1", "hello world")
    idx.index_document("d2", "world peace")
    assert idx.doc_count == 2
    assert idx.term_count >= 2
