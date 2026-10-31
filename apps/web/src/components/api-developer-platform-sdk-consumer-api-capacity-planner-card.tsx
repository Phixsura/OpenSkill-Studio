"use client";

import { useState } from "react";

interface ResourceInfo { name: string; utilization: number; status: string; headroom: string; }

const STATUS_COLOR: Record<string, string> = {
  healthy: "bg-green-500",
  warning: "bg-amber-500",
  critical: "bg-red-500",
};

export default function CapacityPlannerCard() {
  const [resources] = useState<ResourceInfo[]>([
    { name: "CPU", utilization: 62, status: "healthy", headroom: "38%" },
    { name: "Memory", utilization: 78, status: "warning", headroom: "22%" },
    { name: "Storage", utilization: 94, status: "critical", headroom: "6%" },
    { name: "Connections", utilization: 45, status: "healthy", headroom: "55%" },
  ]);

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">Capacity Planner</h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">Capacity planning with growth projection</p>

      <div className="mt-4 space-y-3">
        {resources.map((r) => (
          <div key={r.name}>
            <div className="flex items-center justify-between text-sm">
              <div className="flex items-center gap-2">
                <span className={`h-2 w-2 rounded-full ${STATUS_COLOR[r.status]}`} />
                <span className="text-zinc-800 dark:text-zinc-200">{r.name}</span>
              </div>
              <span className="text-xs text-zinc-400">{r.utilization}% · {r.headroom} free</span>
            </div>
            <div className="mt-1 h-1.5 overflow-hidden rounded-full bg-zinc-100 dark:bg-zinc-800">
              <div className={`h-full rounded-full ${STATUS_COLOR[r.status]}`} style={{ width: `${r.utilization}%` }} />
            </div>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">
        {resources.filter((r) => r.status === "critical").length} critical · {resources.filter((r) => r.status === "warning").length} warning
      </div>
    </div>
  );
}
