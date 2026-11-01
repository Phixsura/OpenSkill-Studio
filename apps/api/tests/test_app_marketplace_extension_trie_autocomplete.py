from app.services.app_marketplace_extension_trie_autocomplete import TrieAutocompleteService


def test_insert_and_search():
    ac = TrieAutocompleteService()
    ac.insert("apple", 10)
    ac.insert("application", 8)
    ac.insert("banana", 5)
    results = ac.search("app")
    words = [w for w, _ in results]
    assert "apple" in words
    assert "application" in words
    assert "banana" not in words


def test_score_ranking():
    ac = TrieAutocompleteService()
    ac.insert("python", 100)
    ac.insert("pytorch", 50)
    ac.insert("pypi", 80)
    results = ac.search("py")
    assert results[0][0] == "python"  # highest score
    assert results[1][0] == "pypi"


def test_limit():
    ac = TrieAutocompleteService()
    for i in range(20):
        ac.insert(f"word{i:02d}", float(i))
    results = ac.search("word", limit=5)
    assert len(results) == 5


def test_contains():
    ac = TrieAutocompleteService()
    ac.insert("hello")
    assert ac.contains("hello") is True
    assert ac.contains("hell") is False
    assert ac.has_prefix("hel") is True


def test_delete():
    ac = TrieAutocompleteService()
    ac.insert("test")
    ac.insert("testing")
    assert ac.delete("test") is True
    assert ac.contains("test") is False
    assert ac.contains("testing") is True
    assert ac.size == 1


def test_delete_cleans_branches():
    ac = TrieAutocompleteService()
    ac.insert("unique")
    ac.delete("unique")
    assert ac.has_prefix("uni") is False


def test_case_insensitive():
    ac = TrieAutocompleteService()
    ac.insert("Hello")
    assert ac.contains("hello") is True
    results = ac.search("HEL")
    assert len(results) == 1


def test_fuzzy_search():
    ac = TrieAutocompleteService()
    ac.insert("python", 10)
    ac.insert("javascript", 8)
    ac.insert("typescript", 7)
    results = ac.fuzzy_search("pythn", max_distance=1)  # missing 'o'
    words = [w for w, _, _ in results]
    assert "python" in words


def test_fuzzy_substitution():
    ac = TrieAutocompleteService()
    ac.insert("react", 10)
    ac.insert("redux", 5)
    results = ac.fuzzy_search("reakt", max_distance=1)  # c→k
    words = [w for w, _, _ in results]
    assert "react" in words


def test_empty_prefix():
    ac = TrieAutocompleteService()
    ac.insert("a", 1)
    ac.insert("b", 2)
    results = ac.search("")
    assert len(results) == 2


def test_no_match():
    ac = TrieAutocompleteService()
    ac.insert("hello")
    assert ac.search("xyz") == []
