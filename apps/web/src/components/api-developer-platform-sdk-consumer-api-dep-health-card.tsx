"use client";

import { useState } from "react";

interface DepInfo { name: string; type: string; healthy: boolean; dependents: number; latencyMs: number; }

export default function DepHealthCard() {
  const [deps] = useState<DepInfo[]>([
    { name: "PostgreSQL", type: "database", healthy: true, dependents: 12, latencyMs: 5 },
    { name: "Redis", type: "cache", healthy: true, dependents: 8, latencyMs: 1 },
    { name: "RabbitMQ", type: "queue", healthy: false, dependents: 4, latencyMs: 250 },
    { name: "Auth API", type: "api", healthy: true, dependents: 15, latencyMs: 45 },
  ]);

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">Dependency Health</h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">Dependency health with cascade impact</p>

      <div className="mt-4 space-y-2">
        {deps.map((d) => (
          <div key={d.name} className="flex items-center justify-between rounded-lg border border-zinc-100 px-3 py-2 dark:border-zinc-700">
            <div className="flex items-center gap-2">
              <span className={`h-2.5 w-2.5 rounded-full ${d.healthy ? "bg-green-500" : "bg-red-500"}`} />
              <span className="text-sm font-medium text-zinc-900 dark:text-zinc-100">{d.name}</span>
              <span className="text-xs text-zinc-400">{d.type}</span>
            </div>
            <div className="text-xs text-zinc-500">
              {d.latencyMs}ms · {d.dependents} deps
            </div>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">
        {deps.filter((d) => d.healthy).length}/{deps.length} healthy
      </div>
    </div>
  );
}
