"use client";

import { useState } from "react";

interface PlanInfo {
  planId: string;
  oldEndpoint: string;
  newEndpoint: string;
  phase: string;
  migrationPct: number;
  sunsetDate: string;
}

const PHASE_COLOR: Record<string, string> = {
  announced: "bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300",
  warning: "bg-amber-100 text-amber-700 dark:bg-amber-900 dark:text-amber-300",
  migration: "bg-orange-100 text-orange-700 dark:bg-orange-900 dark:text-orange-300",
  sunset: "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300",
};

export default function DeprecationPlannerCard() {
  const [plans] = useState<PlanInfo[]>([
    { planId: "dp1", oldEndpoint: "/v1/users", newEndpoint: "/v2/users", phase: "migration", migrationPct: 75, sunsetDate: "2024-06-01" },
    { planId: "dp2", oldEndpoint: "/v1/orders", newEndpoint: "/v2/orders", phase: "announced", migrationPct: 0, sunsetDate: "2024-09-01" },
  ]);

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">Deprecation Planner</h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">Deprecation timeline with migration tracking</p>

      <div className="mt-4 space-y-3">
        {plans.map((p) => (
          <div key={p.planId} className="rounded-lg border border-zinc-100 p-3 dark:border-zinc-700">
            <div className="flex items-center justify-between">
              <div className="font-mono text-sm text-zinc-800 dark:text-zinc-200">
                {p.oldEndpoint} → {p.newEndpoint}
              </div>
              <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${PHASE_COLOR[p.phase] ?? ""}`}>{p.phase}</span>
            </div>
            <div className="mt-1 h-1.5 overflow-hidden rounded-full bg-zinc-100 dark:bg-zinc-800">
              <div className="h-full rounded-full bg-green-500" style={{ width: `${p.migrationPct}%` }} />
            </div>
            <div className="mt-0.5 flex justify-between text-xs text-zinc-400">
              <span>{p.migrationPct}% migrated</span>
              <span>sunset: {p.sunsetDate}</span>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">
        {plans.length} deprecation plans
      </div>
    </div>
  );
}
