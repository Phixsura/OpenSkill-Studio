"use client";

import { useState } from "react";

interface KVEntry {
  key: string;
  value: string;
  sizeBytes: number;
  hasTtl: boolean;
}

export function KVStorePanel({
  entries,
  totalCount,
  onSet,
  onDelete,
  onScan,
}: {
  entries: KVEntry[];
  totalCount: number;
  onSet?: (key: string, value: string) => void;
  onDelete?: (key: string) => void;
  onScan?: (prefix: string) => void;
}) {
  const [showAdd, setShowAdd] = useState(false);
  const [newKey, setNewKey] = useState("");
  const [newValue, setNewValue] = useState("");
  const [prefix, setPrefix] = useState("");

  const handleSet = () => {
    if (newKey.trim() && newValue.trim()) {
      onSet?.(newKey, newValue);
      setNewKey(""); setNewValue(""); setShowAdd(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">🗄️ KV Store</h2>
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-500">{totalCount} keys</span>
          <button onClick={() => setShowAdd(!showAdd)}
            className="text-sm bg-blue-600 text-white px-3 py-1.5 rounded-lg">+ Set</button>
        </div>
      </div>

      <div className="flex gap-2">
        <input type="text" value={prefix} onChange={(e) => setPrefix(e.target.value)}
          placeholder="Scan prefix..."
          className="flex-1 rounded-lg border dark:border-gray-700 bg-white dark:bg-gray-900 px-3 py-1.5 text-sm font-mono" />
        <button onClick={() => onScan?.(prefix)}
          className="text-sm bg-gray-100 dark:bg-gray-800 px-3 py-1.5 rounded-lg">Scan</button>
      </div>

      {showAdd && (
        <div className="rounded-lg border dark:border-gray-700 p-3 bg-gray-50 dark:bg-gray-900/50 space-y-2">
          <input type="text" value={newKey} onChange={(e) => setNewKey(e.target.value)}
            placeholder="Key" className="w-full rounded border dark:border-gray-700 bg-white dark:bg-gray-900 px-2 py-1 text-sm font-mono" />
          <textarea value={newValue} onChange={(e) => setNewValue(e.target.value)}
            placeholder="Value" rows={2}
            className="w-full rounded border dark:border-gray-700 bg-white dark:bg-gray-900 px-2 py-1 text-sm font-mono" />
          <button onClick={handleSet} className="text-sm bg-green-600 text-white px-3 py-1 rounded">Save</button>
        </div>
      )}

      <div className="space-y-0.5">
        {entries.map((entry) => (
          <div key={entry.key} className="rounded-lg border dark:border-gray-700 p-2 flex items-center justify-between">
            <div className="flex items-center gap-2 flex-1 min-w-0">
              <code className="text-sm font-semibold text-blue-600 shrink-0">{entry.key}</code>
              <code className="text-xs text-gray-500 truncate">{entry.value}</code>
            </div>
            <div className="flex items-center gap-2 shrink-0">
              <span className="text-xs text-gray-400">{entry.sizeBytes}B</span>
              {entry.hasTtl && <span className="text-xs text-yellow-600">⏳</span>}
              <button onClick={() => onDelete?.(entry.key)} className="text-xs text-red-500">✕</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
