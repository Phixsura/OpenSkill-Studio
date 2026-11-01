"use client";

import { useState } from "react";

export default function WebhookDedupCard() {
  const [stats] = useState({
    totalChecked: 45200, totalDeduped: 3890, dedupRate: 8.6,
    activeFingerprints: 12500, ttlHours: 1,
  });

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">Webhook Dedup</h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">Content-hash based deduplication</p>

      <div className="mt-4 grid grid-cols-3 gap-3 text-center">
        <div className="rounded-lg bg-zinc-50 p-2 dark:bg-zinc-800">
          <div className="text-lg font-bold text-zinc-900 dark:text-zinc-100">{stats.dedupRate}%</div>
          <div className="text-xs text-zinc-500">Dedup Rate</div>
        </div>
        <div className="rounded-lg bg-zinc-50 p-2 dark:bg-zinc-800">
          <div className="text-lg font-bold text-zinc-900 dark:text-zinc-100">{stats.totalDeduped.toLocaleString()}</div>
          <div className="text-xs text-zinc-500">Deduped</div>
        </div>
        <div className="rounded-lg bg-zinc-50 p-2 dark:bg-zinc-800">
          <div className="text-lg font-bold text-zinc-900 dark:text-zinc-100">{stats.activeFingerprints.toLocaleString()}</div>
          <div className="text-xs text-zinc-500">Fingerprints</div>
        </div>
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">
        {stats.totalChecked.toLocaleString()} checked · {stats.ttlHours}h TTL
      </div>
    </div>
  );
}
