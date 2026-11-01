"use client";

import { useState } from "react";

interface EnvVar {
  key: string;
  value: string;
  isSecret: boolean;
  scope: string;
  description?: string;
}

const scopeColors: Record<string, string> = {
  all: "bg-gray-100 text-gray-600 dark:bg-gray-800",
  development: "bg-blue-100 text-blue-700 dark:bg-blue-900/30",
  staging: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30",
  production: "bg-red-100 text-red-700 dark:bg-red-900/30",
};

export function EnvVarManagerPanel({
  vars: envVars,
  extensionName,
  onAdd,
  onDelete,
}: {
  vars: EnvVar[];
  extensionName: string;
  onAdd?: (key: string, value: string, isSecret: boolean, scope: string) => void;
  onDelete?: (key: string) => void;
}) {
  const [showAdd, setShowAdd] = useState(false);
  const [newKey, setNewKey] = useState("EXT_");
  const [newValue, setNewValue] = useState("");
  const [newSecret, setNewSecret] = useState(false);
  const [newScope, setNewScope] = useState("all");

  const handleAdd = () => {
    if (newKey.trim() && newValue.trim()) {
      onAdd?.(newKey, newValue, newSecret, newScope);
      setNewKey("EXT_"); setNewValue(""); setNewSecret(false); setShowAdd(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">🔐 {extensionName} Environment</h2>
        <button onClick={() => setShowAdd(!showAdd)}
          className="text-sm bg-blue-600 text-white px-3 py-1.5 rounded-lg">+ Add Variable</button>
      </div>

      {showAdd && (
        <div className="rounded-lg border dark:border-gray-700 p-3 bg-gray-50 dark:bg-gray-900/50 space-y-2">
          <div className="grid grid-cols-2 gap-2">
            <input type="text" value={newKey} onChange={(e) => setNewKey(e.target.value)}
              placeholder="EXT_MY_VAR" className="rounded border dark:border-gray-700 bg-white dark:bg-gray-900 px-2 py-1 text-sm font-mono" />
            <input type={newSecret ? "password" : "text"} value={newValue} onChange={(e) => setNewValue(e.target.value)}
              placeholder="value" className="rounded border dark:border-gray-700 bg-white dark:bg-gray-900 px-2 py-1 text-sm" />
          </div>
          <div className="flex items-center gap-3">
            <label className="flex items-center gap-1 text-xs">
              <input type="checkbox" checked={newSecret} onChange={(e) => setNewSecret(e.target.checked)} /> Secret
            </label>
            <select value={newScope} onChange={(e) => setNewScope(e.target.value)}
              className="text-xs rounded border dark:border-gray-700 bg-white dark:bg-gray-900 px-2 py-1">
              <option value="all">All</option>
              <option value="development">Development</option>
              <option value="staging">Staging</option>
              <option value="production">Production</option>
            </select>
            <button onClick={handleAdd} className="text-xs bg-green-600 text-white px-3 py-1 rounded">Save</button>
          </div>
        </div>
      )}

      <div className="space-y-1">
        {envVars.map((v) => (
          <div key={v.key} className="rounded-lg border dark:border-gray-700 p-3 flex items-center justify-between">
            <div className="flex items-center gap-2 flex-1 min-w-0">
              <code className="text-sm font-semibold">{v.key}</code>
              <span className={`text-xs px-1.5 py-0.5 rounded-full ${scopeColors[v.scope] || scopeColors.all}`}>{v.scope}</span>
              {v.isSecret && <span className="text-xs text-yellow-600">🔒 secret</span>}
            </div>
            <div className="flex items-center gap-2 shrink-0">
              <code className="text-xs text-gray-500">{v.value}</code>
              <button onClick={() => onDelete?.(v.key)} className="text-xs text-red-500">✕</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
