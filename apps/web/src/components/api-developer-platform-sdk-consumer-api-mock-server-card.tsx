"use client";

import { useState } from "react";

interface MockEp {
  method: string;
  path: string;
  statusCode: number;
  hitCount: number;
  enabled: boolean;
}

const METHOD_COLOR: Record<string, string> = {
  GET: "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300",
  POST: "bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300",
  PUT: "bg-amber-100 text-amber-700 dark:bg-amber-900 dark:text-amber-300",
  DELETE: "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300",
};

export default function MockServerCard() {
  const [endpoints] = useState<MockEp[]>([
    { method: "GET", path: "/api/users", statusCode: 200, hitCount: 45, enabled: true },
    { method: "POST", path: "/api/orders", statusCode: 201, hitCount: 12, enabled: true },
    { method: "DELETE", path: "/api/users/{id}", statusCode: 204, hitCount: 3, enabled: false },
  ]);

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">
        Mock Server
      </h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
        Endpoint mocking with response templates
      </p>

      <div className="mt-4 space-y-2">
        {endpoints.map((ep) => (
          <div
            key={`${ep.method}:${ep.path}`}
            className={`flex items-center justify-between rounded-lg border border-zinc-100 px-3 py-2 dark:border-zinc-700 ${!ep.enabled ? "opacity-50" : ""}`}
          >
            <div className="flex items-center gap-2">
              <span className={`rounded px-1.5 py-0.5 text-xs font-bold ${METHOD_COLOR[ep.method] ?? ""}`}>
                {ep.method}
              </span>
              <span className="font-mono text-sm text-zinc-800 dark:text-zinc-200">{ep.path}</span>
            </div>
            <div className="flex items-center gap-2 text-xs text-zinc-500">
              <span>{ep.statusCode}</span>
              <span>{ep.hitCount} hits</span>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">
        {endpoints.filter((e) => e.enabled).length}/{endpoints.length} endpoints active
      </div>
    </div>
  );
}
