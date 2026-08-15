"""Media file validation — magic-byte sniffing and MIME whitelists.

Never trust the client-declared Content-Type: verify the actual file
signature matches the declared MIME family before accepting an upload.
Pure-python, no external dependencies.
"""

# MIME whitelists per deliverable media category
IMAGE_MIMES = {"image/png", "image/jpeg", "image/webp", "image/gif"}
VIDEO_MIMES = {"video/mp4", "video/webm"}
AUDIO_MIMES = {"audio/mpeg", "audio/mp3", "audio/wav", "audio/x-wav", "audio/mp4", "audio/x-m4a"}
DOCUMENT_MIMES = {"application/pdf"}

# reference / final_output accept any media + pdf
MEDIA_ALL = IMAGE_MIMES | VIDEO_MIMES | AUDIO_MIMES | DOCUMENT_MIMES


def sniff_mime_family(header: bytes) -> str | None:
    """Identify the file family from its leading bytes.

    Returns one of "png", "jpeg", "webp", "gif", "mp4", "webm",
    "mp3", "wav", "m4a", "pdf" — or None if unrecognized.
    """
    if len(header) < 12:
        return None

    if header.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if header.startswith(b"\xff\xd8\xff"):
        return "jpeg"
    if header[:4] == b"RIFF" and header[8:12] == b"WEBP":
        return "webp"
    if header.startswith((b"GIF87a", b"GIF89a")):
        return "gif"
    # MP4 family: ftyp box at offset 4. M4A audio uses brand "M4A "
    if header[4:8] == b"ftyp":
        if header[8:12] == b"M4A ":
            return "m4a"
        return "mp4"
    # WebM (and Matroska): EBML header
    if header.startswith(b"\x1a\x45\xdf\xa3"):
        return "webm"
    # MP3: ID3 tag or MPEG frame sync
    if header.startswith(b"ID3") or header[:2] in (b"\xff\xfb", b"\xff\xf3", b"\xff\xf2"):
        return "mp3"
    if header[:4] == b"RIFF" and header[8:12] == b"WAVE":
        return "wav"
    if header.startswith(b"%PDF"):
        return "pdf"
    return None


# Map sniffed family → acceptable declared MIME types
_FAMILY_TO_MIMES: dict[str, set[str]] = {
    "png": {"image/png"},
    "jpeg": {"image/jpeg"},
    "webp": {"image/webp"},
    "gif": {"image/gif"},
    "mp4": {"video/mp4", "audio/mp4", "audio/x-m4a"},  # m4a is an mp4 container
    "m4a": {"audio/mp4", "audio/x-m4a"},
    "webm": {"video/webm"},
    "mp3": {"audio/mpeg", "audio/mp3"},
    "wav": {"audio/wav", "audio/x-wav"},
    "pdf": {"application/pdf"},
}


def content_matches_mime(header: bytes, declared_mime: str) -> bool:
    """True if the sniffed file signature is consistent with the declared MIME."""
    family = sniff_mime_family(header)
    if family is None:
        return False
    return declared_mime.lower() in _FAMILY_TO_MIMES.get(family, set())
