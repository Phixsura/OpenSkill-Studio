"use client";
export function FleetTelepresencePanel({ totalSessions, active, intercepts }: { totalSessions: number; active: number; intercepts: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔌 Telepresence</h3>
    <div className="text-sm">{active}/{totalSessions} connected · {intercepts} intercepts</div>
  </div>);
}
