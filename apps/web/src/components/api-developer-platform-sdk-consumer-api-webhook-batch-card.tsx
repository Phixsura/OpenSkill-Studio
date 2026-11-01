"use client";

import { useState } from "react";

export default function WebhookBatchCard() {
  const [stats] = useState({ totalBatches: 245, sent: 230, failed: 5, pending: 10, eventsDelivered: 8500 });
  const [buffers] = useState({ "orders-hook": 12, "analytics-hook": 5 });

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">Webhook Batch Sender</h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">Batch webhook delivery with aggregation</p>

      <div className="mt-4 grid grid-cols-3 gap-2 text-center">
        <div className="rounded-lg bg-green-50 p-2 dark:bg-green-950">
          <div className="text-lg font-bold text-green-600 dark:text-green-400">{stats.sent}</div>
          <div className="text-xs text-green-500">Sent</div>
        </div>
        <div className="rounded-lg bg-amber-50 p-2 dark:bg-amber-950">
          <div className="text-lg font-bold text-amber-600 dark:text-amber-400">{stats.pending}</div>
          <div className="text-xs text-amber-500">Pending</div>
        </div>
        <div className="rounded-lg bg-red-50 p-2 dark:bg-red-950">
          <div className="text-lg font-bold text-red-600 dark:text-red-400">{stats.failed}</div>
          <div className="text-xs text-red-500">Failed</div>
        </div>
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">
        {stats.eventsDelivered.toLocaleString()} events · {Object.values(buffers).reduce((s, v) => s + v, 0)} buffered
      </div>
    </div>
  );
}
