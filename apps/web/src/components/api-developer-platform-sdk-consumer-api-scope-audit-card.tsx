"use client";

import { useState } from "react";

interface AuditResult { keyId: string; grantedCount: number; usedCount: number; overPermPct: number; recommendation: string; }

const REC_COLOR: Record<string, string> = {
  optimal: "text-green-600 dark:text-green-400",
  reduce_scopes: "text-red-600 dark:text-red-400",
  expand_grant: "text-amber-600 dark:text-amber-400",
};

export default function ScopeAuditCard() {
  const [audits] = useState<AuditResult[]>([
    { keyId: "key_prod_1", grantedCount: 3, usedCount: 3, overPermPct: 0, recommendation: "optimal" },
    { keyId: "key_admin", grantedCount: 8, usedCount: 2, overPermPct: 75, recommendation: "reduce_scopes" },
    { keyId: "key_ci", grantedCount: 2, usedCount: 3, overPermPct: 0, recommendation: "expand_grant" },
  ]);

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">Scope Audit</h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">Audit API key scope usage and over-permissions</p>

      <div className="mt-4 space-y-2">
        {audits.map((a) => (
          <div key={a.keyId} className="flex items-center justify-between rounded-lg border border-zinc-100 px-3 py-2 dark:border-zinc-700">
            <div>
              <code className="text-sm text-zinc-800 dark:text-zinc-200">{a.keyId}</code>
              <span className="ml-2 text-xs text-zinc-400">{a.usedCount}/{a.grantedCount} scopes used</span>
            </div>
            <span className={`text-xs font-medium ${REC_COLOR[a.recommendation] ?? "text-zinc-500"}`}>
              {a.recommendation.replace(/_/g, " ")}
            </span>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">
        {audits.filter((a) => a.recommendation === "optimal").length}/{audits.length} keys optimal
      </div>
    </div>
  );
}
