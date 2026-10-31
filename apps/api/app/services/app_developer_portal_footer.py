"""Developer portal footer — footer links and version info."""

FOOTER_LINKS = {
    "Platform": [
        {"label": "Marketplace", "url": "/marketplace"},
        {"label": "Documentation", "url": "/docs/developer"},
        {"label": "API Status", "url": "/status"},
    ],
    "SDKs": [
        {"label": "TypeScript", "url": "https://www.npmjs.com/package/@openskill/sdk"},
        {"label": "Python", "url": "https://pypi.org/project/openskill-sdk/"},
    ],
    "Community": [
        {"label": "GitHub", "url": "https://github.com/Phixsura/OpenSkill-Studio"},
        {"label": "Discussions", "url": "https://github.com/Phixsura/OpenSkill-Studio/discussions"},
    ],
}

def get_footer_data() -> dict:
    return {"links": FOOTER_LINKS, "version": "1.0.0", "copyright": "© 2026 OpenSkill Studio"}
