"use client";
export function FleetTrafficShapePanel({ routes, active, totalWeight, balanced }: { routes: number; active: number; totalWeight: number; balanced: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔀 Traffic Shaping</h3>
    <div className="text-sm">{active}/{routes} active · weight {totalWeight}</div>
    <span className={`text-xs ${balanced ? "text-green-600" : "text-blue-500"}`}>{balanced ? "⚖️ Balanced" : "🔀 Weighted"}</span>
  </div>);
}
