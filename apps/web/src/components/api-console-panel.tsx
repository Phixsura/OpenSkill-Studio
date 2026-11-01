"use client";

import { useState } from "react";

interface ConsoleEnv { envId: string; name: string; isActive: boolean; varCount: number; }

export function ApiConsolePanel({ envs, onExecute, onSetEnv }: {
  envs: ConsoleEnv[];
  onExecute?: (method: string, url: string, body: string) => void;
  onSetEnv?: (envId: string) => void;
}) {
  const [method, setMethod] = useState("GET");
  const [url, setUrl] = useState("");
  const [body, setBody] = useState("");

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">🖥️ API Console</h2>
        <div className="flex gap-1">
          {envs.map((e) => (
            <button key={e.envId} onClick={() => onSetEnv?.(e.envId)}
              className={`text-xs px-2 py-1 rounded ${e.isActive ? "bg-green-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
              {e.name} ({e.varCount})
            </button>
          ))}
        </div>
      </div>

      <div className="flex gap-2">
        <select value={method} onChange={(e) => setMethod(e.target.value)}
          className="rounded-lg border dark:border-gray-700 bg-white dark:bg-gray-900 px-2 py-2 text-sm font-bold">
          {["GET", "POST", "PUT", "DELETE", "PATCH"].map((m) => <option key={m}>{m}</option>)}
        </select>
        <input type="text" value={url} onChange={(e) => setUrl(e.target.value)}
          placeholder="{{base_url}}/api/endpoint"
          className="flex-1 rounded-lg border dark:border-gray-700 bg-white dark:bg-gray-900 px-3 py-2 text-sm font-mono" />
        <button onClick={() => onExecute?.(method, url, body)}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-bold">Send</button>
      </div>

      {method !== "GET" && (
        <textarea value={body} onChange={(e) => setBody(e.target.value)}
          placeholder='{"key": "value"}'
          className="w-full rounded-lg border dark:border-gray-700 bg-white dark:bg-gray-900 px-3 py-2 text-sm font-mono h-20" />
      )}
    </div>
  );
}
