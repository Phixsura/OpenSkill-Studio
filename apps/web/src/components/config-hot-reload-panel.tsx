"use client";

import { useState } from "react";

interface ConfigChange {
  changeId: string;
  key: string;
  oldValue: string;
  newValue: string;
  applied: boolean;
  rolledBack: boolean;
  timestamp: string;
}

export function ConfigHotReloadPanel({
  currentConfig,
  history,
  subscribers,
  onApply,
  onRollback,
  onRollbackAll,
}: {
  currentConfig: Record<string, string>;
  history: ConfigChange[];
  subscribers: string[];
  onApply?: (changes: Record<string, string>) => void;
  onRollback?: (changeId: string) => void;
  onRollbackAll?: () => void;
}) {
  const [tab, setTab] = useState<"config" | "history">("config");
  const [editKey, setEditKey] = useState("");
  const [editValue, setEditValue] = useState("");

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">🔥 Hot Reload</h2>
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-500">{subscribers.length} subscribers</span>
          <button onClick={onRollbackAll} className="text-xs bg-yellow-600 text-white px-2 py-1 rounded">Rollback All</button>
        </div>
      </div>

      <div className="flex gap-1">
        <button onClick={() => setTab("config")}
          className={`text-xs px-3 py-1 rounded-lg ${tab === "config" ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
          Config ({Object.keys(currentConfig).length})
        </button>
        <button onClick={() => setTab("history")}
          className={`text-xs px-3 py-1 rounded-lg ${tab === "history" ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
          History ({history.length})
        </button>
      </div>

      {tab === "config" && (
        <div className="space-y-2">
          <div className="space-y-0.5">
            {Object.entries(currentConfig).map(([key, value]) => (
              <div key={key} className="rounded-lg border dark:border-gray-700 p-2 flex items-center justify-between">
                <code className="text-sm font-semibold text-blue-600">{key}</code>
                <code className="text-sm text-gray-500">{value}</code>
              </div>
            ))}
          </div>
          <div className="flex gap-2">
            <input type="text" value={editKey} onChange={(e) => setEditKey(e.target.value)}
              placeholder="key" className="flex-1 rounded border dark:border-gray-700 bg-white dark:bg-gray-900 px-2 py-1 text-sm font-mono" />
            <input type="text" value={editValue} onChange={(e) => setEditValue(e.target.value)}
              placeholder="value" className="flex-1 rounded border dark:border-gray-700 bg-white dark:bg-gray-900 px-2 py-1 text-sm" />
            <button onClick={() => { onApply?.({ [editKey]: editValue }); setEditKey(""); setEditValue(""); }}
              className="text-xs bg-green-600 text-white px-3 py-1 rounded">Apply</button>
          </div>
        </div>
      )}

      {tab === "history" && (
        <div className="space-y-1">
          {history.map((c) => (
            <div key={c.changeId} className={`rounded-lg border dark:border-gray-700 p-2 ${c.rolledBack ? "opacity-50" : ""}`}>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-xs">
                  <code className="font-semibold">{c.key}</code>
                  <span className="text-red-500">{c.oldValue}</span>
                  <span className="text-gray-400">→</span>
                  <span className="text-green-600">{c.newValue}</span>
                  {c.rolledBack && <span className="text-yellow-600">↩ rolled back</span>}
                </div>
                {c.applied && !c.rolledBack && (
                  <button onClick={() => onRollback?.(c.changeId)}
                    className="text-xs text-yellow-600">Undo</button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
