"use client";
export function FleetAiLrSchedPanel({ schedulers, active, jobs, strategies, adjustments }: { schedulers: number; active: number; jobs: number; strategies: string[]; adjustments: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📈 AI LR Scheduler</h3>
    <div className="text-sm">{active}/{schedulers} active · {jobs} jobs · {strategies.join(", ")} · {adjustments.toLocaleString()} adj</div>
  </div>);
}
