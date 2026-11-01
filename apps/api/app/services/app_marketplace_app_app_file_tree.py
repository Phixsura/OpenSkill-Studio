"""File tree — display project file structure."""


FILE_ICONS = {
    ".ts": "📄", ".tsx": "⚛️", ".py": "🐍", ".json": "📋", ".md": "📝",
    ".yaml": "⚙️", ".yml": "⚙️", ".css": "🎨", ".html": "🌐", ".svg": "🖼️",
}


def build_file_tree(*, files: list[str]) -> dict:
    tree: dict = {}
    for path in sorted(files):
        parts = path.strip("/").split("/")
        node = tree
        for part in parts[:-1]:
            node = node.setdefault(part, {})
        filename = parts[-1]
        ext = "." + filename.rsplit(".", 1)[-1] if "." in filename else ""
        node[filename] = {"type": "file", "icon": FILE_ICONS.get(ext, "📄")}
    return {"tree": tree, "total_files": len(files),
            "file_types": len(set("." + f.rsplit(".", 1)[-1] for f in files if "." in f))}
