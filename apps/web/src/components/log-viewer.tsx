"use client";

import { useState } from "react";

interface LogEntry { raw: string; level: string; icon: string; timestamp: string | null; }
interface LogViewerProps { entries: LogEntry[]; errorCount: number; }

const levelColors: Record<string, string> = {
  DEBUG: "text-gray-400", INFO: "text-blue-500", WARN: "text-yellow-500",
  ERROR: "text-red-500", FATAL: "text-red-700 font-bold",
};

export function LogViewer({ entries, errorCount }: LogViewerProps) {
  const [filter, setFilter] = useState("ALL");
  const filtered = filter === "ALL" ? entries : entries.filter(e => e.level === filter);

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Logs</h3>
        <div className="flex gap-1">
          {["ALL", "ERROR", "WARN", "INFO", "DEBUG"].map(lv => (
            <button key={lv} onClick={() => setFilter(lv)}
              className={`rounded px-2 py-0.5 text-xs ${filter === lv ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800"}`}>
              {lv}{lv === "ERROR" && errorCount > 0 ? ` (${errorCount})` : ""}
            </button>
          ))}
        </div>
      </div>
      <div className="max-h-80 overflow-y-auto rounded-lg bg-gray-950 p-3 font-mono text-xs">
        {filtered.map((e, i) => (
          <div key={i} className={`py-0.5 ${levelColors[e.level] ?? ""}`}>
            {e.timestamp && <span className="text-gray-600 mr-2">{e.timestamp}</span>}
            <span className="mr-1">{e.icon}</span>
            <span>{e.raw}</span>
          </div>
        ))}
        {filtered.length === 0 && <p className="text-gray-600">No log entries</p>}
      </div>
    </div>
  );
}
