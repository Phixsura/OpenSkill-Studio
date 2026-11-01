"use client";

import { useState } from "react";

interface ProfileEntry {
  functionName: string;
  file: string;
  line: number;
  totalTimeMs: number;
  selfTimeMs: number;
  callCount: number;
  avgTimeMs: number;
  memoryDeltaKb: number;
}

interface ProfileSummary {
  status: string;
  totalTimeMs: number;
  totalFunctions: number;
  totalCalls: number;
  totalMemoryKb: number;
}

export function ProfilerPanel({
  summary,
  hotspots,
  byCalls,
  isProfiling,
  onStart,
  onStop,
}: {
  summary: ProfileSummary | null;
  hotspots: ProfileEntry[];
  byCalls: ProfileEntry[];
  isProfiling: boolean;
  onStart?: () => void;
  onStop?: () => void;
}) {
  const [tab, setTab] = useState<"hotspots" | "calls" | "memory">("hotspots");

  const sortedByMemory = [...hotspots].sort((a, b) => b.memoryDeltaKb - a.memoryDeltaKb);
  const displayed = tab === "hotspots" ? hotspots : tab === "calls" ? byCalls : sortedByMemory;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <h2 className="text-lg font-bold">🔬 Profiler</h2>
          {isProfiling && <span className="w-2.5 h-2.5 rounded-full bg-red-500 animate-pulse" />}
        </div>
        {isProfiling ? (
          <button onClick={onStop} className="text-sm bg-red-600 text-white px-3 py-1.5 rounded-lg">Stop</button>
        ) : (
          <button onClick={onStart} className="text-sm bg-green-600 text-white px-3 py-1.5 rounded-lg">Start Profiling</button>
        )}
      </div>

      {summary && (
        <div className="grid grid-cols-4 gap-2 text-center text-xs">
          <div className="rounded-lg border dark:border-gray-700 p-2">
            <span className="text-gray-500 block">Time</span>
            <span className="font-bold">{summary.totalTimeMs}ms</span>
          </div>
          <div className="rounded-lg border dark:border-gray-700 p-2">
            <span className="text-gray-500 block">Functions</span>
            <span className="font-bold">{summary.totalFunctions}</span>
          </div>
          <div className="rounded-lg border dark:border-gray-700 p-2">
            <span className="text-gray-500 block">Calls</span>
            <span className="font-bold">{summary.totalCalls}</span>
          </div>
          <div className="rounded-lg border dark:border-gray-700 p-2">
            <span className="text-gray-500 block">Memory</span>
            <span className="font-bold">{summary.totalMemoryKb}KB</span>
          </div>
        </div>
      )}

      <div className="flex gap-1">
        {(["hotspots", "calls", "memory"] as const).map((t) => (
          <button key={t} onClick={() => setTab(t)}
            className={`text-xs px-3 py-1 rounded-lg ${tab === t ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
            {t === "hotspots" ? "🔥 Hotspots" : t === "calls" ? "📞 By Calls" : "🧠 Memory"}
          </button>
        ))}
      </div>

      <div className="space-y-1">
        {displayed.map((entry, i) => {
          const maxTime = Math.max(...hotspots.map((e) => e.selfTimeMs), 1);
          const pct = Math.round((entry.selfTimeMs / maxTime) * 100);
          return (
            <div key={`${entry.functionName}-${entry.file}`} className="rounded-lg border dark:border-gray-700 p-2">
              <div className="flex items-center justify-between text-sm mb-1">
                <div className="flex items-center gap-2">
                  <span className="text-xs text-gray-400 w-5">#{i + 1}</span>
                  <code className="font-semibold">{entry.functionName}</code>
                  <span className="text-xs text-gray-400">{entry.file}:{entry.line}</span>
                </div>
                <span className="text-xs font-mono">{entry.selfTimeMs}ms · ×{entry.callCount}</span>
              </div>
              <div className="h-1.5 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden">
                <div className="h-full bg-red-500 rounded-full" style={{ width: `${pct}%` }} />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
