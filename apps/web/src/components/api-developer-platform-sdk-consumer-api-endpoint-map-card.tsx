"use client";

import { useState } from "react";

interface NodeInfo { id: string; label: string; type: string; }
interface EdgeInfo { from: string; to: string; type: string; }

const TYPE_ICON: Record<string, string> = { endpoint: "🔗", service: "⚙️", database: "🗄️", cache: "⚡", queue: "📬" };

export default function EndpointMapCard() {
  const [nodes] = useState<NodeInfo[]>([
    { id: "ep-users", label: "Users API", type: "endpoint" },
    { id: "svc-auth", label: "Auth Service", type: "service" },
    { id: "db-pg", label: "PostgreSQL", type: "database" },
    { id: "cache-redis", label: "Redis", type: "cache" },
  ]);
  const [edges] = useState<EdgeInfo[]>([
    { from: "ep-users", to: "svc-auth", type: "calls" },
    { from: "ep-users", to: "db-pg", type: "reads" },
    { from: "ep-users", to: "cache-redis", type: "reads" },
  ]);

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">Endpoint Map</h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">Visual endpoint mapping with relationships</p>

      <div className="mt-4 flex flex-wrap gap-2">
        {nodes.map((n) => (
          <div key={n.id} className="rounded-lg border border-zinc-100 px-2 py-1 text-xs dark:border-zinc-700">
            <span>{TYPE_ICON[n.type] ?? "📦"} {n.label}</span>
          </div>
        ))}
      </div>

      <div className="mt-3 space-y-1">
        {edges.map((e, i) => (
          <div key={i} className="flex items-center gap-1 text-xs text-zinc-500">
            <span>{e.from}</span><span>→</span><span>{e.to}</span>
            <span className="text-zinc-400">({e.type})</span>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">
        {nodes.length} nodes · {edges.length} edges
      </div>
    </div>
  );
}
