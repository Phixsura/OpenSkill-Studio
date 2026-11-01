"use client";

import { useState } from "react";

interface FeedItem {
  id: string;
  type: string;
  actor: string;
  description: string;
  timestamp: string;
  read: boolean;
}

export default function ActivityFeedCard() {
  const [items] = useState<FeedItem[]>([
    { id: "a1", type: "key_created", actor: "alice", description: "Created API key prod-key", timestamp: "2 min ago", read: false },
    { id: "a2", type: "config_changed", actor: "bob", description: "Updated rate limit to 500/min", timestamp: "15 min ago", read: false },
    { id: "a3", type: "alert_triggered", actor: "system", description: "Error rate exceeded 5%", timestamp: "1 hr ago", read: true },
  ]);

  const unread = items.filter((i) => !i.read).length;

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">Activity Feed</h3>
        {unread > 0 && (
          <span className="rounded-full bg-blue-500 px-2 py-0.5 text-xs font-medium text-white">{unread} new</span>
        )}
      </div>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
        Chronological activity stream
      </p>

      <div className="mt-4 space-y-2">
        {items.map((item) => (
          <div key={item.id} className={`rounded-lg border px-3 py-2 ${item.read ? "border-zinc-100 dark:border-zinc-700" : "border-blue-200 bg-blue-50/50 dark:border-blue-800 dark:bg-blue-950/30"}`}>
            <div className="flex items-center justify-between">
              <span className="text-sm text-zinc-800 dark:text-zinc-200">{item.description}</span>
              <span className="text-xs text-zinc-400">{item.timestamp}</span>
            </div>
            <div className="mt-0.5 text-xs text-zinc-400">{item.actor} · {item.type}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
