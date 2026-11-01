"use client";

import { useState } from "react";

interface TraceInfo { traceId: string; method: string; url: string; durationMs: number; hasError: boolean; }

export default function RequestDebuggerCard() {
  const [traces] = useState<TraceInfo[]>([
    { traceId: "tr-a1b2", method: "GET", url: "/api/users", durationMs: 145, hasError: false },
    { traceId: "tr-c3d4", method: "POST", url: "/api/orders", durationMs: 890, hasError: true },
    { traceId: "tr-e5f6", method: "GET", url: "/api/search", durationMs: 320, hasError: false },
  ]);

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">Request Debugger</h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">Request debugging with trace replay</p>

      <div className="mt-4 space-y-2">
        {traces.map((t) => (
          <div key={t.traceId} className="flex items-center justify-between rounded-lg border border-zinc-100 px-3 py-2 dark:border-zinc-700">
            <div className="flex items-center gap-2">
              {t.hasError && <span className="h-2 w-2 rounded-full bg-red-500" />}
              <span className="rounded bg-zinc-100 px-1 py-0.5 text-xs font-bold text-zinc-600 dark:bg-zinc-800 dark:text-zinc-400">{t.method}</span>
              <span className="font-mono text-sm text-zinc-800 dark:text-zinc-200">{t.url}</span>
            </div>
            <span className="text-xs text-zinc-400">{t.durationMs}ms</span>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">
        {traces.length} traces · {traces.filter((t) => t.hasError).length} errors
      </div>
    </div>
  );
}
