"""Container registry — manage Docker image repositories and tags."""
from __future__ import annotations
import hashlib


class ContainerRegistry:
    def __init__(self):
        self._repos: dict[str, dict] = {}

    def create_repo(self, name: str, *, visibility: str = "private") -> dict:
        if name in self._repos:
            return {"error": "Repository already exists"}
        self._repos[name] = {"name": name, "visibility": visibility, "tags": {}, "pulls": 0}
        return {"name": name, "visibility": visibility, "status": "created"}

    def push_tag(self, repo: str, tag: str, *, size_mb: float = 0, layers: int = 0) -> dict:
        r = self._repos.get(repo)
        if not r:
            return {"error": "Repository not found"}
        digest = hashlib.sha256(f"{repo}:{tag}:{size_mb}".encode()).hexdigest()[:12]
        r["tags"][tag] = {"tag": tag, "digest": f"sha256:{digest}",
                          "size_mb": size_mb, "layers": layers}
        return {"repo": repo, "tag": tag, "digest": f"sha256:{digest}", "status": "pushed"}

    def pull(self, repo: str, tag: str = "latest") -> dict:
        r = self._repos.get(repo)
        if not r:
            return {"error": "Repository not found"}
        t = r["tags"].get(tag)
        if not t:
            return {"error": f"Tag {tag} not found"}
        r["pulls"] += 1
        return {"repo": repo, "tag": tag, "digest": t["digest"], "size_mb": t["size_mb"]}

    def list_repos(self) -> list[dict]:
        return [{"name": r["name"], "visibility": r["visibility"],
                 "tag_count": len(r["tags"]), "pulls": r["pulls"]}
                for r in self._repos.values()]
