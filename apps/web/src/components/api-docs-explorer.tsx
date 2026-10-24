"use client";

import { useState } from "react";

interface Endpoint { method: string; path: string; summary: string; auth_required: boolean; }
interface Section { tag: string; endpoints: Endpoint[]; }
interface ApiDocsExplorerProps { title: string; version: string; sections: Section[];
  totalEndpoints: number; onTryIt: (method: string, path: string) => void; }

const methodColor: Record<string, string> = {
  GET: "bg-green-100 text-green-700 dark:bg-green-900/30",
  POST: "bg-blue-100 text-blue-700 dark:bg-blue-900/30",
  PUT: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30",
  DELETE: "bg-red-100 text-red-700 dark:bg-red-900/30",
};

export function ApiDocsExplorer({ title, version, sections, totalEndpoints, onTryIt }: ApiDocsExplorerProps) {
  const [expanded, setExpanded] = useState<string | null>(sections[0]?.tag ?? null);
  return (
    <div className="space-y-4">
      <div className="flex items-baseline gap-2">
        <h2 className="text-xl font-bold">{title}</h2>
        <span className="rounded bg-gray-100 px-2 py-0.5 text-xs dark:bg-gray-800">v{version}</span>
        <span className="text-xs text-gray-400">{totalEndpoints} endpoints</span>
      </div>
      {sections.map(s => (
        <div key={s.tag} className="rounded-lg border dark:border-gray-700">
          <button onClick={() => setExpanded(expanded === s.tag ? null : s.tag)}
            className="flex w-full items-center justify-between px-4 py-2.5 text-left font-medium capitalize">
            {s.tag} <span className="text-xs text-gray-400">{s.endpoints.length}</span>
          </button>
          {expanded === s.tag && (
            <div className="border-t dark:border-gray-700">
              {s.endpoints.map((ep, i) => (
                <div key={i} className="flex items-center justify-between border-b px-4 py-2 last:border-0 dark:border-gray-800">
                  <div className="flex items-center gap-2">
                    <span className={`rounded px-1.5 py-0.5 font-mono text-xs font-bold ${methodColor[ep.method] ?? ""}`}>{ep.method}</span>
                    <span className="font-mono text-sm">{ep.path}</span>
                    {ep.auth_required && <span className="text-xs text-gray-400">🔒</span>}
                  </div>
                  <button onClick={() => onTryIt(ep.method, ep.path)} className="text-xs text-blue-500">Try it</button>
                </div>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
