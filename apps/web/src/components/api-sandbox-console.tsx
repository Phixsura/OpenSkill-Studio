"use client";
import { useState } from "react";

interface SandboxReq { requestId: string; method: string; path: string; responseCode: number; responseBody: string; latencyMs: number; }

const methodColors: Record<string, string> = { GET: "text-green-600", POST: "text-blue-600", PUT: "text-yellow-600", PATCH: "text-purple-600", DELETE: "text-red-600" };

export function ApiSandboxConsole({ history, onExecute }: {
  history: SandboxReq[]; onExecute?: (method: string, path: string, body: string) => void;
}) {
  const [method, setMethod] = useState("GET");
  const [path, setPath] = useState("/api/");
  const [body, setBody] = useState("");

  return (
    <div className="space-y-3">
      <div className="flex gap-2">
        <select value={method} onChange={e => setMethod(e.target.value)}
          className="border dark:border-gray-700 rounded-lg px-2 py-2 text-sm bg-transparent font-mono font-bold">
          {["GET", "POST", "PUT", "PATCH", "DELETE"].map(m => <option key={m}>{m}</option>)}
        </select>
        <input value={path} onChange={e => setPath(e.target.value)}
          className="flex-1 border dark:border-gray-700 rounded-lg px-3 py-2 text-sm bg-transparent font-mono" />
        <button onClick={() => onExecute?.(method, path, body)}
          className="bg-blue-500 text-white px-4 py-2 rounded-lg text-sm font-medium">Send</button>
      </div>
      {(method !== "GET" && method !== "DELETE") && (
        <textarea value={body} onChange={e => setBody(e.target.value)} placeholder='{"key":"value"}'
          className="w-full border dark:border-gray-700 rounded-lg px-3 py-2 text-sm bg-transparent font-mono resize-none" rows={3} />
      )}
      <div className="space-y-1">
        {history.map(r => (
          <div key={r.requestId} className="border dark:border-gray-700 rounded-lg p-2 text-xs font-mono">
            <div className="flex justify-between">
              <span><span className={`font-bold ${methodColors[r.method] || ""}`}>{r.method}</span> {r.path}</span>
              <span className={r.responseCode >= 400 ? "text-red-500" : "text-green-500"}>{r.responseCode} · {r.latencyMs}ms</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
