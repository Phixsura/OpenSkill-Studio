"use client";

import { useState } from "react";

interface Route {
  routeId: string;
  method: string;
  pathPattern: string;
  extensionId: string;
  handler: string;
  middlewares: string[];
  authRequired: boolean;
  rateLimit: number;
  priority: number;
}

const methodColors: Record<string, string> = {
  GET: "bg-green-500", POST: "bg-blue-500", PUT: "bg-yellow-500",
  DELETE: "bg-red-500", PATCH: "bg-purple-500",
};

export function GatewayRouterPanel({
  routes,
  onRemove,
  onTest,
}: {
  routes: Route[];
  onRemove?: (routeId: string) => void;
  onTest?: (method: string, path: string) => void;
}) {
  const [methodFilter, setMethodFilter] = useState<string>("all");
  const methods = [...new Set(routes.map((r) => r.method))].sort();
  const filtered = methodFilter === "all" ? routes : routes.filter((r) => r.method === methodFilter);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">🛣️ API Routes</h2>
        <span className="text-sm text-gray-500">{routes.length} routes</span>
      </div>

      <div className="flex gap-1">
        <button onClick={() => setMethodFilter("all")}
          className={`text-xs px-2.5 py-1 rounded-full ${methodFilter === "all" ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
          All
        </button>
        {methods.map((m) => (
          <button key={m} onClick={() => setMethodFilter(m)}
            className={`text-xs px-2.5 py-1 rounded-full ${methodFilter === m ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
            {m}
          </button>
        ))}
      </div>

      <div className="space-y-1">
        {filtered.map((route) => (
          <div key={route.routeId} className="rounded-lg border dark:border-gray-700 p-3">
            <div className="flex items-center justify-between mb-1">
              <div className="flex items-center gap-2">
                <span className={`text-xs text-white px-2 py-0.5 rounded font-bold ${methodColors[route.method] || "bg-gray-500"}`}>
                  {route.method}
                </span>
                <code className="text-sm">{route.pathPattern}</code>
                {route.authRequired && <span className="text-xs text-gray-400">🔒</span>}
                {route.rateLimit > 0 && <span className="text-xs text-gray-400">⏱{route.rateLimit}/m</span>}
              </div>
              <div className="flex gap-1">
                <button onClick={() => onTest?.(route.method, route.pathPattern)}
                  className="text-xs bg-blue-600 text-white px-2 py-0.5 rounded">Test</button>
                <button onClick={() => onRemove?.(route.routeId)}
                  className="text-xs text-red-500">✕</button>
              </div>
            </div>
            <div className="flex gap-2 text-xs text-gray-500">
              <span>→ {route.extensionId}::{route.handler}</span>
              {route.middlewares.length > 0 && (
                <span className="text-gray-400">[{route.middlewares.join(" → ")}]</span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
