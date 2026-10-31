from app.services.app_marketplace_extension_release_notes import ExtensionReleaseNotesService


def test_create_and_get():
    svc = ExtensionReleaseNotesService()
    svc.create("ext-1", "2.0.0", "Major Update", "Big changes",
               features=["Dark mode", "Export CSV"], fixes=["Login bug"],
               breaking=["New API format"], contributors=["alice", "bob"])
    note = svc.get_latest("ext-1")
    assert note.version == "2.0.0"
    assert len(note.features) == 2


def test_markdown():
    svc = ExtensionReleaseNotesService()
    note = svc.create("ext-1", "1.0", "Launch", "First release",
                      features=["Core feature"], highlights=["Big launch!"])
    md = svc.render_markdown(note)
    assert "# Launch" in md
    assert "Core feature" in md
    assert "Big launch!" in md


def test_user_summary():
    svc = ExtensionReleaseNotesService()
    note = svc.create("ext-1", "1.0", "T", "S",
                      features=["a", "b"], fixes=["c"], breaking=["d"])
    summary = svc.render_user_summary(note)
    assert "2 new features" in summary
    assert "1 bug fixes" in summary
    assert "breaking" in summary


def test_multiple_versions():
    svc = ExtensionReleaseNotesService()
    svc.create("ext-1", "1.0", "V1", "First")
    svc.create("ext-1", "2.0", "V2", "Second")
    assert len(svc.get_all("ext-1")) == 2
    assert svc.get_latest("ext-1").version == "2.0"
