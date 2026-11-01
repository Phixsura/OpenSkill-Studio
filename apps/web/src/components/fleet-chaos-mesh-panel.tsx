"use client";
export function FleetChaosMeshPanel({ total, running, paused, completed }: { total: number; running: number; paused: number; completed: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌪️ Chaos Mesh</h3>
    <div className="text-sm">{running}🔄 {paused}⏸️ {completed}✅ of {total}</div>
  </div>);
}
