"use client";

import { useState } from "react";

interface RatePlan {
  planId: string;
  name: string;
  rpm: number;
  rpd: number;
  burst: number;
  priceCents: number;
}

export default function RatePlanManagerCard() {
  const [plans] = useState<RatePlan[]>([
    { planId: "free", name: "Free", rpm: 60, rpd: 1000, burst: 0, priceCents: 0 },
    { planId: "pro", name: "Pro", rpm: 300, rpd: 50000, burst: 50, priceCents: 2999 },
    { planId: "enterprise", name: "Enterprise", rpm: 1000, rpd: 500000, burst: 200, priceCents: 9999 },
  ]);

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">
        Rate Plan Manager
      </h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
        Tiered rate plans with burst allowance
      </p>

      <div className="mt-4 space-y-3">
        {plans.map((p) => (
          <div
            key={p.planId}
            className="flex items-center justify-between rounded-lg border border-zinc-100 p-3 dark:border-zinc-700"
          >
            <div>
              <span className="font-medium text-zinc-900 dark:text-zinc-100">{p.name}</span>
              <div className="mt-1 text-xs text-zinc-500 dark:text-zinc-400">
                {p.rpm} req/min · {p.rpd.toLocaleString()} req/day
                {p.burst > 0 && ` · ${p.burst} burst`}
              </div>
            </div>
            <span className="text-sm font-semibold text-zinc-700 dark:text-zinc-300">
              {p.priceCents === 0 ? "Free" : `$${(p.priceCents / 100).toFixed(2)}/mo`}
            </span>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">
        {plans.length} plans configured
      </div>
    </div>
  );
}
