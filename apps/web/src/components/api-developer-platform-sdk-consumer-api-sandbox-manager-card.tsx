"use client";

import { useState } from "react";

interface SandboxInfo {
  name: string;
  status: "active" | "paused" | "expired";
  usagePct: number;
  requestCount: number;
}

const STATUS_COLOR: Record<string, string> = {
  active: "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300",
  paused: "bg-amber-100 text-amber-700 dark:bg-amber-900 dark:text-amber-300",
  expired: "bg-zinc-100 text-zinc-500 dark:bg-zinc-800 dark:text-zinc-400",
};

export default function SandboxManagerCard() {
  const [sandboxes] = useState<SandboxInfo[]>([
    { name: "Integration Test", status: "active", usagePct: 45, requestCount: 4500 },
    { name: "Load Test", status: "paused", usagePct: 90, requestCount: 9000 },
    { name: "QA Environment", status: "active", usagePct: 12, requestCount: 1200 },
  ]);

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">
        Sandbox Manager
      </h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
        Isolated sandbox environments for testing
      </p>

      <div className="mt-4 space-y-2">
        {sandboxes.map((s) => (
          <div key={s.name} className="rounded-lg border border-zinc-100 px-3 py-2 dark:border-zinc-700">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-zinc-900 dark:text-zinc-100">{s.name}</span>
              <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${STATUS_COLOR[s.status]}`}>{s.status}</span>
            </div>
            <div className="mt-1 h-1.5 overflow-hidden rounded-full bg-zinc-100 dark:bg-zinc-800">
              <div className="h-full rounded-full bg-blue-500" style={{ width: `${s.usagePct}%` }} />
            </div>
            <div className="mt-0.5 text-xs text-zinc-400">{s.requestCount.toLocaleString()} requests · {s.usagePct}%</div>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">
        {sandboxes.filter((s) => s.status === "active").length} active sandboxes
      </div>
    </div>
  );
}
