"use client";

import { useState } from "react";

interface LogEntry {
  id: string;
  level: "debug" | "info" | "warn" | "error" | "fatal";
  message: string;
  source: string;
  timestamp: string;
}

const levelConfig: Record<string, { color: string; bg: string }> = {
  debug: { color: "text-gray-400", bg: "bg-gray-100 dark:bg-gray-800" },
  info: { color: "text-blue-600", bg: "bg-blue-100 dark:bg-blue-900/30" },
  warn: { color: "text-yellow-600", bg: "bg-yellow-100 dark:bg-yellow-900/30" },
  error: { color: "text-red-600", bg: "bg-red-100 dark:bg-red-900/30" },
  fatal: { color: "text-red-800", bg: "bg-red-200 dark:bg-red-900/40" },
};

export function LogStreamViewer({
  entries,
  errorCount,
  onSearch,
  onClear,
}: {
  entries: LogEntry[];
  errorCount: number;
  onSearch?: (query: string) => void;
  onClear?: () => void;
}) {
  const [levelFilter, setLevelFilter] = useState<string>("all");
  const [searchText, setSearchText] = useState("");

  const filtered = levelFilter === "all" ? entries : entries.filter((e) => e.level === levelFilter);

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">📜 Log Stream</h2>
        <div className="flex items-center gap-2">
          {errorCount > 0 && (
            <span className="text-xs bg-red-600 text-white px-2 py-0.5 rounded-full">{errorCount} errors</span>
          )}
          <button onClick={onClear} className="text-xs bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded">Clear</button>
        </div>
      </div>

      <div className="flex gap-2">
        <input type="text" value={searchText}
          onChange={(e) => { setSearchText(e.target.value); onSearch?.(e.target.value); }}
          placeholder="Search logs..."
          className="flex-1 rounded-lg border dark:border-gray-700 bg-white dark:bg-gray-900 px-3 py-1.5 text-sm" />
        <select value={levelFilter} onChange={(e) => setLevelFilter(e.target.value)}
          className="rounded-lg border dark:border-gray-700 bg-white dark:bg-gray-900 px-2 py-1.5 text-sm">
          <option value="all">All Levels</option>
          <option value="error">Errors</option>
          <option value="warn">Warnings</option>
          <option value="info">Info</option>
          <option value="debug">Debug</option>
        </select>
      </div>

      <div className="rounded-lg border dark:border-gray-700 bg-gray-950 dark:bg-black p-3 max-h-96 overflow-y-auto font-mono text-xs space-y-0.5">
        {filtered.length === 0 && (
          <span className="text-gray-500">No log entries</span>
        )}
        {filtered.map((entry) => {
          const cfg = levelConfig[entry.level];
          return (
            <div key={entry.id} className="flex gap-2">
              <span className="text-gray-500 shrink-0">{entry.timestamp}</span>
              <span className={`shrink-0 uppercase w-12 ${cfg.color}`}>{entry.level}</span>
              <span className="text-gray-400 shrink-0">[{entry.source}]</span>
              <span className="text-gray-200">{entry.message}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
