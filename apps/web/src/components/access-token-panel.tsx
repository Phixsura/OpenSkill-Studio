"use client";

import { useState } from "react";

interface AccessToken {
  id: string;
  scopes: string[];
  expiresAt: string;
  revoked: boolean;
  lastUsed?: string;
  useCount: number;
  createdAt: string;
}

export function AccessTokenPanel({
  tokens,
  extensionName,
  availableScopes,
  onIssue,
  onRevoke,
}: {
  tokens: AccessToken[];
  extensionName: string;
  availableScopes: string[];
  onIssue?: (scopes: string[]) => void;
  onRevoke?: (id: string) => void;
}) {
  const [showCreate, setShowCreate] = useState(false);
  const [selectedScopes, setSelectedScopes] = useState<string[]>([]);

  const toggleScope = (s: string) => {
    setSelectedScopes((prev) =>
      prev.includes(s) ? prev.filter((x) => x !== s) : [...prev, s]
    );
  };

  const active = tokens.filter((t) => !t.revoked).length;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">🔑 {extensionName} Tokens</h2>
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-500">{active} active</span>
          <button onClick={() => setShowCreate(!showCreate)}
            className="text-sm bg-blue-600 text-white px-3 py-1.5 rounded-lg">
            + New Token
          </button>
        </div>
      </div>

      {showCreate && (
        <div className="rounded-lg border dark:border-gray-700 p-4 space-y-3 bg-gray-50 dark:bg-gray-900/50">
          <span className="text-sm font-medium">Select scopes:</span>
          <div className="flex flex-wrap gap-1">
            {availableScopes.map((s) => (
              <button key={s} onClick={() => toggleScope(s)}
                className={`text-xs px-2 py-1 rounded-full border ${
                  selectedScopes.includes(s) ? "bg-blue-600 text-white border-blue-600" : "border-gray-300 dark:border-gray-600"
                }`}>{s}</button>
            ))}
          </div>
          <button onClick={() => { onIssue?.(selectedScopes); setShowCreate(false); setSelectedScopes([]); }}
            disabled={selectedScopes.length === 0}
            className="text-sm bg-green-600 text-white px-4 py-1.5 rounded-lg disabled:opacity-50">
            Issue Token
          </button>
        </div>
      )}

      <div className="space-y-2">
        {tokens.map((t) => (
          <div key={t.id} className={`rounded-xl border dark:border-gray-700 p-3 ${t.revoked ? "opacity-50" : ""}`}>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <code className="text-xs bg-gray-100 dark:bg-gray-800 px-2 py-0.5 rounded">{t.id}</code>
                {t.revoked && <span className="text-xs text-red-500 font-medium">Revoked</span>}
              </div>
              {!t.revoked && (
                <button onClick={() => onRevoke?.(t.id)}
                  className="text-xs text-red-500 hover:text-red-700">Revoke</button>
              )}
            </div>
            <div className="flex flex-wrap gap-1 mt-1">
              {t.scopes.map((s) => (
                <span key={s} className="text-xs bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 px-1.5 py-0.5 rounded-full">{s}</span>
              ))}
            </div>
            <div className="flex gap-3 mt-1 text-xs text-gray-400">
              <span>Used {t.useCount}x</span>
              <span>Expires {t.expiresAt}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
