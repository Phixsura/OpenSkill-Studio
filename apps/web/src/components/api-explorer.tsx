"use client";

import { useState } from "react";

interface Endpoint { method: string; path: string; summary: string; auth: boolean; tags: string[]; }
interface ApiExplorerProps { endpoints: Endpoint[]; tags: string[]; }

const methodColors: Record<string, string> = {
  GET: "bg-green-500", POST: "bg-blue-500", PUT: "bg-yellow-500",
  PATCH: "bg-orange-500", DELETE: "bg-red-500",
};

export function ApiExplorer({ endpoints, tags }: ApiExplorerProps) {
  const [filter, setFilter] = useState("all");
  const filtered = filter === "all" ? endpoints : endpoints.filter(e => e.tags.includes(filter));

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">API Explorer</h3>
        <span className="text-xs text-gray-400">{filtered.length} endpoints</span>
      </div>
      <div className="flex gap-1">
        <button onClick={() => setFilter("all")}
          className={`rounded px-2 py-0.5 text-xs ${filter === "all" ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800"}`}>All</button>
        {tags.map(t => (
          <button key={t} onClick={() => setFilter(t)}
            className={`rounded px-2 py-0.5 text-xs ${filter === t ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800"}`}>{t}</button>
        ))}
      </div>
      <div className="divide-y rounded-lg border dark:divide-gray-700 dark:border-gray-700">
        {filtered.map((ep, i) => (
          <div key={i} className="flex items-center gap-3 px-4 py-2.5">
            <span className={`rounded px-1.5 py-0.5 text-xs text-white font-mono ${methodColors[ep.method] ?? "bg-gray-500"}`}>{ep.method}</span>
            <code className="text-sm font-mono flex-1">{ep.path}</code>
            <span className="text-xs text-gray-400 hidden sm:inline">{ep.summary}</span>
            {ep.auth && <span className="text-xs text-yellow-500">🔒</span>}
          </div>
        ))}
      </div>
    </div>
  );
}
