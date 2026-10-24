"use client";
const SC: Record<string, string> = { operational: "text-green-600", degraded: "text-yellow-600", outage: "text-red-500" };
export function FleetStatusPagePanel({ components, operational, degraded, outage, overall }: { components: number; operational: number; degraded: number; outage: number; overall: string; }) {
  return (<div className="rounded-2xl border-2 dark:border-gray-600 p-6 text-center">
    <h3 className="font-semibold mb-2">📡 Status Page</h3>
    <div className={`text-xl font-bold ${SC[overall] ?? ""}`}>{overall.toUpperCase()}</div>
    <div className="text-xs text-gray-400 mt-1">🟢 {operational} · 🟡 {degraded} · 🔴 {outage} of {components}</div>
  </div>);
}
