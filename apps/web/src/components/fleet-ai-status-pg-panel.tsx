"use client";
const SC: Record<string, string> = { operational: "text-green-600", degraded: "text-yellow-600", outage: "text-red-500" };
export function FleetAiStatusPgPanel({ components, operational, degraded, outage, overall }: { components: number; operational: number; degraded: number; outage: number; overall: string; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📡 AI Status</h3>
    <div className={`text-lg font-bold ${SC[overall] ?? ""}`}>{overall.toUpperCase()}</div>
    <div className="text-xs text-gray-400">🟢 {operational} · 🟡 {degraded} · 🔴 {outage} of {components}</div>
  </div>);
}
