from app.services.app_marketplace_extension_diff_engine import DiffEngineService, DiffOp


def test_identical():
    eng = DiffEngineService()
    diff = eng.diff_lines("hello\nworld", "hello\nworld")
    assert diff.additions == 0
    assert diff.deletions == 0
    assert diff.similarity == 100.0


def test_insertion():
    eng = DiffEngineService()
    diff = eng.diff_lines("a\nc", "a\nb\nc")
    assert diff.additions == 1
    assert diff.deletions == 0
    inserts = [h for h in diff.hunks if h.op == DiffOp.INSERT]
    assert any("b" in h.content for h in inserts)


def test_deletion():
    eng = DiffEngineService()
    diff = eng.diff_lines("a\nb\nc", "a\nc")
    assert diff.deletions == 1


def test_modification():
    eng = DiffEngineService()
    diff = eng.diff_lines("hello\nworld", "hello\nearth")
    # "world" deleted, "earth" inserted
    assert diff.additions >= 1
    assert diff.deletions >= 1


def test_word_diff():
    eng = DiffEngineService()
    diff = eng.diff_words("the quick brown fox", "the slow brown cat")
    # quick→slow, fox→cat
    assert diff.additions == 2
    assert diff.deletions == 2


def test_unified_format():
    eng = DiffEngineService()
    output = eng.unified_diff("a\nb\nc", "a\nx\nc", "old.txt", "new.txt")
    assert "--- old.txt" in output
    assert "+++ new.txt" in output
    assert "-b" in output
    assert "+x" in output


def test_apply_patch():
    eng = DiffEngineService()
    old = "line1\nline2\nline3"
    new = "line1\nmodified\nline3"
    diff = eng.diff_lines(old, new)
    reconstructed = eng.apply_patch(old, diff)
    assert "modified" in reconstructed
    assert "line1" in reconstructed


def test_similarity():
    eng = DiffEngineService()
    diff = eng.diff_lines("a\nb\nc\nd", "a\nb\nx\nd")
    # 3 equal, 1 delete, 1 insert → 3/5 = 60%
    assert diff.similarity == 60.0


def test_empty_to_content():
    eng = DiffEngineService()
    diff = eng.diff_lines("", "new content")
    assert diff.additions >= 1
    assert diff.deletions == 0


def test_content_to_empty():
    eng = DiffEngineService()
    diff = eng.diff_lines("old content", "")
    assert diff.deletions >= 1
    assert diff.additions == 0
