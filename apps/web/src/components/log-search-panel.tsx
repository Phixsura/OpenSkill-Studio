"use client";

import { useState } from "react";

interface LogEntry { level: string; service: string; message: string; timestamp?: string; }
interface LogSearchPanelProps { logs: LogEntry[]; matched: number; total: number;
  levelCounts: Record<string, number>; services: string[]; onSearch: (q: string, level?: string) => void; }

const LEVEL_COLORS: Record<string, string> = {
  error: "text-red-500", warn: "text-yellow-500", info: "text-blue-500", debug: "text-gray-400",
};

export function LogSearchPanel({ logs, matched, total, levelCounts, services, onSearch }: LogSearchPanelProps) {
  const [query, setQuery] = useState("");
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="p-4 border-b dark:border-gray-700">
        <div className="flex items-center justify-between mb-2">
          <h3 className="font-semibold">🔍 Log Search</h3>
          <span className="text-xs text-gray-400">{matched}/{total} logs</span>
        </div>
        <div className="flex gap-2">
          <input value={query} onChange={e => setQuery(e.target.value)}
            onKeyDown={e => e.key === "Enter" && onSearch(query)}
            placeholder="Search logs..." className="flex-1 px-3 py-1.5 text-sm border rounded-lg dark:bg-gray-800 dark:border-gray-600" />
          <div className="flex gap-1">
            {Object.entries(levelCounts).map(([lv, count]) => (
              <button key={lv} onClick={() => onSearch(query, lv)}
                className="px-2 py-1 text-[10px] rounded bg-gray-100 dark:bg-gray-800 hover:bg-gray-200">
                {lv} ({count})
              </button>
            ))}
          </div>
        </div>
      </div>
      <div className="max-h-64 overflow-y-auto divide-y dark:divide-gray-700">
        {logs.map((log, i) => (
          <div key={i} className="flex items-start gap-2 px-4 py-1.5 text-xs font-mono">
            <span className={`uppercase font-bold w-12 ${LEVEL_COLORS[log.level] ?? ""}`}>{log.level}</span>
            <span className="text-gray-400 w-16 truncate">{log.service}</span>
            <span className="flex-1">{log.message}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
