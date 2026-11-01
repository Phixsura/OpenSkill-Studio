"use client";

import { useState } from "react";

interface TraceInfo { traceId: string; services: string[]; spanCount: number; durationMs: number; hasErrors: boolean; }

export default function TraceCorrelatorCard() {
  const [traces] = useState<TraceInfo[]>([
    { traceId: "abc123", services: ["gateway", "auth", "users", "db"], spanCount: 8, durationMs: 245, hasErrors: false },
    { traceId: "def456", services: ["gateway", "orders", "payments"], spanCount: 5, durationMs: 890, hasErrors: true },
  ]);

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">Trace Correlator</h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">Distributed trace correlation with span linking</p>

      <div className="mt-4 space-y-3">
        {traces.map((t) => (
          <div key={t.traceId} className="rounded-lg border border-zinc-100 p-3 dark:border-zinc-700">
            <div className="flex items-center justify-between">
              <code className="text-sm text-zinc-800 dark:text-zinc-200">{t.traceId}</code>
              <div className="flex items-center gap-2 text-xs">
                {t.hasErrors && <span className="text-red-500">error</span>}
                <span className="text-zinc-400">{t.durationMs}ms</span>
              </div>
            </div>
            <div className="mt-1 flex flex-wrap gap-1">
              {t.services.map((s) => (
                <span key={s} className="rounded bg-zinc-100 px-1.5 py-0.5 text-xs text-zinc-600 dark:bg-zinc-800 dark:text-zinc-400">{s}</span>
              ))}
            </div>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">
        {traces.length} traces · {traces.reduce((s, t) => s + t.spanCount, 0)} spans
      </div>
    </div>
  );
}
