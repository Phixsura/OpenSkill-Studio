"use client";

import { useState } from "react";

interface Endpoint { method: string; path: string; fullUrl: string; summary: string; auth: boolean; tag: string; }
interface ApiExplorerPageProps { endpoints: Endpoint[]; tags: string[]; baseUrl: string;
  onFilter: (tag: string | null) => void; }

const methodColors: Record<string, string> = {
  GET: "bg-green-500", POST: "bg-blue-500", PUT: "bg-yellow-500",
  PATCH: "bg-orange-500", DELETE: "bg-red-500",
};

export function ApiExplorerPage({ endpoints, tags, baseUrl, onFilter }: ApiExplorerPageProps) {
  const [active, setActive] = useState<string | null>(null);
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">🔍 API Explorer</h2>
        <span className="text-xs text-gray-400">{endpoints.length} endpoints · {baseUrl}</span>
      </div>
      <div className="flex gap-1">
        <button onClick={() => { setActive(null); onFilter(null); }}
          className={`rounded px-2 py-0.5 text-xs ${!active ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800"}`}>All</button>
        {tags.map(t => (
          <button key={t} onClick={() => { setActive(t); onFilter(t); }}
            className={`rounded px-2 py-0.5 text-xs ${active === t ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800"}`}>{t}</button>
        ))}
      </div>
      <div className="divide-y rounded-xl border dark:divide-gray-700 dark:border-gray-700">
        {endpoints.map((ep, i) => (
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
