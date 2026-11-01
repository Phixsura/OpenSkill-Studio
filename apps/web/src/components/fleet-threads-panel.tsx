"use client";
export function FleetThreadsPanel({ active, max, pct, exhausted }: { active: number; max: number; pct: number; exhausted: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🧵 Fleet Threads</h3>
    <div className="text-sm">{active}/{max} threads ({pct}%)</div>
    {exhausted && <span className="text-xs text-red-500">⚠️ Thread pool near exhaustion</span>}
  </div>);
}
