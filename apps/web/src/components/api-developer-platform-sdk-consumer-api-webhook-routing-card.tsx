"use client";

import { useState } from "react";

interface RuleInfo { name: string; field: string; operator: string; value: string; }

export default function WebhookRoutingCard() {
  const [rules] = useState<RuleInfo[]>([
    { name: "Orders", field: "event", operator: "eq", value: "order.*" },
    { name: "High Value", field: "amount", operator: "gt", value: "1000" },
    { name: "Errors", field: "error", operator: "exists", value: "" },
  ]);

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">Webhook Routing</h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">Content-based webhook routing with filters</p>

      <div className="mt-4 space-y-2">
        {rules.map((r) => (
          <div key={r.name} className="flex items-center justify-between rounded-lg border border-zinc-100 px-3 py-2 dark:border-zinc-700">
            <span className="text-sm font-medium text-zinc-900 dark:text-zinc-100">{r.name}</span>
            <code className="text-xs text-zinc-500">{r.field} {r.operator} {r.value}</code>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">{rules.length} routing rules</div>
    </div>
  );
}
