"""Data masking — PII detection and redaction for logs and exports."""

import re
import html

PATTERNS = {
    "email": re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"),
    "phone": re.compile(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b"),
    "credit_card": re.compile(r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b"),
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "ip_address": re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"),
}


def detect_pii(*, text: str) -> dict:
    findings = []
    for pii_type, pattern in PATTERNS.items():
        for match in pattern.finditer(text):
            findings.append({"type": pii_type, "value": match.group(0),
                              "start": match.start(), "end": match.end()})
    return {"findings": findings, "count": len(findings),
            "types_found": list(set(f["type"] for f in findings)),
            "has_pii": len(findings) > 0}


def mask_pii(*, text: str, mask_char: str = "•") -> dict:
    masked = text
    detections = detect_pii(text=text)
    for f in sorted(detections["findings"], key=lambda x: -x["start"]):
        val = f["value"]
        if f["type"] == "email":
            parts = val.split("@")
            replacement = parts[0][:2] + mask_char * 4 + "@" + parts[1]
        elif f["type"] == "credit_card":
            replacement = mask_char * 12 + val[-4:]
        else:
            replacement = mask_char * len(val)
        masked = masked[:f["start"]] + replacement + masked[f["end"]:]
    return {"original_length": len(text), "masked": html.escape(masked),
            "redactions": detections["count"]}
