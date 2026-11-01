"use client";

import { useState } from "react";

interface RetryItem {
  id: string;
  operation: string;
  status: "pending" | "retrying" | "succeeded" | "dead_letter";
  attempt: number;
  maxAttempts: number;
  strategy: string;
  lastError?: string;
  nextRetryAt?: string;
}

interface RetryStats {
  total: number;
  pending: number;
  retrying: number;
  succeeded: number;
  deadLetter: number;
}

const statusConfig: Record<string, { color: string; icon: string }> = {
  pending: { color: "bg-gray-100 text-gray-600 dark:bg-gray-800", icon: "⏳" },
  retrying: { color: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30", icon: "🔄" },
  succeeded: { color: "bg-green-100 text-green-700 dark:bg-green-900/30", icon: "✅" },
  dead_letter: { color: "bg-red-100 text-red-600 dark:bg-red-900/30", icon: "💀" },
};

export function RetryQueuePanel({
  items,
  stats,
  onRetryDeadLetter,
}: {
  items: RetryItem[];
  stats: RetryStats;
  onRetryDeadLetter?: (id: string) => void;
}) {
  const [filter, setFilter] = useState<string>("all");
  const filtered = filter === "all" ? items : items.filter((i) => i.status === filter);

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold">🔁 Retry Queue</h2>

      <div className="grid grid-cols-4 gap-2 text-center text-xs">
        <div className="rounded-lg border dark:border-gray-700 p-2">
          <span className="text-gray-500 block">Pending</span>
          <span className="font-bold text-lg">{stats.pending}</span>
        </div>
        <div className="rounded-lg border dark:border-gray-700 p-2">
          <span className="text-gray-500 block">Retrying</span>
          <span className="font-bold text-lg text-yellow-600">{stats.retrying}</span>
        </div>
        <div className="rounded-lg border dark:border-gray-700 p-2">
          <span className="text-gray-500 block">Succeeded</span>
          <span className="font-bold text-lg text-green-600">{stats.succeeded}</span>
        </div>
        <div className="rounded-lg border dark:border-gray-700 p-2">
          <span className="text-gray-500 block">Dead Letter</span>
          <span className="font-bold text-lg text-red-600">{stats.deadLetter}</span>
        </div>
      </div>

      <div className="flex gap-1">
        {["all", "retrying", "dead_letter", "succeeded"].map((f) => (
          <button key={f} onClick={() => setFilter(f)}
            className={`text-xs px-2.5 py-1 rounded-full ${filter === f ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
            {f === "all" ? "All" : f.replace("_", " ")}
          </button>
        ))}
      </div>

      <div className="space-y-1">
        {filtered.map((item) => {
          const cfg = statusConfig[item.status];
          return (
            <div key={item.id} className="rounded-lg border dark:border-gray-700 p-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span>{cfg.icon}</span>
                  <code className="text-sm">{item.operation}</code>
                  <span className={`text-xs px-1.5 py-0.5 rounded-full ${cfg.color}`}>{item.status}</span>
                  <span className="text-xs text-gray-400">{item.attempt}/{item.maxAttempts}</span>
                  <span className="text-xs text-gray-400">{item.strategy}</span>
                </div>
                {item.status === "dead_letter" && (
                  <button onClick={() => onRetryDeadLetter?.(item.id)}
                    className="text-xs bg-blue-600 text-white px-2 py-1 rounded">Retry</button>
                )}
              </div>
              {item.lastError && <div className="text-xs text-red-500 mt-1">{item.lastError}</div>}
            </div>
          );
        })}
      </div>
    </div>
  );
}
