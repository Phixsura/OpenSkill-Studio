"use client";

import { useState } from "react";

interface ApiKey { prefix: string; label: string; scopes: string[]; created_at: string; last_used: string | null; status: string; }
interface ApiKeyManagerPanelProps { keys: ApiKey[]; onRevoke: (prefix: string) => void; onCreate: () => void; }

export function ApiKeyManagerPanel({ keys, onRevoke, onCreate }: ApiKeyManagerPanelProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">API Keys</h2>
        <button onClick={onCreate} className="rounded bg-blue-600 px-3 py-1.5 text-sm text-white">
          Create Key
        </button>
      </div>
      {keys.length === 0 ? (
        <p className="text-sm text-gray-400">No API keys yet</p>
      ) : (
        <div className="space-y-2">
          {keys.map(k => (
            <div key={k.prefix} className="flex items-center justify-between rounded-lg border p-3 dark:border-gray-700">
              <div>
                <p className="font-medium">{k.label}</p>
                <p className="font-mono text-xs text-gray-400">{k.prefix}••••••••</p>
                <div className="mt-1 flex gap-1">
                  {k.scopes.map(s => (
                    <span key={s} className="rounded bg-gray-100 px-1.5 py-0.5 text-xs dark:bg-gray-800">{s}</span>
                  ))}
                </div>
              </div>
              <button onClick={() => onRevoke(k.prefix)} className="rounded border border-red-300 px-2 py-1 text-xs text-red-600">
                Revoke
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
