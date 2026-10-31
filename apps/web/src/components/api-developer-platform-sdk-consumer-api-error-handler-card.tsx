"use client";

import { useState } from "react";

interface ErrorInfo { code: string; count: number; retryable: boolean; }

export default function ErrorHandlerCard() {
  const [errors] = useState<ErrorInfo[]>([
    { code: "RATE_LIMIT", count: 245, retryable: true },
    { code: "TIMEOUT", count: 89, retryable: true },
    { code: "VALIDATION", count: 156, retryable: false },
    { code: "AUTH_FAILED", count: 34, retryable: false },
  ]);
  const [alertCount] = useState(3);

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">Error Handler</h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">Centralized error handling with retry policies</p>

      <div className="mt-4 space-y-2">
        {errors.map((e) => (
          <div key={e.code} className="flex items-center justify-between rounded-lg border border-zinc-100 px-3 py-2 dark:border-zinc-700">
            <div className="flex items-center gap-2">
              <code className="text-sm text-zinc-800 dark:text-zinc-200">{e.code}</code>
              {e.retryable && <span className="rounded bg-green-100 px-1 py-0.5 text-xs text-green-700 dark:bg-green-900 dark:text-green-300">retry</span>}
            </div>
            <span className="text-xs text-zinc-500">{e.count} occurrences</span>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">
        {errors.length} error codes · {alertCount} alerts triggered
      </div>
    </div>
  );
}
