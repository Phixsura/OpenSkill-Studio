"use client";

import { useState } from "react";

interface EpInfo { path: string; method: string; status: string; team: string; }

const METHOD_COLOR: Record<string, string> = {
  GET: "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300",
  POST: "bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300",
  PUT: "bg-amber-100 text-amber-700 dark:bg-amber-900 dark:text-amber-300",
  DELETE: "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300",
};

export default function EndpointRegistryCard() {
  const [endpoints] = useState<EpInfo[]>([
    { path: "/api/users", method: "GET", status: "active", team: "backend" },
    { path: "/api/orders", method: "POST", status: "active", team: "commerce" },
    { path: "/api/v1/legacy", method: "GET", status: "deprecated", team: "backend" },
    { path: "/api/beta/search", method: "GET", status: "beta", team: "search" },
  ]);

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">Endpoint Registry</h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">Centralized endpoint metadata registry</p>

      <div className="mt-4 space-y-2">
        {endpoints.map((ep) => (
          <div key={ep.path} className="flex items-center justify-between rounded-lg border border-zinc-100 px-3 py-2 dark:border-zinc-700">
            <div className="flex items-center gap-2">
              <span className={`rounded px-1.5 py-0.5 text-xs font-bold ${METHOD_COLOR[ep.method] ?? ""}`}>{ep.method}</span>
              <span className="font-mono text-sm text-zinc-800 dark:text-zinc-200">{ep.path}</span>
            </div>
            <span className="text-xs text-zinc-400">{ep.status} · {ep.team}</span>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">
        {endpoints.length} endpoints · {new Set(endpoints.map((e) => e.team)).size} teams
      </div>
    </div>
  );
}
