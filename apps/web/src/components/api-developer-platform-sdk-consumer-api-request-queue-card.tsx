"use client";

import { useState } from "react";

export default function RequestQueueCard() {
  const [stats] = useState({
    queued: 42,
    processing: 8,
    completed: 1250,
    failed: 15,
    maxConcurrent: 10,
    utilization: 80,
  });

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">
        Request Queue
      </h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
        Priority queue with concurrency limits
      </p>

      <div className="mt-4 grid grid-cols-2 gap-3">
        <div className="rounded-lg bg-blue-50 p-3 dark:bg-blue-950">
          <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">{stats.queued}</div>
          <div className="text-xs text-blue-500">Queued</div>
        </div>
        <div className="rounded-lg bg-amber-50 p-3 dark:bg-amber-950">
          <div className="text-2xl font-bold text-amber-600 dark:text-amber-400">{stats.processing}</div>
          <div className="text-xs text-amber-500">Processing</div>
        </div>
        <div className="rounded-lg bg-green-50 p-3 dark:bg-green-950">
          <div className="text-2xl font-bold text-green-600 dark:text-green-400">{stats.completed.toLocaleString()}</div>
          <div className="text-xs text-green-500">Completed</div>
        </div>
        <div className="rounded-lg bg-red-50 p-3 dark:bg-red-950">
          <div className="text-2xl font-bold text-red-600 dark:text-red-400">{stats.failed}</div>
          <div className="text-xs text-red-500">Failed</div>
        </div>
      </div>

      <div className="mt-3 flex items-center justify-between text-xs text-zinc-400 dark:text-zinc-500">
        <span>{stats.utilization}% utilization</span>
        <span>max {stats.maxConcurrent} concurrent</span>
      </div>
    </div>
  );
}
