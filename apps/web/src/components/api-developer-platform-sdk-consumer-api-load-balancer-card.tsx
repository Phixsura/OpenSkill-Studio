"use client";

import { useState } from "react";

interface Target {
  targetId: string;
  url: string;
  weight: number;
  healthy: boolean;
  connections: number;
}

export default function LoadBalancerCard() {
  const [targets] = useState<Target[]>([
    { targetId: "t1", url: "us-east-1:8080", weight: 3, healthy: true, connections: 42 },
    { targetId: "t2", url: "us-west-2:8080", weight: 2, healthy: true, connections: 28 },
    { targetId: "t3", url: "eu-west-1:8080", weight: 1, healthy: false, connections: 0 },
  ]);

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">
        Load Balancer
      </h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
        Weighted round-robin with health-aware routing
      </p>

      <div className="mt-4 space-y-2">
        {targets.map((t) => (
          <div key={t.targetId} className="flex items-center justify-between rounded-lg border border-zinc-100 px-3 py-2 dark:border-zinc-700">
            <div className="flex items-center gap-2">
              <span className={`h-2.5 w-2.5 rounded-full ${t.healthy ? "bg-green-500" : "bg-red-500"}`} />
              <span className="font-mono text-sm text-zinc-800 dark:text-zinc-200">{t.url}</span>
            </div>
            <div className="flex items-center gap-3 text-xs text-zinc-500">
              <span>w:{t.weight}</span>
              <span>{t.connections} conn</span>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">
        {targets.filter((t) => t.healthy).length}/{targets.length} targets healthy
      </div>
    </div>
  );
}
