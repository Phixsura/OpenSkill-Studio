"""App support info builder."""

def build_support_info(*, email: str | None = None, docs_url: str | None = None, issues_url: str | None = None) -> dict:
    channels = []
    if email: channels.append({"type": "email", "value": email})
    if docs_url: channels.append({"type": "docs", "value": docs_url})
    if issues_url: channels.append({"type": "issues", "value": issues_url})
    return {"channels": channels, "has_support": len(channels) > 0}
