"use client";

import { useState } from "react";

interface CircuitInfo { id: string; endpoint: string; state: string; trips: number; }

const STATE_COLOR: Record<string, string> = {
  closed: "bg-green-500",
  open: "bg-red-500",
  half_open: "bg-amber-500",
};

export default function CircuitDashboardCard() {
  const [circuits] = useState<CircuitInfo[]>([
    { id: "c1", endpoint: "ep-auth", state: "closed", trips: 0 },
    { id: "c2", endpoint: "ep-search", state: "half_open", trips: 2 },
    { id: "c3", endpoint: "ep-payments", state: "open", trips: 5 },
    { id: "c4", endpoint: "ep-users", state: "closed", trips: 1 },
  ]);

  const overview = {
    closed: circuits.filter((c) => c.state === "closed").length,
    open: circuits.filter((c) => c.state === "open").length,
    halfOpen: circuits.filter((c) => c.state === "half_open").length,
  };

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">Circuit Breakers</h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">Circuit breaker state overview</p>

      <div className="mt-4 space-y-2">
        {circuits.map((c) => (
          <div key={c.id} className="flex items-center justify-between rounded-lg border border-zinc-100 px-3 py-2 dark:border-zinc-700">
            <div className="flex items-center gap-2">
              <span className={`h-2.5 w-2.5 rounded-full ${STATE_COLOR[c.state]}`} />
              <span className="font-mono text-sm text-zinc-800 dark:text-zinc-200">{c.endpoint}</span>
            </div>
            <div className="text-xs text-zinc-500">
              {c.state} · {c.trips} trips
            </div>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">
        {overview.closed} closed · {overview.open} open · {overview.halfOpen} half-open
      </div>
    </div>
  );
}
