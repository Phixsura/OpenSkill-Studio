"use client";
export function FleetDevspacePanel({ total, active, sleeping }: { total: number; active: number; sleeping: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">☁️ DevSpace</h3>
    <div className="text-sm">{active} active · {sleeping} sleeping of {total}</div>
  </div>);
}
