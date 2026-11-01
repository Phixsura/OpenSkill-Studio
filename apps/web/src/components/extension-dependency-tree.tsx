"use client";

import { useState } from "react";

interface TreeNode {
  id: string;
  name: string;
  version: string;
  status: "ok" | "outdated" | "vulnerable" | "missing";
  children: TreeNode[];
}

export function ExtensionDependencyTree({
  root,
  onNodeSelect,
}: {
  root: TreeNode;
  onNodeSelect?: (id: string) => void;
}) {
  const [expanded, setExpanded] = useState<Set<string>>(new Set([root.id]));

  const toggle = (id: string) => {
    setExpanded((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  const statusConfig: Record<string, { icon: string; color: string }> = {
    ok: { icon: "✅", color: "" },
    outdated: { icon: "⚠️", color: "text-yellow-500" },
    vulnerable: { icon: "🔴", color: "text-red-500" },
    missing: { icon: "❓", color: "text-gray-400" },
  };

  const countByStatus = (node: TreeNode): Record<string, number> => {
    const counts: Record<string, number> = { ok: 0, outdated: 0, vulnerable: 0, missing: 0 };
    const walk = (n: TreeNode) => {
      counts[n.status]++;
      n.children.forEach(walk);
    };
    walk(node);
    return counts;
  };

  const counts = countByStatus(root);
  const totalDeps = Object.values(counts).reduce((a, b) => a + b, 0) - 1; // exclude root

  const renderNode = (node: TreeNode, depth: number = 0): JSX.Element => {
    const isExpanded = expanded.has(node.id);
    const hasChildren = node.children.length > 0;
    const cfg = statusConfig[node.status];

    return (
      <div key={node.id}>
        <div className="flex items-center gap-1 py-0.5 hover:bg-gray-50 dark:hover:bg-gray-800 rounded"
          style={{ paddingLeft: `${depth * 20 + 8}px` }}>
          {hasChildren ? (
            <button onClick={() => toggle(node.id)} className="w-4 text-gray-400 text-xs">
              {isExpanded ? "▼" : "▶"}
            </button>
          ) : (
            <span className="w-4 text-gray-300 text-xs">·</span>
          )}
          <span className="text-sm">{cfg.icon}</span>
          <button onClick={() => onNodeSelect?.(node.id)}
            className={`text-sm hover:underline ${cfg.color}`}>
            {node.name}
          </button>
          <span className="text-xs text-gray-400 font-mono">@{node.version}</span>
        </div>
        {isExpanded && node.children.map((child) => renderNode(child, depth + 1))}
      </div>
    );
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">🌳 Dependency Tree</h2>
        <div className="flex gap-3 text-xs">
          <span>{totalDeps} dependencies</span>
          {counts.vulnerable > 0 && <span className="text-red-500">{counts.vulnerable} vulnerable</span>}
          {counts.outdated > 0 && <span className="text-yellow-500">{counts.outdated} outdated</span>}
        </div>
      </div>

      <div className="rounded-xl border dark:border-gray-700 p-3 font-mono text-sm max-h-80 overflow-y-auto">
        {renderNode(root)}
      </div>
    </div>
  );
}
