from app.services.app_marketplace_extension_changelog_parser import (
    ChangelogParserService,
)

SAMPLE_CHANGELOG = """
# Changelog

## [2.0.0] - 2024-06-01

### Added
- New plugin system
- BREAKING: Changed API signature for init()

### Fixed
- Memory leak in event loop

## [1.1.0] - 2024-03-15

### Added
- Dark mode support
- Export to CSV

### Changed
- Improved performance by 40%

## [1.0.0] - 2024-01-01

### Added
- Initial release
"""


def test_parse_releases():
    svc = ChangelogParserService()
    releases = svc.parse(SAMPLE_CHANGELOG)
    assert len(releases) == 3
    assert releases[0].version == "2.0.0"
    assert releases[2].version == "1.0.0"


def test_entries_by_category():
    svc = ChangelogParserService()
    releases = svc.parse(SAMPLE_CHANGELOG)
    r2 = releases[0]
    assert "Added" in r2.by_category
    assert "Fixed" in r2.by_category
    assert len(r2.entries) == 3


def test_breaking_change_detection():
    svc = ChangelogParserService()
    releases = svc.parse(SAMPLE_CHANGELOG)
    assert releases[0].has_breaking_changes is True
    assert releases[1].has_breaking_changes is False


def test_get_release():
    svc = ChangelogParserService()
    releases = svc.parse(SAMPLE_CHANGELOG)
    r = svc.get_release(releases, "1.1.0")
    assert r is not None
    assert r.date == "2024-03-15"


def test_changes_between():
    svc = ChangelogParserService()
    releases = svc.parse(SAMPLE_CHANGELOG)
    changes = svc.get_changes_between(releases, "1.0.0", "2.0.0")
    assert len(changes) > 0


def test_has_breaking_between():
    svc = ChangelogParserService()
    releases = svc.parse(SAMPLE_CHANGELOG)
    assert svc.has_breaking_between(releases, "1.0.0", "2.0.0") is True
    assert svc.has_breaking_between(releases, "1.0.0", "1.1.0") is False


def test_generate_summary():
    svc = ChangelogParserService()
    releases = svc.parse(SAMPLE_CHANGELOG)
    summary = svc.generate_summary(releases[0])
    assert "## 2.0.0" in summary
    assert "### Added" in summary


def test_yanked_release():
    svc = ChangelogParserService()
    releases = svc.parse("## [1.0.0] - 2024-01-01 [YANKED]\n### Fixed\n- Critical bug")
    assert releases[0].yanked is True
