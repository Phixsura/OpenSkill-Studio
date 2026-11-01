"use client";

import { useState } from "react";

interface ThrottleInfo { consumerId: string; baseRate: number; effectiveRate: number; backpressure: boolean; throttled: number; }

export default function RequestThrottleCard() {
  const [consumers] = useState<ThrottleInfo[]>([
    { consumerId: "c-acme", baseRate: 100, effectiveRate: 100, backpressure: false, throttled: 0 },
    { consumerId: "c-beta", baseRate: 50, effectiveRate: 40, backpressure: true, throttled: 25 },
    { consumerId: "c-gamma", baseRate: 200, effectiveRate: 200, backpressure: false, throttled: 3 },
  ]);

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">Request Throttle</h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">Adaptive throttling with backpressure</p>

      <div className="mt-4 space-y-2">
        {consumers.map((c) => (
          <div key={c.consumerId} className="flex items-center justify-between rounded-lg border border-zinc-100 px-3 py-2 dark:border-zinc-700">
            <div className="flex items-center gap-2">
              <span className="font-mono text-sm text-zinc-800 dark:text-zinc-200">{c.consumerId}</span>
              {c.backpressure && <span className="rounded bg-amber-100 px-1.5 py-0.5 text-xs text-amber-700 dark:bg-amber-900 dark:text-amber-300">backpressure</span>}
            </div>
            <span className="text-xs text-zinc-500">{c.effectiveRate}/{c.baseRate} rate · {c.throttled} throttled</span>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">
        {consumers.length} consumers · {consumers.filter((c) => c.backpressure).length} under backpressure
      </div>
    </div>
  );
}
