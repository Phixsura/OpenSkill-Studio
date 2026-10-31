"use client";

import { useState } from "react";

interface PoolStatus {
  poolId: string;
  name: string;
  totalCapacity: number;
  reserved: number;
  used: number;
  available: number;
  utilizationPct: number;
}

export default function QuotaPoolCard() {
  const [pools] = useState<PoolStatus[]>([
    { poolId: "p1", name: "API Calls", totalCapacity: 10000, reserved: 2000, used: 5500, available: 2500, utilizationPct: 75 },
    { poolId: "p2", name: "Storage MB", totalCapacity: 5000, reserved: 500, used: 1200, available: 3300, utilizationPct: 34 },
  ]);

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">
        Quota Pools
      </h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
        Shared quota pools with reservation
      </p>

      <div className="mt-4 space-y-3">
        {pools.map((p) => (
          <div key={p.poolId} className="rounded-lg border border-zinc-100 p-3 dark:border-zinc-700">
            <div className="flex items-center justify-between">
              <span className="font-medium text-zinc-900 dark:text-zinc-100">{p.name}</span>
              <span className="text-xs text-zinc-500">{p.utilizationPct}% used</span>
            </div>
            <div className="mt-2 h-2 overflow-hidden rounded-full bg-zinc-100 dark:bg-zinc-800">
              <div className="flex h-full">
                <div className="bg-blue-500" style={{ width: `${(p.used / p.totalCapacity) * 100}%` }} />
                <div className="bg-blue-300 dark:bg-blue-700" style={{ width: `${(p.reserved / p.totalCapacity) * 100}%` }} />
              </div>
            </div>
            <div className="mt-1 flex justify-between text-xs text-zinc-400">
              <span>{p.available.toLocaleString()} available</span>
              <span>{p.totalCapacity.toLocaleString()} total</span>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">
        {pools.length} pools active
      </div>
    </div>
  );
}
