"use client";

import { useState } from "react";

interface HistoryItem {
  name: string;
  method: string;
  url: string;
  statusCode: number;
  latencyMs: number;
}

const METHOD_COLOR: Record<string, string> = {
  GET: "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300",
  POST: "bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300",
  PUT: "bg-amber-100 text-amber-700 dark:bg-amber-900 dark:text-amber-300",
  DELETE: "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300",
};

export default function PlaygroundCard() {
  const [history] = useState<HistoryItem[]>([
    { name: "List Users", method: "GET", url: "/api/users", statusCode: 200, latencyMs: 45 },
    { name: "Create Order", method: "POST", url: "/api/orders", statusCode: 201, latencyMs: 120 },
    { name: "Delete Item", method: "DELETE", url: "/api/items/5", statusCode: 204, latencyMs: 30 },
  ]);

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">API Playground</h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">Interactive API testing with collections</p>

      <div className="mt-4 space-y-2">
        {history.map((h, i) => (
          <div key={i} className="flex items-center justify-between rounded-lg border border-zinc-100 px-3 py-2 dark:border-zinc-700">
            <div className="flex items-center gap-2">
              <span className={`rounded px-1.5 py-0.5 text-xs font-bold ${METHOD_COLOR[h.method] ?? ""}`}>{h.method}</span>
              <span className="font-mono text-sm text-zinc-800 dark:text-zinc-200">{h.url}</span>
            </div>
            <div className="flex items-center gap-2 text-xs text-zinc-500">
              <span className={h.statusCode < 400 ? "text-green-600" : "text-red-600"}>{h.statusCode}</span>
              <span>{h.latencyMs}ms</span>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">{history.length} recent requests</div>
    </div>
  );
}
