"use client";

import { useState } from "react";

export default function DeadLetterCard() {
  const [stats] = useState({ total: 45, dead: 32, replayed: 10, discarded: 3 });
  const [recent] = useState([
    { letterId: "dl-1", eventType: "order.created", error: "timeout", attempts: 3 },
    { letterId: "dl-2", eventType: "payment.failed", error: "connection refused", attempts: 5 },
  ]);

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">Dead Letter Inspector</h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">Inspect and replay dead letter events</p>

      <div className="mt-4 grid grid-cols-3 gap-2 text-center">
        <div className="rounded-lg bg-red-50 p-2 dark:bg-red-950">
          <div className="text-lg font-bold text-red-600 dark:text-red-400">{stats.dead}</div>
          <div className="text-xs text-red-500">Dead</div>
        </div>
        <div className="rounded-lg bg-green-50 p-2 dark:bg-green-950">
          <div className="text-lg font-bold text-green-600 dark:text-green-400">{stats.replayed}</div>
          <div className="text-xs text-green-500">Replayed</div>
        </div>
        <div className="rounded-lg bg-zinc-50 p-2 dark:bg-zinc-800">
          <div className="text-lg font-bold text-zinc-600 dark:text-zinc-400">{stats.discarded}</div>
          <div className="text-xs text-zinc-500">Discarded</div>
        </div>
      </div>

      <div className="mt-3 space-y-1">
        {recent.map((r) => (
          <div key={r.letterId} className="flex items-center justify-between text-xs">
            <span className="text-zinc-700 dark:text-zinc-300">{r.eventType} — {r.error}</span>
            <span className="text-zinc-400">{r.attempts} attempts</span>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">{stats.total} total letters</div>
    </div>
  );
}
