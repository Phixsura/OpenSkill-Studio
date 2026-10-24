"use client";
const AC: Record<string, string> = { scale_up: "text-red-500", scale_down: "text-blue-500", steady: "text-green-600" };
export function FleetScaleDecPanel({ cpuPct, memPct, queueDepth, action }: { cpuPct: number; memPct: number; queueDepth: number; action: string; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚖️ Scaling Decision</h3>
    <div className={`text-lg font-bold ${AC[action] ?? ""}`}>{action.replace("_", " ").toUpperCase()}</div>
    <div className="text-xs text-gray-400">CPU {cpuPct}% · Mem {memPct}% · Queue {queueDepth}</div>
  </div>);
}
