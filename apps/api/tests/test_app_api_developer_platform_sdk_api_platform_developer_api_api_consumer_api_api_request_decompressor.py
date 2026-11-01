import zlib
import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_request_decompressor import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestDecompressor

class TestRequestDecompressor:
    def test_gzip_decompress(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestDecompressor()
        original = b"hello world " * 100
        compressed = zlib.compress(original, level=9)
        # Use deflate since gzip needs wbits=31 for compress
        result = svc.decompress("inst-1", compressed, "deflate")
        assert result.decompressed_size == len(original)
        assert result.ratio > 1  # expanded

    def test_identity_passthrough(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestDecompressor()
        result = svc.decompress("inst-1", b"plain text", "identity")
        assert result.original_size == result.decompressed_size

    def test_invalid_encoding(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestDecompressor()
        with pytest.raises(ValueError, match="Unsupported"):
            svc.decompress("inst-1", b"data", "brotli")

    def test_bomb_protection(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestDecompressor(max_decompressed_bytes=1024)
        big = zlib.compress(b"x" * 5000)
        with pytest.raises(ValueError, match="exceeds max"):
            svc.decompress("inst-1", big, "deflate")

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestDecompressor()
        svc.decompress("inst-1", b"test", "identity")
        assert svc.savings("inst-2")["decompressed"] == 0
