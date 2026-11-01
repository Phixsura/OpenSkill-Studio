"use client";

import { useState } from "react";

interface DepNode {
  id: string;
  name: string;
  version: string;
  type: "direct" | "transitive" | "root";
}

interface DepEdge {
  from: string;
  to: string;
  relation: "depends_on" | "extends" | "conflicts_with";
}

export function DependencyGraphViewer({
  nodes,
  edges,
  rootId,
}: {
  nodes: DepNode[];
  edges: DepEdge[];
  rootId: string;
}) {
  const [selectedNode, setSelectedNode] = useState<string | null>(null);

  const getNodeDeps = (nodeId: string) => edges.filter((e) => e.from === nodeId);
  const getNodeDependents = (nodeId: string) => edges.filter((e) => e.to === nodeId);

  const selected = nodes.find((n) => n.id === selectedNode);

  const typeColors = {
    root: "border-blue-500 bg-blue-50 dark:bg-blue-900/20",
    direct: "border-green-500 bg-green-50 dark:bg-green-900/20",
    transitive: "border-gray-400 bg-gray-50 dark:bg-gray-800",
  };

  const relationIcons = {
    depends_on: "→",
    extends: "⊃",
    conflicts_with: "⚡",
  };

  const conflicts = edges.filter((e) => e.relation === "conflicts_with");

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">🕸️ Dependency Graph</h2>
        <div className="flex gap-3 text-xs text-gray-500">
          <span>{nodes.length} packages</span>
          <span>{edges.length} edges</span>
          {conflicts.length > 0 && (
            <span className="text-red-500">⚡ {conflicts.length} conflicts</span>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Node list */}
        <div className="space-y-1 max-h-80 overflow-y-auto">
          {nodes.map((node) => (
            <button
              key={node.id}
              onClick={() => setSelectedNode(node.id)}
              className={`w-full text-left px-3 py-2 rounded-lg border-l-4 text-sm ${typeColors[node.type]} ${
                selectedNode === node.id ? "ring-2 ring-blue-400" : ""
              }`}
            >
              <div className="font-medium">{node.name}</div>
              <div className="text-xs text-gray-400">v{node.version} · {node.type}</div>
            </button>
          ))}
        </div>

        {/* Edge list */}
        <div className="space-y-1 max-h-80 overflow-y-auto">
          <div className="text-sm font-medium text-gray-500 mb-2">Dependencies</div>
          {edges.map((edge, i) => (
            <div key={i} className={`text-xs px-2 py-1.5 rounded flex items-center gap-1 ${
              edge.relation === "conflicts_with" ? "bg-red-50 dark:bg-red-900/10 text-red-600" : "bg-gray-50 dark:bg-gray-800"
            }`}>
              <span className="font-mono">{edge.from}</span>
              <span>{relationIcons[edge.relation]}</span>
              <span className="font-mono">{edge.to}</span>
            </div>
          ))}
        </div>

        {/* Detail panel */}
        <div className="rounded-lg border dark:border-gray-700 p-4">
          {selected ? (
            <div className="space-y-3">
              <h3 className="font-bold">{selected.name}</h3>
              <div className="text-sm text-gray-500">v{selected.version} · {selected.type}</div>
              <div>
                <div className="text-xs font-medium text-gray-400 mb-1">Depends on:</div>
                {getNodeDeps(selected.id).map((e, i) => (
                  <div key={i} className="text-xs text-gray-600 dark:text-gray-300">→ {e.to}</div>
                ))}
                {getNodeDeps(selected.id).length === 0 && <div className="text-xs text-gray-400">None</div>}
              </div>
              <div>
                <div className="text-xs font-medium text-gray-400 mb-1">Used by:</div>
                {getNodeDependents(selected.id).map((e, i) => (
                  <div key={i} className="text-xs text-gray-600 dark:text-gray-300">← {e.from}</div>
                ))}
                {getNodeDependents(selected.id).length === 0 && <div className="text-xs text-gray-400">None (root)</div>}
              </div>
            </div>
          ) : (
            <div className="text-sm text-gray-400 text-center py-8">Select a node to view details</div>
          )}
        </div>
      </div>
    </div>
  );
}
