"use client";

import { useState } from "react";

interface Endpoint { method: string; path: string; description: string; auth_required: boolean; }
interface ApiPlaygroundPanelProps { endpoints: Endpoint[]; onExecute: (method: string, path: string) => void; }

const methodColors: Record<string, string> = {
  GET: "bg-green-100 text-green-700 dark:bg-green-900/30", POST: "bg-blue-100 text-blue-700 dark:bg-blue-900/30",
  PUT: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30", DELETE: "bg-red-100 text-red-700 dark:bg-red-900/30",
};

export function ApiPlaygroundPanel({ endpoints, onExecute }: ApiPlaygroundPanelProps) {
  const [selected, setSelected] = useState<number | null>(null);
  return (
    <div className="space-y-3">
      <h2 className="text-lg font-semibold">API Playground</h2>
      <div className="space-y-1.5">
        {endpoints.map((ep, i) => (
          <div key={`${ep.method}-${ep.path}`}
            className={`cursor-pointer rounded-lg border p-3 ${selected === i ? "border-blue-500 bg-blue-50 dark:bg-blue-900/10" : "dark:border-gray-700"}`}
            onClick={() => setSelected(i)}>
            <div className="flex items-center gap-2">
              <span className={`rounded px-1.5 py-0.5 font-mono text-xs font-bold ${methodColors[ep.method] ?? ""}`}>{ep.method}</span>
              <span className="font-mono text-sm">{ep.path}</span>
              {ep.auth_required && <span className="text-xs text-gray-400">🔒</span>}
            </div>
            <p className="mt-0.5 text-xs text-gray-400">{ep.description}</p>
            {selected === i && (
              <button onClick={e => { e.stopPropagation(); onExecute(ep.method, ep.path); }}
                className="mt-2 rounded bg-blue-600 px-3 py-1 text-xs text-white">
                Send Request
              </button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
