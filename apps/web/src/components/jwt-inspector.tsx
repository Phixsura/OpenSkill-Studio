"use client";

import { useState } from "react";

interface JwtInspectorProps { onDecode: (token: string) => { valid: boolean; header?: Record<string, unknown>;
  payload?: Record<string, unknown>; algorithm?: string; expired?: boolean; error?: string }; }

export function JwtInspector({ onDecode }: JwtInspectorProps) {
  const [token, setToken] = useState("");
  const result = token.includes(".") ? onDecode(token) : null;

  return (
    <div className="space-y-3">
      <h3 className="text-sm font-semibold">JWT Inspector</h3>
      <textarea value={token} onChange={e => setToken(e.target.value)}
        placeholder="Paste JWT token here..." rows={3}
        className="w-full rounded border px-3 py-2 text-xs font-mono dark:bg-gray-800 dark:border-gray-600" />
      {result && !result.valid && <p className="text-xs text-red-500">⚠ {result.error}</p>}
      {result?.valid && (
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <span className="rounded bg-blue-100 px-2 py-0.5 text-xs text-blue-700 dark:bg-blue-900/30 dark:text-blue-300">{result.algorithm}</span>
            {result.expired && <span className="rounded bg-red-100 px-2 py-0.5 text-xs text-red-700 dark:bg-red-900/30 dark:text-red-400">Expired</span>}
          </div>
          <div>
            <p className="text-xs font-semibold text-gray-400 mb-1">Header</p>
            <pre className="rounded bg-gray-100 p-2 text-xs font-mono dark:bg-gray-800 overflow-x-auto">{JSON.stringify(result.header, null, 2)}</pre>
          </div>
          <div>
            <p className="text-xs font-semibold text-gray-400 mb-1">Payload</p>
            <pre className="rounded bg-gray-100 p-2 text-xs font-mono dark:bg-gray-800 overflow-x-auto">{JSON.stringify(result.payload, null, 2)}</pre>
          </div>
        </div>
      )}
    </div>
  );
}
