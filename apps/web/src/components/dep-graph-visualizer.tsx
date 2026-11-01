"use client";

import { useState } from "react";

interface DepNode {
  id: string;
  version: string;
  dependencies: string[];
  status: "ok" | "conflict" | "missing" | "circular";
}

interface VersionConflict {
  dependency: string;
  requestedBy: { extension: string; version: string }[];
}

const statusStyles: Record<string, { bg: string; icon: string }> = {
  ok: { bg: "border-green-300 dark:border-green-700 bg-green-50 dark:bg-green-900/20", icon: "✅" },
  conflict: { bg: "border-yellow-300 dark:border-yellow-700 bg-yellow-50 dark:bg-yellow-900/20", icon: "⚠️" },
  missing: { bg: "border-red-300 dark:border-red-700 bg-red-50 dark:bg-red-900/20", icon: "❌" },
  circular: { bg: "border-purple-300 dark:border-purple-700 bg-purple-50 dark:bg-purple-900/20", icon: "🔄" },
};

export function DepGraphVisualizer({
  nodes,
  conflicts,
  installOrder,
  extensionName,
}: {
  nodes: DepNode[];
  conflicts: VersionConflict[];
  installOrder: string[];
  extensionName: string;
}) {
  const [view, setView] = useState<"graph" | "order" | "conflicts">("graph");

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold">🔗 {extensionName} Dependencies</h2>

      <div className="flex gap-1">
        {(["graph", "order", "conflicts"] as const).map((v) => (
          <button key={v} onClick={() => setView(v)}
            className={`text-xs px-3 py-1 rounded-lg ${view === v ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
            {v === "graph" ? "Graph" : v === "order" ? "Install Order" : `Conflicts (${conflicts.length})`}
          </button>
        ))}
      </div>

      {view === "graph" && (
        <div className="space-y-2">
          {nodes.map((node) => {
            const style = statusStyles[node.status];
            return (
              <div key={node.id} className={`rounded-lg border-2 ${style.bg} p-3`}>
                <div className="flex items-center gap-2">
                  <span>{style.icon}</span>
                  <span className="font-mono text-sm font-semibold">{node.id}</span>
                  <span className="text-xs text-gray-500">v{node.version}</span>
                </div>
                {node.dependencies.length > 0 && (
                  <div className="mt-1 ml-6 text-xs text-gray-500">
                    → {node.dependencies.join(", ")}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {view === "order" && (
        <ol className="space-y-1">
          {installOrder.map((id, i) => (
            <li key={id} className="flex items-center gap-2 text-sm">
              <span className="w-6 h-6 rounded-full bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 flex items-center justify-center text-xs font-bold">
                {i + 1}
              </span>
              <span className="font-mono">{id}</span>
            </li>
          ))}
        </ol>
      )}

      {view === "conflicts" && (
        <div className="space-y-2">
          {conflicts.length === 0 && (
            <p className="text-sm text-gray-500">No version conflicts detected.</p>
          )}
          {conflicts.map((c, i) => (
            <div key={i} className="rounded-lg border border-yellow-300 dark:border-yellow-700 bg-yellow-50 dark:bg-yellow-900/20 p-3">
              <span className="font-mono text-sm font-semibold">⚠️ {c.dependency}</span>
              <div className="mt-1 space-y-0.5">
                {c.requestedBy.map((r, j) => (
                  <div key={j} className="text-xs text-gray-600 dark:text-gray-400 ml-4">
                    {r.extension} requires <code>{r.version}</code>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
