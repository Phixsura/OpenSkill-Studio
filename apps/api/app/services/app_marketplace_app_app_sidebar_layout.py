"""Sidebar layout — generate sidebar navigation layout config."""


def build_sidebar_layout(*, sections: list[dict], collapsed: bool = False,
                           user_role: str = "developer") -> dict:
    visible = []
    for sec in sections:
        items = [i for i in sec.get("items", []) if user_role in i.get("roles", ["developer"])]
        if items:
            visible.append({"title": sec["title"], "items": items})
    return {
        "sections": visible,
        "total_items": sum(len(s["items"]) for s in visible),
        "collapsed": collapsed,
        "width": "w-14" if collapsed else "w-56",
    }
