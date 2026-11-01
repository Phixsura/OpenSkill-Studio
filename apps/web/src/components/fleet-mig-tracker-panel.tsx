"use client";
export function FleetMigTrackerPanel({ total, completed, inProgress, blocked, allDone }: { total: number; completed: number; inProgress: number; blocked: number; allDone: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔄 Migrations</h3>
    <div className="text-sm">✅ {completed} · 🔄 {inProgress} · 🚫 {blocked}</div>
    {blocked > 0 && <span className="text-xs text-red-500">⚠️ {blocked} blocked</span>}
  </div>);
}
