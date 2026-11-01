"use client";

import { useState } from "react";

interface ScopeInfo { scopeId: string; name: string; category: string; sensitive: boolean; }

export default function OAuthScopeCard() {
  const [scopes] = useState<ScopeInfo[]>([
    { scopeId: "read:users", name: "Read Users", category: "users", sensitive: false },
    { scopeId: "write:users", name: "Write Users", category: "users", sensitive: true },
    { scopeId: "read:orders", name: "Read Orders", category: "orders", sensitive: false },
    { scopeId: "admin", name: "Admin Access", category: "general", sensitive: true },
  ]);

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">OAuth Scopes</h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">Granular permission management</p>

      <div className="mt-4 space-y-2">
        {scopes.map((s) => (
          <div key={s.scopeId} className="flex items-center justify-between rounded-lg border border-zinc-100 px-3 py-2 dark:border-zinc-700">
            <div className="flex items-center gap-2">
              <code className="text-sm text-zinc-800 dark:text-zinc-200">{s.scopeId}</code>
              {s.sensitive && <span className="text-xs text-red-500">⚠ sensitive</span>}
            </div>
            <span className="text-xs text-zinc-400">{s.category}</span>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">
        {scopes.length} scopes · {scopes.filter((s) => s.sensitive).length} sensitive
      </div>
    </div>
  );
}
