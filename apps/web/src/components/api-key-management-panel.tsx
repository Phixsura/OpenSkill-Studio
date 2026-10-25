"use client";

import { useState } from "react";

interface ApiKey {
  id: string;
  name: string;
  prefix: string;
  scopes: string[];
  createdAt: string;
  lastUsed: string;
  usageCount: number;
  active: boolean;
}

export function ApiKeyManagementPanel({
  keys,
  onCreate,
  onRevoke,
  onRotate,
}: {
  keys: ApiKey[];
  onCreate?: (name: string, scopes: string[]) => void;
  onRevoke?: (id: string) => void;
  onRotate?: (id: string) => void;
}) {
  const [showCreate, setShowCreate] = useState(false);
  const [newName, setNewName] = useState("");
  const [newScopes, setNewScopes] = useState<string[]>([]);

  const availableScopes = ["read", "write", "webhooks", "analytics", "admin"];

  const handleCreate = () => {
    if (newName.trim() && newScopes.length > 0) {
      onCreate?.(newName.trim(), newScopes);
      setNewName("");
      setNewScopes([]);
      setShowCreate(false);
    }
  };

  const toggleScope = (scope: string) => {
    setNewScopes((prev) => prev.includes(scope) ? prev.filter((s) => s !== scope) : [...prev, scope]);
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">🔑 API Keys</h2>
        <button
          onClick={() => setShowCreate(!showCreate)}
          className="text-sm bg-blue-600 text-white px-3 py-1.5 rounded-lg"
        >
          + New Key
        </button>
      </div>

      {showCreate && (
        <div className="rounded-lg border dark:border-gray-700 p-4 space-y-3 bg-gray-50 dark:bg-gray-900/50">
          <input
            type="text"
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            placeholder="Key name (e.g., Production)"
            className="w-full rounded-lg border dark:border-gray-700 bg-white dark:bg-gray-900 px-3 py-2 text-sm"
          />
          <div className="flex flex-wrap gap-2">
            {availableScopes.map((s) => (
              <button
                key={s}
                onClick={() => toggleScope(s)}
                className={`text-xs px-2.5 py-1 rounded-full border ${
                  newScopes.includes(s)
                    ? "bg-blue-600 text-white border-blue-600"
                    : "border-gray-300 dark:border-gray-600"
                }`}
              >
                {s}
              </button>
            ))}
          </div>
          <button onClick={handleCreate} className="text-sm bg-green-600 text-white px-4 py-1.5 rounded-lg">
            Create Key
          </button>
        </div>
      )}

      <div className="space-y-2">
        {keys.map((key) => (
          <div key={key.id} className={`rounded-lg border dark:border-gray-700 p-3 ${!key.active ? "opacity-50" : ""}`}>
            <div className="flex items-center justify-between">
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-medium text-sm">{key.name}</span>
                  <code className="text-xs bg-gray-100 dark:bg-gray-800 px-1.5 py-0.5 rounded">{key.prefix}...</code>
                  {!key.active && <span className="text-xs text-red-500">Revoked</span>}
                </div>
                <div className="flex gap-3 text-xs text-gray-400 mt-1">
                  <span>Created: {key.createdAt}</span>
                  <span>Last used: {key.lastUsed}</span>
                  <span>{key.usageCount.toLocaleString()} calls</span>
                </div>
                <div className="flex gap-1 mt-1">
                  {key.scopes.map((s) => (
                    <span key={s} className="text-xs bg-gray-100 dark:bg-gray-800 px-1.5 py-0.5 rounded">{s}</span>
                  ))}
                </div>
              </div>
              {key.active && (
                <div className="flex gap-2">
                  <button onClick={() => onRotate?.(key.id)} className="text-xs text-blue-500 hover:underline">Rotate</button>
                  <button onClick={() => onRevoke?.(key.id)} className="text-xs text-red-500 hover:underline">Revoke</button>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
