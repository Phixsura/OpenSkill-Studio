"use client";

import { useState } from "react";

interface CompStatus { name: string; status: string; }

const STATUS_DOT: Record<string, string> = {
  operational: "bg-green-500",
  degraded_performance: "bg-yellow-500",
  partial_outage: "bg-orange-500",
  major_outage: "bg-red-500",
  maintenance: "bg-blue-500",
};

export default function StatusPageCard() {
  const [overall] = useState("all_systems_operational");
  const [components] = useState<CompStatus[]>([
    { name: "API Gateway", status: "operational" },
    { name: "Authentication", status: "operational" },
    { name: "Database", status: "operational" },
    { name: "Search", status: "degraded_performance" },
    { name: "Webhooks", status: "operational" },
  ]);

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">Status Page</h3>
        <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${overall === "all_systems_operational" ? "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300" : "bg-amber-100 text-amber-700"}`}>
          {overall.replace(/_/g, " ")}
        </span>
      </div>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">Public status page with component health</p>

      <div className="mt-4 space-y-1.5">
        {components.map((c) => (
          <div key={c.name} className="flex items-center justify-between px-1">
            <span className="text-sm text-zinc-700 dark:text-zinc-300">{c.name}</span>
            <span className={`h-2.5 w-2.5 rounded-full ${STATUS_DOT[c.status] ?? "bg-zinc-300"}`} />
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">
        {components.filter((c) => c.status === "operational").length}/{components.length} operational
      </div>
    </div>
  );
}
