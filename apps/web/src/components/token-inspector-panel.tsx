"use client";

import { useState } from "react";

interface TokenClaims { sub?: string; iss?: string; aud?: string; exp?: number; [key: string]: unknown; }
interface TokenInspectorPanelProps { onDecode: (token: string) => { claims: TokenClaims; expired: boolean; scopes: string[] } | { error: string }; }

export function TokenInspectorPanel({ onDecode }: TokenInspectorPanelProps) {
  const [token, setToken] = useState("");
  const [result, setResult] = useState<any>(null);

  const decode = () => setResult(onDecode(token));

  return (
    <div className="space-y-3 rounded-lg border p-4 dark:border-gray-700">
      <h2 className="text-lg font-semibold">Token Inspector</h2>
      <textarea value={token} onChange={e => setToken(e.target.value)}
        placeholder="Paste JWT token..." rows={2}
        className="w-full rounded border px-3 py-2 font-mono text-xs dark:border-gray-600 dark:bg-gray-700" />
      <button onClick={decode} className="w-full rounded bg-blue-600 py-2 text-sm text-white">Decode</button>
      {result && !result.error && (
        <div className="space-y-2 rounded bg-gray-50 p-3 dark:bg-gray-800">
          <div className="flex justify-between text-xs">
            <span className="text-gray-400">Subject</span>
            <span className="font-mono">{result.claims.sub ?? "—"}</span>
          </div>
          <div className="flex justify-between text-xs">
            <span className="text-gray-400">Issuer</span>
            <span className="font-mono">{result.claims.iss ?? "—"}</span>
          </div>
          <div className="flex justify-between text-xs">
            <span className="text-gray-400">Expired</span>
            <span className={result.expired ? "text-red-500" : "text-green-500"}>
              {result.expired ? "Yes ❌" : "No ✅"}
            </span>
          </div>
          {result.scopes.length > 0 && (
            <div className="flex gap-1">
              {result.scopes.map((s: string) => (
                <span key={s} className="rounded bg-blue-100 px-1.5 py-0.5 text-xs dark:bg-blue-900/30">{s}</span>
              ))}
            </div>
          )}
        </div>
      )}
      {result?.error && <p className="text-sm text-red-500">{result.error}</p>}
    </div>
  );
}
