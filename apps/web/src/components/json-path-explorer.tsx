"use client";

import { useState } from "react";

interface JsonPathExplorerProps { onQuery: (path: string) => { found: boolean; value?: unknown; error?: string; type?: string }; }

export function JsonPathExplorer({ onQuery }: JsonPathExplorerProps) {
  const [path, setPath] = useState("");
  const result = path.length > 1 ? onQuery(path) : null;

  return (
    <div className="space-y-3">
      <h3 className="text-sm font-semibold">JSONPath Explorer</h3>
      <input type="text" value={path} onChange={e => setPath(e.target.value)}
        placeholder="$.app.config.port"
        className="w-full rounded border px-3 py-2 text-sm font-mono dark:bg-gray-800 dark:border-gray-600" />
      {result && (
        <div className={`rounded-lg border p-3 ${result.found ? "dark:border-gray-700" : "border-red-300 dark:border-red-700"}`}>
          {result.found ? (
            <>
              <div className="flex items-center gap-2 mb-1">
                <span className="text-xs text-gray-400">Type: {result.type}</span>
              </div>
              <pre className="text-sm font-mono bg-gray-100 dark:bg-gray-800 p-2 rounded overflow-x-auto">
                {JSON.stringify(result.value, null, 2)}
              </pre>
            </>
          ) : (
            <p className="text-xs text-red-500">⚠ {result.error}</p>
          )}
        </div>
      )}
    </div>
  );
}
