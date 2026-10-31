"use client";

import { useState } from "react";

interface PrefRow {
  eventType: string;
  email: boolean;
  slack: boolean;
  webhook: boolean;
  muted: boolean;
}

export default function NotifPrefsCard() {
  const [prefs] = useState<PrefRow[]>([
    { eventType: "Incidents", email: true, slack: true, webhook: true, muted: false },
    { eventType: "Maintenance", email: true, slack: false, webhook: false, muted: false },
    { eventType: "Billing", email: true, slack: false, webhook: false, muted: false },
    { eventType: "Security", email: true, slack: true, webhook: true, muted: false },
    { eventType: "Changelog", email: false, slack: true, webhook: false, muted: true },
  ]);

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">
        Notification Preferences
      </h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
        Per-consumer notification channel settings
      </p>

      <div className="mt-4 space-y-2">
        {prefs.map((p) => (
          <div
            key={p.eventType}
            className={`flex items-center justify-between rounded-lg border border-zinc-100 px-3 py-2 dark:border-zinc-700 ${p.muted ? "opacity-50" : ""}`}
          >
            <span className="text-sm text-zinc-800 dark:text-zinc-200">{p.eventType}</span>
            <div className="flex items-center gap-2 text-xs">
              {p.email && <span className="rounded bg-blue-100 px-1.5 py-0.5 text-blue-700 dark:bg-blue-900 dark:text-blue-300">email</span>}
              {p.slack && <span className="rounded bg-purple-100 px-1.5 py-0.5 text-purple-700 dark:bg-purple-900 dark:text-purple-300">slack</span>}
              {p.webhook && <span className="rounded bg-green-100 px-1.5 py-0.5 text-green-700 dark:bg-green-900 dark:text-green-300">webhook</span>}
              {p.muted && <span className="text-zinc-400">muted</span>}
            </div>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">
        {prefs.filter((p) => !p.muted).length}/{prefs.length} event types active
      </div>
    </div>
  );
}
