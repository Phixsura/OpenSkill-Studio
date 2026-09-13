"""ETag support tests — pure logic, no DB needed."""

from app.talent.api.etag import compute_etag


class TestComputeEtag:
    def test_same_content_same_etag(self):
        body = b'{"data": [1, 2, 3]}'
        assert compute_etag(body) == compute_etag(body)

    def test_different_content_different_etag(self):
        a = compute_etag(b'{"data": [1]}')
        b = compute_etag(b'{"data": [2]}')
        assert a != b

    def test_weak_etag_format(self):
        etag = compute_etag(b"hello")
        assert etag.startswith('W/"')
        assert etag.endswith('"')

    def test_empty_body(self):
        etag = compute_etag(b"")
        assert etag.startswith('W/"')
        # MD5 of empty string is d41d8cd98f00b204e9800998ecf8427e
        assert "d41d8cd98f00b204e9800998ecf8427e" in etag

    def test_consistent_across_calls(self):
        """ETag must be deterministic — same bytes always produce same hash."""
        body = b"some response body content"
        results = {compute_etag(body) for _ in range(100)}
        assert len(results) == 1

    def test_large_body(self):
        """ETags work on large response bodies."""
        body = b"x" * 1_000_000
        etag = compute_etag(body)
        assert etag.startswith('W/"')
        assert len(etag) == 36  # W/" + 32 hex + "
