"use client";
export function FleetAiGradMonPanel({ monitors, active, jobs, vanishing, exploding, healthy }: { monitors: number; active: number; jobs: number; vanishing: number; exploding: number; healthy: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 AI Gradient Monitor</h3>
    <div className="text-sm">{active}/{monitors} active · {jobs} jobs · ✅{healthy} healthy · ⬇️{vanishing} · ⬆️{exploding}</div>
  </div>);
}
