"use client";

interface RuntimeProfilerProps { gcPauseMs: number; heapPct: number;
  eventLoopLagMs: number; activeHandles: number; health: string; issues: string[]; }

const HEALTH_COLORS: Record<string, string> = {
  healthy: "text-green-600", degraded: "text-yellow-600", critical: "text-red-600",
};

export function RuntimeProfiler({ gcPauseMs, heapPct, eventLoopLagMs, activeHandles, health, issues }: RuntimeProfilerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">⚡ Runtime Profiler</h3>
        <span className={`text-xs font-medium ${HEALTH_COLORS[health] ?? ""}`}>{health}</span>
      </div>
      <div className="grid grid-cols-4 gap-px bg-gray-200 dark:bg-gray-700 border-b dark:border-gray-700">
        {[{ l: "GC Pause", v: `${gcPauseMs}ms` }, { l: "Heap", v: `${heapPct}%` },
          { l: "Loop Lag", v: `${eventLoopLagMs}ms` }, { l: "Handles", v: activeHandles }].map(s => (
          <div key={s.l} className="bg-white dark:bg-gray-900 p-2 text-center">
            <div className="text-sm font-bold">{s.v}</div>
            <div className="text-[9px] text-gray-400">{s.l}</div>
          </div>
        ))}
      </div>
      {issues.length > 0 && (
        <div className="p-3">
          {issues.map((i, idx) => <div key={idx} className="text-xs text-red-500 py-0.5">⚠ {i}</div>)}
        </div>
      )}
    </div>
  );
}
