"use client";

import { useState } from "react";

interface SubInfo { subId: string; topic: string; active: boolean; delivered: number; }

export default function EventBusCard() {
  const [subs] = useState<SubInfo[]>([
    { subId: "s1", topic: "order.*", active: true, delivered: 1250 },
    { subId: "s2", topic: "user.created", active: true, delivered: 340 },
    { subId: "s3", topic: "payment.*", active: false, delivered: 0 },
  ]);
  const [stats] = useState({ totalEvents: 4500, uniqueTopics: 12 });

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">Event Bus</h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">Pub/sub event bus with topic filtering</p>

      <div className="mt-4 space-y-2">
        {subs.map((s) => (
          <div key={s.subId} className={`flex items-center justify-between rounded-lg border border-zinc-100 px-3 py-2 dark:border-zinc-700 ${!s.active ? "opacity-50" : ""}`}>
            <div className="flex items-center gap-2">
              <span className={`h-2 w-2 rounded-full ${s.active ? "bg-green-500" : "bg-zinc-300"}`} />
              <code className="text-sm text-zinc-800 dark:text-zinc-200">{s.topic}</code>
            </div>
            <span className="text-xs text-zinc-400">{s.delivered.toLocaleString()} delivered</span>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">
        {stats.totalEvents.toLocaleString()} events · {stats.uniqueTopics} topics
      </div>
    </div>
  );
}
