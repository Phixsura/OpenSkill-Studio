"use client";
export function FleetAiHealthAggPanel({ aggregators, active, services, healthy, degraded, down, healthPct }: { aggregators: number; active: number; services: number; healthy: number; degraded: number; down: number; healthPct: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💚 AI Health Aggregator</h3>
    <div className="text-sm">{active}/{aggregators} active · 🟢 {healthy} · 🟡 {degraded} · 🔴 {down} of {services} · {healthPct}%</div>
  </div>);
}
