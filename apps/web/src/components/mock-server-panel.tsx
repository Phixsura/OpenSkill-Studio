"use client";

import { useState } from "react";

interface MockEndpoint {
  id: string;
  method: string;
  pathPattern: string;
  statusCode: number;
  callCount: number;
  enabled: boolean;
  latencyMs: number;
}

interface RecordedRequest {
  method: string;
  path: string;
  matchedEndpoint: string;
}

const methodColors: Record<string, string> = {
  GET: "bg-green-500", POST: "bg-blue-500", PUT: "bg-yellow-500",
  DELETE: "bg-red-500", PATCH: "bg-purple-500",
};

export function MockServerPanel({
  endpoints,
  requests,
  onRemove,
  onReset,
  onToggle,
}: {
  endpoints: MockEndpoint[];
  requests: RecordedRequest[];
  onRemove?: (id: string) => void;
  onReset?: () => void;
  onToggle?: (id: string) => void;
}) {
  const [tab, setTab] = useState<"endpoints" | "requests">("endpoints");

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">🎭 Mock Server</h2>
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-500">{requests.length} recorded</span>
          <button onClick={onReset} className="text-xs bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded">Reset</button>
        </div>
      </div>

      <div className="flex gap-1">
        <button onClick={() => setTab("endpoints")}
          className={`text-xs px-3 py-1 rounded-lg ${tab === "endpoints" ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
          Endpoints ({endpoints.length})
        </button>
        <button onClick={() => setTab("requests")}
          className={`text-xs px-3 py-1 rounded-lg ${tab === "requests" ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
          Requests ({requests.length})
        </button>
      </div>

      {tab === "endpoints" && (
        <div className="space-y-1">
          {endpoints.map((ep) => (
            <div key={ep.id} className={`rounded-lg border dark:border-gray-700 p-3 flex items-center justify-between ${!ep.enabled ? "opacity-50" : ""}`}>
              <div className="flex items-center gap-2">
                <span className={`text-xs text-white px-2 py-0.5 rounded font-bold ${methodColors[ep.method] || "bg-gray-500"}`}>
                  {ep.method}
                </span>
                <code className="text-sm">{ep.pathPattern}</code>
                <span className="text-xs text-gray-400">→ {ep.statusCode}</span>
                {ep.latencyMs > 0 && <span className="text-xs text-gray-400">{ep.latencyMs}ms</span>}
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs text-gray-400">×{ep.callCount}</span>
                <button onClick={() => onToggle?.(ep.id)}
                  className={`text-xs px-2 py-0.5 rounded ${ep.enabled ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-500"}`}>
                  {ep.enabled ? "On" : "Off"}
                </button>
                <button onClick={() => onRemove?.(ep.id)} className="text-xs text-red-500">✕</button>
              </div>
            </div>
          ))}
        </div>
      )}

      {tab === "requests" && (
        <div className="space-y-1">
          {requests.map((req, i) => (
            <div key={i} className="rounded-lg border dark:border-gray-700 p-2 flex items-center gap-2 text-sm">
              <span className={`text-xs text-white px-1.5 py-0.5 rounded font-bold ${methodColors[req.method] || "bg-gray-500"}`}>
                {req.method}
              </span>
              <code className="text-xs flex-1">{req.path}</code>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
