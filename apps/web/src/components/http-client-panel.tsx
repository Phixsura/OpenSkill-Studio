"use client";

import { useState } from "react";

interface RequestLog {
  requestId: string;
  method: string;
  url: string;
  statusCode: number;
  latencyMs: number;
  blocked: boolean;
  blockReason?: string;
}

interface AllowlistEntry {
  pattern: string;
}

const methodColors: Record<string, string> = {
  GET: "text-green-600", POST: "text-blue-600", PUT: "text-yellow-600",
  DELETE: "text-red-600", PATCH: "text-purple-600",
};

export function HttpClientPanel({
  logs,
  allowlist,
  blockedCount,
  onAddPattern,
  onRemovePattern,
}: {
  logs: RequestLog[];
  allowlist: AllowlistEntry[];
  blockedCount: number;
  onAddPattern?: (pattern: string) => void;
  onRemovePattern?: (pattern: string) => void;
}) {
  const [tab, setTab] = useState<"logs" | "allowlist">("logs");
  const [newPattern, setNewPattern] = useState("");

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">🌐 HTTP Client</h2>
        <div className="flex items-center gap-2 text-sm">
          <span>{logs.length} requests</span>
          {blockedCount > 0 && <span className="text-red-500">{blockedCount} blocked</span>}
        </div>
      </div>

      <div className="flex gap-1">
        <button onClick={() => setTab("logs")}
          className={`text-xs px-3 py-1 rounded-lg ${tab === "logs" ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
          Request Log
        </button>
        <button onClick={() => setTab("allowlist")}
          className={`text-xs px-3 py-1 rounded-lg ${tab === "allowlist" ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
          Allowlist ({allowlist.length})
        </button>
      </div>

      {tab === "logs" && (
        <div className="space-y-1">
          {logs.map((log) => (
            <div key={log.requestId} className={`rounded-lg border dark:border-gray-700 p-2 flex items-center gap-2 text-sm ${log.blocked ? "opacity-50 bg-red-50 dark:bg-red-900/5" : ""}`}>
              <span className={`font-bold text-xs w-12 ${methodColors[log.method] || ""}`}>{log.method}</span>
              <code className="text-xs flex-1 truncate">{log.url}</code>
              {log.blocked ? (
                <span className="text-xs text-red-500 shrink-0">🚫 {log.blockReason}</span>
              ) : (
                <>
                  <span className={`text-xs font-bold shrink-0 ${log.statusCode < 400 ? "text-green-600" : "text-red-600"}`}>{log.statusCode}</span>
                  <span className="text-xs text-gray-400 shrink-0">{log.latencyMs}ms</span>
                </>
              )}
            </div>
          ))}
        </div>
      )}

      {tab === "allowlist" && (
        <div className="space-y-2">
          <div className="flex gap-1">
            <input type="text" value={newPattern} onChange={(e) => setNewPattern(e.target.value)}
              placeholder="https://api.example.com/*"
              className="flex-1 rounded border dark:border-gray-700 bg-white dark:bg-gray-900 px-2 py-1 text-sm font-mono" />
            <button onClick={() => { onAddPattern?.(newPattern); setNewPattern(""); }}
              className="text-xs bg-green-600 text-white px-3 py-1 rounded">Add</button>
          </div>
          {allowlist.map((entry) => (
            <div key={entry.pattern} className="flex items-center justify-between rounded-lg border dark:border-gray-700 p-2">
              <code className="text-sm">{entry.pattern}</code>
              <button onClick={() => onRemovePattern?.(entry.pattern)} className="text-xs text-red-500">✕</button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
