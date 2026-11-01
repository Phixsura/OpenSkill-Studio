"use client";

import { useState } from "react";

interface EndpointHealth {
  endpointId: string;
  status: "healthy" | "degraded" | "unhealthy";
  circuit: "closed" | "open" | "half_open";
  uptimePct: number;
  avgLatencyMs: number;
}

const STATUS_COLOR: Record<string, string> = {
  healthy: "bg-green-500",
  degraded: "bg-yellow-500",
  unhealthy: "bg-red-500",
};

export default function HealthCheckerCard() {
  const [endpoints] = useState<EndpointHealth[]>([
    { endpointId: "ep-auth", status: "healthy", circuit: "closed", uptimePct: 99.9, avgLatencyMs: 32 },
    { endpointId: "ep-search", status: "degraded", circuit: "closed", uptimePct: 95.2, avgLatencyMs: 180 },
    { endpointId: "ep-legacy", status: "unhealthy", circuit: "open", uptimePct: 72.0, avgLatencyMs: 450 },
  ]);

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">
        Health Checker
      </h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
        Endpoint health probes with circuit breaker
      </p>

      <div className="mt-4 space-y-2">
        {endpoints.map((ep) => (
          <div
            key={ep.endpointId}
            className="flex items-center justify-between rounded-lg border border-zinc-100 px-3 py-2 dark:border-zinc-700"
          >
            <div className="flex items-center gap-2">
              <span className={`h-2.5 w-2.5 rounded-full ${STATUS_COLOR[ep.status]}`} />
              <span className="font-mono text-sm text-zinc-800 dark:text-zinc-200">
                {ep.endpointId}
              </span>
            </div>
            <div className="flex items-center gap-3 text-xs text-zinc-500">
              <span>{ep.uptimePct}%</span>
              <span>{ep.avgLatencyMs}ms</span>
              <span className="rounded bg-zinc-100 px-1.5 py-0.5 dark:bg-zinc-800">
                {ep.circuit}
              </span>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">
        {endpoints.filter((e) => e.status === "healthy").length}/{endpoints.length} healthy
      </div>
    </div>
  );
}
