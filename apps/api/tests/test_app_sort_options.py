from app.services.app_sort_options import get_sort_config, list_sort_options, SORT_OPTIONS

def test_get_relevance():
    c = get_sort_config("relevance")
    assert c["order"] == "desc"

def test_get_name():
    c = get_sort_config("name")
    assert c["order"] == "asc"

def test_unknown_defaults():
    c = get_sort_config("xxx")
    assert c == SORT_OPTIONS["relevance"]

def test_list():
    opts = list_sort_options()
    assert len(opts) == len(SORT_OPTIONS)
    assert all("key" in o for o in opts)
