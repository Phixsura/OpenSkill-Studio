"use client";

import { useState } from "react";

interface MergeConflict {
  path: string;
  values: unknown[];
  resolvedValue: unknown;
}

interface MergeResult {
  merged: Record<string, unknown>;
  conflicts: MergeConflict[];
  sourcesMerged: number;
}

export function ConfigMergePanel({
  result,
  sourceCount,
  onMerge,
}: {
  result: MergeResult | null;
  sourceCount: number;
  onMerge?: (strategy: string) => void;
}) {
  const [tab, setTab] = useState<"merged" | "conflicts">("merged");
  const [strategy, setStrategy] = useState("last_wins");

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">🔀 Config Merge</h2>
        <div className="flex items-center gap-2">
          <select value={strategy} onChange={(e) => setStrategy(e.target.value)}
            className="text-xs rounded border dark:border-gray-700 bg-white dark:bg-gray-900 px-2 py-1">
            <option value="last_wins">Last Wins</option>
            <option value="first_wins">First Wins</option>
            <option value="error">Error on Conflict</option>
          </select>
          <button onClick={() => onMerge?.(strategy)}
            className="text-sm bg-green-600 text-white px-3 py-1.5 rounded-lg">Merge {sourceCount} Sources</button>
        </div>
      </div>

      {result && (
        <>
          <div className="flex gap-1">
            <button onClick={() => setTab("merged")}
              className={`text-xs px-3 py-1 rounded-lg ${tab === "merged" ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
              Result ({Object.keys(result.merged).length} keys)
            </button>
            <button onClick={() => setTab("conflicts")}
              className={`text-xs px-3 py-1 rounded-lg ${tab === "conflicts" ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
              Conflicts ({result.conflicts.length})
            </button>
          </div>

          {tab === "merged" && (
            <pre className="rounded-lg border dark:border-gray-700 bg-gray-950 dark:bg-black p-3 text-xs text-green-400 font-mono overflow-auto max-h-48">
              {JSON.stringify(result.merged, null, 2)}
            </pre>
          )}

          {tab === "conflicts" && (
            <div className="space-y-1">
              {result.conflicts.length === 0 && <span className="text-sm text-green-600">No conflicts</span>}
              {result.conflicts.map((c, i) => (
                <div key={i} className="rounded-lg border-l-4 border-yellow-400 bg-yellow-50 dark:bg-yellow-900/10 p-2">
                  <code className="text-xs font-bold">{c.path}</code>
                  <div className="flex gap-2 text-xs mt-0.5">
                    {c.values.map((v, j) => (
                      <span key={j} className="text-gray-500">{JSON.stringify(v)}</span>
                    ))}
                    <span className="text-green-600 font-bold">→ {JSON.stringify(c.resolvedValue)}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}
