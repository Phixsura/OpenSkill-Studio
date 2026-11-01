"use client";

import { useState } from "react";

interface SlaInfo {
  slaId: string;
  metric: string;
  target: number;
  compliancePct: number;
  status: "compliant" | "at_risk" | "breached";
}

const STATUS_STYLE: Record<string, string> = {
  compliant: "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300",
  at_risk: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300",
  breached: "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300",
};

export default function SlaTrackerCard() {
  const [slas] = useState<SlaInfo[]>([
    { slaId: "s1", metric: "Uptime %", target: 99.9, compliancePct: 100, status: "compliant" },
    { slaId: "s2", metric: "P99 Latency", target: 200, compliancePct: 96.5, status: "at_risk" },
    { slaId: "s3", metric: "Error Rate", target: 1.0, compliancePct: 88.0, status: "breached" },
  ]);

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">
        SLA Tracker
      </h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
        SLA compliance monitoring with breach detection
      </p>

      <div className="mt-4 space-y-2">
        {slas.map((s) => (
          <div
            key={s.slaId}
            className="flex items-center justify-between rounded-lg border border-zinc-100 px-3 py-2 dark:border-zinc-700"
          >
            <div>
              <span className="text-sm font-medium text-zinc-900 dark:text-zinc-100">{s.metric}</span>
              <span className="ml-2 text-xs text-zinc-400">target: {s.target}</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-sm font-semibold text-zinc-700 dark:text-zinc-300">
                {s.compliancePct}%
              </span>
              <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${STATUS_STYLE[s.status]}`}>
                {s.status}
              </span>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">
        {slas.filter((s) => s.status === "compliant").length}/{slas.length} SLAs met
      </div>
    </div>
  );
}
