"use client";

import { useState } from "react";

interface EndpointInfo {
  path: string; method: string; version: string; description: string;
  deprecated: boolean; callCount: number; avgLatencyMs: number; tags: string[];
}

interface RegistryStats { total: number; deprecated: number; totalCalls: number; versions: string[]; extensions: number; }

const mc: Record<string, string> = { GET: "text-green-600", POST: "text-blue-600", PUT: "text-yellow-600", DELETE: "text-red-600" };

export function EndpointRegistryPanel({ endpoints, stats, onSelect }: {
  endpoints: EndpointInfo[]; stats: RegistryStats; onSelect?: (path: string) => void;
}) {
  const [vFilter, setVFilter] = useState<string>("all");
  const filtered = vFilter === "all" ? endpoints : endpoints.filter((e) => e.version === vFilter);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">📡 Endpoint Registry</h2>
        <span className="text-sm text-gray-500">{stats.total} endpoints · {stats.totalCalls.toLocaleString()} calls</span>
      </div>

      <div className="flex gap-1">
        <button onClick={() => setVFilter("all")} className={`text-xs px-2.5 py-1 rounded-full ${vFilter === "all" ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>All</button>
        {stats.versions.map((v) => (
          <button key={v} onClick={() => setVFilter(v)} className={`text-xs px-2.5 py-1 rounded-full ${vFilter === v ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>{v}</button>
        ))}
      </div>

      <div className="space-y-0.5">
        {filtered.map((ep) => (
          <div key={`${ep.method}:${ep.version}:${ep.path}`} onClick={() => onSelect?.(ep.path)}
            className={`rounded-lg border dark:border-gray-700 p-2 flex items-center justify-between cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800/50 ${ep.deprecated ? "opacity-50 line-through" : ""}`}>
            <div className="flex items-center gap-2">
              <span className={`text-xs font-bold w-12 ${mc[ep.method] || ""}`}>{ep.method}</span>
              <code className="text-xs">{ep.path}</code>
              <span className="text-xs text-gray-400">{ep.version}</span>
              {ep.tags.map((t) => <span key={t} className="text-[10px] bg-gray-100 dark:bg-gray-800 px-1 py-0.5 rounded">{t}</span>)}
            </div>
            <div className="flex gap-2 text-xs text-gray-400">
              <span>{ep.callCount} calls</span>
              <span>{ep.avgLatencyMs}ms</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
