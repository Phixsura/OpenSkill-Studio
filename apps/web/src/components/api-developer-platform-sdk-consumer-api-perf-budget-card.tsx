"use client";

import { useState } from "react";

interface BudgetCheck {
  endpointId: string;
  status: string;
  p95Ms: number;
  p99Ms: number;
  violations: number;
}

export default function PerfBudgetCard() {
  const [checks] = useState<BudgetCheck[]>([
    { endpointId: "ep-auth", status: "within_budget", p95Ms: 45, p99Ms: 120, violations: 0 },
    { endpointId: "ep-search", status: "over_budget", p95Ms: 380, p99Ms: 920, violations: 2 },
    { endpointId: "ep-upload", status: "within_budget", p95Ms: 150, p99Ms: 400, violations: 0 },
  ]);

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">Performance Budget</h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">Performance budget tracking with alerting</p>

      <div className="mt-4 space-y-2">
        {checks.map((c) => (
          <div key={c.endpointId} className="flex items-center justify-between rounded-lg border border-zinc-100 px-3 py-2 dark:border-zinc-700">
            <div className="flex items-center gap-2">
              <span className={`h-2.5 w-2.5 rounded-full ${c.status === "within_budget" ? "bg-green-500" : "bg-red-500"}`} />
              <span className="font-mono text-sm text-zinc-800 dark:text-zinc-200">{c.endpointId}</span>
            </div>
            <div className="text-xs text-zinc-500">
              P95: {c.p95Ms}ms · P99: {c.p99Ms}ms
              {c.violations > 0 && <span className="ml-1 text-red-500">({c.violations} violations)</span>}
            </div>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">
        {checks.filter((c) => c.status === "within_budget").length}/{checks.length} within budget
      </div>
    </div>
  );
}
