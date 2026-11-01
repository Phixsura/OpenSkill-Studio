from app.services.app_marketplace_extension_string_similarity import StringSimilarityService


def test_levenshtein():
    ss = StringSimilarityService()
    assert ss.levenshtein("kitten", "sitting") == 3
    assert ss.levenshtein("", "abc") == 3
    assert ss.levenshtein("same", "same") == 0


def test_levenshtein_similarity():
    ss = StringSimilarityService()
    assert ss.levenshtein_similarity("hello", "hello") == 1.0
    assert ss.levenshtein_similarity("hello", "hallo") > 0.7
    assert ss.levenshtein_similarity("abc", "xyz") < 0.5


def test_jaro():
    ss = StringSimilarityService()
    assert ss.jaro("martha", "martha") == 1.0
    assert ss.jaro("martha", "marhta") > 0.9
    assert ss.jaro("abc", "xyz") == 0.0


def test_jaro_winkler():
    ss = StringSimilarityService()
    # Jaro-Winkler boosts common prefix
    jw = ss.jaro_winkler("MARTHA", "MARHTA")
    j = ss.jaro("MARTHA", "MARHTA")
    assert jw >= j  # winkler boost for "MAR" prefix


def test_cosine():
    ss = StringSimilarityService()
    assert ss.cosine("night", "nacht") > 0.2
    assert ss.cosine("hello", "hello") == 1.0
    assert ss.cosine("abc", "xyz") == 0.0


def test_lcs():
    ss = StringSimilarityService()
    assert ss.lcs_length("ABCBDAB", "BDCAB") == 4  # BCAB
    assert ss.lcs_length("", "abc") == 0


def test_lcs_similarity():
    ss = StringSimilarityService()
    assert ss.lcs_similarity("abc", "abc") == 1.0
    assert ss.lcs_similarity("abc", "def") == 0.0
    assert 0 < ss.lcs_similarity("abcde", "ace") < 1


def test_best_match():
    ss = StringSimilarityService()
    candidates = ["python", "javascript", "typescript", "pythn", "java"]
    matches = ss.best_match("python", candidates)
    assert matches[0][0] == "python"  # exact match first
    assert matches[1][0] == "pythn"   # close second


def test_best_match_jaro():
    ss = StringSimilarityService()
    candidates = ["Smith", "Smyth", "Jones", "Smithe"]
    matches = ss.best_match("Smith", candidates, algorithm="jaro_winkler")
    assert matches[0][0] == "Smith"


def test_empty_strings():
    ss = StringSimilarityService()
    assert ss.levenshtein_similarity("", "") == 1.0
    assert ss.jaro("", "") == 1.0
    assert ss.lcs_similarity("", "") == 1.0
