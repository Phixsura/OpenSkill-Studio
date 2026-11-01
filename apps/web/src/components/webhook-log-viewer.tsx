"use client";

import { useState } from "react";

interface WebhookLogEntry {
  id: string;
  direction: "inbound" | "outbound";
  eventType: string;
  endpointUrl: string;
  status: "success" | "failed" | "timeout" | "rejected";
  statusCode: number;
  latencyMs: number;
  payloadSizeBytes: number;
  errorMessage?: string;
  timestamp: string;
}

interface WebhookStats {
  total: number;
  successRate: number;
  avgLatencyMs: number;
}

const statusStyles: Record<string, string> = {
  success: "text-green-600", failed: "text-red-600",
  timeout: "text-yellow-600", rejected: "text-gray-500",
};

export function WebhookLogViewer({
  entries,
  stats,
  onFilter,
}: {
  entries: WebhookLogEntry[];
  stats: WebhookStats;
  onFilter?: (status: string | null) => void;
}) {
  const [filter, setFilter] = useState<string | null>(null);

  const filtered = filter ? entries.filter((e) => e.status === filter) : entries;

  const handleFilter = (s: string | null) => {
    setFilter(s);
    onFilter?.(s);
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">📜 Webhook Log</h2>
        <div className="flex gap-3 text-sm">
          <span>{stats.total} events</span>
          <span className="text-green-600">{stats.successRate}% success</span>
          <span className="text-gray-500">{stats.avgLatencyMs}ms avg</span>
        </div>
      </div>

      <div className="flex gap-1">
        {[null, "success", "failed", "timeout"].map((s) => (
          <button key={String(s)} onClick={() => handleFilter(s)}
            className={`text-xs px-2.5 py-1 rounded-full ${filter === s ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
            {s || "All"}
          </button>
        ))}
      </div>

      <div className="space-y-1">
        {filtered.map((entry) => (
          <div key={entry.id} className="rounded-lg border dark:border-gray-700 p-2 flex items-center gap-3 text-sm">
            <span className="text-xs">{entry.direction === "inbound" ? "📥" : "📤"}</span>
            <span className="font-mono text-xs flex-1 truncate">{entry.eventType}</span>
            <span className={`font-bold text-xs ${statusStyles[entry.status]}`}>
              {entry.statusCode || entry.status}
            </span>
            <span className="text-xs text-gray-400">{entry.latencyMs}ms</span>
            <span className="text-xs text-gray-400">{(entry.payloadSizeBytes / 1024).toFixed(1)}KB</span>
          </div>
        ))}
      </div>
    </div>
  );
}
