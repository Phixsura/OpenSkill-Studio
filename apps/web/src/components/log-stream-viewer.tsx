"use client";

import { useState } from "react";

interface LogEntry { timestamp: string; level: string; icon: string; color: string; message: string; source: string; }
interface LogStreamViewerProps { logs: LogEntry[]; errorCount: number; hasErrors: boolean;
  onFilterLevel: (level: string) => void; onSearch: (query: string) => void; }

const levelColors: Record<string, string> = {
  debug: "text-gray-400", info: "text-blue-500", warn: "text-yellow-500",
  error: "text-red-500", fatal: "text-red-700 font-bold",
};

export function LogStreamViewer({ logs, errorCount, hasErrors, onFilterLevel, onSearch }: LogStreamViewerProps) {
  const [search, setSearch] = useState("");
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">📋 Log Stream</h3>
        <div className="flex items-center gap-2">
          {hasErrors && <span className="text-xs text-red-600">{errorCount} errors</span>}
          <select onChange={e => onFilterLevel(e.target.value)}
            className="rounded border px-2 py-0.5 text-xs dark:bg-gray-800 dark:border-gray-600">
            <option value="debug">All</option><option value="info">Info+</option>
            <option value="warn">Warn+</option><option value="error">Errors</option>
          </select>
        </div>
      </div>
      <input value={search} onChange={e => { setSearch(e.target.value); onSearch(e.target.value); }}
        placeholder="Search logs..." className="w-full rounded border px-3 py-1.5 text-xs dark:bg-gray-800 dark:border-gray-600" />
      <div className="max-h-80 overflow-y-auto rounded-lg bg-gray-950 p-3 font-mono text-xs">
        {logs.map((l, i) => (
          <div key={i} className={`py-0.5 ${levelColors[l.level] ?? ""}`}>
            <span className="text-gray-600 mr-2">{l.timestamp.slice(11, 19)}</span>
            <span className="mr-1">{l.icon}</span>
            <span>{l.message}</span>
          </div>
        ))}
        {logs.length === 0 && <p className="text-gray-600 text-center py-4">No logs matching filter</p>}
      </div>
    </div>
  );
}
