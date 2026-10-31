"use client";

import { useState } from "react";

interface InspectEntry { requestId: string; eventType: string; status: number; latencyMs: number; }

export default function WebhookInspectorCard() {
  const [entries] = useState<InspectEntry[]>([
    { requestId: "req_a1b2", eventType: "order.created", status: 200, latencyMs: 45 },
    { requestId: "req_c3d4", eventType: "user.signup", status: 200, latencyMs: 120 },
    { requestId: "req_e5f6", eventType: "payment.failed", status: 500, latencyMs: 3200 },
  ]);

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">Webhook Inspector</h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">Real-time webhook request/response inspection</p>

      <div className="mt-4 space-y-2">
        {entries.map((e) => (
          <div key={e.requestId} className="flex items-center justify-between rounded-lg border border-zinc-100 px-3 py-2 dark:border-zinc-700">
            <div>
              <code className="text-xs text-zinc-500">{e.requestId}</code>
              <span className="ml-2 text-sm text-zinc-800 dark:text-zinc-200">{e.eventType}</span>
            </div>
            <div className="flex items-center gap-2 text-xs">
              <span className={e.status < 400 ? "text-green-600" : "text-red-600"}>{e.status}</span>
              <span className="text-zinc-400">{e.latencyMs}ms</span>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">
        {entries.length} recent inspections
      </div>
    </div>
  );
}
