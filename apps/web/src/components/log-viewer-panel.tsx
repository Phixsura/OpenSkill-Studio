"use client";

import { useState } from "react";

interface LogEntry { level: string; message: string; timestamp?: string; }
interface LogViewerPanelProps { logs: LogEntry[]; totalMatched: number;
  onFilter: (level: string, search: string) => void; }

const levelColors: Record<string, string> = {
  debug: "text-gray-400", info: "text-blue-500", warning: "text-yellow-500",
  error: "text-red-500", critical: "text-red-700 font-bold",
};

export function LogViewerPanel({ logs, totalMatched, onFilter }: LogViewerPanelProps) {
  const [level, setLevel] = useState("debug");
  const [search, setSearch] = useState("");

  return (
    <div className="space-y-3">
      <h2 className="text-lg font-semibold">Logs</h2>
      <div className="flex gap-2">
        <select value={level} onChange={e => { setLevel(e.target.value); onFilter(e.target.value, search); }}
          className="rounded border px-2 py-1.5 text-sm dark:border-gray-600 dark:bg-gray-700">
          <option value="debug">Debug+</option>
          <option value="info">Info+</option>
          <option value="warning">Warning+</option>
          <option value="error">Error+</option>
        </select>
        <input value={search} onChange={e => { setSearch(e.target.value); onFilter(level, e.target.value); }}
          placeholder="Search logs..." className="flex-1 rounded border px-3 py-1.5 text-sm dark:border-gray-600 dark:bg-gray-700" />
        <span className="flex items-center text-xs text-gray-400">{totalMatched} results</span>
      </div>
      <div className="max-h-80 overflow-y-auto rounded border bg-gray-900 p-3 font-mono text-xs dark:border-gray-700">
        {logs.map((l, i) => (
          <div key={i} className="flex gap-2 py-0.5">
            {l.timestamp && <span className="text-gray-500">{l.timestamp}</span>}
            <span className={`w-16 uppercase ${levelColors[l.level] ?? "text-gray-400"}`}>{l.level}</span>
            <span className="text-gray-200">{l.message}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
