"use client";

import { useState } from "react";

interface AuditEntry { action: string; webhookId: string; actor: string; time: string; }

export default function WebhookAuditCard() {
  const [entries] = useState<AuditEntry[]>([
    { action: "created", webhookId: "wh-orders", actor: "alice", time: "5 min ago" },
    { action: "secret_rotated", webhookId: "wh-orders", actor: "bob", time: "1 hr ago" },
    { action: "delivered", webhookId: "wh-users", actor: "system", time: "2 hr ago" },
    { action: "failed", webhookId: "wh-legacy", actor: "system", time: "3 hr ago" },
  ]);

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">Webhook Audit Log</h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">Immutable webhook audit log</p>

      <div className="mt-4 space-y-2">
        {entries.map((e, i) => (
          <div key={i} className="flex items-center justify-between rounded-lg border border-zinc-100 px-3 py-2 dark:border-zinc-700">
            <div>
              <span className="text-xs font-medium text-zinc-600 dark:text-zinc-400">{e.action}</span>
              <span className="ml-2 font-mono text-sm text-zinc-800 dark:text-zinc-200">{e.webhookId}</span>
            </div>
            <span className="text-xs text-zinc-400">{e.actor} · {e.time}</span>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">{entries.length} audit entries</div>
    </div>
  );
}
