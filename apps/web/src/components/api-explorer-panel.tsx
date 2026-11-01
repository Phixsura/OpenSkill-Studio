"use client";

import { useState } from "react";

interface Endpoint { method: string; path: string; summary: string; try_url: string; }
interface ApiExplorerPanelProps { groups: Record<string, Endpoint[]>; baseUrl: string; }

const METHOD_COLORS: Record<string, string> = {
  GET: "bg-green-100 text-green-700", POST: "bg-blue-100 text-blue-700",
  PUT: "bg-yellow-100 text-yellow-700", DELETE: "bg-red-100 text-red-700",
};

export function ApiExplorerPanel({ groups, baseUrl }: ApiExplorerPanelProps) {
  const [expanded, setExpanded] = useState<string | null>(null);
  return (
    <div className="rounded-lg border border-gray-200 dark:border-gray-700">
      <div className="border-b p-3 dark:border-gray-700">
        <h3 className="text-sm font-semibold">API Explorer</h3>
        <p className="text-xs text-gray-400">{baseUrl}</p>
      </div>
      {Object.entries(groups).map(([tag, endpoints]) => (
        <div key={tag} className="border-b last:border-0 dark:border-gray-700">
          <button onClick={() => setExpanded(expanded === tag ? null : tag)}
            className="flex w-full items-center justify-between px-3 py-2 text-sm font-medium hover:bg-gray-50 dark:hover:bg-gray-800">
            <span className="capitalize">{tag}</span>
            <span className="text-xs text-gray-400">{endpoints.length}</span>
          </button>
          {expanded === tag && endpoints.map((ep, i) => (
            <div key={i} className="flex items-center gap-2 border-t px-4 py-1.5 text-xs dark:border-gray-700">
              <span className={`rounded px-1.5 py-0.5 font-mono ${METHOD_COLORS[ep.method] || "bg-gray-100"}`}>{ep.method}</span>
              <code className="flex-1">{ep.path}</code>
              <span className="text-gray-400">{ep.summary}</span>
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}
