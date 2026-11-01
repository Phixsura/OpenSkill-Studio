"use client";

import { useState } from "react";

interface RunbookInfo { id: string; name: string; trigger: string; steps: number; }

export default function RunbookCard() {
  const [runbooks] = useState<RunbookInfo[]>([
    { id: "rb1", name: "Incident Response", trigger: "incident", steps: 5 },
    { id: "rb2", name: "Deployment Rollback", trigger: "alert", steps: 4 },
    { id: "rb3", name: "Database Failover", trigger: "manual", steps: 7 },
  ]);

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">API Runbooks</h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">Operational runbooks with step execution</p>

      <div className="mt-4 space-y-2">
        {runbooks.map((r) => (
          <div key={r.id} className="flex items-center justify-between rounded-lg border border-zinc-100 px-3 py-2 dark:border-zinc-700">
            <div>
              <span className="text-sm font-medium text-zinc-900 dark:text-zinc-100">{r.name}</span>
              <span className="ml-2 rounded bg-zinc-100 px-1.5 py-0.5 text-xs text-zinc-600 dark:bg-zinc-800 dark:text-zinc-400">{r.trigger}</span>
            </div>
            <span className="text-xs text-zinc-500">{r.steps} steps</span>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">{runbooks.length} runbooks</div>
    </div>
  );
}
