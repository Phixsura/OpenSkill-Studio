"use client";

import { useState } from "react";

interface PoolInfo { name: string; active: number; idle: number; maxSize: number; utilization: number; }

export default function ConnPoolCard() {
  const [pools] = useState<PoolInfo[]>([
    { name: "DB Primary", active: 8, idle: 12, maxSize: 20, utilization: 40 },
    { name: "Redis Cache", active: 3, idle: 7, maxSize: 10, utilization: 30 },
    { name: "External API", active: 4, idle: 1, maxSize: 5, utilization: 80 },
  ]);

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">Connection Pool</h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">Connection pool management with health</p>

      <div className="mt-4 space-y-3">
        {pools.map((p) => (
          <div key={p.name} className="rounded-lg border border-zinc-100 px-3 py-2 dark:border-zinc-700">
            <div className="flex items-center justify-between text-sm">
              <span className="font-medium text-zinc-900 dark:text-zinc-100">{p.name}</span>
              <span className="text-xs text-zinc-400">{p.active + p.idle}/{p.maxSize}</span>
            </div>
            <div className="mt-1 h-1.5 overflow-hidden rounded-full bg-zinc-100 dark:bg-zinc-800">
              <div className="h-full rounded-full bg-blue-500" style={{ width: `${p.utilization}%` }} />
            </div>
            <div className="mt-0.5 flex justify-between text-xs text-zinc-400">
              <span>{p.active} active</span>
              <span>{p.idle} idle</span>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">{pools.length} pools</div>
    </div>
  );
}
