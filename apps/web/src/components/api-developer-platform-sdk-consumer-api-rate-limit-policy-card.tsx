"use client";

import { useState } from "react";

interface PolicyInfo { endpoint: string; maxReqs: number; windowSec: number; burst: number; }

export default function RateLimitPolicyCard() {
  const [policies] = useState<PolicyInfo[]>([
    { endpoint: "/api/users", maxReqs: 100, windowSec: 60, burst: 20 },
    { endpoint: "/api/search", maxReqs: 30, windowSec: 60, burst: 5 },
    { endpoint: "/api/upload", maxReqs: 10, windowSec: 60, burst: 0 },
  ]);
  const [stats] = useState({ allowed: 45200, denied: 1580, denyRate: 3.4 });

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">Rate Limit Policy</h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">Tiered rate limits with sliding window</p>

      <div className="mt-4 space-y-2">
        {policies.map((p) => (
          <div key={p.endpoint} className="flex items-center justify-between rounded-lg border border-zinc-100 px-3 py-2 dark:border-zinc-700">
            <span className="font-mono text-sm text-zinc-800 dark:text-zinc-200">{p.endpoint}</span>
            <span className="text-xs text-zinc-500">
              {p.maxReqs}/min{p.burst > 0 ? ` +${p.burst} burst` : ""}
            </span>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">
        {stats.denyRate}% deny rate · {stats.denied.toLocaleString()} denied
      </div>
    </div>
  );
}
