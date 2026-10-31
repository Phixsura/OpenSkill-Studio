"use client";

import { useState } from "react";

interface SandboxLog {
  id: string;
  level: "debug" | "info" | "warn" | "error";
  message: string;
  timestamp: string;
  source: string;
}

interface SandboxState {
  status: "running" | "paused" | "stopped" | "crashed";
  pid: string;
  uptime: string;
  cpuPercent: number;
  memoryMb: number;
  memoryLimitMb: number;
}

export function SandboxDebuggerPanel({
  logs,
  state,
  onPause,
  onResume,
  onStop,
  onClearLogs,
}: {
  logs: SandboxLog[];
  state: SandboxState;
  onPause?: () => void;
  onResume?: () => void;
  onStop?: () => void;
  onClearLogs?: () => void;
}) {
  const [levelFilter, setLevelFilter] = useState<string>("all");

  const filtered = levelFilter === "all" ? logs : logs.filter((l) => l.level === levelFilter);

  const levelColors: Record<string, string> = {
    debug: "text-gray-400",
    info: "text-blue-400",
    warn: "text-yellow-400",
    error: "text-red-400",
  };

  const statusColors: Record<string, string> = {
    running: "bg-green-500",
    paused: "bg-yellow-500",
    stopped: "bg-gray-400",
    crashed: "bg-red-500",
  };

  const memPercent = Math.round((state.memoryMb / state.memoryLimitMb) * 100);

  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      {/* Header */}
      <div className="bg-gray-50 dark:bg-gray-800 px-4 py-3 flex items-center justify-between border-b dark:border-gray-700">
        <div className="flex items-center gap-3">
          <h2 className="font-bold">🐞 Sandbox Debugger</h2>
          <div className="flex items-center gap-1.5">
            <div className={`w-2 h-2 rounded-full ${statusColors[state.status]} ${state.status === "running" ? "animate-pulse" : ""}`} />
            <span className="text-xs text-gray-500">{state.status} · PID {state.pid} · {state.uptime}</span>
          </div>
        </div>
        <div className="flex gap-2">
          {state.status === "running" && (
            <button onClick={onPause} className="text-xs border dark:border-gray-600 px-2 py-1 rounded">⏸ Pause</button>
          )}
          {state.status === "paused" && (
            <button onClick={onResume} className="text-xs border dark:border-gray-600 px-2 py-1 rounded">▶ Resume</button>
          )}
          <button onClick={onStop} className="text-xs text-red-500 border border-red-300 dark:border-red-700 px-2 py-1 rounded">⏹ Stop</button>
        </div>
      </div>

      {/* Resources */}
      <div className="px-4 py-2 flex gap-6 text-xs border-b dark:border-gray-700 bg-gray-50/50 dark:bg-gray-800/50">
        <div>CPU: <span className={state.cpuPercent > 80 ? "text-red-500 font-bold" : ""}>{state.cpuPercent}%</span></div>
        <div>Memory: {state.memoryMb}/{state.memoryLimitMb}MB ({memPercent}%)</div>
      </div>

      {/* Log controls */}
      <div className="px-4 py-2 flex items-center justify-between border-b dark:border-gray-700">
        <div className="flex gap-1">
          {["all", "debug", "info", "warn", "error"].map((lvl) => (
            <button
              key={lvl}
              onClick={() => setLevelFilter(lvl)}
              className={`text-xs px-2 py-0.5 rounded ${levelFilter === lvl ? "bg-blue-600 text-white" : "text-gray-500"}`}
            >
              {lvl}
            </button>
          ))}
        </div>
        <button onClick={onClearLogs} className="text-xs text-gray-400 hover:text-gray-600">Clear</button>
      </div>

      {/* Logs */}
      <div className="bg-gray-900 p-3 max-h-64 overflow-y-auto font-mono text-xs">
        {filtered.map((log) => (
          <div key={log.id} className="flex gap-2 py-0.5">
            <span className="text-gray-600 shrink-0">{log.timestamp}</span>
            <span className={`shrink-0 w-12 ${levelColors[log.level]}`}>[{log.level.toUpperCase()}]</span>
            <span className="text-gray-300">{log.message}</span>
          </div>
        ))}
        {filtered.length === 0 && <div className="text-gray-600">No logs to display</div>}
      </div>
    </div>
  );
}
