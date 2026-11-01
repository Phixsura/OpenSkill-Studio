"use client";

import { useState } from "react";

export default function MaintenanceModeCard() {
  const [status] = useState({
    enabled: false,
    message: "All systems operational",
    bypassKeys: 2,
    allowedIps: 3,
  });

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">Maintenance Mode</h3>
        <span className={`rounded-full px-3 py-1 text-xs font-medium ${status.enabled ? "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300" : "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300"}`}>
          {status.enabled ? "ACTIVE" : "OFF"}
        </span>
      </div>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
        Maintenance mode toggle with bypass keys
      </p>

      <div className="mt-4 rounded-lg bg-zinc-50 p-3 text-sm text-zinc-700 dark:bg-zinc-800 dark:text-zinc-300">
        {status.message}
      </div>

      <div className="mt-3 flex justify-between text-xs text-zinc-400 dark:text-zinc-500">
        <span>{status.bypassKeys} bypass keys</span>
        <span>{status.allowedIps} allowed IPs</span>
      </div>
    </div>
  );
}
