"use client";
import { useState } from "react";

interface LogEntry { level: string; service: string; message: string; timestamp?: string; }
interface LogSearchPanelProps { logs: LogEntry[]; total: number; onSearch: (q: string, level: string) => void; }

const LEVEL_STYLE: Record<string, string> = {
  error: "text-red-600 bg-red-50 dark:bg-red-900/20",
  warn: "text-yellow-600 bg-yellow-50 dark:bg-yellow-900/20",
  info: "text-blue-600 bg-blue-50 dark:bg-blue-900/20",
  debug: "text-gray-500 bg-gray-50 dark:bg-gray-800",
};

export function LogSearchPanel({ logs, total, onSearch }: LogSearchPanelProps) {
  const [query, setQuery] = useState("");
  const [level, setLevel] = useState("all");

  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold mb-3">🔍 Log Search</h3>
        <div className="flex gap-2">
          <input value={query} onChange={e => setQuery(e.target.value)} placeholder="Search logs..."
            className="flex-1 px-3 py-1.5 border rounded text-sm dark:bg-gray-800 dark:border-gray-600" />
          <select value={level} onChange={e => setLevel(e.target.value)}
            className="px-2 py-1.5 border rounded text-sm dark:bg-gray-800 dark:border-gray-600">
            <option value="all">All levels</option>
            <option value="error">Error</option>
            <option value="warn">Warn</option>
            <option value="info">Info</option>
          </select>
          <button onClick={() => onSearch(query, level)}
            className="px-4 py-1.5 bg-blue-600 text-white text-sm rounded hover:bg-blue-700">Search</button>
        </div>
      </div>
      <div className="px-4 py-2 text-xs text-gray-400 border-b dark:border-gray-700">{total} results</div>
      <div className="max-h-96 overflow-y-auto font-mono text-xs">
        {logs.map((log, i) => (
          <div key={i} className="flex gap-2 px-4 py-1.5 border-b last:border-0 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800/50">
            <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold uppercase ${LEVEL_STYLE[log.level] || ""}`}>{log.level}</span>
            <span className="text-gray-400 shrink-0">{log.service}</span>
            <span className="truncate">{log.message}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
