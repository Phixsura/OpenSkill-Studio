"""Container image scanner — scan images for vulnerabilities and best practices."""
from __future__ import annotations


def scan_image(name: str, tag: str, layers: int, size_mb: float, vulns: list[dict]) -> dict:
    critical = sum(1 for v in vulns if v.get("severity") == "critical")
    high = sum(1 for v in vulns if v.get("severity") == "high")
    pass_scan = critical == 0 and high == 0
    issues = []
    if size_mb > 500:
        issues.append("Image too large — consider multi-stage build")
    if layers > 20:
        issues.append("Too many layers — squash layers")
    return {"image": f"{name}:{tag}", "layers": layers, "size_mb": round(size_mb, 1),
            "vulns": len(vulns), "critical": critical, "high": high,
            "pass": pass_scan, "issues": issues}


def registry_scan(images: list[dict]) -> dict:
    total_vulns = sum(i.get("vulns", 0) for i in images)
    passing = sum(1 for i in images if i.get("pass", False))
    return {"total_images": len(images), "passing": passing,
            "failing": len(images) - passing, "total_vulns": total_vulns,
            "pass_rate": round(passing / max(len(images), 1) * 100)}
