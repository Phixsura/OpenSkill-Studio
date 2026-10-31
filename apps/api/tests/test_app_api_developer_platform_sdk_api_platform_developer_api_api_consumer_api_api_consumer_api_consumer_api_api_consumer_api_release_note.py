import pytest
from datetime import datetime
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_api_consumer_api_release_note import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiReleaseNote, ReleaseNote,
)

class TestConsumerApiReleaseNote:
    def _now(self):
        return datetime(2026, 6, 1)

    def test_create_and_publish(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiReleaseNote()
        svc.create("inst-1", ReleaseNote(note_id="n1", version="2.0", title="OAuth2", body="Added OAuth2 support", change_type="feature"))
        svc.publish("inst-1", "n1", self._now())
        published = svc.list_published("inst-1")
        assert len(published) == 1 and published[0].published

    def test_list_by_version(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiReleaseNote()
        svc.create("inst-1", ReleaseNote(note_id="n1", version="2.0", title="A", body="x"))
        svc.create("inst-1", ReleaseNote(note_id="n2", version="2.1", title="B", body="y"))
        assert len(svc.list_by_version("inst-1", "2.0")) == 1

    def test_search(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiReleaseNote()
        svc.create("inst-1", ReleaseNote(note_id="n1", version="1.0", title="Auth Fix", body="Fixed auth"))
        svc.create("inst-1", ReleaseNote(note_id="n2", version="1.1", title="Perf", body="Improved speed"))
        assert len(svc.search("inst-1", "auth")) == 1

    def test_duplicate(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiReleaseNote()
        svc.create("inst-1", ReleaseNote(note_id="n1", version="1.0", title="X", body="y"))
        with pytest.raises(ValueError, match="already exists"):
            svc.create("inst-1", ReleaseNote(note_id="n1", version="1.0", title="Z", body="w"))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiReleaseNote()
        svc.create("inst-1", ReleaseNote(note_id="n1", version="1.0", title="X", body="y"))
        assert len(svc.list_published("inst-2")) == 0
