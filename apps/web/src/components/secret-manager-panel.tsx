"use client";

import { useState } from "react";

interface SecretEntry {
  name: string;
  scope: string;
  version: number;
  accessCount: number;
}

export function SecretManagerPanel({
  secrets: secretEntries,
  onStore,
  onRotate,
  onDelete,
}: {
  secrets: SecretEntry[];
  onStore?: (name: string, value: string, scope: string) => void;
  onRotate?: (name: string) => void;
  onDelete?: (name: string) => void;
}) {
  const [showAdd, setShowAdd] = useState(false);
  const [name, setName] = useState("");
  const [value, setValue] = useState("");
  const [scope, setScope] = useState("sandbox");

  const handleStore = () => {
    if (name.trim() && value.trim()) {
      onStore?.(name, value, scope);
      setName(""); setValue(""); setShowAdd(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">🔒 Secrets</h2>
        <button onClick={() => setShowAdd(!showAdd)}
          className="text-sm bg-blue-600 text-white px-3 py-1.5 rounded-lg">+ Add Secret</button>
      </div>

      {showAdd && (
        <div className="rounded-lg border dark:border-gray-700 p-3 bg-gray-50 dark:bg-gray-900/50 space-y-2">
          <input type="text" value={name} onChange={(e) => setName(e.target.value)}
            placeholder="SECRET_NAME" className="w-full rounded border dark:border-gray-700 bg-white dark:bg-gray-900 px-2 py-1 text-sm font-mono" />
          <input type="password" value={value} onChange={(e) => setValue(e.target.value)}
            placeholder="Secret value" className="w-full rounded border dark:border-gray-700 bg-white dark:bg-gray-900 px-2 py-1 text-sm" />
          <div className="flex gap-2">
            <select value={scope} onChange={(e) => setScope(e.target.value)}
              className="rounded border dark:border-gray-700 bg-white dark:bg-gray-900 px-2 py-1 text-xs">
              <option value="sandbox">Sandbox</option>
              <option value="extension">Extension</option>
            </select>
            <button onClick={handleStore} className="text-xs bg-green-600 text-white px-3 py-1 rounded">Store</button>
          </div>
        </div>
      )}

      <div className="space-y-1">
        {secretEntries.map((s) => (
          <div key={s.name} className="rounded-lg border dark:border-gray-700 p-3 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-yellow-500">🔑</span>
              <code className="text-sm font-semibold">{s.name}</code>
              <span className="text-xs bg-gray-100 dark:bg-gray-800 px-1.5 py-0.5 rounded">{s.scope}</span>
              <span className="text-xs text-gray-400">v{s.version}</span>
              <span className="text-xs text-gray-400">accessed {s.accessCount}x</span>
            </div>
            <div className="flex gap-1">
              <button onClick={() => onRotate?.(s.name)}
                className="text-xs bg-blue-600 text-white px-2 py-1 rounded">Rotate</button>
              <button onClick={() => onDelete?.(s.name)}
                className="text-xs text-red-500">✕</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
