"use client";
export function FleetTechRadarPanel({ total, adopt, trial, assess, hold }: { total: number; adopt: number; trial: number; assess: number; hold: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📡 Tech Radar</h3>
    <div className="text-sm">✅ {adopt} adopt · 🔬 {trial} trial · 🔍 {assess} assess · ⏸️ {hold} hold</div>
  </div>);
}
