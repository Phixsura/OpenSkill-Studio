"use client";

import { useState } from "react";

interface ExecutionResult {
  id: string;
  method: string;
  path: string;
  statusCode: number;
  body: string;
  latencyMs: number;
  assertionsPassed: number;
  assertionsFailed: number;
}

const methodColors: Record<string, string> = {
  GET: "bg-green-100 text-green-700 dark:bg-green-900/30",
  POST: "bg-blue-100 text-blue-700 dark:bg-blue-900/30",
  PUT: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30",
  DELETE: "bg-red-100 text-red-700 dark:bg-red-900/30",
  PATCH: "bg-purple-100 text-purple-700 dark:bg-purple-900/30",
};

export function ApiPlaygroundUI({
  history,
  variables,
  onExecute,
  onSetVariable,
}: {
  history: ExecutionResult[];
  variables: Record<string, string>;
  onExecute?: (method: string, path: string, body: string) => void;
  onSetVariable?: (key: string, value: string) => void;
}) {
  const [method, setMethod] = useState("GET");
  const [path, setPath] = useState("/api/v1/");
  const [body, setBody] = useState("");
  const [tab, setTab] = useState<"request" | "history" | "vars">("request");

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold">🧪 API Playground</h2>

      <div className="flex gap-2">
        <select value={method} onChange={(e) => setMethod(e.target.value)}
          className="rounded-lg border dark:border-gray-700 bg-white dark:bg-gray-900 px-2 py-2 text-sm font-bold">
          {["GET", "POST", "PUT", "DELETE", "PATCH"].map((m) => (
            <option key={m} value={m}>{m}</option>
          ))}
        </select>
        <input type="text" value={path} onChange={(e) => setPath(e.target.value)}
          className="flex-1 rounded-lg border dark:border-gray-700 bg-white dark:bg-gray-900 px-3 py-2 text-sm font-mono" />
        <button onClick={() => onExecute?.(method, path, body)}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-semibold">Send</button>
      </div>

      <div className="flex gap-1">
        {(["request", "history", "vars"] as const).map((t) => (
          <button key={t} onClick={() => setTab(t)}
            className={`text-xs px-3 py-1 rounded-lg ${tab === t ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
            {t === "request" ? "Body" : t === "history" ? `History (${history.length})` : "Variables"}
          </button>
        ))}
      </div>

      {tab === "request" && method !== "GET" && (
        <textarea value={body} onChange={(e) => setBody(e.target.value)}
          placeholder='{"key": "value"}' rows={4}
          className="w-full rounded-lg border dark:border-gray-700 bg-white dark:bg-gray-900 px-3 py-2 text-sm font-mono" />
      )}

      {tab === "history" && (
        <div className="space-y-2">
          {history.map((r) => (
            <div key={r.id} className="rounded-lg border dark:border-gray-700 p-3">
              <div className="flex items-center gap-2 mb-1">
                <span className={`text-xs px-1.5 py-0.5 rounded font-bold ${methodColors[r.method] || ""}`}>{r.method}</span>
                <span className="text-sm font-mono truncate">{r.path}</span>
                <span className={`text-xs font-bold ${r.statusCode < 400 ? "text-green-600" : "text-red-600"}`}>{r.statusCode}</span>
                <span className="text-xs text-gray-400">{r.latencyMs}ms</span>
              </div>
              {(r.assertionsPassed > 0 || r.assertionsFailed > 0) && (
                <div className="text-xs">
                  <span className="text-green-600">✓ {r.assertionsPassed}</span>
                  {r.assertionsFailed > 0 && <span className="text-red-500 ml-2">✗ {r.assertionsFailed}</span>}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {tab === "vars" && (
        <div className="space-y-1">
          {Object.entries(variables).map(([k, v]) => (
            <div key={k} className="flex gap-2 text-sm">
              <code className="text-blue-600">{`{{${k}}}`}</code>
              <span className="text-gray-500">= {v}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
