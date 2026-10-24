"""Service dependency graph visualizer — generate DOT/Mermaid from deps."""
from __future__ import annotations


def to_mermaid(nodes: list[str], edges: list[dict]) -> str:
    lines = ["graph LR"]
    for edge in edges:
        src = edge["source"]
        dst = edge["destination"]
        label = edge.get("label", "")
        if label:
            lines.append(f"    {src} -->|{label}| {dst}")
        else:
            lines.append(f"    {src} --> {dst}")
    return "\n".join(lines)


def graph_metrics(nodes: list[str], edges: list[dict]) -> dict:
    in_degree: dict[str, int] = {n: 0 for n in nodes}
    out_degree: dict[str, int] = {n: 0 for n in nodes}
    for e in edges:
        out_degree[e["source"]] = out_degree.get(e["source"], 0) + 1
        in_degree[e["destination"]] = in_degree.get(e["destination"], 0) + 1
    most_depended = max(in_degree.items(), key=lambda x: x[1]) if in_degree else ("none", 0)
    most_dependent = max(out_degree.items(), key=lambda x: x[1]) if out_degree else ("none", 0)
    density = round(len(edges) / max(len(nodes) * (len(nodes) - 1), 1), 3)
    return {"nodes": len(nodes), "edges": len(edges), "density": density,
            "most_depended_on": most_depended[0],
            "most_dependent": most_dependent[0]}
