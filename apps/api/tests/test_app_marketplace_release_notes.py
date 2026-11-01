from app.services.app_marketplace_release_notes import (
    ReleaseNotesGenerator, ReleaseNotes, ReleaseHighlight,
)


def _sample_notes() -> ReleaseNotes:
    return ReleaseNotes(
        extension_id="slack-bot", version="3.0.0",
        summary="Major release with new messaging features",
        highlights=[
            ReleaseHighlight("Thread Support", "Reply in threads natively", "🧵"),
            ReleaseHighlight("File Sharing", "Share files directly from the extension", "📎"),
        ],
        changes={
            "feat": ["Add thread reply support", "Add file sharing via drag-and-drop"],
            "fix": ["Fix message ordering bug", "Fix emoji rendering"],
            "perf": ["Reduce API latency by 40%"],
        },
        breaking_changes=["Removed v1 webhook format", "Changed auth header name"],
        dependency_updates=[
            {"name": "slack-sdk", "from": "3.0.0", "to": "4.0.0"},
        ],
        migration_notes="Update your webhook URLs to use the v2 format.",
        contributors=["alice", "bob", "carol"],
    )


def test_create_and_get():
    rng = ReleaseNotesGenerator()
    notes = rng.create(_sample_notes())
    assert rng.get("slack-bot", "3.0.0") is not None


def test_render_markdown():
    rng = ReleaseNotesGenerator()
    md = rng.render_markdown(_sample_notes())
    assert "# slack-bot v3.0.0" in md
    assert "Thread Support" in md
    assert "Breaking Changes" in md
    assert "Removed v1 webhook" in md
    assert "slack-sdk" in md
    assert "@alice" in md
    assert "Migration Guide" in md


def test_render_summary():
    rng = ReleaseNotesGenerator()
    summary = rng.render_summary(_sample_notes())
    assert summary["version"] == "3.0.0"
    assert summary["highlights"] == 2
    assert summary["total_changes"] == 5
    assert summary["breaking_changes"] == 2
    assert summary["has_migration"] is True
    assert summary["contributors"] == 3


def test_minimal_notes():
    rng = ReleaseNotesGenerator()
    notes = ReleaseNotes("ext-1", "1.0.0", "Initial release",
                          changes={"feat": ["Everything is new"]})
    md = rng.render_markdown(notes)
    assert "Initial release" in md
    assert "Everything is new" in md
    assert "Breaking" not in md
