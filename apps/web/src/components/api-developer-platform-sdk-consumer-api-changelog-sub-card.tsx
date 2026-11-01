"use client";

import { useState } from "react";

export default function ChangelogSubCard() {
  const [stats] = useState({ subscribers: 42, active: 38, notifications: 156, totalSent: 4520 });
  const [recent] = useState([
    { version: "2.1.0", type: "added", summary: "Batch API", sent: 38 },
    { version: "2.0.0", type: "removed", summary: "Legacy endpoints removed", sent: 42 },
  ]);

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">Changelog Subscribers</h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">Changelog subscription with notifications</p>

      <div className="mt-4 grid grid-cols-2 gap-3 text-center">
        <div className="rounded-lg bg-zinc-50 p-2 dark:bg-zinc-800">
          <div className="text-lg font-bold text-zinc-900 dark:text-zinc-100">{stats.active}</div>
          <div className="text-xs text-zinc-500">Active Subscribers</div>
        </div>
        <div className="rounded-lg bg-zinc-50 p-2 dark:bg-zinc-800">
          <div className="text-lg font-bold text-zinc-900 dark:text-zinc-100">{stats.totalSent.toLocaleString()}</div>
          <div className="text-xs text-zinc-500">Emails Sent</div>
        </div>
      </div>

      <div className="mt-3 space-y-1">
        {recent.map((n, i) => (
          <div key={i} className="flex items-center justify-between text-xs">
            <span className="text-zinc-700 dark:text-zinc-300">v{n.version} — {n.summary}</span>
            <span className="text-zinc-400">{n.sent} sent</span>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">
        {stats.notifications} notifications sent
      </div>
    </div>
  );
}
