"use client";

import { useState } from "react";

export default function WebhookDashboardCard() {
  const [overview] = useState({
    totalWebhooks: 12,
    healthy: 9,
    degraded: 2,
    critical: 1,
    totalDeliveries: 45200,
    overallSuccessRate: 97.8,
  });

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">Webhook Dashboard</h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">Webhook health overview with delivery metrics</p>

      <div className="mt-4 grid grid-cols-3 gap-3 text-center">
        <div className="rounded-lg bg-green-50 p-2 dark:bg-green-950">
          <div className="text-xl font-bold text-green-600 dark:text-green-400">{overview.healthy}</div>
          <div className="text-xs text-green-500">Healthy</div>
        </div>
        <div className="rounded-lg bg-amber-50 p-2 dark:bg-amber-950">
          <div className="text-xl font-bold text-amber-600 dark:text-amber-400">{overview.degraded}</div>
          <div className="text-xs text-amber-500">Degraded</div>
        </div>
        <div className="rounded-lg bg-red-50 p-2 dark:bg-red-950">
          <div className="text-xl font-bold text-red-600 dark:text-red-400">{overview.critical}</div>
          <div className="text-xs text-red-500">Critical</div>
        </div>
      </div>

      <div className="mt-3 flex justify-between text-xs text-zinc-400 dark:text-zinc-500">
        <span>{overview.totalDeliveries.toLocaleString()} deliveries</span>
        <span>{overview.overallSuccessRate}% success</span>
      </div>
    </div>
  );
}
