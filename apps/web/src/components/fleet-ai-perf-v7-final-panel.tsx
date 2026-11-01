"use client";
export function FleetAiPerfV7FinalPanel({ monitors, active, p50, p99, throughput, efficiency }: { monitors: number; active: number; p50: number; p99: number; throughput: number; efficiency: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚡ AI Performance v7</h3>
    <div className="text-sm">{active}/{monitors} active · p50 {p50}ms · p99 {p99}ms · {throughput.toLocaleString()} RPS · {efficiency}% eff</div>
  </div>);
}
