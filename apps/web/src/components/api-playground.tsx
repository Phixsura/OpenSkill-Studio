"use client";

import { useState } from "react";

interface ApiPlaygroundProps { history: { method: string; path: string; status: number; responseMs: number }[];
  onSend: (method: string, path: string, body: string) => void; }

const METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE"];
const METHOD_COLORS: Record<string, string> = {
  GET: "bg-green-500", POST: "bg-blue-500", PUT: "bg-yellow-500",
  PATCH: "bg-orange-500", DELETE: "bg-red-500",
};

export function ApiPlayground({ history, onSend }: ApiPlaygroundProps) {
  const [method, setMethod] = useState("GET");
  const [path, setPath] = useState("/api/");
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold mb-2">🧪 API Playground</h3>
        <div className="flex gap-2">
          <select value={method} onChange={e => setMethod(e.target.value)}
            className="text-xs border rounded px-2 py-1.5 dark:bg-gray-800 dark:border-gray-600 font-mono">
            {METHODS.map(m => <option key={m}>{m}</option>)}
          </select>
          <input value={path} onChange={e => setPath(e.target.value)}
            className="flex-1 px-3 py-1.5 text-sm font-mono border rounded dark:bg-gray-800 dark:border-gray-600" />
          <button onClick={() => onSend(method, path, "")}
            className="px-4 py-1.5 text-xs bg-blue-500 text-white rounded font-medium">Send</button>
        </div>
      </div>
      {history.length > 0 && (
        <div className="divide-y dark:divide-gray-700 max-h-40 overflow-y-auto">
          {history.map((h, i) => (
            <div key={i} className="flex items-center justify-between px-4 py-1.5 text-xs">
              <div className="flex items-center gap-2">
                <span className={`px-1.5 py-0.5 text-[10px] text-white rounded ${METHOD_COLORS[h.method] ?? "bg-gray-500"}`}>{h.method}</span>
                <span className="font-mono">{h.path}</span>
              </div>
              <div className="flex gap-2 text-gray-400">
                <span className={h.status < 400 ? "text-green-600" : "text-red-500"}>{h.status}</span>
                <span>{h.responseMs}ms</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
