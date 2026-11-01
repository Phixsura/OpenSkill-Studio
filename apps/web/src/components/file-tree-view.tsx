"use client";

import { useState } from "react";

interface FileTreeViewProps { tree: Record<string, unknown>; depth?: number; }

function isFile(node: unknown): node is { type: string; icon: string } {
  return typeof node === "object" && node !== null && "type" in (node as Record<string, unknown>);
}

export function FileTreeView({ tree, depth = 0 }: FileTreeViewProps) {
  const [expanded, setExpanded] = useState<Set<string>>(new Set(Object.keys(tree)));
  const toggle = (key: string) => {
    const next = new Set(expanded);
    next.has(key) ? next.delete(key) : next.add(key);
    setExpanded(next);
  };

  return (
    <div style={{ paddingLeft: depth * 16 }}>
      {Object.entries(tree).map(([name, node]) => {
        if (isFile(node)) {
          return (
            <div key={name} className="flex items-center gap-1.5 py-0.5 text-sm">
              <span className="text-xs">{node.icon}</span>
              <span className="text-gray-600 dark:text-gray-300">{name}</span>
            </div>
          );
        }
        const isOpen = expanded.has(name);
        return (
          <div key={name}>
            <button onClick={() => toggle(name)} className="flex items-center gap-1 py-0.5 text-sm font-medium">
              <span className="text-xs text-gray-400">{isOpen ? "📂" : "📁"}</span>
              <span>{name}</span>
            </button>
            {isOpen && <FileTreeView tree={node as Record<string, unknown>} depth={depth + 1} />}
          </div>
        );
      })}
    </div>
  );
}
