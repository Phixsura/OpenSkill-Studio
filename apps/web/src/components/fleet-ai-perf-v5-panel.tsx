"use client";
export function FleetAiPerfV5Panel({ monitors, active, p50, p99, rps }: { monitors: number; active: number; p50: number; p99: number; rps: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚡ AI Performance v5</h3>
    <div className="text-sm">{active}/{monitors} active · p50 {p50}ms · p99 {p99}ms · {rps.toLocaleString()} RPS</div>
  </div>);
}
