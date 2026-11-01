"use client";
export function FleetWaypointPanel({ total, successful, released, unreleased }: { total: number; successful: number; released: number; unreleased: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🧭 Waypoint</h3>
    <div className="text-sm">{successful}/{total} successful · {released} released</div>
    {unreleased > 0 && <span className="text-xs text-blue-500">{unreleased} awaiting release</span>}
  </div>);
}
