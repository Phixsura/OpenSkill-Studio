"use client";

import { useState } from "react";

export default function RetryQueueCard() {
  const [stats] = useState({
    total: 24, pending: 12, retrying: 5, dead: 7, succeeded: 0,
  });

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">Retry Queue</h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">Dead letter queue with manual retry</p>

      <div className="mt-4 grid grid-cols-3 gap-3 text-center">
        <div className="rounded-lg bg-amber-50 p-2 dark:bg-amber-950">
          <div className="text-xl font-bold text-amber-600 dark:text-amber-400">{stats.pending}</div>
          <div className="text-xs text-amber-500">Pending</div>
        </div>
        <div className="rounded-lg bg-blue-50 p-2 dark:bg-blue-950">
          <div className="text-xl font-bold text-blue-600 dark:text-blue-400">{stats.retrying}</div>
          <div className="text-xs text-blue-500">Retrying</div>
        </div>
        <div className="rounded-lg bg-red-50 p-2 dark:bg-red-950">
          <div className="text-xl font-bold text-red-600 dark:text-red-400">{stats.dead}</div>
          <div className="text-xs text-red-500">Dead</div>
        </div>
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">
        {stats.total} total deliveries in queue
      </div>
    </div>
  );
}
