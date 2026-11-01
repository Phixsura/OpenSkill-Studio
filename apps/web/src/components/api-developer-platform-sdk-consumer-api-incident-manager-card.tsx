"use client";

import { useState } from "react";

interface IncidentInfo {
  id: string;
  title: string;
  severity: "critical" | "high" | "medium" | "low";
  status: string;
}

const SEV_COLOR: Record<string, string> = {
  critical: "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300",
  high: "bg-orange-100 text-orange-700 dark:bg-orange-900 dark:text-orange-300",
  medium: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300",
  low: "bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300",
};

export default function IncidentManagerCard() {
  const [incidents] = useState<IncidentInfo[]>([
    { id: "inc-1", title: "Payment API Timeout", severity: "critical", status: "investigating" },
    { id: "inc-2", title: "Elevated Error Rate", severity: "high", status: "monitoring" },
    { id: "inc-3", title: "Slow Search Queries", severity: "medium", status: "resolved" },
  ]);

  const active = incidents.filter((i) => i.status !== "resolved").length;

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">
        Incident Manager
      </h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
        Incident lifecycle with severity tracking
      </p>

      <div className="mt-4 space-y-2">
        {incidents.map((i) => (
          <div key={i.id} className="flex items-center justify-between rounded-lg border border-zinc-100 px-3 py-2 dark:border-zinc-700">
            <div className="flex items-center gap-2">
              <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${SEV_COLOR[i.severity]}`}>
                {i.severity}
              </span>
              <span className="text-sm text-zinc-800 dark:text-zinc-200">{i.title}</span>
            </div>
            <span className="text-xs text-zinc-500">{i.status}</span>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">
        {active} active incident{active !== 1 ? "s" : ""}
      </div>
    </div>
  );
}
