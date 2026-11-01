"use client";

import { useState } from "react";

interface AuditEntry {
  eventId: string;
  actor: string;
  action: string;
  resource: string;
  timestamp: string;
}

const ACTION_COLOR: Record<string, string> = {
  create: "text-green-600 dark:text-green-400",
  update: "text-blue-600 dark:text-blue-400",
  delete: "text-red-600 dark:text-red-400",
};

export default function AuditTrailCard() {
  const [entries] = useState<AuditEntry[]>([
    { eventId: "e1", actor: "alice", action: "create", resource: "api_key:k-1234", timestamp: "2 min ago" },
    { eventId: "e2", actor: "bob", action: "update", resource: "endpoint:ep-users", timestamp: "15 min ago" },
    { eventId: "e3", actor: "alice", action: "delete", resource: "webhook:wh-old", timestamp: "1 hr ago" },
  ]);
  const [integrity] = useState({ valid: true, checked: 156 });

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">
          Audit Trail
        </h3>
        <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${integrity.valid ? "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300" : "bg-red-100 text-red-700"}`}>
          {integrity.valid ? "Chain Valid" : "Tampered"}
        </span>
      </div>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
        Immutable event log with tamper detection
      </p>

      <div className="mt-4 space-y-2">
        {entries.map((e) => (
          <div
            key={e.eventId}
            className="flex items-center justify-between rounded-lg border border-zinc-100 px-3 py-2 dark:border-zinc-700"
          >
            <div className="flex items-center gap-2">
              <span className={`text-xs font-medium ${ACTION_COLOR[e.action] ?? "text-zinc-500"}`}>
                {e.action}
              </span>
              <span className="font-mono text-sm text-zinc-800 dark:text-zinc-200">
                {e.resource}
              </span>
            </div>
            <div className="text-xs text-zinc-400">
              {e.actor} · {e.timestamp}
            </div>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">
        {integrity.checked} entries verified
      </div>
    </div>
  );
}
