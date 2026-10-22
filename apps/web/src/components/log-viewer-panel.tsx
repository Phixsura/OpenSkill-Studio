"use client";

import { useState } from "react";

interface LogEntry { timestamp: string; level: string; message: string; }
interface LogViewerPanelProps { logs: LogEntry[]; onFilter: (level: string | null, search: string) => void; }

const LEVEL_COLORS: Record<string, string> = {
  error: "text-red-600", warn: "text-yellow-600", info: "text-blue-600", debug: "text-gray-400",
};

export function LogViewerPanel({ logs, onFilter }: LogViewerPanelProps) {
  const [search, setSearch] = useState("");
  const [level, setLevel] = useState<string | null>(null);

  const handleFilter = (newLevel: string | null) => { setLevel(newLevel); onFilter(newLevel, search); };

  return (
    <div className="rounded-lg border border-gray-200 dark:border-gray-700">
      <div className="flex items-center gap-2 border-b p-3 dark:border-gray-700">
        <input value={search} onChange={e => { setSearch(e.target.value); onFilter(level, e.target.value); }}
          placeholder="Search logs..." className="flex-1 rounded border px-2 py-1 text-sm dark:border-gray-600 dark:bg-gray-700" />
        {["error", "warn", "info"].map(l => (
          <button key={l} onClick={() => handleFilter(level === l ? null : l)}
            className={`rounded px-2 py-1 text-xs ${level === l ? "bg-blue-100 font-semibold" : "text-gray-500"}`}>{l}</button>
        ))}
      </div>
      <div className="max-h-64 overflow-y-auto p-2 font-mono text-xs">
        {logs.length === 0 ? <p className="p-2 text-gray-400">No logs found.</p> : logs.map((l, i) => (
          <div key={i} className="py-0.5">
            <span className="text-gray-400">{l.timestamp.slice(11, 19)}</span>{" "}
            <span className={LEVEL_COLORS[l.level] || ""}>{l.level.toUpperCase().padEnd(5)}</span>{" "}
            <span>{l.message}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
