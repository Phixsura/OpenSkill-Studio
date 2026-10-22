"use client";

import { useState } from "react";

interface Endpoint { method: string; path: string; description: string; auth: boolean; }
interface ApiPlaygroundProps { endpoints: Endpoint[]; onExecute: (endpoint: Endpoint) => void; }

const METHOD_COLORS: Record<string, string> = { GET: "bg-green-100 text-green-800", POST: "bg-blue-100 text-blue-800", PUT: "bg-yellow-100 text-yellow-800", DELETE: "bg-red-100 text-red-800" };

export function ApiPlayground({ endpoints, onExecute }: ApiPlaygroundProps) {
  const [selected, setSelected] = useState<number | null>(null);
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <h4 className="mb-3 font-semibold">🧪 API Playground</h4>
      <div className="space-y-2">
        {endpoints.map((ep, i) => (
          <div key={i} onClick={() => setSelected(i)}
            className={`flex cursor-pointer items-center gap-2 rounded border p-2 transition ${selected === i ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20" : "border-gray-200 hover:border-gray-300 dark:border-gray-700"}`}>
            <span className={`rounded px-1.5 py-0.5 text-xs font-bold ${METHOD_COLORS[ep.method] ?? "bg-gray-100"}`}>{ep.method}</span>
            <code className="flex-1 text-xs">{ep.path}</code>
            <span className="text-xs text-gray-500">{ep.description}</span>
            {selected === i && <button onClick={(e) => { e.stopPropagation(); onExecute(ep); }} className="rounded bg-blue-600 px-2 py-0.5 text-xs text-white">Run</button>}
          </div>
        ))}
      </div>
    </div>
  );
}
