"use client";
export function FleetAiChangeMgmtPanel({ systems, active, changes, approved, rejected }: { systems: number; active: number; changes: number; approved: number; rejected: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📋 AI Change Management</h3>
    <div className="text-sm">{active}/{systems} active · {changes} changes · ✅ {approved} · ❌ {rejected}</div>
  </div>);
}
