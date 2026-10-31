"use client";

import { useState } from "react";

interface ScopedKey {
  keyId: string;
  name: string;
  scopes: string[];
  usageCount: number;
  maxUsage: number;
  revoked: boolean;
  hasIpRestriction: boolean;
  hasExpiry: boolean;
}

export function ApiKeyScopePanel({
  keys,
  availableScopes,
  onCreateKey,
  onRevoke,
}: {
  keys: ScopedKey[];
  availableScopes: string[];
  onCreateKey?: (name: string, scopes: string[]) => void;
  onRevoke?: (keyId: string) => void;
}) {
  const [showCreate, setShowCreate] = useState(false);
  const [name, setName] = useState("");
  const [selectedScopes, setSelectedScopes] = useState<string[]>([]);

  const toggleScope = (s: string) => {
    setSelectedScopes((prev) => prev.includes(s) ? prev.filter((x) => x !== s) : [...prev, s]);
  };

  const active = keys.filter((k) => !k.revoked).length;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">🔐 Scoped API Keys</h2>
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-500">{active} active</span>
          <button onClick={() => setShowCreate(!showCreate)}
            className="text-sm bg-blue-600 text-white px-3 py-1.5 rounded-lg">+ New Key</button>
        </div>
      </div>

      {showCreate && (
        <div className="rounded-lg border dark:border-gray-700 p-3 bg-gray-50 dark:bg-gray-900/50 space-y-2">
          <input type="text" value={name} onChange={(e) => setName(e.target.value)}
            placeholder="Key name" className="w-full rounded border dark:border-gray-700 bg-white dark:bg-gray-900 px-2 py-1 text-sm" />
          <div className="flex flex-wrap gap-1">
            {availableScopes.map((s) => (
              <button key={s} onClick={() => toggleScope(s)}
                className={`text-xs px-2 py-0.5 rounded-full border ${selectedScopes.includes(s) ? "bg-blue-600 text-white border-blue-600" : "border-gray-300 dark:border-gray-600"}`}>
                {s}
              </button>
            ))}
          </div>
          <button onClick={() => { onCreateKey?.(name, selectedScopes); setShowCreate(false); setName(""); setSelectedScopes([]); }}
            disabled={!name.trim() || selectedScopes.length === 0}
            className="text-xs bg-green-600 text-white px-3 py-1 rounded disabled:opacity-50">Create Key</button>
        </div>
      )}

      <div className="space-y-1">
        {keys.map((key) => (
          <div key={key.keyId} className={`rounded-lg border dark:border-gray-700 p-3 ${key.revoked ? "opacity-50" : ""}`}>
            <div className="flex items-center justify-between mb-1">
              <div className="flex items-center gap-2">
                <code className="text-sm font-semibold">{key.name}</code>
                {key.revoked && <span className="text-xs text-red-500">revoked</span>}
                {key.hasIpRestriction && <span className="text-xs text-gray-400">🌐 IP</span>}
                {key.hasExpiry && <span className="text-xs text-gray-400">⏰</span>}
                {key.maxUsage > 0 && <span className="text-xs text-gray-400">{key.usageCount}/{key.maxUsage}</span>}
              </div>
              {!key.revoked && (
                <button onClick={() => onRevoke?.(key.keyId)}
                  className="text-xs bg-red-600 text-white px-2 py-0.5 rounded">Revoke</button>
              )}
            </div>
            <div className="flex flex-wrap gap-1">
              {key.scopes.map((s) => (
                <span key={s} className="text-xs bg-blue-100 dark:bg-blue-900/30 text-blue-700 px-1.5 py-0.5 rounded-full">{s}</span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
