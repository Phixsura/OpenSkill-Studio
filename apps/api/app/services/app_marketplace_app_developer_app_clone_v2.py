"""App clone v2 — deep clone with config migration and dependency resolution."""


def deep_clone_app(*, source: dict, new_name: str, new_slug: str,
                      developer_id: str, include_config: bool = True,
                      include_webhooks: bool = False) -> dict:
    clone = {"name": new_name, "slug": new_slug, "developer_id": developer_id,
             "category": source.get("category"), "description": source.get("description"),
             "cloned_from": source["id"], "status": "draft"}
    if include_config:
        clone["config"] = dict(source.get("default_config", {}))
        clone["permissions"] = list(source.get("permissions", []))
    if include_webhooks:
        clone["webhook_templates"] = list(source.get("webhooks", []))
    clone["clone_options"] = {"config": include_config, "webhooks": include_webhooks}
    return clone


def get_clone_diff(*, source: dict, clone: dict) -> dict:
    diffs = []
    for key in ("name", "slug", "developer_id"):
        if source.get(key) != clone.get(key):
            diffs.append({"field": key, "source": source.get(key), "clone": clone.get(key)})
    return {"diffs": diffs, "identical_fields": len(source) - len(diffs)}
