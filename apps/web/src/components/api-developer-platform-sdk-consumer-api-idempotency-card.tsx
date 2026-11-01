"use client";

import { useState } from "react";

export default function IdempotencyCard() {
  const [stats] = useState({
    totalRecords: 8420,
    maxRecords: 100000,
    usagePct: 8.4,
    defaultTtlHrs: 24,
  });

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">Idempotency Manager</h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">Idempotent request handling with key tracking</p>

      <div className="mt-4 grid grid-cols-2 gap-3 text-center">
        <div className="rounded-lg bg-zinc-50 p-3 dark:bg-zinc-800">
          <div className="text-xl font-bold text-zinc-900 dark:text-zinc-100">{stats.totalRecords.toLocaleString()}</div>
          <div className="text-xs text-zinc-500">Active Keys</div>
        </div>
        <div className="rounded-lg bg-zinc-50 p-3 dark:bg-zinc-800">
          <div className="text-xl font-bold text-zinc-900 dark:text-zinc-100">{stats.usagePct}%</div>
          <div className="text-xs text-zinc-500">Capacity Used</div>
        </div>
      </div>

      <div className="mt-3 h-2 overflow-hidden rounded-full bg-zinc-100 dark:bg-zinc-800">
        <div className="h-full rounded-full bg-blue-500" style={{ width: `${stats.usagePct}%` }} />
      </div>

      <div className="mt-2 text-xs text-zinc-400 dark:text-zinc-500">
        TTL: {stats.defaultTtlHrs}h · Max: {stats.maxRecords.toLocaleString()} keys
      </div>
    </div>
  );
}
