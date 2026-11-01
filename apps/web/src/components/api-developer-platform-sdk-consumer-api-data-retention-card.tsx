"use client";

import { useState } from "react";

interface PolicyRow {
  category: string;
  retentionDays: number | null;
  autoPurge: boolean;
  archive: boolean;
}

export default function DataRetentionCard() {
  const [policies] = useState<PolicyRow[]>([
    { category: "Logs", retentionDays: 30, autoPurge: true, archive: false },
    { category: "Analytics", retentionDays: 90, autoPurge: true, archive: true },
    { category: "Audit", retentionDays: 365, autoPurge: false, archive: true },
    { category: "Requests", retentionDays: 7, autoPurge: true, archive: false },
  ]);

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">Data Retention</h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">Retention policies with purge scheduling</p>

      <div className="mt-4 space-y-2">
        {policies.map((p) => (
          <div key={p.category} className="flex items-center justify-between rounded-lg border border-zinc-100 px-3 py-2 dark:border-zinc-700">
            <div>
              <span className="text-sm font-medium text-zinc-900 dark:text-zinc-100">{p.category}</span>
              {p.archive && <span className="ml-2 text-xs text-zinc-400">📦 archive</span>}
            </div>
            <div className="flex items-center gap-2 text-xs">
              <span className="text-zinc-500">{p.retentionDays}d</span>
              <span className={p.autoPurge ? "text-green-600 dark:text-green-400" : "text-zinc-400"}>
                {p.autoPurge ? "auto" : "manual"}
              </span>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">
        {policies.length} policies configured
      </div>
    </div>
  );
}
