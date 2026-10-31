"use client";

import { useState } from "react";

interface SvcInfo { name: string; lifecycle: string; deps: number; instantiated: boolean; }

const LC_COLOR: Record<string, string> = {
  singleton: "bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300",
  transient: "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300",
  scoped: "bg-purple-100 text-purple-700 dark:bg-purple-900 dark:text-purple-300",
};

export default function DiContainerCard() {
  const [services] = useState<SvcInfo[]>([
    { name: "DatabasePool", lifecycle: "singleton", deps: 0, instantiated: true },
    { name: "UserRepository", lifecycle: "singleton", deps: 1, instantiated: true },
    { name: "OrderService", lifecycle: "transient", deps: 2, instantiated: false },
    { name: "EmailSender", lifecycle: "singleton", deps: 1, instantiated: true },
  ]);

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">DI Container</h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">Service dependency container with lifecycle</p>

      <div className="mt-4 space-y-2">
        {services.map((s) => (
          <div key={s.name} className="flex items-center justify-between rounded-lg border border-zinc-100 px-3 py-2 dark:border-zinc-700">
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium text-zinc-900 dark:text-zinc-100">{s.name}</span>
              <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${LC_COLOR[s.lifecycle] ?? ""}`}>{s.lifecycle}</span>
            </div>
            <span className="text-xs text-zinc-400">{s.deps} deps</span>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">
        {services.length} services · {services.filter((s) => s.instantiated).length} instantiated
      </div>
    </div>
  );
}
