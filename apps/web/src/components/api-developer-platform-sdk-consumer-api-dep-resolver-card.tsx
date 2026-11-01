"use client";

import { useState } from "react";

interface DepNode {
  id: string;
  dependsOn: string[];
}

export default function DependencyResolverCard() {
  const [nodes] = useState<DepNode[]>([
    { id: "auth-service", dependsOn: [] },
    { id: "user-service", dependsOn: ["auth-service"] },
    { id: "order-service", dependsOn: ["user-service", "auth-service"] },
    { id: "notification-service", dependsOn: ["order-service"] },
  ]);

  const roots = nodes.filter((n) => n.dependsOn.length === 0);

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">
        Dependency Resolver
      </h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
        Topological sort with cycle detection
      </p>

      <div className="mt-4 space-y-2">
        {nodes.map((n, i) => (
          <div
            key={n.id}
            className="flex items-center gap-2 rounded-lg border border-zinc-100 px-3 py-2 dark:border-zinc-700"
          >
            <span className="flex h-6 w-6 items-center justify-center rounded-full bg-blue-100 text-xs font-bold text-blue-700 dark:bg-blue-900 dark:text-blue-300">
              {i + 1}
            </span>
            <span className="font-mono text-sm text-zinc-800 dark:text-zinc-200">
              {n.id}
            </span>
            {n.dependsOn.length > 0 && (
              <span className="ml-auto text-xs text-zinc-400">
                depends on: {n.dependsOn.join(", ")}
              </span>
            )}
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">
        {roots.length} root node{roots.length !== 1 ? "s" : ""} · {nodes.length} total
      </div>
    </div>
  );
}
