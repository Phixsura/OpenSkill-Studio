"use client";
import { useState } from "react";

interface LogEntry { logId: string; level: string; message: string; timestamp: number; }

const levelColors: Record<string, string> = {
  debug: "text-gray-400", info: "text-blue-500", warn: "text-yellow-500", error: "text-red-500", fatal: "text-red-700 font-bold",
};

const levels = ["all", "debug", "info", "warn", "error", "fatal"];

export function LogViewer({ logs, onSearch }: { logs: LogEntry[]; onSearch?: (query: string, level: string) => void }) {
  const [level, setLevel] = useState("all");
  const [search, setSearch] = useState("");
  const filtered = level === "all" ? logs : logs.filter(l => l.level === level);

  return (
    <div className="space-y-2">
      <div className="flex gap-2">
        <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search logs..."
          onKeyDown={e => e.key === "Enter" && onSearch?.(search, level)}
          className="flex-1 border dark:border-gray-700 rounded-lg px-3 py-1.5 text-xs bg-transparent font-mono" />
        <select value={level} onChange={e => setLevel(e.target.value)}
          className="border dark:border-gray-700 rounded-lg px-2 py-1.5 text-xs bg-transparent">
          {levels.map(l => <option key={l}>{l}</option>)}
        </select>
      </div>
      <div className="bg-gray-900 rounded-xl p-3 max-h-64 overflow-y-auto font-mono text-xs space-y-0.5">
        {filtered.length === 0 ? (
          <span className="text-gray-500">No logs</span>
        ) : filtered.map(l => (
          <div key={l.logId} className="flex gap-2">
            <span className={`w-12 shrink-0 uppercase ${levelColors[l.level] || "text-gray-400"}`}>{l.level}</span>
            <span className="text-gray-300">{l.message}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
