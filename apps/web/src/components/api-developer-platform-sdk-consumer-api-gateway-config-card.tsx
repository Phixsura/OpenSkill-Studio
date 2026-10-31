"use client";

import { useState } from "react";

interface RouteInfo { routeId: string; path: string; target: string; methods: string[]; enabled: boolean; }

export default function GatewayConfigCard() {
  const [routes] = useState<RouteInfo[]>([
    { routeId: "r1", path: "/api/users/*", target: "users-svc:8080", methods: ["GET", "POST"], enabled: true },
    { routeId: "r2", path: "/api/orders/*", target: "orders-svc:8080", methods: ["GET", "POST", "PUT"], enabled: true },
    { routeId: "r3", path: "/api/legacy/*", target: "legacy-svc:8080", methods: ["GET"], enabled: false },
  ]);

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">Gateway Config</h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">Gateway routing with middleware chain</p>

      <div className="mt-4 space-y-2">
        {routes.map((r) => (
          <div key={r.routeId} className={`flex items-center justify-between rounded-lg border border-zinc-100 px-3 py-2 dark:border-zinc-700 ${!r.enabled ? "opacity-50" : ""}`}>
            <div>
              <span className="font-mono text-sm text-zinc-800 dark:text-zinc-200">{r.path}</span>
              <span className="ml-2 text-xs text-zinc-400">→ {r.target}</span>
            </div>
            <div className="flex gap-1">
              {r.methods.map((m) => (
                <span key={m} className="rounded bg-zinc-100 px-1 py-0.5 text-xs text-zinc-600 dark:bg-zinc-800 dark:text-zinc-400">{m}</span>
              ))}
            </div>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">
        {routes.filter((r) => r.enabled).length}/{routes.length} routes active
      </div>
    </div>
  );
}
