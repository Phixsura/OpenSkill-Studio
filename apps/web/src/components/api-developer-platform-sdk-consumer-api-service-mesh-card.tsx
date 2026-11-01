"use client";

import { useState } from "react";

interface MeshNode { id: string; name: string; healthy: boolean; }
interface MeshLink { from: string; to: string; circuitOpen: boolean; }

export default function ServiceMeshCard() {
  const [nodes] = useState<MeshNode[]>([
    { id: "auth", name: "Auth", healthy: true },
    { id: "users", name: "Users", healthy: true },
    { id: "orders", name: "Orders", healthy: true },
    { id: "payments", name: "Payments", healthy: false },
  ]);
  const [links] = useState<MeshLink[]>([
    { from: "users", to: "auth", circuitOpen: false },
    { from: "orders", to: "users", circuitOpen: false },
    { from: "orders", to: "payments", circuitOpen: true },
  ]);

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">Service Mesh</h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">Service-to-service routing with circuit breaker</p>

      <div className="mt-4 flex flex-wrap gap-2">
        {nodes.map((n) => (
          <div key={n.id} className="flex items-center gap-1 rounded-lg border border-zinc-100 px-2 py-1 dark:border-zinc-700">
            <span className={`h-2 w-2 rounded-full ${n.healthy ? "bg-green-500" : "bg-red-500"}`} />
            <span className="text-xs text-zinc-800 dark:text-zinc-200">{n.name}</span>
          </div>
        ))}
      </div>

      <div className="mt-3 space-y-1">
        {links.map((l, i) => (
          <div key={i} className="flex items-center gap-2 text-xs text-zinc-500">
            <span>{l.from}</span>
            <span>→</span>
            <span>{l.to}</span>
            {l.circuitOpen && <span className="text-red-500 font-medium">circuit open</span>}
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">
        {nodes.length} services · {links.filter((l) => l.circuitOpen).length} open circuits
      </div>
    </div>
  );
}
