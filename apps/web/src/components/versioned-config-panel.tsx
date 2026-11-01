"use client";

import { useState } from "react";

interface ConfigVersion {
  version: number;
  author: string;
  message: string;
  createdAt: string;
  keyCount: number;
}

interface ConfigDiff {
  added: Record<string, unknown>;
  removed: Record<string, unknown>;
  changed: Record<string, { from: unknown; to: unknown }>;
  hasChanges: boolean;
}

export function VersionedConfigPanel({
  versions,
  currentData,
  diff,
  onRollback,
  onCompare,
}: {
  versions: ConfigVersion[];
  currentData: Record<string, unknown>;
  diff: ConfigDiff | null;
  onRollback?: (version: number) => void;
  onCompare?: (v1: number, v2: number) => void;
}) {
  const [tab, setTab] = useState<"current" | "history" | "diff">("current");

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold">⚙️ Configuration</h2>

      <div className="flex gap-1">
        {(["current", "history", "diff"] as const).map((t) => (
          <button key={t} onClick={() => setTab(t)}
            className={`text-xs px-3 py-1 rounded-lg ${tab === t ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
            {t === "current" ? "Current" : t === "history" ? `History (${versions.length})` : "Diff"}
          </button>
        ))}
      </div>

      {tab === "current" && (
        <div className="rounded-lg border dark:border-gray-700 bg-gray-950 dark:bg-black p-3 font-mono text-xs text-gray-200 overflow-x-auto">
          <pre>{JSON.stringify(currentData, null, 2)}</pre>
        </div>
      )}

      {tab === "history" && (
        <div className="space-y-1">
          {versions.map((v) => (
            <div key={v.version} className="rounded-lg border dark:border-gray-700 p-3 flex items-center justify-between">
              <div>
                <span className="text-sm font-bold">v{v.version}</span>
                <span className="text-xs text-gray-500 ml-2">by {v.author}</span>
                {v.message && <span className="text-xs text-gray-400 ml-2">{v.message}</span>}
                <span className="text-xs text-gray-400 ml-2">{v.keyCount} keys</span>
              </div>
              <div className="flex gap-1">
                {v.version < versions.length && (
                  <button onClick={() => onCompare?.(v.version, versions.length)}
                    className="text-xs bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded">Compare</button>
                )}
                <button onClick={() => onRollback?.(v.version)}
                  className="text-xs bg-yellow-600 text-white px-2 py-1 rounded">Rollback</button>
              </div>
            </div>
          ))}
        </div>
      )}

      {tab === "diff" && diff && (
        <div className="space-y-2">
          {Object.entries(diff.added).map(([k, v]) => (
            <div key={k} className="text-xs text-green-600">+ {k}: {JSON.stringify(v)}</div>
          ))}
          {Object.entries(diff.removed).map(([k, v]) => (
            <div key={k} className="text-xs text-red-600">- {k}: {JSON.stringify(v)}</div>
          ))}
          {Object.entries(diff.changed).map(([k, v]) => (
            <div key={k} className="text-xs">
              <span className="text-yellow-600">~ {k}:</span>
              <span className="text-red-500 ml-1">{JSON.stringify(v.from)}</span>
              <span className="text-gray-400 mx-1">→</span>
              <span className="text-green-500">{JSON.stringify(v.to)}</span>
            </div>
          ))}
          {!diff.hasChanges && <span className="text-sm text-gray-500">No differences</span>}
        </div>
      )}
    </div>
  );
}
