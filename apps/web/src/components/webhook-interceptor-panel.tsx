"use client";

import { useState } from "react";

interface InterceptedWebhook {
  interceptId: string;
  direction: "inbound" | "outbound";
  url: string;
  method: string;
  body: string;
  statusCode: number;
  paused: boolean;
  modified: boolean;
  timestamp: string;
}

export function WebhookInterceptorPanel({
  captures,
  pausedCount,
  onResume,
  onModify,
  onClear,
}: {
  captures: InterceptedWebhook[];
  pausedCount: number;
  onResume?: (id: string) => void;
  onModify?: (id: string, body: string) => void;
  onClear?: () => void;
}) {
  const [filter, setFilter] = useState<string>("all");
  const filtered = filter === "all" ? captures
    : filter === "paused" ? captures.filter((c) => c.paused)
    : captures.filter((c) => c.direction === filter);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">🕵️ Webhook Interceptor</h2>
        <div className="flex items-center gap-2">
          {pausedCount > 0 && (
            <span className="text-xs bg-yellow-500 text-white px-2 py-0.5 rounded-full animate-pulse">{pausedCount} paused</span>
          )}
          <button onClick={onClear} className="text-xs bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded">Clear</button>
        </div>
      </div>

      <div className="flex gap-1">
        {["all", "inbound", "outbound", "paused"].map((f) => (
          <button key={f} onClick={() => setFilter(f)}
            className={`text-xs px-2.5 py-1 rounded-full ${filter === f ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
            {f}
          </button>
        ))}
      </div>

      <div className="space-y-1">
        {filtered.map((cap) => (
          <div key={cap.interceptId} className={`rounded-lg border dark:border-gray-700 p-3 ${cap.paused ? "border-yellow-400 bg-yellow-50 dark:bg-yellow-900/10" : ""}`}>
            <div className="flex items-center justify-between mb-1">
              <div className="flex items-center gap-2 text-sm">
                <span className={cap.direction === "inbound" ? "text-blue-600" : "text-green-600"}>
                  {cap.direction === "inbound" ? "📥" : "📤"}
                </span>
                <span className="font-bold text-xs">{cap.method}</span>
                <code className="text-xs truncate max-w-xs">{cap.url}</code>
                {cap.statusCode > 0 && <span className="text-xs text-gray-400">{cap.statusCode}</span>}
                {cap.modified && <span className="text-xs text-purple-600">✏ modified</span>}
                {cap.paused && <span className="text-xs text-yellow-600 font-bold">⏸ PAUSED</span>}
              </div>
              {cap.paused && (
                <div className="flex gap-1">
                  <button onClick={() => onResume?.(cap.interceptId)}
                    className="text-xs bg-green-600 text-white px-2 py-1 rounded">Resume</button>
                  <button onClick={() => onModify?.(cap.interceptId, cap.body)}
                    className="text-xs bg-purple-600 text-white px-2 py-1 rounded">Edit</button>
                </div>
              )}
            </div>
            <pre className="text-xs text-gray-500 bg-gray-50 dark:bg-gray-900/50 rounded p-1 overflow-hidden max-h-12">
              {cap.body.slice(0, 200)}
            </pre>
          </div>
        ))}
      </div>
    </div>
  );
}
