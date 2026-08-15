"""Unit tests for magic-byte media sniffing (app/core/media.py)."""

from app.core.media import (
    AUDIO_MIMES,
    IMAGE_MIMES,
    MEDIA_ALL,
    VIDEO_MIMES,
    content_matches_mime,
    sniff_mime_family,
)

# Minimal valid file headers (12+ bytes each)
PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 8
JPEG = b"\xff\xd8\xff\xe0" + b"\x00" * 8
WEBP = b"RIFF\x00\x00\x00\x00WEBP" + b"\x00" * 4
GIF = b"GIF89a" + b"\x00" * 8
MP4 = b"\x00\x00\x00\x18ftypmp42" + b"\x00" * 4
M4A = b"\x00\x00\x00\x18ftypM4A " + b"\x00" * 4
WEBM = b"\x1a\x45\xdf\xa3" + b"\x00" * 8
MP3_ID3 = b"ID3\x04\x00\x00\x00\x00\x00\x00\x00\x00"
MP3_FRAME = b"\xff\xfb\x90\x00" + b"\x00" * 8
WAV = b"RIFF\x00\x00\x00\x00WAVE" + b"\x00" * 4
PDF = b"%PDF-1.7\n%\xe2\xe3"


def test_sniff_png():
    assert sniff_mime_family(PNG) == "png"


def test_sniff_jpeg():
    assert sniff_mime_family(JPEG) == "jpeg"


def test_sniff_webp():
    assert sniff_mime_family(WEBP) == "webp"


def test_sniff_gif():
    assert sniff_mime_family(GIF) == "gif"


def test_sniff_mp4():
    assert sniff_mime_family(MP4) == "mp4"


def test_sniff_m4a():
    assert sniff_mime_family(M4A) == "m4a"


def test_sniff_webm():
    assert sniff_mime_family(WEBM) == "webm"


def test_sniff_mp3_id3():
    assert sniff_mime_family(MP3_ID3) == "mp3"


def test_sniff_mp3_frame():
    assert sniff_mime_family(MP3_FRAME) == "mp3"


def test_sniff_wav():
    assert sniff_mime_family(WAV) == "wav"


def test_sniff_pdf():
    assert sniff_mime_family(PDF) == "pdf"


def test_sniff_unknown():
    assert sniff_mime_family(b"hello world!") is None


def test_sniff_too_short():
    assert sniff_mime_family(b"\x89PNG") is None


def test_sniff_empty():
    assert sniff_mime_family(b"") is None


def test_svg_not_recognized():
    """SVG must never be sniffed as a valid media type (XSS vector)."""
    svg = b'<svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script></svg>'
    assert sniff_mime_family(svg) is None


# ── content_matches_mime ──


def test_match_png():
    assert content_matches_mime(PNG, "image/png")


def test_match_case_insensitive():
    assert content_matches_mime(PNG, "IMAGE/PNG")


def test_mismatch_png_declared_jpeg():
    """Spoofed content-type: PNG bytes declared as JPEG must be rejected."""
    assert not content_matches_mime(PNG, "image/jpeg")


def test_mismatch_text_declared_png():
    """Text file declared as PNG must be rejected."""
    assert not content_matches_mime(b"just some text 1234", "image/png")


def test_match_m4a_as_audio_mp4():
    assert content_matches_mime(M4A, "audio/mp4")
    assert content_matches_mime(M4A, "audio/x-m4a")


def test_match_mp4_video():
    assert content_matches_mime(MP4, "video/mp4")


def test_match_mp3_both_mimes():
    assert content_matches_mime(MP3_ID3, "audio/mpeg")
    assert content_matches_mime(MP3_FRAME, "audio/mp3")


def test_match_wav():
    assert content_matches_mime(WAV, "audio/wav")
    assert content_matches_mime(WAV, "audio/x-wav")


def test_match_pdf():
    assert content_matches_mime(PDF, "application/pdf")


def test_whitelist_shapes():
    assert "image/png" in IMAGE_MIMES
    assert "image/svg+xml" not in IMAGE_MIMES  # SVG banned
    assert "video/mp4" in VIDEO_MIMES
    assert "audio/mpeg" in AUDIO_MIMES
    assert "application/pdf" in MEDIA_ALL
