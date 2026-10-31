"use client";

import { useState } from "react";

interface WebhookDelivery {
  id: string;
  eventType: string;
  url: string;
  status: "delivered" | "failed" | "retrying" | "dead_letter";
  statusCode: number;
  attempt: number;
  maxAttempts: number;
  durationMs: number;
  timestamp: string;
  requestBody: string;
  responseBody: string;
}

export function WebhookDebuggerPanel({
  deliveries,
  onRetry,
}: {
  deliveries: WebhookDelivery[];
  onRetry?: (id: string) => void;
}) {
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [filter, setFilter] = useState<string>("all");

  const filtered = filter === "all" ? deliveries : deliveries.filter((d) => d.status === filter);

  const statusConfig: Record<string, { color: string; icon: string }> = {
    delivered: { color: "text-green-600 bg-green-100 dark:bg-green-900/30 dark:text-green-300", icon: "✅" },
    failed: { color: "text-red-600 bg-red-100 dark:bg-red-900/30 dark:text-red-300", icon: "❌" },
    retrying: { color: "text-yellow-600 bg-yellow-100 dark:bg-yellow-900/30 dark:text-yellow-300", icon: "🔄" },
    dead_letter: { color: "text-gray-600 bg-gray-100 dark:bg-gray-800 dark:text-gray-300", icon: "💀" },
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">🐛 Webhook Debugger</h2>
        <div className="flex gap-1">
          {["all", "delivered", "failed", "retrying", "dead_letter"].map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`text-xs px-2.5 py-1 rounded-full ${
                filter === f ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-300"
              }`}
            >
              {f === "all" ? "All" : f.replace("_", " ")}
            </button>
          ))}
        </div>
      </div>

      <div className="text-sm text-gray-500">{filtered.length} deliveries</div>

      <div className="space-y-2">
        {filtered.map((d) => {
          const cfg = statusConfig[d.status];
          const expanded = expandedId === d.id;
          return (
            <div key={d.id} className="rounded-lg border dark:border-gray-700 overflow-hidden">
              <button
                onClick={() => setExpandedId(expanded ? null : d.id)}
                className="w-full flex items-center justify-between p-3 text-left hover:bg-gray-50 dark:hover:bg-gray-800/50"
              >
                <div className="flex items-center gap-3 text-sm">
                  <span className={`text-xs px-2 py-0.5 rounded-full ${cfg.color}`}>
                    {cfg.icon} {d.status}
                  </span>
                  <span className="font-mono text-xs">{d.eventType}</span>
                  <span className="text-gray-400 text-xs">{d.statusCode} · {d.durationMs}ms · {d.timestamp}</span>
                </div>
                <span className="text-gray-400 text-xs">
                  {d.attempt}/{d.maxAttempts} {expanded ? "▼" : "▶"}
                </span>
              </button>
              {expanded && (
                <div className="border-t dark:border-gray-700 p-3 space-y-3 bg-gray-50 dark:bg-gray-900/50">
                  <div className="text-xs"><span className="font-medium">URL:</span> {d.url}</div>
                  <div>
                    <div className="text-xs font-medium mb-1">Request Body</div>
                    <pre className="text-xs bg-gray-900 text-green-400 p-2 rounded overflow-auto max-h-24">{d.requestBody}</pre>
                  </div>
                  <div>
                    <div className="text-xs font-medium mb-1">Response Body</div>
                    <pre className="text-xs bg-gray-900 text-yellow-400 p-2 rounded overflow-auto max-h-24">{d.responseBody}</pre>
                  </div>
                  {d.status === "failed" && (
                    <button onClick={() => onRetry?.(d.id)} className="text-xs text-blue-500 hover:underline">
                      🔄 Retry Delivery
                    </button>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
