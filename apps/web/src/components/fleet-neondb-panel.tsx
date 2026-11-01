"use client";
export function FleetNeondbPanel({ projects, active, computeHours, branches }: { projects: number; active: number; computeHours: number; branches: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🟢 Neon</h3>
    <div className="text-sm">{active}/{projects} active · {computeHours}h compute · {branches} branches</div>
  </div>);
}
